#!/usr/bin/env python3
"""Debug the /ask endpoint"""

import asyncio
import os
from dotenv import load_dotenv
from services.agent_orchestrator import get_orchestrator

load_dotenv()

async def test_ask_debug():
    """Test what the orchestrator actually returns"""
    orchestrator = get_orchestrator()
    
    print("Testing AgentOrchestrator directly...")
    print("=" * 60)
    
    query = "What is the current price of TSLA with technical levels?"
    
    # Test the orchestrator directly
    result = await orchestrator.process_query(query, [], stream=False)
    
    print(f"Result type: {type(result)}")
    print(f"Result keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
    
    if isinstance(result, dict):
        print(f"\nText: {result.get('text', 'NO TEXT')[:200]}...")
        print(f"Tools used: {result.get('tools_used', [])}")
        print(f"Model: {result.get('model', 'unknown')}")
        
        # Check if Responses API was used
        if result.get('model') and not result.get('cached'):
            print("\n✅ Responses API appears to be active")
        else:
            print("\n⚠️ May have fallen back to Chat Completions")
            
        # Check data
        if 'data' in result:
            data_keys = list(result['data'].keys())
            print(f"\nData keys: {data_keys}")
            
            # Check for comprehensive data
            if 'get_comprehensive_stock_data' in result['data']:
                comp_data = result['data']['get_comprehensive_stock_data']
                if 'technical_levels' in comp_data:
                    levels = comp_data['technical_levels']
                    print("\n✅ Technical levels found:")
                    for level, value in levels.items():
                        print(f"   {level}: ${value}")

if __name__ == "__main__":
    asyncio.run(test_ask_debug())