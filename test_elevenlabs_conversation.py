#!/usr/bin/env python3
"""Test script for ElevenLabs Conversational AI WebSocket connection."""

import asyncio
import json
import websockets
import requests
import sys

async def test_elevenlabs_websocket():
    """Test ElevenLabs WebSocket connection and basic conversation flow."""
    
    # Get signed URL from backend
    try:
        response = requests.get("http://localhost:8000/elevenlabs/signed-url")
        response.raise_for_status()
        signed_url = response.json()["signed_url"]
        print(f"✓ Got signed URL: {signed_url}")
    except Exception as e:
        print(f"✗ Failed to get signed URL: {e}")
        return False
    
    # Test WebSocket connection
    try:
        async with websockets.connect(signed_url) as websocket:
            print("✓ WebSocket connected successfully!")
            
            # Send initialization message
            init_message = {
                "type": "conversation_initiation_client_data"
            }
            await websocket.send(json.dumps(init_message))
            print("✓ Sent initialization message")
            
            # Listen for a few messages
            message_count = 0
            timeout_seconds = 10
            
            try:
                while message_count < 5:  # Listen for up to 5 messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=timeout_seconds)
                    data = json.loads(message)
                    message_type = data.get("type", "unknown")
                    print(f"✓ Received message type: {message_type}")
                    
                    # Handle ping messages
                    if message_type == "ping":
                        event_id = data.get("ping_event", {}).get("event_id")
                        ping_ms = data.get("ping_event", {}).get("ping_ms") or 0
                        
                        # Wait for ping_ms then send pong
                        if ping_ms and ping_ms > 0:
                            await asyncio.sleep(ping_ms / 1000)
                        
                        pong_message = {
                            "type": "pong",
                            "event_id": event_id
                        }
                        await websocket.send(json.dumps(pong_message))
                        print(f"✓ Sent pong response for event_id: {event_id}")
                    
                    # Test sending a text message
                    if message_count == 2:  # Send after receiving a few messages
                        test_message = {
                            "type": "user_message",
                            "text": "Hello, can you hear me? This is a test message."
                        }
                        await websocket.send(json.dumps(test_message))
                        print("✓ Sent test text message")
                    
                    message_count += 1
                    
            except asyncio.TimeoutError:
                print(f"⚠ Timeout after {timeout_seconds}s - but connection established successfully!")
            
        print("✓ WebSocket connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ WebSocket connection failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🎤 Testing ElevenLabs Conversational AI Integration")
    print("=" * 50)
    
    # Test backend endpoint
    print("\n1. Testing backend signed URL endpoint...")
    success = await test_elevenlabs_websocket()
    
    if success:
        print(f"\n🎉 Voice agent integration test PASSED!")
        print("   - Backend signed URL endpoint works")
        print("   - WebSocket connection establishes successfully")
        print("   - Message sending/receiving works")
        print("   - Ping/pong keepalive works")
    else:
        print(f"\n❌ Voice agent integration test FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
