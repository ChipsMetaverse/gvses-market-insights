#!/usr/bin/env python3
"""
Test HTTP MCP Endpoint
======================
Test script to verify the HTTP MCP endpoint works correctly for OpenAI Agent Builder integration.
"""

import asyncio
import json
import httpx
import os
from typing import Dict, Any


async def test_mcp_http_endpoint():
    """Test the HTTP MCP endpoint with various JSON-RPC requests."""
    
    base_url = "http://localhost:8000"
    # Use the hardcoded token for testing
    token = "fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ"
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        
        print("🧪 Testing HTTP MCP Endpoint")
        print("=" * 50)
        
        # Test 1: Initialize
        print("\n1. Testing initialize method...")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-01",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            },
            "id": "init-1"
        }
        
        try:
            response = await client.post(f"{base_url}/api/mcp", json=init_request, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Initialize test failed: {e}")
        
        # Test 2: List tools
        print("\n2. Testing tools/list method...")
        list_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": "list-1"
        }
        
        try:
            response = await client.post(f"{base_url}/api/mcp", json=list_request, headers=headers)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Show available tools
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"\n📋 Available tools: {len(tools)}")
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                if len(tools) > 3:
                    print(f"  ... and {len(tools) - 3} more tools")
                    
        except Exception as e:
            print(f"❌ List tools test failed: {e}")
        
        # Test 3: Call a tool (try get_stock_quote)
        print("\n3. Testing tools/call method...")
        call_request = {
            "jsonrpc": "2.0", 
            "method": "tools/call",
            "params": {
                "name": "get_stock_quote",
                "arguments": {"symbol": "AAPL"}
            },
            "id": "call-1"
        }
        
        try:
            response = await client.post(f"{base_url}/api/mcp", json=call_request, headers=headers)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
                    
        except Exception as e:
            print(f"❌ Call tool test failed: {e}")
        
        # Test 4: Test with query parameter token
        print("\n4. Testing with query parameter token...")
        try:
            response = await client.post(
                f"{base_url}/api/mcp?token={token}", 
                json=init_request,
                headers={"Content-Type": "application/json"}  # No auth header
            )
            print(f"Status: {response.status_code}")
            print(f"Query token auth: {'✅ Success' if response.status_code == 200 else '❌ Failed'}")
        except Exception as e:
            print(f"❌ Query token test failed: {e}")
        
        # Test 5: Test authentication failure
        print("\n5. Testing authentication failure...")
        try:
            response = await client.post(
                f"{base_url}/api/mcp", 
                json=init_request,
                headers={"Content-Type": "application/json"}  # No auth
            )
            print(f"Status: {response.status_code}")
            print(f"No auth rejection: {'✅ Success' if response.status_code == 401 else '❌ Failed'}")
        except Exception as e:
            print(f"❌ Auth failure test failed: {e}")
        
        # Test 6: Alternative endpoint
        print("\n6. Testing alternative endpoint /mcp/http...")
        try:
            response = await client.post(f"{base_url}/mcp/http", json=init_request, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Alt endpoint: {'✅ Success' if response.status_code == 200 else '❌ Failed'}")
        except Exception as e:
            print(f"❌ Alt endpoint test failed: {e}")


async def test_mcp_status():
    """Test the MCP status endpoint."""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("\n🔍 Testing MCP Status Endpoint")
        print("=" * 40)
        
        try:
            response = await client.get(f"{base_url}/mcp/status")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Status test failed: {e}")


async def main():
    """Run all tests."""
    print("🚀 Starting HTTP MCP Endpoint Tests")
    print("Make sure the backend server is running on localhost:8000")
    print()
    
    await test_mcp_status()
    await test_mcp_http_endpoint()
    
    print("\n✅ All tests completed!")
    print()
    print("💡 For OpenAI Agent Builder, use:")
    print("   URL: https://your-domain.com/api/mcp")
    print("   Auth: Add 'Authorization: Bearer fo1_...' header")
    print("   Or:  Add '?token=fo1_...' query parameter")


if __name__ == "__main__":
    asyncio.run(main())