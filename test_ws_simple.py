#!/usr/bin/env python3
"""Simple WebSocket test with timeout"""

import asyncio
import websockets
import json
import requests
import signal

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
    """Test WebSocket connection with short timeout"""
    print("Getting signed URL...")
    signed_url = get_signed_url()
    print(f"URL: {signed_url[:100]}...")
    
    print("\nAttempting connection (5 second timeout)...")
    try:
        # Try to connect with a 5 second timeout
        websocket = await asyncio.wait_for(
            websockets.connect(signed_url),
            timeout=5.0
        )
        print("✅ Connected!")
        
        # Send init immediately
        init = {"type": "conversation_initiation_client_data", "custom_llm_extra_body": {}}
        await websocket.send(json.dumps(init))
        print("✅ Sent init message")
        
        # Wait for response (5 second timeout)
        print("\nWaiting for response (5 seconds)...")
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            print(f"📥 Got response: {data.get('type')}")
            print(f"   Data: {json.dumps(data)[:200]}")
        except asyncio.TimeoutError:
            print("⏱️ No response within 5 seconds")
        
        await websocket.close()
        print("✅ Closed cleanly")
        
    except asyncio.TimeoutError:
        print("❌ Connection timeout - could not establish WebSocket connection")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("SIMPLE WEBSOCKET TEST")
    print("=" * 60)
    
    # Set up signal handler for Ctrl+C
    def signal_handler(sig, frame):
        print("\n\nInterrupted by user")
        exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    asyncio.run(test_websocket())
    print("=" * 60)