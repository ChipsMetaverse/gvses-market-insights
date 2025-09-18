#!/usr/bin/env python3
"""
Test OpenAI Relay Server Tool Configuration
============================================
Verifies that tools are properly sent to OpenAI after session.created
"""

import asyncio
import json
import websockets
from websockets.client import WebSocketClientProtocol

async def test_relay_tools():
    """Test that relay server properly configures tools."""
    
    print("\n🔧 === TESTING RELAY SERVER TOOL CONFIGURATION ===\n")
    
    relay_url = "ws://localhost:8000/realtime-relay/test-session-123"
    
    try:
        print("1️⃣ Connecting to relay server...")
        async with websockets.connect(relay_url, subprotocols=["openai-realtime"]) as ws:
            print("✅ Connected to relay server")
            
            messages_received = []
            tools_configured = False
            tool_count = 0
            
            # Listen for messages
            print("\n2️⃣ Listening for session configuration...")
            for i in range(10):  # Listen for up to 10 messages
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    data = json.loads(msg)
                    msg_type = data.get("type", "unknown")
                    messages_received.append(msg_type)
                    
                    print(f"   📨 Received: {msg_type}")
                    
                    if msg_type == "session.created":
                        session = data.get("session", {})
                        initial_tools = session.get("tools", [])
                        print(f"      Initial tools: {len(initial_tools)}")
                        
                    elif msg_type == "session.updated":
                        session = data.get("session", {})
                        tools = session.get("tools", [])
                        tool_count = len(tools)
                        print(f"      ✅ Session updated with {tool_count} tools")
                        
                        if tool_count > 0:
                            tools_configured = True
                            print("\n   📋 Tools configured:")
                            for tool in tools[:5]:  # Show first 5 tools
                                # Handle both flat and nested formats
                                if "name" in tool:
                                    print(f"      - {tool['name']}")
                                elif "function" in tool and "name" in tool["function"]:
                                    print(f"      - {tool['function']['name']}")
                            if len(tools) > 5:
                                print(f"      ... and {len(tools) - 5} more")
                            break
                            
                    elif msg_type == "error":
                        error = data.get("error", {})
                        print(f"   ❌ Error: {error.get('message', 'Unknown error')}")
                        
                except asyncio.TimeoutError:
                    continue
            
            print(f"\n3️⃣ Summary:")
            print(f"   Messages received: {messages_received}")
            print(f"   Tools configured: {'✅ Yes' if tools_configured else '❌ No'}")
            print(f"   Tool count: {tool_count}")
            
            if tools_configured:
                print("\n4️⃣ Testing tool execution...")
                # Send a message that should trigger tool use
                test_msg = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "message",
                        "role": "user",
                        "content": [{
                            "type": "input_text",
                            "text": "What's the current price of Tesla stock?"
                        }]
                    }
                }
                
                await ws.send(json.dumps(test_msg))
                await ws.send(json.dumps({"type": "response.create"}))
                print("   📤 Sent test query: 'What's the current price of Tesla stock?'")
                
                # Listen for tool calls
                tool_called = False
                for _ in range(10):
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)
                        msg_type = data.get("type", "")
                        
                        if "function_call" in msg_type or "tool_call" in msg_type:
                            tool_called = True
                            print(f"   🛠️ Tool activity detected: {msg_type}")
                            
                    except asyncio.TimeoutError:
                        continue
                
                if tool_called:
                    print("   ✅ Tools are working!")
                else:
                    print("   ⚠️  No tool calls detected")
            
            print("\n✅ === TEST COMPLETE ===")
            
            if tools_configured and tool_count > 0:
                print(f"\n🎉 SUCCESS: Relay server configured {tool_count} tools for OpenAI!")
                print("The agent now has market analysis capabilities!")
            else:
                print("\n❌ FAILURE: Tools were not configured")
                print("The relay server may not be sending tools after session.created")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("1. Backend server not running on port 8000")
        print("2. Relay endpoint not configured")
        print("3. OpenAI API key not set")

if __name__ == "__main__":
    asyncio.run(test_relay_tools())
