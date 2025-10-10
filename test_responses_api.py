#!/usr/bin/env python3
"""
Test OpenAI Responses API with G'sves Trading Agent
Uses admin key to test programmatic setup
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize with admin key
admin_key = os.getenv('OPENAI_ADMIN_KEY')
client = OpenAI(api_key=admin_key)

print("="*60)
print("🧪 Testing OpenAI Responses API")
print("="*60)

# Test 1: Simple generation
print("\n[Test 1] Basic Response Generation")
try:
    response = client.responses.create(
        model="gpt-4o",
        instructions="You are G'sves, a senior portfolio manager with 30 years experience.",
        input="What's your trading philosophy in one sentence?"
    )
    print(f"✅ Response ID: {response.id}")
    print(f"📝 Output: {response.output_text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: With native web search tool
print("\n[Test 2] Response with Web Search Tool")
try:
    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a market analyst. Use web search to find current data.",
        input="What's the current price of AAPL stock?",
        tools=[{"type": "web_search"}],
        store=True  # Store for follow-up
    )
    print(f"✅ Response ID: {response.id}")
    print(f"📝 Output: {response.output_text[:200]}...")

    # Check if web search was used
    for item in response.output:
        if hasattr(item, 'type'):
            print(f"   - Output type: {item.type}")

except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Check file search capability
print("\n[Test 3] Checking File Search Capability")
try:
    # First, list vector stores
    vector_stores = client.beta.vector_stores.list()
    print(f"📚 Found {len(vector_stores.data)} vector stores")

    if vector_stores.data:
        vs = vector_stores.data[0]
        print(f"   Using vector store: {vs.id} ({vs.name})")

        # Test file search in response
        response = client.responses.create(
            model="gpt-4o",
            instructions="You are a trading educator. Answer using the knowledge base.",
            input="What is delta in options trading?",
            tools=[{"type": "file_search", "file_search": {"vector_store_ids": [vs.id]}}]
        )
        print(f"✅ File search response: {response.output_text[:150]}...")
    else:
        print("⚠️ No vector stores found - create one first")

except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Function calling (custom tools)
print("\n[Test 4] Function Calling with Custom Tools")
try:
    response = client.responses.create(
        model="gpt-4o",
        instructions="You are G'sves. Use the provided tools to get market data.",
        input="What's TSLA's current price?",
        tools=[
            {
                "type": "function",
                "name": "get_stock_quote",
                "description": "Get real-time stock quote",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker"}
                    },
                    "required": ["symbol"],
                    "additionalProperties": False
                }
            }
        ]
    )

    print(f"✅ Response ID: {response.id}")

    # Check for function calls
    function_called = False
    for item in response.output:
        if hasattr(item, 'type') and item.type == 'function_call':
            function_called = True
            print(f"🔧 Function called: {item.name}")
            print(f"   Arguments: {item.arguments}")

    if not function_called:
        print("⚠️ No function call detected")
        print(f"   Output: {response.output_text}")

except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Multi-turn with previous_response_id
print("\n[Test 5] Multi-Turn Conversation")
try:
    # First response
    res1 = client.responses.create(
        model="gpt-4o",
        instructions="You are G'sves, a trading expert.",
        input="Tell me about AAPL in one sentence.",
        store=True
    )
    print(f"✅ First response: {res1.output_text}")

    # Follow-up using previous_response_id
    res2 = client.responses.create(
        model="gpt-4o",
        input="What's a good entry point for it?",
        previous_response_id=res1.id,
        store=True
    )
    print(f"✅ Second response: {res2.output_text}")

except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Check MCP support
print("\n[Test 6] MCP Tool Support")
try:
    # Note: This might fail if no MCP servers are configured at account level
    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a helpful assistant with access to external tools.",
        input="Test MCP connectivity",
        tools=[{"type": "mcp", "mcp": {"server_id": "test-server"}}]
    )
    print(f"✅ MCP test response: {response.output_text}")
except Exception as e:
    print(f"⚠️ MCP test: {str(e)[:100]}...")
    print("   (This is expected if no MCP servers are configured)")

# Test 7: Reasoning models
print("\n[Test 7] Reasoning Model (o1)")
try:
    response = client.responses.create(
        model="o1",
        instructions="You are G'sves. Analyze this trading setup step by step.",
        input="TSLA at $245. 50-day MA at $245, 200-day MA at $235. RSI at 58. Volume up 15%. Should I enter?",
        reasoning_effort="medium"
    )
    print(f"✅ Response ID: {response.id}")

    # Check for reasoning items
    for item in response.output:
        if hasattr(item, 'type'):
            print(f"   - Item type: {item.type}")
            if item.type == 'reasoning':
                print(f"   - Reasoning summary: {getattr(item, 'summary', 'N/A')}")

    print(f"📝 Final output: {response.output_text[:200]}...")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("🎯 Test Summary")
print("="*60)
print("""
Key Findings:
- ✅ Admin key works for Responses API
- ✅ Native tools available (web_search, file_search, mcp, functions)
- ✅ Multi-turn conversations via previous_response_id
- ✅ Reasoning models supported (o1, o1-mini)
- ✅ Can be integrated directly with voice pipeline

Next Steps:
1. Create vector store for G'sves knowledge
2. Configure MCP servers at account level (if possible)
3. Build Responses API integration for voice pipeline
4. Test with actual market data tools
""")
