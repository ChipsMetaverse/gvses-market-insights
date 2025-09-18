#!/usr/bin/env python3
"""
Simple Agent Test - Direct API Calls
====================================
Tests the agent without complex imports.
"""

import httpx
import json
import asyncio

async def test_agent_endpoints():
    """Test the agent via HTTP endpoints."""
    
    print("="*60)
    print("SIMPLE AGENT TEST VIA HTTP")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "endpoint": "/health",
            "expected": ["status", "timestamp"]
        },
        {
            "name": "Stock Price Check",
            "method": "GET", 
            "endpoint": "/api/stock-price?symbol=AAPL",
            "expected": ["symbol", "price"]
        },
        {
            "name": "Agent Ask - Trading Levels",
            "method": "POST",
            "endpoint": "/ask",
            "data": {"query": "What are the trading levels for TSLA?"},
            "expected": ["response", "tools_used"]
        },
        {
            "name": "Agent Ask - Morning Greeting",
            "method": "POST",
            "endpoint": "/ask",
            "data": {"query": "Good morning"},
            "expected": ["response"]
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in tests:
            print(f"\n🔍 Testing: {test['name']}")
            print("-" * 40)
            
            try:
                if test['method'] == 'GET':
                    response = await client.get(f"{base_url}{test['endpoint']}")
                else:
                    response = await client.post(
                        f"{base_url}{test['endpoint']}", 
                        json=test.get('data', {})
                    )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check expected fields
                    for field in test['expected']:
                        if field in data:
                            print(f"✅ Found '{field}'")
                            
                            # Print sample of response for agent tests
                            if field == 'response':
                                preview = str(data[field])[:200]
                                print(f"   Response preview: {preview}...")
                                
                                # Check for trading levels
                                if "trading levels" in test['name'].lower():
                                    levels = ['BTD', 'Buy Low', 'Sell High', 'Retest']
                                    for level in levels:
                                        if level.lower() in data['response'].lower():
                                            print(f"   ✅ Found {level} level")
                                        else:
                                            print(f"   ❌ Missing {level} level")
                            
                            if field == 'tools_used' and data.get(field):
                                print(f"   Tools: {data[field]}")
                        else:
                            print(f"❌ Missing '{field}'")
                else:
                    print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
                    
            except httpx.ConnectError:
                print("❌ Connection failed - is the server running?")
                print("   Start with: cd backend && uvicorn mcp_server:app --reload")
                return False
            except httpx.TimeoutException:
                print("⏱️ Request timed out (30s)")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("Test complete!")
    return True

if __name__ == "__main__":
    print("\n⚠️ Make sure the backend server is running:")
    print("cd backend && uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000")
    print("\nStarting tests in 3 seconds...\n")
    import time
    time.sleep(3)
    
    asyncio.run(test_agent_endpoints())