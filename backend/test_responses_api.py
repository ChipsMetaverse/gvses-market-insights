#!/usr/bin/env python3
"""Test script to verify Responses API is being used"""

import asyncio
import json
from services.agent_orchestrator import get_orchestrator

async def test_responses_api():
    """Test if Responses API is being activated"""
    orchestrator = get_orchestrator()
    
    print("=" * 60)
    print("RESPONSES API TEST")
    print("=" * 60)
    
    # Check if Responses API is detected
    has_responses = orchestrator._has_responses_support()
    print(f"✅ Responses API support: {has_responses}")
    
    if orchestrator._responses_client:
        print(f"✅ Responses client type: {type(orchestrator._responses_client)}")
    else:
        print("❌ Responses client is None")
    
    # Test a query that should use Responses API
    print("\nTesting query processing...")
    query = "What are the technical levels for TSLA?"
    
    result = await orchestrator.process_query(query, [], stream=False)
    
    # Check if the query was processed
    if result.get("text"):
        print("✅ Query processed successfully")
        print(f"✅ Model used: {result.get('model', 'unknown')}")
        print(f"✅ Tools used: {result.get('tools_used', [])}")
        
        # Check for technical levels in the response
        if "data" in result:
            comprehensive_data = result["data"].get("get_comprehensive_stock_data", {})
            levels = comprehensive_data.get("technical_levels", {})
            if levels:
                print("\n✅ Technical levels found:")
                for level_name, value in levels.items():
                    print(f"   {level_name}: ${value}")
            else:
                print("❌ No technical levels in response")
        
        # The presence of structured data indicates Responses API is working
        if result.get("cached") is False and result.get("model"):
            print("\n✅ Response structure indicates Responses API is active")
        else:
            print("\n⚠️  Response structure suggests fallback to Chat Completions")
    else:
        print("❌ Query failed")
        print(f"   Error: {result}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_responses_api())