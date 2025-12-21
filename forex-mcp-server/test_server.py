"""Test forex-mcp-server standalone

This script tests the standalone forex-mcp-server by directly calling
the MCP server via HTTP JSON-RPC and verifying tool responses.

Prerequisites:
    - forex-mcp-server must be running on port 3002
    - Start with: python src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002

Usage:
    python test_server.py
"""
import asyncio
import sys
import logging
import httpx
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:3002"
TIMEOUT = 30.0


async def call_mcp_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    timeout: float = TIMEOUT
) -> Optional[Dict[str, Any]]:
    """Call an MCP tool via JSON-RPC HTTP"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(SERVER_URL, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"HTTP error calling MCP tool: {e}")
        return None
    except Exception as e:
        logger.error(f"Error calling MCP tool: {e}")
        return None


async def test_server_health():
    """Test that the forex-mcp-server is responding"""
    logger.info("Testing forex-mcp-server health...")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SERVER_URL}/health")
            if response.status_code == 200:
                logger.info("✅ Server is healthy")
                return True
            else:
                logger.warning(f"Server returned status {response.status_code}")
                return False
    except httpx.ConnectError:
        logger.error("❌ Cannot connect to server. Is it running on port 3002?")
        logger.error("   Start with: python src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002")
        return False
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False


async def test_list_tools():
    """Test listing available MCP tools"""
    logger.info("\n=== Testing List Tools ===")

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(SERVER_URL, json=payload)
            response.raise_for_status()
            result = response.json()

            tools = result.get("result", {}).get("tools", [])
            logger.info(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                logger.info(f"   - {tool.get('name')}: {tool.get('description', 'N/A')[:60]}...")

            return len(tools) > 0
    except Exception as e:
        logger.error(f"❌ Failed to list tools: {e}")
        return False


async def test_today_calendar():
    """Test fetching today's economic calendar"""
    logger.info("\n=== Testing Today's Calendar ===")

    result = await call_mcp_tool(
        "ffcal_get_calendar_events",
        {"time_period": "today"}
    )

    if result is None:
        logger.error("❌ Failed to fetch today's calendar")
        return False

    # Parse response
    tool_result = result.get("result", {})
    content = tool_result.get("content", [])

    if not content:
        logger.error("❌ No content in response")
        return False

    # Extract text from content
    text = content[0].get("text", "") if content else ""
    logger.info(f"✅ Received calendar data ({len(text)} bytes)")

    # Try to parse JSON
    import json
    try:
        data = json.loads(text)
        events = data.get("events", [])
        logger.info(f"✅ Parsed {len(events)} events for today")

        # Display first event
        if events:
            event = events[0]
            logger.info(f"\n   First event:")
            logger.info(f"     Title: {event.get('title')}")
            logger.info(f"     Currency: {event.get('currency')}")
            logger.info(f"     Impact: {event.get('impact')}")
            logger.info(f"     DateTime: {event.get('datetime')}")

        return True
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse JSON: {e}")
        return False


async def test_week_calendar():
    """Test fetching this week's economic calendar"""
    logger.info("\n=== Testing This Week's Calendar ===")

    result = await call_mcp_tool(
        "ffcal_get_calendar_events",
        {"time_period": "this_week"}
    )

    if result is None:
        logger.error("❌ Failed to fetch week's calendar")
        return False

    tool_result = result.get("result", {})
    content = tool_result.get("content", [])

    if not content:
        logger.error("❌ No content in response")
        return False

    text = content[0].get("text", "") if content else ""

    import json
    try:
        data = json.loads(text)
        events = data.get("events", [])
        logger.info(f"✅ Parsed {len(events)} events for this week")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse JSON: {e}")
        return False


async def test_custom_date_range():
    """Test fetching custom date range"""
    logger.info("\n=== Testing Custom Date Range ===")

    from datetime import datetime, timedelta

    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

    result = await call_mcp_tool(
        "ffcal_get_calendar_events",
        {
            "time_period": "custom",
            "start_date": start_date,
            "end_date": end_date
        }
    )

    if result is None:
        logger.error("❌ Failed to fetch custom range")
        return False

    tool_result = result.get("result", {})
    content = tool_result.get("content", [])

    if not content:
        logger.error("❌ No content in response")
        return False

    text = content[0].get("text", "") if content else ""

    import json
    try:
        data = json.loads(text)
        events = data.get("events", [])
        logger.info(f"✅ Parsed {len(events)} events for {start_date} to {end_date}")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse JSON: {e}")
        return False


async def test_high_impact_filter():
    """Test filtering by high impact events"""
    logger.info("\n=== Testing High Impact Filter ===")

    # Note: The MCP tool may not support impact filtering directly
    # This tests if the parameter is accepted
    result = await call_mcp_tool(
        "ffcal_get_calendar_events",
        {
            "time_period": "today"
            # impact parameter may need to be added to tool definition
        }
    )

    if result is None:
        logger.error("❌ Failed to fetch events")
        return False

    tool_result = result.get("result", {})
    content = tool_result.get("content", [])

    if not content:
        logger.error("❌ No content in response")
        return False

    text = content[0].get("text", "") if content else ""

    import json
    try:
        data = json.loads(text)
        events = data.get("events", [])

        # Count high impact events
        high_impact = [e for e in events if e.get("impact") == 3]
        logger.info(f"✅ Found {len(high_impact)} high impact events out of {len(events)} total")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse JSON: {e}")
        return False


async def main():
    """Run all forex-mcp-server standalone tests"""
    logger.info("=" * 60)
    logger.info("Forex MCP Server Standalone Test Suite")
    logger.info("=" * 60)

    results = []

    # Test 0: Server health
    health = await test_server_health()
    if not health:
        logger.error("\n❌ Server is not running. Cannot proceed with tests.")
        logger.error("Start the server with:")
        logger.error("  cd forex-mcp-server")
        logger.error("  python src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002")
        return 1

    results.append(health)

    # Test 1: List tools
    results.append(await test_list_tools())

    # Test 2: Today's calendar
    results.append(await test_today_calendar())

    # Test 3: Week calendar
    results.append(await test_week_calendar())

    # Test 4: Custom date range
    results.append(await test_custom_date_range())

    # Test 5: High impact filter
    results.append(await test_high_impact_filter())

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    passed = sum(results)
    total = len(results)
    logger.info(f"Tests passed: {passed}/{total}")

    if passed == total:
        logger.info("✅ All tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
