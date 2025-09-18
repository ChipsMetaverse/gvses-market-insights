#!/usr/bin/env python3
import asyncio
import websockets
import json
import sys

async def test_connection():
    # First create a session
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/openai/realtime/session")
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"✅ Session created: {session_id}")
    
    # Connect to WebSocket
    ws_url = f"ws://localhost:8000/realtime-relay/{session_id}?model=gpt-4o-realtime-preview-2024-10-01"
    print(f"🔗 Connecting to: {ws_url}")
    
    try:
        async with websockets.connect(
            ws_url,
            subprotocols=["realtime"],
            close_timeout=10
        ) as websocket:
            print(f"✅ Connected with subprotocol: {websocket.subprotocol}")
            
            # Listen for messages
            message_count = 0
            while message_count < 10:  # Listen for up to 10 messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    print(f"📨 Received: {data.get('type', 'unknown')}")
                    if data.get('type') == 'error':
                        print(f"   Error details: {json.dumps(data, indent=2)}")
                    message_count += 1
                    
                    # If we get session.created, send a test message
                    if data.get('type') == 'session.created':
                        print("🎉 Session created! Sending test message...")
                        test_msg = {
                            "type": "conversation.item.create",
                            "item": {
                                "type": "message",
                                "role": "user",
                                "content": [
                                    {"type": "input_text", "text": "Hello, can you hear me?"}
                                ]
                            }
                        }
                        await websocket.send(json.dumps(test_msg))
                        print("📤 Sent test message")
                        
                        # Request response
                        await asyncio.sleep(0.1)
                        await websocket.send(json.dumps({"type": "response.create"}))
                        print("📤 Sent response.create")
                        
                except asyncio.TimeoutError:
                    print("⏱️ Timeout waiting for message")
                    break
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"❌ Connection closed: code={e.code}, reason={e.reason}")
                    break
                    
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())