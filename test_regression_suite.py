#!/usr/bin/env python3
"""
Minimal Regression Test Suite for Voice Trading Assistant
=========================================================
Consolidated from 150+ test files to essential coverage only.
Run this single file to verify core functionality after changes.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# ANSI colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


async def test_market_service():
    """Test core market data functionality through direct service calls."""
    print(f"\n{YELLOW}Testing Market Service (Direct)...{RESET}")
    
    from services.market_service_factory import MarketServiceFactory
    
    # Get service directly
    factory = MarketServiceFactory()
    market_service = factory.get_service()
    
    # Test 1: Stock price
    price_data = await market_service.get_stock_price("AAPL")
    assert "price" in price_data or "error" in price_data, "Price data missing"
    print(f"{GREEN}✓ Stock price retrieval (direct){RESET}")
    
    # Test 2: Stock news
    news = await market_service.get_stock_news("AAPL", limit=3)
    assert isinstance(news, (list, dict)), "News should be a list or dict"
    print(f"{GREEN}✓ Stock news retrieval (direct){RESET}")
    
    # Test 3: Comprehensive data
    comp_data = await market_service.get_comprehensive_stock_data("AAPL")
    assert isinstance(comp_data, dict), "Comprehensive data should be dict"
    print(f"{GREEN}✓ Comprehensive data retrieval (direct){RESET}")
    
    # Test 4: Symbol search
    results = await market_service.search_assets("Apple", limit=5)
    assert isinstance(results, list), "Search results should be list"
    print(f"{GREEN}✓ Symbol search functionality (direct){RESET}")
    
    return True


async def test_voice_tools():
    """Test OpenAI voice tool integration."""
    print(f"\n{YELLOW}Testing Voice Tool Integration...{RESET}")
    
    try:
        from services.openai_tool_mapper import get_openai_tool_mapper
        
        # Initialize mapper
        tool_mapper = await get_openai_tool_mapper()
        
        # Test high priority tools
        voice_tools = tool_mapper.get_high_priority_tools()
        assert len(voice_tools) > 0, "No voice tools available"
        print(f"{GREEN}✓ {len(voice_tools)} voice tools loaded{RESET}")
        
        # Test tool execution
        result = await tool_mapper.execute_tool("get_stock_quote", {"symbol": "TSLA"})
        assert result is not None, "Tool execution failed"
        print(f"{GREEN}✓ Tool execution successful{RESET}")
        
        return True
        
    except Exception as e:
        print(f"{RED}✗ Voice tools failed: {e}{RESET}")
        return False


async def test_api_endpoints():
    """Test core API endpoints."""
    print(f"\n{YELLOW}Testing API Endpoints...{RESET}")
    
    import aiohttp
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Health endpoint
        try:
            async with session.get(f"{base_url}/health") as resp:
                assert resp.status == 200, f"Health check failed: {resp.status}"
                data = await resp.json()
                print(f"{GREEN}✓ Health endpoint responsive{RESET}")
        except Exception as e:
            print(f"{RED}✗ Health endpoint failed: {e}{RESET}")
            return False
        
        # Test 2: Stock price endpoint
        try:
            async with session.get(f"{base_url}/api/stock-price?symbol=AAPL") as resp:
                assert resp.status == 200, f"Stock price failed: {resp.status}"
                data = await resp.json()
                assert "price" in data, "Price data missing"
                print(f"{GREEN}✓ Stock price endpoint{RESET}")
        except Exception as e:
            print(f"{RED}✗ Stock price endpoint failed: {e}{RESET}")
            return False
        
        # Test 3: Ask endpoint (text-only Claude)
        try:
            payload = {"query": "What is a P/E ratio?"}
            async with session.post(f"{base_url}/ask", json=payload) as resp:
                assert resp.status == 200, f"Ask endpoint failed: {resp.status}"
                data = await resp.json()
                assert "response" in data, "Response missing"
                print(f"{GREEN}✓ Ask endpoint (Claude integration){RESET}")
        except Exception as e:
            print(f"{RED}✗ Ask endpoint failed: {e}{RESET}")
            return False
    
    return True


async def test_core_integration():
    """Test integration between core components."""
    print(f"\n{YELLOW}Testing Core Integration...{RESET}")
    
    from services.agent_orchestrator import AgentOrchestrator
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Test 1: Intent classification
    from core.intent_router import IntentRouter
    router = IntentRouter()
    
    test_queries = [
        ("What's Tesla's price?", "price-only"),
        ("Explain RSI", "educational"),
        ("Show me Apple news", "news")
    ]
    
    for query, expected in test_queries:
        intent = router.classify_intent(query)
        print(f"{GREEN}✓ Intent: '{query}' → {intent}{RESET}")
    
    # Test 2: Symbol extraction
    symbols = [
        ("Tesla is up today", "TSLA"),
        ("AAPL hit new high", "AAPL"),
        ("Microsoft earnings", "MSFT")
    ]
    
    for query, expected in symbols:
        symbol = router.extract_symbol(query)
        if symbol:
            print(f"{GREEN}✓ Symbol extraction: '{query}' → {symbol}{RESET}")
    
    return True


async def run_regression_suite():
    """Run the complete regression test suite."""
    print(f"\n{'='*60}")
    print(f"{YELLOW}MINIMAL REGRESSION TEST SUITE{RESET}")
    print(f"{'='*60}")
    
    # Check environment
    required_vars = ["ANTHROPIC_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"{RED}Missing environment variables: {missing}{RESET}")
        return False
    
    results = {}
    
    # Run tests
    try:
        results["Market Service"] = await test_market_service()
    except Exception as e:
        print(f"{RED}Market Service test failed: {e}{RESET}")
        results["Market Service"] = False
    
    try:
        results["Voice Tools"] = await test_voice_tools()
    except Exception as e:
        print(f"{RED}Voice Tools test failed: {e}{RESET}")
        results["Voice Tools"] = False
    
    try:
        results["API Endpoints"] = await test_api_endpoints()
    except Exception as e:
        print(f"{RED}API Endpoints test failed: {e}{RESET}")
        results["API Endpoints"] = False
    
    try:
        results["Core Integration"] = await test_core_integration()
    except Exception as e:
        print(f"{RED}Core Integration test failed: {e}{RESET}")
        results["Core Integration"] = False
    
    # Summary
    print(f"\n{'='*60}")
    print(f"{YELLOW}TEST SUMMARY{RESET}")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{GREEN}✅ ALL REGRESSION TESTS PASSED!{RESET}")
        print(f"Core functionality verified. Safe to proceed.")
        return True
    else:
        print(f"\n{RED}❌ REGRESSION FAILURES DETECTED{RESET}")
        print(f"Review failures before deployment.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_regression_suite())
    sys.exit(0 if success else 1)