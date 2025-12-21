"""Test forex MCP integration

This script tests the backend integration with the forex-mcp-server,
verifying that economic calendar data can be fetched via the MCP client.

Usage:
    python test_forex_mcp.py
"""
import asyncio
import sys
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_forex_connection():
    """Test basic forex MCP client connection"""
    logger.info("Testing forex MCP client connection...")

    try:
        from services.forex_mcp_client import get_forex_mcp_client

        client = await get_forex_mcp_client()
        logger.info("✅ Forex MCP client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize forex MCP client: {e}")
        return False


async def test_today_events():
    """Test fetching today's economic events"""
    logger.info("\n=== Testing Today's Events ===")

    try:
        from services.forex_mcp_client import get_forex_mcp_client

        client = await get_forex_mcp_client()
        events = await client.get_calendar_events(time_period="today")

        logger.info(f"✅ Today's events: {len(events.get('events', []))} total")
        logger.info(f"   Time period: {events.get('time_period', 'N/A')}")

        # Display first 3 events
        for i, event in enumerate(events.get('events', [])[:3], 1):
            logger.info(f"\n   Event {i}:")
            logger.info(f"     Title: {event.get('title')}")
            logger.info(f"     Currency: {event.get('currency')}")
            logger.info(f"     Impact: {event.get('impact')}")
            logger.info(f"     DateTime: {event.get('datetime')}")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to fetch today's events: {e}")
        return False


async def test_week_events():
    """Test fetching this week's economic events"""
    logger.info("\n=== Testing This Week's Events ===")

    try:
        from services.forex_mcp_client import get_forex_mcp_client

        client = await get_forex_mcp_client()
        events = await client.get_calendar_events(time_period="this_week")

        logger.info(f"✅ This week's events: {len(events.get('events', []))} total")
        logger.info(f"   Time period: {events.get('time_period', 'N/A')}")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to fetch week events: {e}")
        return False


async def test_impact_filtering():
    """Test filtering events by impact level"""
    logger.info("\n=== Testing Impact Filtering ===")

    try:
        from services.forex_mcp_client import get_forex_mcp_client

        client = await get_forex_mcp_client()

        # Test high impact
        high_impact = await client.get_calendar_events(
            time_period="today",
            impact="high"
        )
        logger.info(f"✅ High impact events today: {len(high_impact.get('events', []))}")

        # Test medium impact
        medium_impact = await client.get_calendar_events(
            time_period="today",
            impact="medium"
        )
        logger.info(f"✅ Medium impact events today: {len(medium_impact.get('events', []))}")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to test impact filtering: {e}")
        return False


async def test_custom_date_range():
    """Test custom date range filtering"""
    logger.info("\n=== Testing Custom Date Range ===")

    try:
        from services.forex_mcp_client import get_forex_mcp_client
        from datetime import datetime, timedelta

        client = await get_forex_mcp_client()

        # Get next 7 days
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        events = await client.get_calendar_events(
            time_period="custom",
            start=start_date,
            end=end_date
        )

        logger.info(f"✅ Custom range ({start_date} to {end_date}): {len(events.get('events', []))} events")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to test custom date range: {e}")
        return False


async def main():
    """Run all forex MCP integration tests"""
    logger.info("=" * 60)
    logger.info("Forex MCP Integration Test Suite")
    logger.info("=" * 60)

    results = []

    # Test 1: Connection
    results.append(await test_forex_connection())

    # Test 2: Today's events
    results.append(await test_today_events())

    # Test 3: Week events
    results.append(await test_week_events())

    # Test 4: Impact filtering
    results.append(await test_impact_filtering())

    # Test 5: Custom date range
    results.append(await test_custom_date_range())

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
