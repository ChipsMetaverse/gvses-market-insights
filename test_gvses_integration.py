#!/usr/bin/env python3
"""
Test script for G'sves Assistant integration with voice pipeline.
"""

import asyncio
import httpx
import json

async def test_gvses_query():
    """Test a trading analysis query with G'sves assistant."""

    url = "http://localhost:8000/api/agent/orchestrate"

    # Test query for trading analysis
    payload = {
        "query": "What's your trading philosophy and how do you approach risk management?",
        "conversation_history": [],
        "stream": False
    }

    print("🧪 Testing G'sves Assistant Integration")
    print("=" * 60)
    print(f"Query: {payload['query']}")
    print("=" * 60)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                result = response.json()
                print("\n✅ Success!")
                print(f"Model: {result.get('model')}")
                print(f"Tools Used: {result.get('tools_used', [])}")
                print(f"\nResponse:\n{result.get('text', '')[:500]}...")
                print(f"\nFull response length: {len(result.get('text', ''))} characters")
                return True
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                return False

    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False

async def test_chart_command():
    """Test that chart commands still work (should not use G'sves)."""

    url = "http://localhost:8000/api/agent/orchestrate"

    payload = {
        "query": "Show me TSLA chart",
        "conversation_history": [],
        "stream": False
    }

    print("\n\n🧪 Testing Chart Command (should not use G'sves)")
    print("=" * 60)
    print(f"Query: {payload['query']}")
    print("=" * 60)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                result = response.json()
                print("\n✅ Success!")
                print(f"Model: {result.get('model')}")
                print(f"Chart Commands: {result.get('chart_commands', [])}")
                return True
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                return False

    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("G'SVES ASSISTANT INTEGRATION TEST")
    print("=" * 60)

    asyncio.run(test_gvses_query())
    asyncio.run(test_chart_command())

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)
