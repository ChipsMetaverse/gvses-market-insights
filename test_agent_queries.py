#!/usr/bin/env python3
"""
Test the ElevenLabs agent with specific market queries
to verify tools are being called and returning real data
"""

import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
import time

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')

# Test queries
TEST_QUERIES = [
    "What's the price of Apple stock?",
    "Show me Bitcoin price",
    "Get market overview"
]

async def test_agent():
    """Test agent with WebSocket connection"""
    
    # Get signed URL for WebSocket
    import requests
    url_response = requests.get(
        "https://api.elevenlabs.io/v1/convai/conversation/get_signed_url",
        params={"agent_id": AGENT_ID},
        headers={"xi-api-key": API_KEY}
    )
    
    if url_response.status_code != 200:
        print(f"❌ Failed to get signed URL: {url_response.status_code}")
        print(f"   Error: {url_response.text}")
        return
    
    signed_url = url_response.json().get("signed_url")
    print(f"✅ Got signed URL")
    print("=" * 60)
    
    # Connect to WebSocket
    try:
        async with websockets.connect(signed_url) as websocket:
            print("🔌 Connected to agent")
            
            # Initialize conversation
            init_message = {
                "type": "conversation_initiation_client_data",
                "custom_llm_extra_body": {},
                "conversation_config_override": {}
            }
            await websocket.send(json.dumps(init_message))
            
            # Wait for agent ready
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                if data.get("type") == "conversation_initiation_metadata":
                    print("✅ Agent ready\n")
                    break
            
            # Test each query
            for i, query in enumerate(TEST_QUERIES, 1):
                print(f"\n🧪 Test {i}: \"{query}\"")
                print("-" * 40)
                
                # Send the query
                message = {
                    "type": "user_transcript",
                    "text": query
                }
                await websocket.send(json.dumps(message))
                
                # Collect agent response
                agent_response = ""
                tool_called = None
                
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    # Check for tool call
                    if data.get("type") == "tool_call":
                        tool_called = data.get("tool_name", "unknown")
                        print(f"   🔧 Tool called: {tool_called}")
                        if data.get("parameters"):
                            print(f"      Parameters: {data['parameters']}")
                    
                    # Collect transcript
                    elif data.get("type") == "agent_transcript":
                        agent_response += data.get("text", "")
                    
                    # Check if response complete
                    elif data.get("type") == "agent_response_complete":
                        break
                
                # Display results
                if agent_response:
                    # Truncate long responses
                    display = agent_response[:200] + "..." if len(agent_response) > 200 else agent_response
                    print(f"   💬 Response: {display}")
                
                # Check for real data
                if "Apple" in query and "$" in agent_response:
                    print("   ✅ Real price data returned!")
                elif "Bitcoin" in query and ("$" in agent_response or "USD" in agent_response):
                    print("   ✅ Real Bitcoin data returned!")
                elif "market overview" in query.lower() and any(x in agent_response for x in ["S&P", "Dow", "NASDAQ", "$"]):
                    print("   ✅ Real market data returned!")
                
                if not tool_called:
                    print("   ⚠️  No tool was called")
                
                # Small delay between tests
                await asyncio.sleep(2)
            
            print("\n" + "=" * 60)
            print("✅ Testing complete!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing ElevenLabs Agent with Market Queries")
    print("=" * 60)
    print(f"Agent ID: {AGENT_ID}")
    print(f"Testing {len(TEST_QUERIES)} queries\n")
    
    asyncio.run(test_agent())