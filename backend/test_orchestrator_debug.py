#!/usr/bin/env python3
"""Debug test to see exactly what the orchestrator is doing."""

import asyncio
import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.agent_orchestrator import get_orchestrator

async def main():
    """Test the orchestrator directly with detailed debugging."""
    
    orchestrator = get_orchestrator()
    
    # Check system prompt
    system_prompt = orchestrator._build_system_prompt()
    print("=" * 60)
    print("SYSTEM PROMPT:")
    print("=" * 60)
    print(system_prompt)
    print()
    
    # Check available tools
    print("=" * 60)
    print("AVAILABLE TOOLS:")
    print("=" * 60)
    tools = orchestrator._get_tool_schemas()
    for tool in tools:
        func = tool.get('function', {})
        print("- " + func.get('name', 'unknown'))
    print()
    
    # Test query processing
    query = "Give me entry points for swing trades on AAPL tomorrow"
    print("=" * 60)
    print("PROCESSING QUERY:")
    print("=" * 60)
    print("Query:", query)
    print()
    
    # Check if it's caught by static response
    static_response = await orchestrator._maybe_answer_with_static_template(query, None)
    if static_response:
        print("⚠️  CAUGHT BY STATIC TEMPLATE!")
        print("Response:", static_response.get('text', '')[:200] + "...")
    else:
        print("✅ Not caught by static template")
    
    # Check if it's caught by price query
    price_response = await orchestrator._maybe_answer_with_price_query(query, None)
    if price_response:
        print("⚠️  CAUGHT BY PRICE QUERY HANDLER!")
        print("Response:", price_response.get('text', '')[:200] + "...")
    else:
        print("✅ Not caught by price query handler")
    
    # Check cache
    cached = await orchestrator._get_cached_response(query, "")
    if cached:
        print("⚠️  FOUND IN CACHE!")
        print("Cached response:", cached.get('text', '')[:200] + "...")
    else:
        print("✅ Not in cache")
    
    print()
    
    # Now process the full query
    print("=" * 60)
    print("FULL QUERY PROCESSING:")
    print("=" * 60)
    
    result = await orchestrator.process_query(
        query=query,
        conversation_history=None,
        stream=False
    )
    
    print("Tools Used:", result.get('tools_used', []))
    print("Model:", result.get('model', 'unknown'))
    print("Cached:", result.get('cached', False))
    print("Response Length:", len(result.get('text', '')))
    
    # Check if it's a templated response
    text = result.get('text', '')
    if "Market Snapshot" in text:
        print("⚠️  TEMPLATED RESPONSE DETECTED")
    else:
        print("✅ Custom response generated")
    
    print()
    print("Response Preview:")
    print(text[:300] + "...")

if __name__ == "__main__":
    print("\n🔍 ORCHESTRATOR DEBUG TEST\n")
    asyncio.run(main())
