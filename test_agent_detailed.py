#!/usr/bin/env python3
"""
Detailed test of ElevenLabs agent to diagnose response issues
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

print("🔍 Detailed Agent Test")
print("=" * 60)

# First check agent configuration
print("\n1️⃣ Checking agent configuration...")
agent_response = requests.get(
    f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if agent_response.status_code == 200:
    agent_data = agent_response.json()
    
    # Check configuration details
    conv_config = agent_data.get('conversation_config', {})
    agent_config = conv_config.get('agent', {})
    prompt_config = agent_config.get('prompt', {})
    
    prompt_text = prompt_config.get('prompt', '')
    tool_ids = prompt_config.get('tool_ids', [])
    llm = prompt_config.get('llm', 'N/A')
    
    print(f"   ✅ Agent found: {agent_data.get('name', 'N/A')}")
    print(f"   • Prompt: {'Yes' if prompt_text else 'No'} ({len(prompt_text)} chars)")
    print(f"   • Tools: {len(tool_ids)} assigned")
    print(f"   • LLM: {llm}")
    
    if prompt_text:
        # Check if G'sves personality is loaded
        if "G'sves" in prompt_text or "30 years" in prompt_text:
            print(f"   ✅ G'sves personality loaded!")
        else:
            print(f"   ⚠️  Prompt may not have G'sves personality")
else:
    print(f"   ❌ Failed to get agent: {agent_response.status_code}")
    exit(1)

# Test conversation
async def test_conversation():
    print("\n2️⃣ Testing conversation...")
    
    # Get signed URL
    response = requests.get(f"{BACKEND_URL}/elevenlabs/signed-url")
    if response.status_code != 200:
        print(f"   ❌ Failed to get signed URL: {response.status_code}")
        return
    
    signed_url = response.json()['signed_url']
    print(f"   ✅ Got signed URL")
    
    # Connect to WebSocket
    try:
        async with websockets.connect(signed_url) as websocket:
            print(f"   ✅ Connected to WebSocket")
            
            # Send initialization
            init_message = {
                "type": "conversation_initiation_metadata",
                "conversation_initiation_metadata_event": {
                    "conversation_id": f"test_{datetime.now().isoformat()}",
                    "custom_llm_extra_body": {}
                }
            }
            
            await websocket.send(json.dumps(init_message))
            print(f"   ✅ Sent initialization")
            
            # Wait for initialization response
            await asyncio.sleep(1)
            
            # Send a simple test query
            test_query = "What is the current price of Bitcoin?"
            print(f"\n   📊 Sending: '{test_query}'")
            
            message = {
                "type": "user_message",
                "text": test_query
            }
            
            await websocket.send(json.dumps(message))
            print(f"   ✅ Message sent")
            
            # Collect all responses for 15 seconds
            print(f"   ⏳ Waiting for response (15s)...")
            responses = []
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < 15:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    responses.append(data)
                    
                    # Print event types as they come
                    event_type = data.get("type", "unknown")
                    print(f"      • Received: {event_type}")
                    
                    # Check for specific event types
                    if event_type == "agent_text":
                        text = data.get("agent_text_event", {}).get("text", "")
                        if text:
                            print(f"      💬 Agent says: {text[:100]}...")
                    
                    elif event_type == "agent_response":
                        # Agent response format
                        agent_resp = data.get("agent_response_event", {})
                        agent_text = agent_resp.get("agent_response", "")
                        if agent_text:
                            print(f"      💬 Agent response: {agent_text[:200]}...")
                    
                    elif event_type == "agent_tool_call":
                        tool_data = data.get("agent_tool_call_event", {})
                        tool_name = tool_data.get("tool_name", "unknown")
                        print(f"      🔧 Tool called: {tool_name}")
                    
                    elif event_type == "tool_call":
                        # Alternative tool call format
                        tool_name = data.get("tool_call_event", {}).get("tool_name", "unknown")
                        print(f"      🔧 Tool called: {tool_name}")
                    
                    elif event_type == "interruption":
                        print(f"      ⚠️  Interruption event")
                    
                    elif event_type == "error":
                        error_data = data.get("error", {})
                        print(f"      ❌ Error: {error_data}")
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"      ⚠️  Exception: {e}")
            
            print(f"\n   📊 Response Summary:")
            print(f"      Total events: {len(responses)}")
            
            # Analyze responses
            text_events = [r for r in responses if r.get("type") == "agent_text"]
            tool_events = [r for r in responses if r.get("type") == "agent_tool_call"]
            error_events = [r for r in responses if r.get("type") == "error"]
            
            print(f"      Text events: {len(text_events)}")
            print(f"      Tool calls: {len(tool_events)}")
            print(f"      Errors: {len(error_events)}")
            
            if len(responses) == 0:
                print(f"\n   ❌ No response from agent!")
                print(f"   💡 Possible issues:")
                print(f"      • Agent may not be properly configured")
                print(f"      • LLM might not support tool calls")
                print(f"      • WebSocket connection issues")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")

print("\n" + "=" * 60)
asyncio.run(test_conversation())
print("\n✅ Test complete!")