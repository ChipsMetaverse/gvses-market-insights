#!/usr/bin/env python3
"""
API-Based Regression Test Suite
================================
Tests all API endpoints directly via HTTP for Docker compatibility.
"""

import asyncio
import httpx
import json
import time
import uuid
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Test configuration
BASE_URL = os.getenv("TEST_URL", "http://localhost:8000")
TIMEOUT_SECONDS = 30

class APIRegressionTestSuite:
    """Comprehensive API regression test suite."""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.results: List[Dict[str, Any]] = []
        self.session_id = str(uuid.uuid4())
        
    async def run_test(self, name: str, test_func) -> Dict[str, Any]:
        """Run a single test with error handling."""
        print(f"  Running: {name}...", end=" ")
        start_time = time.time()
        
        try:
            result = await test_func()
            elapsed = time.time() - start_time
            
            if result:
                print(f"✅ ({elapsed:.2f}s)")
                return {"name": name, "passed": True, "time": elapsed}
            else:
                print(f"❌ ({elapsed:.2f}s)")
                return {"name": name, "passed": False, "time": elapsed, "error": "Test assertion failed"}
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ ({elapsed:.2f}s) - {str(e)}")
            return {"name": name, "passed": False, "time": elapsed, "error": str(e)}
    
    # === Core API Tests ===
    
    async def test_health_endpoint(self) -> bool:
        """Test /health endpoint."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(f"{self.base_url}/health")
            return response.status_code == 200 and "status" in response.json()
    
    async def test_ask_endpoint_basic(self) -> bool:
        """Test /ask endpoint with basic query."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{self.base_url}/ask",
                json={"query": "What is RSI?", "session_id": str(uuid.uuid4())}
            )
            data = response.json()
            return response.status_code == 200 and "response" in data
    
    async def test_ask_with_history(self) -> bool:
        """Test /ask maintains conversation context."""
        session_id = str(uuid.uuid4())
        
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            # First message
            response1 = await client.post(
                f"{self.base_url}/ask",
                json={"query": "Remember this: I like AAPL stock", "session_id": session_id, "include_history": True}
            )
            if response1.status_code != 200:
                return False
            
            # Wait for DB persistence
            await asyncio.sleep(1.5)
            
            # Second message referencing first
            response2 = await client.post(
                f"{self.base_url}/ask",
                json={"query": "What stock did I mention?", "session_id": session_id, "include_history": True}
            )
            
            if response2.status_code != 200:
                return False
                
            data = response2.json()
            response_text = data.get("response", "").lower()
            
            # Check if response mentions AAPL or Apple
            return "aapl" in response_text or "apple" in response_text
    
    async def test_cache_performance(self) -> bool:
        """Test cache returns faster on second query."""
        # Use unique query variation to test normalization
        query1 = "What is MACD indicator?"
        query2 = "what's macd?"  # Should normalize to same cache key
        
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            # First query (may or may not be cached)
            start1 = time.time()
            response1 = await client.post(
                f"{self.base_url}/ask",
                json={"query": query1, "session_id": str(uuid.uuid4())}
            )
            time1 = time.time() - start1
            
            if response1.status_code != 200:
                return False
            
            # Second query with variation (should hit cache due to normalization)
            start2 = time.time()
            response2 = await client.post(
                f"{self.base_url}/ask",
                json={"query": query2, "session_id": str(uuid.uuid4())}
            )
            time2 = time.time() - start2
            
            # Cache should be faster or at least similar
            return response2.status_code == 200 and time2 <= (time1 + 0.5)
    
    async def test_metrics_endpoint(self) -> bool:
        """Test /metrics endpoint."""
        token = os.getenv("METRICS_TOKEN", "test-token")
        
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{self.base_url}/metrics",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should work or return 401 (auth required)
            return response.status_code in [200, 401]
    
    # === Market Data API Tests ===
    
    async def test_stock_price_endpoint(self) -> bool:
        """Test /api/stock-price endpoint."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{self.base_url}/api/stock-price",
                params={"symbol": "AAPL"}
            )
            
            if response.status_code != 200:
                return False
                
            data = response.json()
            return "price" in data and data["price"] > 0
    
    async def test_stock_history_endpoint(self) -> bool:
        """Test /api/stock-history endpoint."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{self.base_url}/api/stock-history",
                params={"symbol": "TSLA", "days": 5}
            )
            
            if response.status_code != 200:
                return False
                
            data = response.json()
            return "candles" in data and len(data["candles"]) > 0
    
    async def test_stock_news_endpoint(self) -> bool:
        """Test /api/stock-news endpoint."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{self.base_url}/api/stock-news",
                params={"symbol": "NVDA"}
            )
            
            if response.status_code != 200:
                return False
                
            data = response.json()
            return "news" in data and isinstance(data["news"], list)
    
    async def test_market_overview_endpoint(self) -> bool:
        """Test /api/market-overview endpoint."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(f"{self.base_url}/api/market-overview")
            
            if response.status_code != 200:
                return False
                
            data = response.json()
            return "indices" in data or "market_status" in data
    
    # === Error Handling Tests ===
    
    async def test_invalid_symbol_handling(self) -> bool:
        """Test handling of invalid stock symbol."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{self.base_url}/api/stock-price",
                params={"symbol": "INVALID123XYZ"}
            )
            
            # Should return 404 or handle gracefully
            return response.status_code in [200, 404]
    
    async def test_missing_parameters(self) -> bool:
        """Test handling of missing required parameters."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            # Missing symbol parameter
            response = await client.get(f"{self.base_url}/api/stock-price")
            
            # Should return 400 or 422 for validation error
            return response.status_code in [400, 422]
    
    async def test_empty_query_handling(self) -> bool:
        """Test handling of empty query."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{self.base_url}/ask",
                json={"query": "", "session_id": str(uuid.uuid4())}
            )
            
            # Should handle gracefully
            return response.status_code in [200, 400, 422]
    
    # === Performance Tests ===
    
    async def test_response_time_sla(self) -> bool:
        """Test response times meet SLA."""
        queries = [
            ("What is RSI?", 5.0),  # Educational query
            ("Get AAPL price", 3.0),  # Simple tool query
        ]
        
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            for query, max_time in queries:
                start = time.time()
                response = await client.post(
                    f"{self.base_url}/ask",
                    json={"query": query, "session_id": str(uuid.uuid4())}
                )
                duration = time.time() - start
                
                if response.status_code != 200:
                    print(f"    SLA test failed: {query} returned {response.status_code}")
                    return False
                if duration > max_time:
                    print(f"    SLA test failed: {query} took {duration:.2f}s > {max_time}s")
                    return False
        
        return True
    
    async def test_concurrent_load(self) -> bool:
        """Test handling of concurrent requests."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            # Send 5 concurrent requests
            tasks = []
            for i in range(5):
                task = client.get(
                    f"{self.base_url}/api/stock-price",
                    params={"symbol": ["AAPL", "TSLA", "NVDA", "SPY", "MSFT"][i]}
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successful responses
            success_count = sum(
                1 for r in responses 
                if not isinstance(r, Exception) and r.status_code == 200
            )
            
            # At least 80% should succeed
            return success_count >= 4
    
    async def run_all_tests(self):
        """Run all regression tests."""
        print("\n" + "="*60)
        print("API REGRESSION TEST SUITE")
        print("="*60)
        print(f"Target: {self.base_url}")
        print(f"Timeout: {TIMEOUT_SECONDS}s per test")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n📋 Running Tests:\n")
        
        # Define all tests
        tests = [
            # Core API Tests
            ("Health Endpoint", self.test_health_endpoint),
            ("Basic /ask Query", self.test_ask_endpoint_basic),
            ("Conversation History", self.test_ask_with_history),
            ("Cache Performance", self.test_cache_performance),
            ("Metrics Endpoint", self.test_metrics_endpoint),
            
            # Market Data API Tests
            ("Stock Price API", self.test_stock_price_endpoint),
            ("Stock History API", self.test_stock_history_endpoint),
            ("Stock News API", self.test_stock_news_endpoint),
            ("Market Overview API", self.test_market_overview_endpoint),
            
            # Error Handling Tests
            ("Invalid Symbol Handling", self.test_invalid_symbol_handling),
            ("Missing Parameters", self.test_missing_parameters),
            ("Empty Query Handling", self.test_empty_query_handling),
            
            # Performance Tests
            ("Response Time SLA", self.test_response_time_sla),
            ("Concurrent Load", self.test_concurrent_load),
        ]
        
        # Run tests
        for name, test_func in tests:
            result = await self.run_test(name, test_func)
            self.results.append(result)
        
        # Calculate statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        total_time = sum(r["time"] for r in self.results)
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Average Time: {total_time/total:.2f}s per test")
        
        # Show failures if any
        if failed > 0:
            print("\n❌ Failed Tests:")
            for r in self.results:
                if not r["passed"]:
                    print(f"  - {r['name']}: {r.get('error', 'Unknown error')}")
        
        # Success criteria
        print("\n" + "="*60)
        if pass_rate >= 95:
            print("✅ REGRESSION SUITE PASSED (≥95% pass rate)")
            print("✅ PRODUCTION READY")
        elif pass_rate >= 80:
            print("⚠️  REGRESSION SUITE MARGINAL (80-94% pass rate)")
            print("⚠️  REVIEW FAILURES BEFORE DEPLOYMENT")
        else:
            print("❌ REGRESSION SUITE FAILED (<80% pass rate)")
            print("❌ NOT READY FOR DEPLOYMENT")
        print("="*60 + "\n")
        
        return pass_rate >= 95

async def main():
    """Main entry point."""
    suite = APIRegressionTestSuite()
    success = await suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    # For Docker compatibility
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    asyncio.run(main())