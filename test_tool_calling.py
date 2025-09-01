#!/usr/bin/env python3
"""
Test if ElevenLabs agent is properly calling tools
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

async def test_tool_calling():
    """Test if agent calls tools properly"""
    
    print("🔧 Testing Tool Calling")
    print("=" * 60)
    
    # Get signed URL
    response = requests.get(
        f'https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id={AGENT_ID}',
        headers={'xi-api-key': API_KEY}
    )
    
    if response.status_code != 200:
        print(f'❌ Failed to get signed URL: {response.status_code}')
        return False
    
    signed_url = response.json()['signed_url']
    print('✅ Got signed URL')
    
    # Test queries
    test_queries = [
        "What is the current price of Apple stock?",
        "Show me the market overview",
        "Get news for Tesla"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 40)
        
        try:
            async with websockets.connect(signed_url) as ws:
                # Send initialization
                init_message = {
                    'type': 'conversation_initiation_client_data',
                    'custom_llm_extra_body': {}
                }
                await ws.send(json.dumps(init_message))
                
                # Wait for initialization
                await asyncio.sleep(0.5)
                
                # Send query
                message = {
                    'type': 'user_message',
                    'text': query
                }
                await ws.send(json.dumps(message))
                
                # Collect responses
                tool_calls = []
                agent_responses = []
                start_time = time.time()
                
                while time.time() - start_time < 15:  # 15 second timeout
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=1)
                        data = json.loads(response)
                        msg_type = data.get('type')
                        
                        if msg_type == 'tool_call':
                            tool_name = data.get('tool_name')
                            params = data.get('parameters', {})
                            tool_calls.append({
                                'name': tool_name,
                                'params': params
                            })
                            print(f"   🔧 Tool called: {tool_name}")
                            print(f"      Parameters: {params}")
                            
                        elif msg_type == 'tool_call_result':
                            result = data.get('result', '')
                            if result:
                                # Parse if JSON
                                try:
                                    result_data = json.loads(result) if isinstance(result, str) else result
                                    if isinstance(result_data, dict):
                                        # Show key data points
                                        if 'symbol' in result_data:
                                            print(f"      📊 Result: {result_data.get('symbol')} = ${result_data.get('last', 'N/A')}")
                                        else:
                                            print(f"      📊 Result received ({len(str(result_data))} chars)")
                                except:
                                    print(f"      📊 Result: {result[:100]}...")
                                    
                        elif msg_type == 'agent_response':
                            text = data.get('text', '')
                            if text:
                                agent_responses.append(text)
                                print(f"   💬 Agent: {text[:150]}...")
                                
                        elif msg_type == 'internal_tentative_agent_response':
                            text = data.get('text', '')
                            if text and 'tool' in text.lower():
                                print(f"   🤔 Planning: {text[:100]}...")
                                
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        break
                
                # Summary for this query
                if tool_calls:
                    print(f"   ✅ {len(tool_calls)} tool(s) called")
                else:
                    print(f"   ❌ No tools called")
                    
                if agent_responses:
                    final_response = agent_responses[-1] if agent_responses else ""
                    if final_response:
                        print(f"   📝 Final response: {final_response[:200]}...")
                        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
        # Small delay between tests
        await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Tool calling test complete")
    return True

if __name__ == "__main__":
    asyncio.run(test_tool_calling())