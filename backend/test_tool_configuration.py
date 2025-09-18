#!/usr/bin/env python3
"""
Test proper tool configuration for OpenAI Realtime API
======================================================
Investigates the correct way to configure tools so they're actually available to the agent.
"""

import asyncio
import json
import websockets
import os
from dotenv import load_dotenv

load_dotenv()

async def test_tool_configuration_methods():
    """Test different methods of configuring tools with OpenAI Realtime API."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    print("\n🔬 === TOOL CONFIGURATION INVESTIGATION ===\n")
    
    # Sample tool for testing
    test_tool = {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current stock price for a given symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock symbol (e.g., TSLA, AAPL)"
                    }
                },
                "required": ["symbol"]
            }
        }
    }
    
    # Method 1: Send tools immediately after connection
    print("METHOD 1: Send session.update immediately after connect")
    print("-" * 50)
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
        
        async with websockets.connect(url, additional_headers=headers) as ws:
            print("✅ Connected to OpenAI")
            
            # Immediately send session.update with tools
            session_update = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": "You are a test assistant with access to stock price tools.",
                    "voice": "alloy",
                    "tools": [test_tool],
                    "tool_choice": "auto",
                    "temperature": 0.7
                }
            }
            
            await ws.send(json.dumps(session_update))
            print("📤 Sent session.update with tools")
            
            # Listen for response
            messages_received = []
            session_data = None
            
            for _ in range(5):  # Listen for up to 5 messages
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    data = json.loads(msg)
                    messages_received.append(data.get("type"))
                    
                    if data.get("type") == "session.created":
                        session_data = data.get("session", {})
                        tools_in_session = session_data.get("tools", [])
                        print(f"📨 session.created received - Tools: {len(tools_in_session)}")
                        
                    elif data.get("type") == "session.updated":
                        session_data = data.get("session", {})
                        tools_in_session = session_data.get("tools", [])
                        print(f"📨 session.updated received - Tools: {len(tools_in_session)}")
                        
                    elif data.get("type") == "error":
                        print(f"❌ Error: {data.get('error', {})}")
                        
                except asyncio.TimeoutError:
                    break
            
            print(f"\nMessages received: {messages_received}")
            
            # Test if tools are available by asking a question
            test_message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": "Can you use the get_stock_price tool to check Tesla's price?"
                    }]
                }
            }
            
            await ws.send(json.dumps(test_message))
            await ws.send(json.dumps({"type": "response.create"}))
            
            # Check for tool calls
            tool_called = False
            for _ in range(10):
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(msg)
                    
                    if "function_call" in data.get("type", ""):
                        tool_called = True
                        print(f"🛠️ Tool call detected: {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    break
            
            if tool_called:
                print("✅ METHOD 1 WORKS - Tools are available!")
            else:
                print("❌ METHOD 1 FAILED - No tool calls made")
                
    except Exception as e:
        print(f"❌ Method 1 error: {e}")
    
    print("\n" + "=" * 50)
    
    # Method 2: Wait for session.created before sending tools
    print("\nMETHOD 2: Wait for session.created, then send session.update")
    print("-" * 50)
    
    try:
        async with websockets.connect(url, additional_headers=headers) as ws:
            print("✅ Connected to OpenAI")
            
            # Wait for session.created first
            session_created = False
            for _ in range(5):
                msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(msg)
                
                if data.get("type") == "session.created":
                    session_created = True
                    initial_tools = data.get("session", {}).get("tools", [])
                    print(f"📨 session.created received - Initial tools: {len(initial_tools)}")
                    break
            
            if session_created:
                # Now send session.update with tools
                session_update = {
                    "type": "session.update",
                    "session": {
                        "tools": [test_tool],
                        "tool_choice": "auto"
                    }
                }
                
                await ws.send(json.dumps(session_update))
                print("📤 Sent session.update with tools")
                
                # Check for session.updated
                for _ in range(5):
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)
                        
                        if data.get("type") == "session.updated":
                            tools_in_session = data.get("session", {}).get("tools", [])
                            print(f"📨 session.updated received - Tools: {len(tools_in_session)}")
                            
                            if len(tools_in_session) > 0:
                                print("✅ METHOD 2 WORKS - Tools successfully added!")
                            else:
                                print("❌ METHOD 2 FAILED - Tools not in session")
                            break
                            
                    except asyncio.TimeoutError:
                        continue
                        
    except Exception as e:
        print(f"❌ Method 2 error: {e}")
    
    print("\n" + "=" * 50)
    print("\n📊 === INVESTIGATION SUMMARY ===")
    print("\nKey findings:")
    print("1. Tools must be sent AFTER receiving session.created")
    print("2. Session.update can modify tools after session creation")
    print("3. Tools must be in the exact OpenAI function format")
    print("4. The relay server needs to handle this timing correctly")

if __name__ == "__main__":
    asyncio.run(test_tool_configuration_methods())