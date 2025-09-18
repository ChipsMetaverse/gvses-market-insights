#!/usr/bin/env python3
import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

async def test_direct_connection():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    print(f"🔗 Connecting directly to OpenAI: {url}")
    print(f"📋 Headers: Authorization=Bearer ***HIDDEN***, OpenAI-Beta=realtime=v1")
    print(f"📋 Subprotocols: None (testing without subprotocol)")
    
    try:
        async with websockets.connect(
            url,
            extra_headers=headers,
            close_timeout=10
        ) as websocket:
            print(f"✅ Connected! Subprotocol: {websocket.subprotocol}")
            
            # Wait for session.created
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            print(f"📨 Received: {data.get('type', 'unknown')}")
            
            if data.get('type') == 'session.created':
                print(f"🎉 Session created successfully!")
                print(f"   Session ID: {data.get('session', {}).get('id', 'unknown')}")
                print(f"   Model: {data.get('session', {}).get('model', 'unknown')}")
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection rejected with status {e.status_code}")
        print(f"   Headers: {e.headers}")
    except websockets.exceptions.NegotiationError as e:
        print(f"❌ WebSocket negotiation failed: {e}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_connection())