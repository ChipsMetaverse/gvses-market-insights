#!/usr/bin/env python3
"""Test script for OpenAI Realtime API proxy endpoint."""

import asyncio
import json
import httpx
import websockets
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Configuration
BACKEND_URL = "http://localhost:8000"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def test_session_creation():
    """Test creating an OpenAI Realtime session."""
    print("\n🔍 Testing session creation...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}/openai/realtime/session",
                json={
                    "model": "gpt-realtime-2025-08-28",
                    "voice": "alloy"
                }
            )
            response.raise_for_status()
            data = response.json()
            print(f"✅ Session created successfully!")
            print(f"   Session ID: {data['sessionId']}")
            print(f"   WebSocket URL: {data['wsUrl']}")
            print(f"   Model: {data['model']}")
            print(f"   Voice: {data['voice']}")
            return data
        except Exception as e:
            print(f"❌ Failed to create session: {e}")
            return None

async def test_websocket_connection(session_data):
    """Test WebSocket connection to OpenAI Realtime proxy."""
    if not session_data:
        print("⚠️ Skipping WebSocket test (no session)")
        return
    
    print("\n🔍 Testing WebSocket connection...")
    
    # Extract WebSocket URL
    ws_url = session_data['wsUrl']
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ Connected to WebSocket!")
            
            # Set up message handler
            async def receive_messages():
                try:
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(f"   📥 Received: {data.get('type', 'unknown')}")
                        
                        # Handle specific message types
                        if data.get('type') == 'session.created':
                            print(f"   ✅ Session initialized!")
                            print(f"      Model: {data['session']['model']}")
                            print(f"      Voice: {data['session']['voice']}")
                            return True
                        elif data.get('type') == 'error':
                            print(f"   ❌ Error: {data['error']['message']}")
                            return False
                except websockets.exceptions.ConnectionClosed:
                    print("   WebSocket connection closed")
                    return False
                except Exception as e:
                    print(f"   Error receiving messages: {e}")
                    return False
            
            # Wait for session creation
            result = await asyncio.wait_for(receive_messages(), timeout=10)
            
            if result:
                # Test sending a simple text message
                print("\n🔍 Testing text message...")
                
                # Send a text message
                message = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "Hello, can you hear me?"
                            }
                        ]
                    }
                }
                await websocket.send(json.dumps(message))
                print("   📤 Sent text message")
                
                # Trigger response
                await websocket.send(json.dumps({"type": "response.create"}))
                print("   📤 Triggered response generation")
                
                # Listen for response
                response_received = False
                timeout = 15  # seconds
                start_time = asyncio.get_event_loop().time()
                
                while not response_received:
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        print("   ⏱️ Timeout waiting for response")
                        break
                    
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1)
                        data = json.loads(message)
                        msg_type = data.get('type', '')
                        
                        if msg_type == 'response.audio_transcript.delta':
                            print(f"   📝 Transcript: {data.get('delta', '')}")
                        elif msg_type == 'response.done':
                            print("   ✅ Response completed!")
                            response_received = True
                        elif msg_type == 'error':
                            print(f"   ❌ Error: {data['error']['message']}")
                            break
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"   Error: {e}")
                        break
                
            print("\n✅ WebSocket test completed!")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

async def test_backend_health():
    """Test if backend is running and configured."""
    print("🔍 Testing backend health...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}/health")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Backend is healthy!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Service Mode: {data.get('service_mode', 'unknown')}")
            return True
        except Exception as e:
            print(f"❌ Backend health check failed: {e}")
            return False

async def main():
    """Run all tests."""
    print("=" * 50)
    print("OpenAI Realtime API Proxy Test")
    print("=" * 50)
    
    # Check if API key is configured
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-your-openai-api-key-here":
        print("\n⚠️ WARNING: OpenAI API key not configured!")
        print("Please set OPENAI_API_KEY in backend/.env")
        print("You can still test the proxy endpoints, but WebSocket connection will fail.")
    
    # Test backend health
    if not await test_backend_health():
        print("\n❌ Backend is not running!")
        print("Please start the backend with: cd backend && uvicorn mcp_server:app --reload")
        return
    
    # Test session creation
    session_data = await test_session_creation()
    
    # Test WebSocket connection
    await test_websocket_connection(session_data)
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())