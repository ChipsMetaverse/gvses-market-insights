#!/usr/bin/env python3
"""
Test get_support_resistance MCP tool directly
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from services.http_mcp_client import HTTPMCPClient


async def test_support_resistance():
    print("🧪 Testing get_support_resistance MCP Tool")
    print("=" * 60)

    # Initialize MCP client
    try:
        client = HTTPMCPClient(base_url="http://localhost:3001/mcp")
        print("✅ MCP client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize MCP client: {e}")
        return False

    # Initialize session
    try:
        result = await client.initialize()
        print(f"✅ MCP session initialized: {client._session_id}")
    except Exception as e:
        print(f"❌ Failed to initialize session: {e}")
        return False

    # Test symbols
    test_symbols = ["TSLA", "AAPL", "MSFT"]

    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}...")
        print("-" * 60)

        try:
            # Call get_support_resistance tool
            result = await client.call_tool(
                "get_support_resistance",
                {"symbol": symbol, "period": "3mo"}
            )

            print(f"✅ Tool call successful!")
            print(f"📋 Result type: {type(result)}")

            # Parse result
            if isinstance(result, dict):
                # Extract content from JSON-RPC response
                if "result" in result:
                    content = result.get("result", {}).get("content", [])
                    if content and len(content) > 0:
                        import json
                        text = content[0].get("text", "{}")
                        data = json.loads(text)

                        print(f"\n📈 {symbol} Technical Levels:")
                        print(f"   Current Price: ${data.get('currentPrice', 0):.2f}")
                        print(f"   Support Levels: {data.get('support', [])[:3]}")
                        print(f"   Resistance Levels: {data.get('resistance', [])[:3]}")
                        print(f"   Pivot Points: {data.get('pivotPoints', {})}")
                    else:
                        print(f"⚠️  Empty content in response")
                        print(f"   Full result: {result}")
                else:
                    print(f"⚠️  No 'result' key in response")
                    print(f"   Keys: {result.keys()}")
                    print(f"   Full result: {result}")

        except Exception as e:
            print(f"❌ Error calling tool: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ Test complete!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_support_resistance())
    sys.exit(0 if success else 1)
