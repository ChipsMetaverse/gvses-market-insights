#!/usr/bin/env python3
"""
Test if agent uses tools when explicitly asked
"""

import requests
import json
import asyncio
import websockets
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')
BACKEND_URL = "http://localhost:8000"

async def test_tool_usage():
    print("🔧 Testing Tool Usage")
    print("=" * 60)
    
    # Get signed URL
    response = requests.get(f"{BACKEND_URL}/elevenlabs/signed-url")
    if response.status_code != 200:
        print(f"❌ Failed to get signed URL")
        return
    
    signed_url = response.json()['signed_url']
    
    # Test queries designed to trigger tool usage
    test_queries = [
        "Use the get_stock_price tool to check Bitcoin price",
        "Call get_market_overview tool to show market status",
        "Get the current price of TSLA stock",
        "What is the market overview right now?"
    ]
    
    try:
        async with websockets.connect(signed_url) as websocket:
            print("✅ Connected to WebSocket\n")
            
            # Send initialization
            init_message = {
                "type": "conversation_initiation_metadata",
                "conversation_initiation_metadata_event": {
                    "conversation_id": f"test_{datetime.now().isoformat()}"
                }
            }
            
            await websocket.send(json.dumps(init_message))
            await asyncio.sleep(1)
            
            for query in test_queries:
                print(f"📊 Testing: '{query}'")
                print("-" * 40)
                
                # Send message
                message = {
                    "type": "user_message",
                    "text": query
                }
                
                await websocket.send(json.dumps(message))
                
                # Collect response
                tool_calls = []
                agent_response = ""
                start_time = asyncio.get_event_loop().time()
                
                while asyncio.get_event_loop().time() - start_time < 8:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(response)
                        
                        event_type = data.get("type", "")
                        
                        if event_type == "agent_response":
                            resp = data.get("agent_response_event", {})
                            text = resp.get("agent_response", "")
                            if text:
                                agent_response = text
                        
                        elif event_type == "tool_call":
                            tool_event = data.get("tool_call_event", {})
                            tool_name = tool_event.get("tool_name", "unknown")
                            tool_calls.append(tool_name)
                            print(f"   🔧 Tool called: {tool_name}")
                        
                        elif event_type == "agent_tool_call":
                            tool_event = data.get("agent_tool_call_event", {})
                            tool_name = tool_event.get("tool_name", "unknown")
                            tool_calls.append(tool_name)
                            print(f"   🔧 Tool called: {tool_name}")
                            
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"   ⚠️  Error: {e}")
                        break
                
                # Show results
                if agent_response:
                    print(f"   💬 Response: {agent_response[:150]}...")
                
                if tool_calls:
                    print(f"   ✅ Tools used: {', '.join(tool_calls)}")
                else:
                    print(f"   ❌ No tools were called")
                
                # Check if response contains real data
                if "$" in agent_response and any(x in agent_response for x in ["111", "112", "Bitcoin"]):
                    print(f"   ✅ Response contains real market data!")
                elif "unable" in agent_response.lower() or "cannot" in agent_response.lower():
                    print(f"   ⚠️  Agent says it cannot access data")
                
                print()
                await asyncio.sleep(2)
            
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n🧪 Tool Usage Test\n")
asyncio.run(test_tool_usage())
print("\n✅ Test complete!")