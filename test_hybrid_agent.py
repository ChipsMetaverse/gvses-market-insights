#!/usr/bin/env python3
"""
Test Hybrid Agent Implementation
=================================
Tests the new backend agent orchestrator and hybrid voice provider.
"""

import asyncio
import json
import httpx
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from main .env
load_dotenv('.env')

# Configuration
BACKEND_URL = "http://localhost:8000"
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")

async def test_agent_health():
    """Test agent health endpoint."""
    print("\n=== Testing Agent Health ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/api/agent/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Health: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False

async def test_get_tools():
    """Test getting available tools."""
    print("\n=== Testing Get Tools ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/api/agent/tools")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            tools = response.json()
            print(f"Available tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False

async def test_orchestrate_simple():
    """Test simple query without tools."""
    print("\n=== Testing Simple Query (No Tools) ===")
    query = "What is your opinion on the market today?"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/api/agent/orchestrate",
            json={
                "query": query,
                "conversation_history": [],
                "stream": False
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['text'][:200]}...")
            print(f"Tools used: {data['tools_used']}")
            print(f"Model: {data['model']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False

async def test_orchestrate_with_tools():
    """Test query that requires tool usage."""
    print("\n=== Testing Query with Tools ===")
    query = "What is the current price of TSLA and what's the latest news?"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BACKEND_URL}/api/agent/orchestrate",
            json={
                "query": query,
                "conversation_history": [],
                "stream": False
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['text'][:300]}...")
            print(f"Tools used: {data['tools_used']}")
            if data.get('data'):
                print(f"Tool data keys: {list(data['data'].keys())}")
                # Show sample of tool data
                for tool_name, tool_data in data['data'].items():
                    if isinstance(tool_data, dict):
                        print(f"  {tool_name}: {list(tool_data.keys())[:5]}")
            return True
        else:
            print(f"Error: {response.text}")
            return False

async def test_orchestrate_complex():
    """Test complex query requiring multiple tools."""
    print("\n=== Testing Complex Query (Multiple Tools) ===")
    query = "Give me a comprehensive analysis of AAPL including price, recent news, and 30-day history"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BACKEND_URL}/api/agent/orchestrate",
            json={
                "query": query,
                "conversation_history": [],
                "stream": False
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response preview: {data['text'][:400]}...")
            print(f"Tools used: {data['tools_used']}")
            print(f"Number of tools: {len(data['tools_used'])}")
            return True
        else:
            print(f"Error: {response.text}")
            return False

async def test_streaming():
    """Test streaming response."""
    print("\n=== Testing Streaming Response ===")
    query = "Tell me about Bitcoin's current price"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Use stream=True in the request
        response = await client.post(
            f"{BACKEND_URL}/api/agent/stream",
            json={
                "query": query,
                "conversation_history": [],
                "stream": True
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            # Process SSE stream
            buffer = ""
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    json_str = line[6:]
                    if json_str.strip():
                        try:
                            chunk = json.loads(json_str)
                            if chunk['type'] == 'content':
                                buffer += chunk.get('text', '')
                                print(chunk.get('text', ''), end='', flush=True)
                            elif chunk['type'] == 'done':
                                print("\n[Stream complete]")
                                break
                        except json.JSONDecodeError:
                            pass
            return True
        else:
            print(f"Error: {response.text}")
            return False

async def test_conversation_history():
    """Test conversation with history."""
    print("\n=== Testing Conversation History ===")
    
    history = [
        {"role": "user", "content": "What stocks should I watch?"},
        {"role": "assistant", "content": "I recommend watching TSLA and AAPL for their recent momentum."}
    ]
    
    query = "What was the first stock you mentioned?"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BACKEND_URL}/api/agent/orchestrate",
            json={
                "query": query,
                "conversation_history": history,
                "stream": False
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['text']}")
            # Check if it correctly references TSLA from history
            if "TSLA" in data['text'] or "Tesla" in data['text'].upper():
                print("✓ Correctly referenced conversation history")
                return True
            else:
                print("✗ Did not reference conversation history correctly")
                return False
        else:
            print(f"Error: {response.text}")
            return False

async def test_cache():
    """Test caching behavior."""
    print("\n=== Testing Cache Behavior ===")
    query = "What is the price of MSFT?"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First request
        print("First request...")
        start = datetime.now()
        response1 = await client.post(
            f"{BACKEND_URL}/api/agent/orchestrate",
            json={"query": query}
        )
        time1 = (datetime.now() - start).total_seconds()
        
        # Second request (should use cache)
        print("Second request (should be cached)...")
        start = datetime.now()
        response2 = await client.post(
            f"{BACKEND_URL}/api/agent/orchestrate",
            json={"query": query}
        )
        time2 = (datetime.now() - start).total_seconds()
        
        print(f"First request time: {time1:.2f}s")
        print(f"Second request time: {time2:.2f}s")
        
        if time2 < time1 * 0.7:  # Second should be at least 30% faster
            print("✓ Cache appears to be working")
            return True
        else:
            print("✗ Cache may not be working effectively")
            return False

async def main():
    """Run all tests."""
    print("=" * 50)
    print("HYBRID AGENT IMPLEMENTATION TEST SUITE")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  WARNING: OPENAI_API_KEY not set in backend/.env")
        print("The agent orchestrator will not work without it.")
        print("Please add: OPENAI_API_KEY=your-key-here")
        return
    
    tests = [
        ("Agent Health", test_agent_health),
        ("Get Tools", test_get_tools),
        ("Simple Query", test_orchestrate_simple),
        ("Query with Tools", test_orchestrate_with_tools),
        ("Complex Query", test_orchestrate_complex),
        ("Streaming", test_streaming),
        ("Conversation History", test_conversation_history),
        ("Cache", test_cache),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The hybrid agent is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the implementation.")

if __name__ == "__main__":
    asyncio.run(main())