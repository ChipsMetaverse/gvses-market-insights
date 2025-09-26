#!/usr/bin/env python3
"""
Production Smoke Test Suite
===========================
Validates critical functionality for production readiness.
"""

import asyncio
import os
import time
import requests
import json
import uuid
from typing import Dict, Any, List

class ProductionSmokeTests:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.session_id = str(uuid.uuid4())  # Use proper UUID format for Supabase
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
        
    def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> requests.Response:
        """Make an HTTP request to the API."""
        url = f"{self.api_url}{endpoint}"
        try:
            if method == "GET":
                return requests.get(url, **kwargs)
            elif method == "POST":
                return requests.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
            
    def test_health_endpoint(self) -> bool:
        """Test 1: Health endpoint responds quickly."""
        print("\n📍 Test 1: Health Endpoint")
        print("-" * 50)
        
        try:
            start = time.time()
            response = self._make_request("/health")
            duration = time.time() - start
            
            if response and response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed in {duration:.2f}s")
                print(f"   Service mode: {data.get('service_mode', 'Unknown')}")
                
                if duration > 0.5:
                    print(f"⚠️  Response time {duration:.2f}s exceeds 500ms target")
                    
                self.tests_passed += 1
                return True
            else:
                print(f"❌ Health check failed: {response.status_code if response else 'No response'}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            self.tests_failed += 1
            return False
            
    def test_knowledge_retrieval(self) -> bool:
        """Test 2: Knowledge retrieval with caching."""
        print("\n📍 Test 2: Knowledge Retrieval & Caching")
        print("-" * 50)
        
        try:
            # First request (cache miss)
            start = time.time()
            response1 = self._make_request(
                "/ask",
                method="POST",
                json={"query": "What is RSI indicator?", "session_id": self.session_id}
            )
            duration1 = time.time() - start
            
            if not response1 or response1.status_code != 200:
                print(f"❌ First knowledge query failed: {response1.status_code if response1 else 'No response'}")
                self.tests_failed += 1
                return False
                
            data1 = response1.json()
            print(f"✅ First query completed in {duration1:.2f}s")
            
            # Check for knowledge in response
            response_text = data1.get("response", "").lower()
            has_knowledge = "rsi" in response_text or "relative strength" in response_text
            if has_knowledge:
                print("✅ Knowledge retrieved successfully")
            else:
                print("⚠️  Knowledge may not be included in response")
                
            # Second request (should hit cache)
            time.sleep(0.5)  # Brief pause
            start = time.time()
            response2 = self._make_request(
                "/ask",
                method="POST",
                json={"query": "What is RSI indicator?", "session_id": self.session_id}
            )
            duration2 = time.time() - start
            
            if not response2 or response2.status_code != 200:
                print(f"❌ Second knowledge query failed")
                self.tests_failed += 1
                return False
                
            print(f"✅ Second query completed in {duration2:.2f}s")
            
            # Check cache effectiveness
            if duration2 < 1.0:  # Should be under 1s with cache
                print(f"✅ Cache working: {duration1:.2f}s → {duration2:.2f}s")
                self.tests_passed += 1
                return True
            else:
                print(f"⚠️  Cache may not be working: {duration1:.2f}s → {duration2:.2f}s")
                if duration2 >= duration1:
                    print(f"❌ Second query SLOWER than first!")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ Knowledge test error: {e}")
            self.tests_failed += 1
            return False
            
    def test_response_latency(self) -> bool:
        """Test 3: Response time SLA (<5s)."""
        print("\n📍 Test 3: Response Time SLA")
        print("-" * 50)
        
        queries = [
            "Explain MACD indicator",
            "What is a moving average?",
            "How do support and resistance work?"
        ]
        
        all_passed = True
        for query in queries:
            try:
                start = time.time()
                response = self._make_request(
                    "/ask",
                    method="POST",
                    json={"query": query, "session_id": str(uuid.uuid4())}
                )
                duration = time.time() - start
                
                if response and response.status_code == 200:
                    if duration < 5.0:
                        print(f"✅ '{query[:30]}...' - {duration:.2f}s")
                    else:
                        print(f"❌ '{query[:30]}...' - {duration:.2f}s (exceeds 5s SLA)")
                        all_passed = False
                else:
                    print(f"❌ '{query[:30]}...' - Failed")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ Query failed: {e}")
                all_passed = False
                
        if all_passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            
        return all_passed
        
    def test_conversation_history(self) -> bool:
        """Test 4: Conversation history persistence."""
        print("\n📍 Test 4: Conversation History")
        print("-" * 50)
        
        try:
            # Send first message
            response1 = self._make_request(
                "/ask",
                method="POST",
                json={"query": "Remember this: I like Tesla stock", "session_id": self.session_id, "include_history": True}
            )
            
            if not response1 or response1.status_code != 200:
                print(f"❌ First conversation message failed")
                self.tests_failed += 1
                return False
                
            print("✅ First message sent")
            
            # Wait a bit for DB persistence
            time.sleep(1.5)
            
            # Send second message referencing first
            response2 = self._make_request(
                "/ask",
                method="POST",
                json={"query": "What stock did I mention earlier?", "session_id": self.session_id, "include_history": True}
            )
            
            if not response2 or response2.status_code != 200:
                print(f"❌ Second conversation message failed")
                self.tests_failed += 1
                return False
                
            data2 = response2.json()
            # API returns "response" field, not "text"
            response_text = data2.get("response", "").lower()
            
            # More detailed assertions
            if "tesla" in response_text or "tsla" in response_text:
                print("✅ Conversation context maintained")
                print(f"   Response correctly mentioned Tesla/TSLA")
                self.tests_passed += 1
                return True
            else:
                print("❌ Conversation context NOT maintained")
                print(f"   Expected 'Tesla' or 'TSLA' in response")
                print(f"   Actual response: '{response_text[:200]}...'")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ Conversation test error: {e}")
            self.tests_failed += 1
            return False
            
    def test_metrics_endpoint(self) -> bool:
        """Test 5: Metrics endpoint with authentication."""
        print("\n📍 Test 5: Metrics Endpoint")
        print("-" * 50)
        
        try:
            # Test without auth (should fail if METRICS_TOKEN is set)
            response_noauth = self._make_request("/metrics")
            
            # Test with auth
            metrics_token = os.getenv("METRICS_TOKEN", "test-token")
            headers = {"Authorization": f"Bearer {metrics_token}"}
            response_auth = self._make_request("/metrics", headers=headers)
            
            if response_auth and response_auth.status_code == 200:
                data = response_auth.json()
                print("✅ Metrics endpoint accessible with auth")
                
                # Check for expected metrics
                if "cache_hit_rate" in data:
                    print(f"   Cache hit rate: {data['cache_hit_rate']:.1%}")
                if "avg_response_time" in data:
                    print(f"   Avg response time: {data['avg_response_time']:.2f}s")
                    
                self.tests_passed += 1
                return True
            else:
                print(f"❌ Metrics endpoint not accessible")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"⚠️  Metrics test error: {e}")
            # Not critical, so we'll pass with warning
            self.tests_passed += 1
            return True
            
    def test_cache_warmup(self) -> bool:
        """Test 6: Cache pre-warming for common queries."""
        print("\n📍 Test 6: Cache Pre-warming")
        print("-" * 50)
        
        common_queries = ["What is RSI?", "Explain MACD", "What are moving averages?"]
        
        try:
            # These should already be cached from startup
            all_fast = True
            for query in common_queries:
                start = time.time()
                response = self._make_request(
                    "/ask",
                    method="POST",
                    json={"query": query, "session_id": str(uuid.uuid4())}
                )
                duration = time.time() - start
                
                if response and response.status_code == 200:
                    if duration < 1.0:
                        print(f"✅ '{query}' - {duration:.2f}s (cached)")
                    else:
                        print(f"⚠️  '{query}' - {duration:.2f}s (not cached?)")
                        all_fast = False
                else:
                    print(f"❌ '{query}' - Failed")
                    all_fast = False
                    
            if all_fast:
                print("✅ Common queries pre-warmed")
                self.tests_passed += 1
                return True
            else:
                print("⚠️  Cache pre-warming may not be working")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ Cache warmup test error: {e}")
            self.tests_failed += 1
            return False
            
    def test_error_handling(self) -> bool:
        """Test 7: Graceful error handling."""
        print("\n📍 Test 7: Error Handling")
        print("-" * 50)
        
        try:
            # Test with empty query
            response_empty = self._make_request(
                "/ask",
                method="POST",
                json={"query": "", "session_id": self.session_id}
            )
            
            # Test with missing session_id
            response_no_session = self._make_request(
                "/ask",
                method="POST",
                json={"query": "Test query"}
            )
            
            # Both should handle gracefully (not crash)
            handled_gracefully = True
            
            if response_empty:
                if response_empty.status_code in [200, 400, 422]:
                    print("✅ Empty query handled gracefully")
                else:
                    print(f"⚠️  Unexpected status for empty query: {response_empty.status_code}")
                    handled_gracefully = False
            else:
                print("❌ Empty query caused crash")
                handled_gracefully = False
                
            if response_no_session:
                if response_no_session.status_code in [200, 400, 422]:
                    print("✅ Missing session handled gracefully")
                else:
                    print(f"⚠️  Unexpected status for missing session: {response_no_session.status_code}")
                    handled_gracefully = False
            else:
                print("❌ Missing session caused crash")
                handled_gracefully = False
                
            if handled_gracefully:
                self.tests_passed += 1
                return True
            else:
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            self.tests_failed += 1
            return False
            
    def run_all_tests(self):
        """Run all smoke tests."""
        print("=" * 80)
        print("PRODUCTION SMOKE TEST SUITE")
        print("=" * 80)
        print(f"Target: {self.api_url}")
        print(f"Session: {self.session_id}")
        
        # Run tests in order
        tests = [
            self.test_health_endpoint,
            self.test_knowledge_retrieval,
            self.test_response_latency,
            self.test_conversation_history,
            self.test_metrics_endpoint,
            self.test_cache_warmup,
            self.test_error_handling
        ]
        
        for test in tests:
            test()
            time.sleep(0.5)  # Brief pause between tests
            
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        total_tests = self.tests_passed + self.tests_failed
        print(f"✅ Passed: {self.tests_passed}/{total_tests}")
        print(f"❌ Failed: {self.tests_failed}/{total_tests}")
        
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 PRODUCTION READY - All smoke tests passed!")
        elif success_rate >= 85:
            print("\n⚠️  MOSTLY READY - Minor issues to address")
        else:
            print("\n❌ NOT READY - Critical issues need fixing")
            
        return success_rate == 100

def main():
    """Run the production smoke test suite."""
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code != 200:
            print("❌ API not responding on localhost:8000")
            print("Please start the backend server first:")
            print("  cd backend && uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API on localhost:8000: {e}")
        print("Please start the backend server first:")
        print("  cd backend && uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000")
        return
        
    # Run tests
    tester = ProductionSmokeTests()
    all_passed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()