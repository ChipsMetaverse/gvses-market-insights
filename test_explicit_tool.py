#!/usr/bin/env python3
"""
Test with very explicit tool requests
"""

import asyncio
import websockets
import json
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')

async def test_explicit_tool_request():
    """Test with very explicit tool calling requests"""
    
    print("🔧 Testing Explicit Tool Requests")
    print("=" * 60)
    
    # Get signed URL
    response = requests.get(
        f'https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id={AGENT_ID}',
        headers={'xi-api-key': API_KEY}
    )
    
    if response.status_code != 200:
        print(f'❌ Failed to get signed URL: {response.status_code}')
        return
    
    signed_url = response.json()['signed_url']
    print('✅ Got signed URL')
    
    # Very explicit tool requests
    test_queries = [
        "Please use the get_stock_price tool to fetch the current price of AAPL",
        "Call the get_market_overview tool to show market status",
        "Use get_stock_price with symbol TSLA to get Tesla's price"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        try:
            async with websockets.connect(signed_url) as ws:
                # Send initialization
                init_message = {
                    'type': 'conversation_initiation_client_data',
                    'custom_llm_extra_body': {}
                }
                await ws.send(json.dumps(init_message))
                
                # Wait briefly
                await asyncio.sleep(0.5)
                
                # Send query
                message = {
                    'type': 'user_message',
                    'text': query
                }
                await ws.send(json.dumps(message))
                print("   ✅ Message sent")
                
                # Collect responses
                tool_called = False
                agent_response = ""
                start_time = time.time()
                
                while time.time() - start_time < 10:
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=1)
                        data = json.loads(response)
                        msg_type = data.get('type')
                        
                        if msg_type == 'tool_call':
                            tool_called = True
                            tool_name = data.get('tool_name')
                            params = data.get('parameters', {})
                            print(f"   🔧 TOOL CALLED: {tool_name}")
                            print(f"      Parameters: {params}")
                            
                        elif msg_type == 'tool_call_result':
                            result = data.get('result', '')
                            if result:
                                try:
                                    result_data = json.loads(result) if isinstance(result, str) else result
                                    if isinstance(result_data, dict) and 'symbol' in result_data:
                                        print(f"      📊 Result: {result_data.get('symbol')} = ${result_data.get('last', 'N/A')}")
                                    else:
                                        print(f"      📊 Result received")
                                except:
                                    print(f"      📊 Result: {str(result)[:100]}")
                                    
                        elif msg_type == 'agent_response':
                            text = data.get('text', '')
                            if text:
                                agent_response = text
                                
                        elif msg_type == 'internal_tentative_agent_response':
                            text = data.get('text', '')
                            if text:
                                print(f"   🤔 Thinking: {text[:100]}...")
                                
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        break
                
                # Summary
                if tool_called:
                    print(f"   ✅ Tool was successfully called!")
                else:
                    print(f"   ❌ No tool was called")
                    if agent_response:
                        print(f"   💬 Agent said: {agent_response[:150]}...")
                        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        await asyncio.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ Explicit tool test complete")

if __name__ == "__main__":
    asyncio.run(test_explicit_tool_request())