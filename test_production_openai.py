#!/usr/bin/env python3
"""Test OpenAI relay on production server."""

import asyncio
import json
import websockets
import sys

async def test_openai_relay():
    """Test the OpenAI relay WebSocket endpoint."""
    
    # Use production URL
    url = "wss://gvses-market-insights.fly.dev/ws/openai/relay"
    
    print(f"Connecting to {url}...")
    
    try:
        async with websockets.connect(url) as websocket:
            print("✓ Connected to WebSocket")
            
            # Wait for initial messages
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    print(f"  Message {i+1}: type={data.get('type')}")
                    
                    if data.get("type") == "session.created":
                        print("✓ Session created successfully")
                        # Check for tools
                        session = data.get("session", {})
                        tools = session.get("tools", [])
                        print(f"  Tools configured: {len(tools)}")
                        if tools:
                            print("  First 3 tools:")
                            for tool in tools[:3]:
                                print(f"    - {tool.get('name', 'unknown')}")
                        
                        # Check instructions
                        instructions = session.get("instructions", "")
                        if "MarketSage" in instructions:
                            print("✓ Enhanced training loaded (MarketSage persona found)")
                        else:
                            print("✗ Enhanced training not loaded")
                        
                        print(f"  Instructions length: {len(instructions)} chars")
                        
                except asyncio.TimeoutError:
                    break
            
            print("✓ Test completed successfully")
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_openai_relay())
    sys.exit(0 if success else 1)