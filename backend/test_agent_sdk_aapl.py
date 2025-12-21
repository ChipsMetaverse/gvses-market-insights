#!/usr/bin/env python3
"""
Test Agent SDK workflow with AAPL query to debug response routing
"""

import asyncio
import json
import sys
import os
from datetime import datetime
import httpx
import logging

# Configure logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_agent_sdk_aapl():
    """Test the Agent SDK workflow with an AAPL query"""
    
    print("🧪 Testing Agent SDK Workflow - AAPL Query")
    print("=" * 60)
    
    # Test payload matching the frontend format
    payload = {
        "query": "aapl",
        "conversation_history": [],
        "session_id": "test-aapl-debug",
        "user_id": "test-user"
    }
    
    print(f"📤 Sending request to Agent SDK endpoint...")
    print(f"   Query: '{payload['query']}'")
    print(f"   Session: {payload['session_id']}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Call the Agent SDK orchestrate endpoint
            response = await client.post(
                "http://localhost:8000/api/agent/sdk-orchestrate",
                json=payload
            )
            
            print(f"\n📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Agent SDK Response Received!")
                print(f"   Text: '{result.get('text', '')[:200]}...'")
                print(f"   Tools Used: {result.get('tools_used', [])}")
                print(f"   Data Keys: {list(result.get('data', {}).keys())}")
                print(f"   Chart Commands: {result.get('chart_commands', [])}")
                print(f"   Model: {result.get('model', 'unknown')}")
                print(f"   Cached: {result.get('cached', False)}")
                
                # Check if we got meaningful market data
                data = result.get('data', {})
                if 'symbol' in data or 'price' in data:
                    print(f"📊 Market Data Found: Symbol={data.get('symbol')}, Price={data.get('price')}")
                else:
                    print(f"⚠️  No market data in response")
                    
                return True
                
            else:
                print(f"❌ Request Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"💥 Test Failed: {str(e)}")
        return False

async def test_comparison_with_regular_orchestrate():
    """Test the same query against the regular orchestrate endpoint for comparison"""
    
    print(f"\n🔍 Comparison Test - Regular Orchestrate Endpoint")
    print("=" * 60)
    
    payload = {
        "query": "aapl",
        "conversation_history": [],
        "session_id": "test-aapl-regular",
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/api/agent/orchestrate", 
                json=payload
            )
            
            print(f"📡 Regular Orchestrate Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Regular Orchestrate Response:")
                print(f"   Text: '{result.get('text', '')[:200]}...'")
                print(f"   Tools Used: {result.get('tools_used', [])}")
                print(f"   Data Keys: {list(result.get('data', {}).keys())}")
                
                return True
            else:
                print(f"❌ Regular orchestrate failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"💥 Regular orchestrate test failed: {str(e)}")
        return False

async def main():
    print("🚀 Agent SDK AAPL Query Debug Test")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Test 1: Agent SDK workflow
    sdk_success = await test_agent_sdk_aapl()
    
    # Test 2: Regular orchestrate for comparison  
    regular_success = await test_comparison_with_regular_orchestrate()
    
    print(f"\n📊 Test Results:")
    print(f"   Agent SDK: {'✅ SUCCESS' if sdk_success else '❌ FAILED'}")
    print(f"   Regular Orchestrate: {'✅ SUCCESS' if regular_success else '❌ FAILED'}")
    
    if sdk_success and regular_success:
        print(f"\n🎉 Both endpoints working - check logs for workflow differences")
    elif not sdk_success and regular_success:
        print(f"\n🚨 Agent SDK has issues - regular orchestrate works")
    elif sdk_success and not regular_success:
        print(f"\n⚠️  Regular orchestrate has issues - Agent SDK works")  
    else:
        print(f"\n💥 Both endpoints have issues - check backend logs")

if __name__ == "__main__":
    asyncio.run(main())