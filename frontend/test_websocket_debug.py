#!/usr/bin/env python3
"""
Test WebSocket connection to our proxy to debug the immediate closure issue
"""

import asyncio
import websockets
import json

async def test_proxy_websocket():
    """Test connection to our WebSocket proxy"""
    
    print("🔗 TESTING PROXY WEBSOCKET CONNECTION")
    print("=" * 50)
    
    try:
        # Connect to our proxy
        url = "ws://localhost:8000/openai/realtime/ws?model=gpt-realtime-2025-08-28"
        
        print(f"🌐 Connecting to proxy: {url}")
        
        websocket = await websockets.connect(url, subprotocols=["realtime"])
        print("✅ Connected to proxy successfully!")
        
        # Wait for connection establishment message
        print("⏱️ Waiting for connection establishment message...")
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            print(f"📨 Received: {message}")
            
            # Parse message
            if isinstance(message, str):
                data = json.loads(message)
                message_type = data.get("type", "unknown")
                print(f"📋 Message type: {message_type}")
                
                if message_type == "connection.established":
                    print("✅ Connection established successfully")
                elif message_type == "error":
                    error_details = data.get("error", {})
                    print(f"❌ Proxy Error: {error_details}")
                
        except asyncio.TimeoutError:
            print("⏰ No establishment message within 10 seconds")
        
        # Try sending a simple message
        print("📤 Sending test message...")
        test_message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Hello, can you help me with market data?"
                    }
                ]
            }
        }
        
        await websocket.send(json.dumps(test_message))
        print("✅ Test message sent")
        
        # Wait for responses
        print("⏱️ Waiting for responses (10 seconds)...")
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📨 Response: {message[:200]}...")
        except asyncio.TimeoutError:
            print("⏰ No more responses")
        
        print(f"🔍 Connection state: {websocket.state.name}")
        
        # Keep connection alive
        print("⏱️ Keeping connection alive for 15 seconds...")
        await asyncio.sleep(15)
        
        print(f"🔍 Final connection state: {websocket.state.name}")
        
        await websocket.close()
        print("✅ Connection closed cleanly")
        
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
        print(f"   Close code: {e.code}")
        print(f"   Close reason: {e.reason}")
        
    except Exception as e:
        import traceback
        print(f"❌ Unexpected error: {e}")
        print(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_proxy_websocket())