#!/usr/bin/env python3
"""
Test the WebSocket endpoint directly
"""
import asyncio
import websockets
import json

async def test_websocket_endpoint():
    uri = "ws://localhost:8000/realtime-relay/test-session-123"
    print(f"Testing WebSocket endpoint: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection successful!")
            
            # Send a test message
            test_message = {
                "type": "session.update",
                "session": {
                    "model": "gpt-realtime",
                    "voice": "alloy"
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message")
            
            # Wait for a response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds (this might be expected)")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: code={e.code}, reason={e.reason}")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Invalid status code: {e.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_endpoint())