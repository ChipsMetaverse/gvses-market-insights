#!/usr/bin/env python3
"""Direct WebSocket test for ElevenLabs"""

import asyncio
import websockets
import json
import requests

API_KEY = "sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb"
AGENT_ID = "agent_4901k2tkkq54f4mvgpndm3pgzm7g"

def get_signed_url():
    """Get signed URL from ElevenLabs API"""
    url = f"https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id={AGENT_ID}"
    headers = {"xi-api-key": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["signed_url"]
    else:
        raise Exception(f"Failed to get signed URL: {response.status_code}")

async def test_websocket():
    """Test WebSocket connection"""
    print("Getting signed URL...")
    signed_url = get_signed_url()
    print(f"Got signed URL: {signed_url[:100]}...")
    
    print("\nConnecting to WebSocket...")
    try:
        async with websockets.connect(signed_url) as websocket:
            print("✅ WebSocket connected!")
            
            # Send initialization message
            init_message = {
                "type": "conversation_initiation_client_data",
                "custom_llm_extra_body": {}
            }
            print(f"\nSending init message: {json.dumps(init_message)}")
            await websocket.send(json.dumps(init_message))
            print("✅ Init message sent")
            
            # Listen for messages
            print("\nListening for messages (30 seconds)...")
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    print(f"📥 Received: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'conversation_initiation_metadata':
                        print("🎉 Conversation initialized successfully!")
                        print(f"   Conversation ID: {data.get('conversation_id')}")
                    elif data.get('type') == 'ping':
                        print("🏓 Ping received, sending pong...")
                        pong = {
                            "type": "pong",
                            "event_id": data.get('ping_event', {}).get('event_id')
                        }
                        await websocket.send(json.dumps(pong))
                        print("✅ Pong sent")
                    
                    # Print first 200 chars of message
                    print(f"   Data: {json.dumps(data)[:200]}...")
                    
            except asyncio.TimeoutError:
                print("\n⏱️ Timeout after 30 seconds (normal)")
            
            print("\nClosing connection...")
            
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        print(f"   Type: {type(e).__name__}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Type: {type(e).__name__}")

if __name__ == "__main__":
    print("=" * 60)
    print("ELEVENLABS WEBSOCKET TEST")
    print("=" * 60)
    asyncio.run(test_websocket())
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)