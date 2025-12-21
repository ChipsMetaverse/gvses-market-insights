#!/usr/bin/env python3
"""Debug yearly aggregation issue"""
import asyncio
import sys
import traceback
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, '/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend')

# Load environment variables
load_dotenv('/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/.env')

async def test_yearly_aggregation():
    try:
        from services.historical_data_service import get_historical_data_service
        from services.bar_aggregator import get_bar_aggregator

        symbol = 'TSLA'
        days = 18250  # 50 years
        interval = '1y'

        print(f"Testing yearly aggregation for {symbol}...")
        print(f"Days: {days}, Interval: {interval}")

        # Get historical data service
        data_service = get_historical_data_service()

        # Calculate date range (timezone-aware)
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(days=days)

        print(f"\nDate range: {start_dt.date()} to {end_dt.date()}")

        # For yearly aggregation, fetch monthly bars first
        fetch_interval = '1mo' if interval == '1y' else interval
        print(f"Fetching interval: {fetch_interval}")

        # Fetch data
        print("\n1. Fetching monthly bars...")
        bars = await data_service.get_bars(
            symbol=symbol,
            interval=fetch_interval,
            start_date=start_dt,
            end_date=end_dt
        )

        print(f"   ✅ Fetched {len(bars)} monthly bars")
        if len(bars) > 0:
            print(f"   First bar: {bars[0]}")
            print(f"   Last bar: {bars[-1]}")

        # Handle yearly aggregation
        if interval == '1y' and len(bars) > 0:
            print("\n2. Aggregating to yearly bars...")
            aggregator = get_bar_aggregator()
            bars = aggregator.aggregate_to_yearly(bars)
            print(f"   ✅ Aggregated to {len(bars)} yearly bars")

            if len(bars) > 0:
                print(f"   First yearly bar: {bars[0]}")
                print(f"   Last yearly bar: {bars[-1]}")

        # Determine cache tier
        print("\n3. Getting metrics...")
        metrics = data_service.get_metrics()
        print(f"   Metrics: {metrics}")

        total = metrics.get('total_requests', 0)
        redis_hits = metrics.get('redis_hits', 0) or 0
        db_hits = metrics.get('db_hits', 0) or 0

        print(f"   Total requests: {total}")
        print(f"   Redis hits: {redis_hits}")
        print(f"   DB hits: {db_hits}")

        if total > 0 and redis_hits == total:
            cache_tier = "redis"
        elif total > 0 and (db_hits + redis_hits) == total:
            cache_tier = "database"
        else:
            cache_tier = "alpaca"

        print(f"   Cache tier: {cache_tier}")

        print(f"\n✅ SUCCESS! Got {len(bars)} yearly candles")
        return bars

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = asyncio.run(test_yearly_aggregation())
    if result:
        print(f"\nFinal result: {len(result)} candles")
    else:
        print("\nTest failed!")
        sys.exit(1)
