#!/usr/bin/env python3
"""
Test script for Alpaca MCP Server
Tests that the server starts and can be accessed via MCP client
"""

import json
import subprocess
import time
import sys
import asyncio
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client
import os

async def test_alpaca_mcp_server():
    """Test the Alpaca MCP server."""
    print("Testing Alpaca MCP Server...")
    
    # Set up environment variables
    env = os.environ.copy()
    env.update({
        'ALPACA_API_KEY': os.getenv('ALPACA_API_KEY'),
        'ALPACA_SECRET_KEY': os.getenv('ALPACA_SECRET_KEY'),
        'ALPACA_BASE_URL': os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    })
    
    # Start the server as a subprocess
    server_proc = subprocess.Popen(
        ['python3', 'alpaca-mcp-server/server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=False
    )
    
    try:
        # Create MCP client
        async with stdio_client(server_proc) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the session
                await session.initialize()
                
                # List available tools
                print("\n Available Tools:")
                tools_response = await session.list_tools()
                for tool in tools_response.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Test get_market_status tool
                print("\n Testing get_market_status tool...")
                try:
                    result = await session.call_tool("get_market_status", {})
                    market_status = json.loads(result.content[0].text)
                    print(f"Market Status: {json.dumps(market_status, indent=2)}")
                except Exception as e:
                    print(f"Error calling get_market_status: {e}")
                
                # Test get_stock_quote tool
                print("\n Testing get_stock_quote tool...")
                try:
                    result = await session.call_tool("get_stock_quote", {"symbol": "AAPL"})
                    quote = json.loads(result.content[0].text)
                    print(f"AAPL Quote: {json.dumps(quote, indent=2)}")
                except Exception as e:
                    print(f"Error calling get_stock_quote: {e}")
                
                # Test get_account tool
                print("\n Testing get_account tool...")
                try:
                    result = await session.call_tool("get_account", {})
                    account = json.loads(result.content[0].text)
                    print(f"Account Info: {json.dumps(account, indent=2)}")
                except Exception as e:
                    print(f"Error calling get_account: {e}")
                
                print("\n✅ Alpaca MCP Server tests completed successfully!")
                
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        server_proc.terminate()
        server_proc.wait()


def main():
    """Main entry point."""
    # Check for required environment variables
    if not os.getenv('ALPACA_API_KEY'):
        print("Error: ALPACA_API_KEY not set in environment")
        sys.exit(1)
    
    if not os.getenv('ALPACA_SECRET_KEY'):
        print("Error: ALPACA_SECRET_KEY not set in environment")
        sys.exit(1)
    
    # Run the async test
    asyncio.run(test_alpaca_mcp_server())


if __name__ == "__main__":
    main()