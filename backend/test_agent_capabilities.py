#!/usr/bin/env python3
"""Test what capabilities the OpenAI agent actually has."""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.openai_tool_mapper import get_tool_mapper
from services.agent_orchestrator import AgentOrchestrator

async def test_agent_capabilities():
    print("\n🤖 OPENAI AGENT CAPABILITY TEST\n")
    print("=" * 50)
    
    # Initialize tool mapper
    print("\n1. Initializing Tool Mapper...")
    mapper = await get_tool_mapper()
    print("   ✅ Tool mapper initialized")
    
    # Get orchestrator for MCP tools
    print("\n2. Getting MCP Tools...")
    orchestrator = AgentOrchestrator()
    mcp_tools = await orchestrator.get_available_tools()
    print(f"   📦 Found {len(mcp_tools)} MCP tools")
    
    # Convert to OpenAI format
    print("\n3. Converting to OpenAI Format...")
    openai_tools = mapper.map_tools_to_openai(mcp_tools)
    print(f"   ✅ Successfully mapped {len(openai_tools)} tools")
    
    # Categorize tools
    print("\n4. Tool Categories:")
    categories = {
        "market": [],
        "stock": [],
        "crypto": [],
        "news": [],
        "chart": [],
        "other": []
    }
    
    for tool in openai_tools:
        name = tool["function"]["name"].lower()
        if "market" in name:
            categories["market"].append(tool["function"]["name"])
        elif "stock" in name or "quote" in name or "price" in name:
            categories["stock"].append(tool["function"]["name"])
        elif "crypto" in name or "bitcoin" in name:
            categories["crypto"].append(tool["function"]["name"])
        elif "news" in name:
            categories["news"].append(tool["function"]["name"])
        elif "chart" in name:
            categories["chart"].append(tool["function"]["name"])
        else:
            categories["other"].append(tool["function"]["name"])
    
    for category, tools in categories.items():
        if tools:
            print(f"\n   📊 {category.upper()} ({len(tools)} tools):")
            for tool_name in tools[:5]:
                print(f"      - {tool_name}")
            if len(tools) > 5:
                print(f"      ... and {len(tools) - 5} more")
    
    # Test tool execution
    print("\n5. Testing Tool Execution:")
    test_tools = [
        ("get_stock_price", {"symbol": "TSLA"}),
        ("get_market_status", {}),
    ]
    
    for tool_name, args in test_tools:
        # Find the original MCP tool name
        mcp_tool_name = tool_name
        for mcp_tool in mcp_tools:
            if mcp_tool.get("name", "").replace("-", "_").replace(".", "_") == tool_name:
                mcp_tool_name = mcp_tool["name"]
                break
        
        print(f"\n   🧪 Testing: {tool_name}")
        print(f"      Args: {args}")
        
        try:
            # Test if we can execute the tool
            if hasattr(mapper, 'execute_tool'):
                result = await mapper.execute_tool(mcp_tool_name, args)
                print(f"      ✅ Result: {json.dumps(result, indent=2)[:200]}...")
            else:
                print(f"      ⚠️ Tool execution not available in mapper")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Check agent instructions
    print("\n6. Agent Instructions:")
    instructions_file = os.path.join(os.path.dirname(__file__), "../idealagent.md")
    if os.path.exists(instructions_file):
        with open(instructions_file, 'r') as f:
            instructions = f.read()
            print(f"   ✅ Instructions file found ({len(instructions)} chars)")
            print(f"   First 200 chars: {instructions[:200]}...")
    else:
        print("   ❌ Instructions file not found")
    
    print("\n" + "=" * 50)
    print("\n✅ AGENT CAPABILITY SUMMARY:")
    print(f"   • {len(openai_tools)} tools available")
    print(f"   • Tool categories: {', '.join(k for k, v in categories.items() if v)}")
    print(f"   • Tool execution: {'Available' if hasattr(mapper, 'execute_tool') else 'Not available'}")
    print(f"   • Agent instructions: {'Configured' if os.path.exists(instructions_file) else 'Missing'}")
    
    return openai_tools

if __name__ == "__main__":
    tools = asyncio.run(test_agent_capabilities())