#!/usr/bin/env python3
"""
Test MCP WebSocket endpoint in production
"""
import asyncio
import websockets
import json
import sys

async def test_mcp_websocket():
    """Test MCP WebSocket endpoint with proper authentication"""
    # Production WebSocket URL
    url = "wss://gvses-market-insights.fly.dev/mcp"
    token = "fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ"
    
    # Add token as query parameter
    auth_url = f"{url}?token={token}"
    
    try:
        print(f"Connecting to: {auth_url}")
        
        async with websockets.connect(auth_url) as websocket:
            print("✅ WebSocket connection established!")
            
            # Send MCP initialize message
            init_message = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-01",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                },
                "id": "1"
            }
            
            print("Sending initialize message...")
            await websocket.send(json.dumps(init_message))
            
            # Wait for initialization response
            response = await websocket.recv()
            print(f"Initialize response: {response}")
            
            init_response = json.loads(response)
            if "result" in init_response:
                print("✅ MCP initialized successfully!")
                
                # Send initialized notification
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                await websocket.send(json.dumps(initialized_notification))
                
                # List available tools
                tools_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": "2"
                }
                
                print("Requesting tools list...")
                await websocket.send(json.dumps(tools_request))
                
                tools_response = await websocket.recv()
                print(f"Tools response: {tools_response}")
                
                tools_data = json.loads(tools_response)
                if "result" in tools_data and "tools" in tools_data["result"]:
                    tools = tools_data["result"]["tools"]
                    print(f"✅ Found {len(tools)} MCP tools available!")
                    for i, tool in enumerate(tools[:5], 1):  # Show first 5 tools
                        print(f"  {i}. {tool.get('name', 'Unknown')}")
                    if len(tools) > 5:
                        print(f"  ... and {len(tools) - 5} more tools")
                        
                    # Test calling a tool
                    if tools:
                        test_tool = next((t for t in tools if t.get('name') == 'get_market_overview'), tools[0])
                        tool_request = {
                            "jsonrpc": "2.0",
                            "method": "tools/call",
                            "params": {
                                "name": test_tool["name"],
                                "arguments": {}
                            },
                            "id": "3"
                        }
                        
                        print(f"Testing tool call: {test_tool['name']}")
                        await websocket.send(json.dumps(tool_request))
                        
                        tool_response = await websocket.recv()
                        print(f"Tool response length: {len(tool_response)} chars")
                        
                        tool_data = json.loads(tool_response)
                        if "result" in tool_data:
                            print("✅ Tool call successful!")
                        else:
                            print(f"❌ Tool call failed: {tool_data}")
                            
                else:
                    print(f"❌ No tools found in response: {tools_data}")
            else:
                print(f"❌ Initialization failed: {init_response}")
                
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ WebSocket connection closed: {e}")
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing MCP WebSocket endpoint in production...")
    asyncio.run(test_mcp_websocket())