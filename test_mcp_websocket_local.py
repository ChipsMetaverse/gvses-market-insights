#!/usr/bin/env python3
"""
Test MCP WebSocket endpoint locally
"""
import asyncio
import websockets
import json
import sys

async def test_mcp_websocket_local():
    """Test MCP WebSocket endpoint locally"""
    # Local WebSocket URL
    url = "ws://127.0.0.1:8001/mcp"
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
                print(f"Tools response length: {len(tools_response)} chars")
                
                tools_data = json.loads(tools_response)
                if "result" in tools_data and "tools" in tools_data["result"]:
                    tools = tools_data["result"]["tools"]
                    print(f"✅ Found {len(tools)} MCP tools available!")
                    print("Available tools:")
                    for i, tool in enumerate(tools, 1):
                        print(f"  {i}. {tool.get('name', 'Unknown')} - {tool.get('description', 'No description')[:80]}")
                        
                    return True
                else:
                    print(f"❌ No tools found in response: {tools_data}")
                    return False
            else:
                print(f"❌ Initialization failed: {init_response}")
                return False
                
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ WebSocket connection closed: {e}")
        return False
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing MCP WebSocket endpoint locally...")
    result = asyncio.run(test_mcp_websocket_local())
    sys.exit(0 if result else 1)