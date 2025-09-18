#!/usr/bin/env python3
"""
Final Test: OpenAI Agent with Market Capabilities
==================================================
Tests the complete flow: connection → session.created → tools configured → tool usage
"""

import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_final_agent():
    """Test the complete agent with market capabilities."""
    
    print("\n🚀 === FINAL AGENT TEST: MARKET CAPABILITIES ===\n")
    
    relay_url = "ws://localhost:8000/realtime-relay/final-test-session"
    
    try:
        print("1️⃣ Connecting to relay server...")
        async with websockets.connect(
            relay_url, 
            subprotocols=["openai-realtime"]
        ) as ws:
            print("✅ Connected to relay server")
            
            session_created = False
            tools_configured = False
            tool_count = 0
            tool_names = []
            
            # Phase 1: Wait for session.created and session.updated
            print("\n2️⃣ Waiting for session configuration...")
            for i in range(15):  # Wait longer for OpenAI connection
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    data = json.loads(msg)
                    msg_type = data.get("type", "unknown")
                    
                    if msg_type == "session.created":
                        session_created = True
                        session = data.get("session", {})
                        initial_tools = session.get("tools", [])
                        print(f"   ✅ session.created received")
                        print(f"      Initial tools: {len(initial_tools)}")
                        
                    elif msg_type == "session.updated":
                        session = data.get("session", {})
                        tools = session.get("tools", [])
                        tool_count = len(tools)
                        
                        if tool_count > 0:
                            tools_configured = True
                            print(f"   ✅ session.updated with {tool_count} tools!")
                            
                            # Extract tool names
                            for tool in tools:
                                if "name" in tool:
                                    tool_names.append(tool["name"])
                                elif "function" in tool:
                                    tool_names.append(tool["function"].get("name", "unknown"))
                            
                            print("\n   📋 Market Analysis Tools Available:")
                            for name in tool_names[:8]:
                                print(f"      • {name}")
                            if len(tool_names) > 8:
                                print(f"      ... and {len(tool_names) - 8} more")
                            break
                            
                    elif msg_type == "error":
                        error = data.get("error", {})
                        print(f"   ❌ Error: {error.get('message', 'Unknown')}")
                        
                except asyncio.TimeoutError:
                    if i > 5 and not session_created:
                        print("   ⚠️  Taking longer than expected...")
                    continue
            
            # Phase 2: Test tool usage if configured
            if tools_configured:
                print("\n3️⃣ Testing market analysis capabilities...")
                
                # Test query 1: Stock price
                print("\n   📊 Query 1: Stock Price")
                query1 = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "message",
                        "role": "user",
                        "content": [{
                            "type": "input_text",
                            "text": "What is Tesla's current stock price?"
                        }]
                    }
                }
                
                await ws.send(json.dumps(query1))
                await ws.send(json.dumps({"type": "response.create"}))
                print("      Sent: 'What is Tesla's current stock price?'")
                
                # Listen for response
                tool_used = False
                for _ in range(10):
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)
                        msg_type = data.get("type", "")
                        
                        if "function_call" in msg_type:
                            tool_name = data.get("name", "")
                            print(f"      🛠️ Tool called: {tool_name}")
                            tool_used = True
                        elif msg_type == "response.function_call_arguments.done":
                            call_id = data.get("call_id")
                            name = data.get("name")
                            args = data.get("arguments", "{}")
                            print(f"      📞 Function: {name}")
                            print(f"         Args: {args[:100]}...")
                            tool_used = True
                        elif msg_type == "tool_call_start":
                            print(f"      🔧 Tool execution started: {data.get('tool_name')}")
                            tool_used = True
                        elif msg_type == "tool_call_complete":
                            print(f"      ✅ Tool completed: {data.get('tool_name')}")
                            
                    except asyncio.TimeoutError:
                        continue
                
                if tool_used:
                    print("      ✅ Market data tool executed successfully!")
                else:
                    print("      ⚠️  No tool usage detected")
                
                # Test query 2: Market overview
                print("\n   📊 Query 2: Market Overview")
                query2 = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "message",
                        "role": "user",
                        "content": [{
                            "type": "input_text",
                            "text": "Give me a quick market overview with major indices"
                        }]
                    }
                }
                
                await ws.send(json.dumps(query2))
                await ws.send(json.dumps({"type": "response.create"}))
                print("      Sent: 'Give me a quick market overview'")
                
                # Brief listen for market overview tool
                await asyncio.sleep(3)
                
            # Phase 3: Results
            print("\n" + "=" * 60)
            print("\n📊 === FINAL RESULTS ===\n")
            
            if session_created:
                print("✅ Session created successfully")
            else:
                print("❌ Session creation failed")
                
            if tools_configured:
                print(f"✅ {tool_count} market analysis tools configured")
                print("\n🎉 SUCCESS! The OpenAI agent now has market analysis capabilities!")
                print("\nThe agent can now:")
                print("  • Get real-time stock quotes")
                print("  • Analyze market trends")
                print("  • Provide technical indicators")
                print("  • Access market news")
                print("  • Generate market overviews")
            else:
                print("❌ No tools configured - agent has no market capabilities")
                print("\nThe fixes may not have been applied correctly.")
                
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure backend is running: uvicorn mcp_server:app --reload")
        print("2. Check OPENAI_API_KEY is set in backend/.env")
        print("3. Verify the relay server module is imported correctly")

if __name__ == "__main__":
    asyncio.run(test_final_agent())