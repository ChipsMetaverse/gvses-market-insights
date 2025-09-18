#!/usr/bin/env python3
"""
Direct test of OpenAI Realtime WebSocket connection to isolate issues
"""

import asyncio
import json
import websockets
import os
from dotenv import load_dotenv

load_dotenv()

async def test_openai_realtime_direct():
    """Test direct connection to OpenAI Realtime API to identify issues"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    print("🔗 TESTING DIRECT OPENAI REALTIME CONNECTION")
    print("=" * 50)
    
    try:
        # Connection parameters
        url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        print(f"🌐 Connecting to: {url}")
        print(f"🔑 API Key length: {len(api_key)} chars")
        
        # Connect to OpenAI
        websocket = await websockets.connect(url, additional_headers=headers)
        print("✅ Connected successfully!")
        
        # Send basic session update (minimal config)
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "You are a helpful assistant.",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "temperature": 0.7
            }
        }
        
        print("📤 Sending session configuration...")
        await websocket.send(json.dumps(session_config))
        print("✅ Session config sent")
        
        # Wait for messages for a few seconds
        print("⏱️ Waiting for OpenAI response (10 seconds)...")
        
        try:
            # Set a timeout to avoid hanging
            message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            print(f"📨 Received message: {message}")
            
            # Parse and check message type
            if isinstance(message, str):
                data = json.loads(message)
                message_type = data.get("type", "unknown")
                print(f"📋 Message type: {message_type}")
                
                if message_type == "session.updated":
                    print("✅ Session updated successfully")
                elif message_type == "error":
                    error_details = data.get("error", {})
                    print(f"❌ OpenAI Error: {error_details}")
                else:
                    print(f"ℹ️ Other message type: {message_type}")
            
            # Try to receive more messages
            print("⏱️ Checking for additional messages (5 seconds)...")
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"📨 Additional message: {message[:200]}...")
            except asyncio.TimeoutError:
                print("⏰ No more messages after 5 seconds")
                
        except asyncio.TimeoutError:
            print("⏰ No response from OpenAI within 10 seconds")
            
        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ Connection closed by OpenAI: {e}")
            print(f"   Close code: {e.code}")
            print(f"   Close reason: {e.reason}")
            
        # Check connection state
        print(f"🔍 Connection state: {websocket.state.name}")
        
        # Keep connection alive for a bit
        print("⏱️ Keeping connection alive for 15 seconds...")
        await asyncio.sleep(15)
        
        print(f"🔍 Final connection state: {websocket.state.name}")
        
        # Clean close
        await websocket.close()
        print("✅ Connection closed cleanly")
        
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        
    except Exception as e:
        import traceback
        print(f"❌ Unexpected error: {e}")
        print(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_openai_realtime_direct())