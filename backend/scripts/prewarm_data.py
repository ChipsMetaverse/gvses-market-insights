#!/usr/bin/env python3
"""
Data Pre-warming Script

Run this script to pre-populate the database with popular symbols.
Should be run once at deployment or when adding new symbols to the watchlist.

Usage:
    python3 -m backend.scripts.prewarm_data

    # Or with custom symbols:
    python3 -m backend.scripts.prewarm_data --symbols AAPL TSLA NVDA

    # Or just specific intervals:
    python3 -m backend.scripts.prewarm_data --intervals 5m 1h
"""

import asyncio
import sys
import os
import logging
import argparse
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.data_prewarming_service import DataPrewarmingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('prewarm_data.log')
    ]
)
logger = logging.getLogger(__name__)


async def main(symbols=None, intervals=None):
    """Run data pre-warming."""
    try:
        service = DataPrewarmingService()

        # Build config if custom intervals specified
        config = None
        if intervals:
            config = []
            interval_days = {
                '1m': 7,      # 1 week of 1-minute data
                '5m': 60,     # 2 months of 5-minute data
                '15m': 90,    # 3 months of 15-minute data
                '30m': 180,   # 6 months of 30-minute data
                '1h': 365,    # 1 year of hourly data
                '4h': 730,    # 2 years of 4-hour data
                '1d': 2555,   # 7 years of daily data
                '1w': 2555,   # 7 years of weekly data
                '1mo': 2555   # 7 years of monthly data
            }

            for interval in intervals:
                if interval not in interval_days:
                    logger.warning(f"Unknown interval '{interval}', skipping")
                    continue

                config.append({
                    'interval': interval,
                    'days': interval_days[interval],
                    'description': f'{interval} bars'
                })

        logger.info("Starting data pre-warming...")
        logger.info(f"Symbols: {symbols or 'default (top 20)'}")
        logger.info(f"Intervals: {intervals or 'default (5m, 1h, 1d)'}")

        stats = await service.prewarm_top_symbols(
            symbols=symbols,
            config=config
        )

        # Print summary
        print("\n" + "=" * 80)
        print("PRE-WARMING SUMMARY")
        print("=" * 80)
        print(f"Symbols processed: {stats['symbols_processed']}")
        print(f"Intervals processed: {stats['intervals_processed']}")
        print(f"Total bars stored: {stats['total_bars_stored']:,}")
        print(f"Errors: {stats['errors']}")
        print(f"Duration: {(stats['end_time'] - stats['start_time']).total_seconds():.1f}s")
        print("=" * 80)

        if stats['errors'] > 0:
            logger.warning(f"{stats['errors']} errors occurred. Check logs for details.")
            return 1

        logger.info("✅ Pre-warming completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"❌ Pre-warming failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pre-warm database with historical market data')
    parser.add_argument(
        '--symbols',
        nargs='+',
        help='Symbols to pre-warm (space-separated). Default: top 20 symbols'
    )
    parser.add_argument(
        '--intervals',
        nargs='+',
        choices=['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1mo'],
        help='Intervals to pre-warm. Default: 5m 1h 1d'
    )

    args = parser.parse_args()

    exit_code = asyncio.run(main(
        symbols=args.symbols,
        intervals=args.intervals
    ))

    sys.exit(exit_code)
