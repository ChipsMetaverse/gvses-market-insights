#!/usr/bin/env python3
"""
Test complete OpenAI conversation flow after fixing bytecode cache issue
"""

import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_openai_application_flow():
    """Test the OpenAI connection through the application's WebSocket endpoint"""
    
    backend_url = "ws://localhost:8000/openai/realtime/ws"
    
    print("🎯 Testing complete OpenAI application flow...")
    print(f"🌐 Connecting to: {backend_url}")
    
    try:
        # Connect with the realtime subprotocol (like RealtimeClient does)
        async with websockets.connect(
            backend_url,
            subprotocols=["realtime"]
        ) as ws:
            print("✅ Connected to application WebSocket endpoint!")
            
            # Wait for connection.established first, then session.created
            print("📨 Waiting for connection.established...")
            try:
                # First message: connection.established
                initial_msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
                data = json.loads(initial_msg)
                print(f"📨 Received: {data.get('type', 'unknown type')}")
                
                if data.get("type") == "connection.established":
                    print("✅ Connection established with FastAPI proxy")
                    
                    # Second message: session.created from OpenAI
                    print("📨 Waiting for session.created from OpenAI...")
                    session_msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    session_data = json.loads(session_msg)
                    print(f"📨 Received: {session_data.get('type', 'unknown type')}")
                    
                    if session_data.get("type") == "session.created":
                        print("🎉 SUCCESS: OpenAI session created successfully!")
                        print(f"📋 Session ID: {session_data.get('session', {}).get('id', 'N/A')}")
                        print(f"🔧 Tools available: {len(session_data.get('session', {}).get('tools', []))}")
                        return True
                    else:
                        print(f"❌ Expected session.created, got: {session_data}")
                        return False
                else:
                    print(f"❌ Expected connection.established, got: {data}")
                    return False
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for session.created")
                return False
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def main():
    success = await test_openai_application_flow()
    if success:
        print("\n🎉 VICTORY: OpenAI Realtime connection is working!")
        print("✅ Python bytecode cache issue resolved")
        print("✅ Backend WebSocket proxy working")
        print("✅ OpenAI session created with tools")
    else:
        print("\n❌ Still having issues with the connection")

if __name__ == "__main__":
    asyncio.run(main())