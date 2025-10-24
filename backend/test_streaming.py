#!/usr/bin/env python3
"""
Streaming Test Script for Python MCP Client
Tests the call_tool_streaming method
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.http_mcp_client import get_http_mcp_client


async def test_streaming():
    """Test SSE streaming functionality"""
    
    print("🧪 Python MCP Client Streaming Test")
    print("=" * 40)
    print(f"Symbol: TSLA")
    print(f"Duration: 20 seconds")
    print(f"Interval: 5 seconds")
    print()
    
    try:
        client = await get_http_mcp_client()
        print("✅ Client initialized")
        print()
        
        event_count = 0
        progress_count = 0
        start_time = datetime.now()
        
        print("📡 Starting stream...")
        print()
        
        async for event in client.call_tool_streaming(
            "stream_market_news",
            {"symbol": "TSLA", "interval": 5000, "duration": 20000}
        ):
            event_count += 1
            
            if event.get("method") == "notifications/progress":
                progress_count += 1
                params = event.get("params", {})
                progress = params.get("progress", 0) * 100
                
                print(f"📊 Progress {progress_count}: {progress:.1f}%")
                
                try:
                    message = json.loads(params.get("message", "{}"))
                    news_count = message.get("news", {}).get("count", 0)
                    timestamp = message.get("timestamp", "")
                    
                    print(f"   News articles: {news_count}")
                    print(f"   Timestamp: {timestamp}")
                except Exception as e:
                    print(f"   (Parse error: {e})")
                
                print()
                
            elif "result" in event:
                elapsed = (datetime.now() - start_time).total_seconds()
                
                print("✅ Stream Complete")
                print(f"   Total events: {event_count}")
                print(f"   Progress updates: {progress_count}")
                print(f"   Duration: {elapsed:.1f}s")
                print()
                break
                
            elif "error" in event:
                error = event.get("error", {})
                print(f"❌ Error: {error.get('message', 'Unknown')}")
                print(f"   Code: {error.get('code', 'N/A')}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_security():
    """Test security features"""
    
    print("\n🔒 Security Test")
    print("=" * 40)
    
    try:
        client = await get_http_mcp_client()
        
        # Test 1: Check session initialization
        print("Test 1: Session initialization")
        if client._session_id:
            print(f"   ✅ Session ID: {client._session_id[:16]}...")
        else:
            print("   ❌ No session ID")
            return False
        
        # Test 2: Check API key
        print("\nTest 2: API key configuration")
        if client._api_key:
            print(f"   ✅ API key configured: {client._api_key[:8]}...")
        else:
            print("   ⚠️  No API key (development mode)")
        
        # Test 3: List tools
        print("\nTest 3: List tools endpoint")
        tools_response = await client.list_tools()
        tools = tools_response.get("result", {}).get("tools", [])
        print(f"   ✅ Retrieved {len(tools)} tools")
        
        # Test 4: Call a tool
        print("\nTest 4: Call tool endpoint")
        quote_response = await client.call_tool("get_stock_quote", {"symbol": "AAPL"})
        if "result" in quote_response:
            print("   ✅ Tool call successful")
        elif "error" in quote_response:
            error = quote_response.get("error", {})
            print(f"   ❌ Tool call failed: {error.get('message')}")
            return False
        
        print("\n✅ All security tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    
    print("🚀 MCP Server Test Suite")
    print("=" * 40)
    print()
    
    # Test security features
    security_passed = await test_security()
    
    if not security_passed:
        print("\n❌ Security tests failed")
        return 1
    
    # Test streaming
    print()
    streaming_passed = await test_streaming()
    
    if not streaming_passed:
        print("\n❌ Streaming tests failed")
        return 1
    
    print("\n" + "=" * 40)
    print("✅ ALL TESTS PASSED")
    print("=" * 40)
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
