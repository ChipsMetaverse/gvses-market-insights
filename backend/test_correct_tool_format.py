#!/usr/bin/env python3
"""
Test the CORRECT tool format for OpenAI Realtime API
=====================================================
The Realtime API uses a different tool format than the Chat Completions API!
"""

import asyncio
import json
import websockets
import os
from dotenv import load_dotenv

load_dotenv()

async def test_correct_tool_format():
    """Test the correct tool format for OpenAI Realtime API."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    print("\n🔧 === TESTING CORRECT TOOL FORMAT ===\n")
    
    # Format 1: Chat Completions format (what we're currently using)
    chat_format_tool = {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current stock price",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"}
                },
                "required": ["symbol"]
            }
        }
    }
    
    # Format 2: Realtime API format (flat structure)
    realtime_format_tool = {
        "type": "function",
        "name": "get_stock_price",
        "description": "Get the current stock price",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol"}
            },
            "required": ["symbol"]
        }
    }
    
    # Format 3: Minimal format (no type field)
    minimal_format_tool = {
        "name": "get_stock_price",
        "description": "Get the current stock price",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol"}
            },
            "required": ["symbol"]
        }
    }
    
    tools_to_test = [
        ("Chat Completions Format", chat_format_tool),
        ("Realtime Flat Format", realtime_format_tool),
        ("Minimal Format", minimal_format_tool)
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2025-08-28"
    
    for format_name, tool in tools_to_test:
        print(f"\nTesting: {format_name}")
        print("-" * 40)
        
        try:
            async with websockets.connect(url, additional_headers=headers) as ws:
                # Wait for session.created
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get("type") == "session.created":
                    print("✅ Session created")
                
                # Send session.update with the tool
                session_update = {
                    "type": "session.update",
                    "session": {
                        "tools": [tool],
                        "tool_choice": "auto",
                        "instructions": "You have access to a stock price tool. Use it when asked about stock prices."
                    }
                }
                
                await ws.send(json.dumps(session_update))
                print(f"📤 Sent tool in {format_name} format")
                
                # Check response
                success = False
                error = None
                tools_count = 0
                
                for _ in range(3):
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)
                        
                        if data.get("type") == "error":
                            error = data.get("error", {}).get("message", "Unknown error")
                            print(f"❌ Error: {error}")
                            break
                            
                        elif data.get("type") == "session.updated":
                            tools_count = len(data.get("session", {}).get("tools", []))
                            if tools_count > 0:
                                success = True
                                print(f"✅ Session updated with {tools_count} tool(s)")
                                
                                # Test if tool can be called
                                test_msg = {
                                    "type": "conversation.item.create",
                                    "item": {
                                        "type": "message",
                                        "role": "user",
                                        "content": [{
                                            "type": "input_text",
                                            "text": "What's the stock price of TSLA?"
                                        }]
                                    }
                                }
                                await ws.send(json.dumps(test_msg))
                                await ws.send(json.dumps({"type": "response.create"}))
                                
                                # Check for function call
                                for _ in range(5):
                                    try:
                                        msg = await asyncio.wait_for(ws.recv(), timeout=0.5)
                                        data = json.loads(msg)
                                        if "function_call" in data.get("type", ""):
                                            print(f"🛠️ Tool called successfully!")
                                            break
                                    except asyncio.TimeoutError:
                                        continue
                            break
                            
                    except asyncio.TimeoutError:
                        continue
                
                if success:
                    print(f"✅ {format_name} WORKS!")
                elif error:
                    print(f"❌ {format_name} FAILED: {error}")
                else:
                    print(f"❌ {format_name} FAILED: No tools registered")
                    
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    print("\n" + "=" * 50)
    print("\n📊 === RESULTS ===")
    print("\nThe correct tool format for OpenAI Realtime API is:")
    print("- Tools should be a flat structure with 'name' at the top level")
    print("- NOT nested under 'function' like in Chat Completions API")
    print("- Must include: name, description, parameters")
    print("- Optional: type field (defaults to 'function')")

if __name__ == "__main__":
    asyncio.run(test_correct_tool_format())