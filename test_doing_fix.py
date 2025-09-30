#!/usr/bin/env python3
"""
Test to verify DOING is not extracted as a ticker symbol
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.agent_orchestrator import AgentOrchestrator

async def test_doing_extraction():
    """Test that DOING is not extracted from queries"""
    print("🧪 Testing DOING Symbol Extraction Fix\n")
    print("=" * 60)
    
    # Test queries that previously incorrectly extracted DOING
    test_queries = [
        "What is the market doing today?",
        "How is AAPL doing?",
        "What are tech stocks doing?",
        "Is everything doing well?",
        "Why is the market doing poorly?"
    ]
    
    orchestrator = AgentOrchestrator()
    
    print("\n✅ PASS/❌ FAIL | Query | Extracted Symbol")
    print("-" * 60)
    
    all_passed = True
    for query in test_queries:
        # Test the extraction
        extracted = orchestrator._extract_symbol_from_query(query)
        
        # DOING should NOT be extracted
        passed = extracted != "DOING"
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        symbol_str = f"'{extracted}'" if extracted else "None"
        print(f"{status} | {query:<40} | {symbol_str}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✨ All tests passed! DOING is properly excluded from ticker extraction.")
    else:
        print("⚠️  Some tests failed. DOING is still being extracted as a ticker.")
        
    # Test that valid tickers still work
    print("\n🧪 Testing Valid Ticker Extraction")
    print("-" * 60)
    
    valid_queries = [
        ("Show me AAPL chart", "AAPL"),
        ("What is TSLA price?", "TSLA"),
        ("Load NVDA", "NVDA"),
        ("BTC-USD chart", "BTC-USD")
    ]
    
    print("\n✅ PASS/❌ FAIL | Query | Expected | Extracted")
    print("-" * 60)
    
    for query, expected in valid_queries:
        extracted = orchestrator._extract_symbol_from_query(query)
        passed = extracted == expected
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {query:<25} | {expected:<8} | {extracted or 'None'}")
    
    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(test_doing_extraction())