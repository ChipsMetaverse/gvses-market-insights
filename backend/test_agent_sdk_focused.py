#!/usr/bin/env python3
"""
Focused Agent SDK test to trace the exact workflow execution path
"""

import asyncio
import httpx
import logging

# Configure logging to show detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_agent_sdk_focused():
    """Test Agent SDK with focused logging to trace workflow execution"""
    
    print("🔍 FOCUSED Agent SDK Test - Tracing Workflow Execution")
    print("=" * 70)
    
    payload = {
        "query": "aapl",
        "conversation_history": [],
        "session_id": "test-focused-debug",
        "user_id": "test-user"
    }
    
    print(f"📤 Testing Agent SDK with query: '{payload['query']}'")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/api/agent/sdk-orchestrate",
                json=payload
            )
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n📊 Agent SDK Response Analysis:")
                print(f"   Intent: {result.get('data', {}).get('intent', 'unknown')}")
                print(f"   Confidence: {result.get('data', {}).get('confidence', 'unknown')}")
                print(f"   Reasoning: {result.get('data', {}).get('reasoning', 'unknown')}")
                print(f"   Text Preview: '{result.get('text', '')[:100]}...'")
                print(f"   Tools Used: {result.get('tools_used', [])}")
                print(f"   Model: {result.get('model', 'unknown')}")
                
                # Check if we actually got market data
                data = result.get('data', {})
                has_market_data = any(key in data for key in ['symbol', 'price', 'stock_data'])
                print(f"   Market Data Present: {has_market_data}")
                
                if has_market_data:
                    print(f"   ✅ SUCCESS: Agent SDK provided market data")
                else:
                    print(f"   ⚠️  ISSUE: Agent SDK didn't provide actual market data")
                
                return result
                
            else:
                print(f"❌ Request Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
    except Exception as e:
        print(f"💥 Test Failed: {str(e)}")
        return None

async def main():
    print("🚀 Agent SDK Focused Workflow Debug")
    print("=" * 50)
    
    # Run focused test
    result = await test_agent_sdk_focused()
    
    print(f"\n📝 Next Steps:")
    print(f"   1. Check backend logs for detailed Agent SDK workflow execution")
    print(f"   2. Look for the comprehensive logging I added to _handle_market_data_query")
    print(f"   3. Verify if the workflow is actually calling MCP tools or just the orchestrator")

if __name__ == "__main__":
    asyncio.run(main())