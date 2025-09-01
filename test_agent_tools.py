#!/usr/bin/env python3
"""
Test ElevenLabs agent with configured tools for real market data
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

# Test queries to validate tools
TEST_QUERIES = [
    "What is the current price of Bitcoin?",
    "Show me the market overview",
    "Get me news about Tesla", 
    "What's the price of Apple stock?",
    "Tell me about SPY performance"
]

async def test_conversation():
    """Test conversation with specific market queries"""
    
    print("🧪 Testing ElevenLabs Agent with Market Tools")
    print("=" * 60)
    
    # Get signed URL
    print("\n📡 Getting signed URL from backend...")
    response = requests.get(f"{BACKEND_URL}/elevenlabs/signed-url")
    if response.status_code != 200:
        print(f"❌ Failed to get signed URL: {response.status_code}")
        return
    
    signed_url = response.json()['signed_url']
    print("✅ Got signed URL")
    
    # Connect to WebSocket
    print("\n🔌 Connecting to ElevenLabs...")
    try:
        async with websockets.connect(signed_url) as websocket:
            print("✅ Connected to ElevenLabs")
            
            # Send initialization
            init_message = {
                "type": "conversation_initiation_metadata",
                "conversation_initiation_metadata_event": {
                    "conversation_id": f"test_{datetime.now().isoformat()}",
                    "custom_llm_extra_body": {}
                }
            }
            
            await websocket.send(json.dumps(init_message))
            print("✅ Sent initialization")
            
            # Process each test query
            for i, query in enumerate(TEST_QUERIES, 1):
                print(f"\n📊 Test {i}/{len(TEST_QUERIES)}: {query}")
                print("-" * 40)
                
                # Send the query
                message = {
                    "type": "user_message",
                    "user_message_event": {
                        "text": query
                    }
                }
                
                await websocket.send(json.dumps(message))
                print(f"   → Sent: {query}")
                
                # Collect response
                response_text = ""
                tool_calls = []
                start_time = asyncio.get_event_loop().time()
                
                while asyncio.get_event_loop().time() - start_time < 10:  # 10 second timeout
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(response)
                        
                        # Check for agent text response
                        if data.get("type") == "agent_text":
                            text = data.get("agent_text_event", {}).get("text", "")
                            response_text += text
                            
                        # Check for tool calls
                        elif data.get("type") == "agent_tool_call":
                            tool_data = data.get("agent_tool_call_event", {})
                            tool_name = tool_data.get("tool_name", "unknown")
                            tool_calls.append(tool_name)
                            print(f"   🔧 Tool called: {tool_name}")
                            
                        # Check for completion
                        elif data.get("type") == "agent_response" and data.get("agent_response_event", {}).get("status") == "done":
                            break
                            
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"   ⚠️  Error: {e}")
                        break
                
                # Print results
                if response_text:
                    # Truncate long responses
                    display_text = response_text[:200] + "..." if len(response_text) > 200 else response_text
                    print(f"   ← Response: {display_text}")
                    
                    # Check if response contains expected data
                    if "Bitcoin" in query and "$" in response_text:
                        print(f"   ✅ Bitcoin price mentioned")
                    elif "market overview" in query.lower() and ("S&P" in response_text or "NASDAQ" in response_text):
                        print(f"   ✅ Market indices mentioned")
                    elif "Tesla" in query and ("TSLA" in response_text or "news" in response_text.lower()):
                        print(f"   ✅ Tesla information provided")
                    elif "Apple" in query and "$" in response_text:
                        print(f"   ✅ Apple price mentioned")
                    elif "SPY" in query and "$" in response_text:
                        print(f"   ✅ SPY data provided")
                else:
                    print(f"   ❌ No response received")
                
                if tool_calls:
                    print(f"   📊 Tools used: {', '.join(tool_calls)}")
                
                # Small delay between queries
                await asyncio.sleep(2)
            
            print("\n" + "=" * 60)
            print("🏁 Test Complete!")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

# Also test the tools directly via API
def test_tools_directly():
    """Test if tools can be called directly"""
    
    print("\n🔧 Testing Tools Directly via API")
    print("=" * 60)
    
    # List tools
    response = requests.get(
        f"https://api.elevenlabs.io/v1/convai/tools",
        headers={"xi-api-key": API_KEY}
    )
    
    if response.status_code == 200:
        tools = response.json().get('tools', [])
        print(f"\n📋 Found {len(tools)} configured tools:")
        
        tool_names = set()
        for tool in tools:
            config = tool.get('tool_config', {})
            name = config.get('name', 'unnamed')
            tool_id = tool.get('id')
            tool_names.add(name)
            
            # Check if it's one of our market tools
            if name in ['get_stock_price', 'get_market_overview', 'get_stock_news', 
                       'get_stock_history', 'get_analyst_ratings', 'get_options_chain']:
                print(f"   ✅ {name} (ID: {tool_id})")
            else:
                print(f"   • {name} (ID: {tool_id})")
        
        # Check for expected tools
        expected_tools = ['get_stock_price', 'get_market_overview', 'get_stock_news']
        missing_tools = [t for t in expected_tools if t not in tool_names]
        
        if missing_tools:
            print(f"\n⚠️  Missing tools: {', '.join(missing_tools)}")
        else:
            print(f"\n✅ All essential tools are configured!")
            
    else:
        print(f"❌ Failed to list tools: {response.status_code}")

if __name__ == "__main__":
    # Test tools configuration
    test_tools_directly()
    
    # Test conversation with tools
    print("\n" + "=" * 60)
    asyncio.run(test_conversation())