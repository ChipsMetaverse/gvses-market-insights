"""
Data Pre-warming Service - Initial Database Population

Pre-loads popular symbols into database to ensure instant chart loads.
Similar to how TradingView pre-caches major indices and popular stocks.

Strategy:
- Load top 20 symbols on deployment
- 3 intervals per symbol (5m, 1h, 1d)
- Configurable history depth per interval
- Run once at startup or via manual script

Benefits:
- Users get sub-200ms load times for popular symbols
- No API calls for pre-warmed data
- Cache hit rate > 90% after warming
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from services.historical_data_service import get_historical_data_service

logger = logging.getLogger(__name__)


class DataPrewarmingService:
    """
    Pre-populate database with popular symbols.

    Architecture inspired by competitor research:
    - TradingView: Pre-loads popular symbols on their servers
    - Webull: Caches top movers and indices
    - Yahoo: Pre-computes popular screener results
    """

    # Top 20 most requested symbols (from existing cache_service.py)
    TOP_SYMBOLS = [
        'TSLA', 'AAPL', 'NVDA', 'SPY', 'MSFT',
        'GOOGL', 'AMZN', 'META', 'AMD', 'PLTR',
        'QQQ', 'NFLX', 'COIN', 'DIS', 'BABA',
        'BA', 'F', 'GE', 'GM', 'INTC'
    ]

    # Intervals to pre-load with history depth
    PREWARM_CONFIG = [
        {
            'interval': '5m',
            'days': 60,  # 2 months (good for day trading analysis)
            'description': '5-minute bars for short-term trading'
        },
        {
            'interval': '1h',
            'days': 365,  # 1 year (swing trading timeframe)
            'description': '1-hour bars for medium-term analysis'
        },
        {
            'interval': '1d',
            'days': 2555,  # 7 years (maximum Alpaca history)
            'description': 'Daily bars for long-term investing'
        }
    ]

    def __init__(self):
        """Initialize with historical data service."""
        self.data_service = get_historical_data_service()
        self.stats = {
            'symbols_processed': 0,
            'intervals_processed': 0,
            'total_bars_stored': 0,
            'api_calls_made': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }

    async def prewarm_top_symbols(
        self,
        symbols: Optional[List[str]] = None,
        config: Optional[List[dict]] = None
    ):
        """
        Pre-warm database with top symbols.

        Args:
            symbols: List of symbols to pre-warm (defaults to TOP_SYMBOLS)
            config: Pre-warming configuration (defaults to PREWARM_CONFIG)

        Example:
            service = DataPrewarmingService()
            await service.prewarm_top_symbols()
        """
        symbols = symbols or self.TOP_SYMBOLS
        config = config or self.PREWARM_CONFIG

        self.stats['start_time'] = datetime.now()

        logger.info("=" * 80)
        logger.info("🔥 DATA PRE-WARMING STARTED")
        logger.info("=" * 80)
        logger.info(f"Symbols: {len(symbols)}")
        logger.info(f"Intervals: {len(config)}")
        logger.info(f"Total datasets: {len(symbols) * len(config)}")
        logger.info(f"Start time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

        # Process each symbol × interval combination
        for symbol in symbols:
            logger.info(f"\n📊 Processing {symbol}...")

            for interval_config in config:
                interval = interval_config['interval']
                days = interval_config['days']
                description = interval_config['description']

                try:
                    logger.info(f"  → {interval} ({description}): {days} days of history")

                    # Calculate date range
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days)

                    # Fetch and store data (service handles caching/DB/API logic)
                    start_fetch = datetime.now()
                    bars = await self.data_service.get_bars(
                        symbol=symbol,
                        interval=interval,
                        start_date=start_date,
                        end_date=end_date
                    )
                    duration_ms = int((datetime.now() - start_fetch).total_seconds() * 1000)

                    # Update stats
                    self.stats['intervals_processed'] += 1
                    self.stats['total_bars_stored'] += len(bars)

                    logger.info(
                        f"  ✅ {symbol} {interval}: {len(bars)} bars "
                        f"({duration_ms}ms)"
                    )

                except Exception as e:
                    self.stats['errors'] += 1
                    logger.error(f"  ❌ {symbol} {interval}: {str(e)}")

            self.stats['symbols_processed'] += 1

        # Finalize
        self.stats['end_time'] = datetime.now()
        duration_total = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        logger.info("\n" + "=" * 80)
        logger.info("🎉 DATA PRE-WARMING COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Symbols processed: {self.stats['symbols_processed']}/{len(symbols)}")
        logger.info(f"Intervals processed: {self.stats['intervals_processed']}")
        logger.info(f"Total bars stored: {self.stats['total_bars_stored']:,}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Total duration: {duration_total:.1f}s")
        logger.info(f"Avg per symbol: {duration_total/len(symbols):.1f}s")
        logger.info("=" * 80)

        # Print service metrics
        metrics = self.data_service.get_metrics()
        logger.info("\n📊 Service Metrics:")
        logger.info(f"  Redis hits: {metrics['redis_hits']}")
        logger.info(f"  DB hits: {metrics['db_hits']}")
        logger.info(f"  API calls: {metrics['api_calls']}")
        logger.info(f"  Total requests: {metrics['total_requests']}")
        logger.info(f"  Redis hit rate: {metrics['redis_hit_rate']}%")
        logger.info(f"  DB hit rate: {metrics['db_hit_rate']}%")
        logger.info(f"  API call rate: {metrics['api_call_rate']}%")

        return self.stats

    async def update_recent_data(
        self,
        symbols: Optional[List[str]] = None,
        intervals: Optional[List[str]] = None
    ):
        """
        Incremental update - fetch only new bars since last update.

        Run this via cron every 15 minutes during market hours (9:30am-4pm ET).

        Args:
            symbols: Symbols to update (defaults to all symbols in data_coverage)
            intervals: Intervals to update (defaults to all intervals)

        Example cron:
            # Update every 15 minutes during market hours (9:30am-4pm ET Mon-Fri)
            */15 9-16 * * 1-5 python -m backend.scripts.update_recent_data
        """
        logger.info("🔄 INCREMENTAL DATA UPDATE STARTED")

        # If no symbols specified, get all from data_coverage
        if symbols is None:
            symbols = await self._get_active_symbols()

        intervals = intervals or ['5m', '1h', '1d']

        updated_count = 0
        error_count = 0

        for symbol in symbols:
            for interval in intervals:
                try:
                    # Get coverage info to determine last update
                    coverage = await self._get_coverage_record(symbol, interval)

                    if not coverage:
                        logger.debug(f"Skipping {symbol} {interval} (no coverage)")
                        continue

                    # Fetch from last bar to now
                    last_bar = datetime.fromisoformat(coverage['latest_bar'])
                    now = datetime.now()

                    # Only update if more than 15 minutes old
                    if (now - last_bar).total_seconds() < 900:  # 15 minutes
                        logger.debug(f"Skipping {symbol} {interval} (already current)")
                        continue

                    # Fetch new bars
                    bars = await self.data_service.get_bars(
                        symbol=symbol,
                        interval=interval,
                        start_date=last_bar,
                        end_date=now
                    )

                    # Count truly new bars
                    new_bars = [
                        b for b in bars
                        if datetime.fromisoformat(b['timestamp']) > last_bar
                    ]

                    if new_bars:
                        logger.info(
                            f"📊 Updated {symbol} {interval}: +{len(new_bars)} new bars"
                        )
                        updated_count += 1

                except Exception as e:
                    logger.error(f"❌ Failed to update {symbol} {interval}: {e}")
                    error_count += 1

        logger.info(
            f"✅ Incremental update complete: "
            f"{updated_count} updated, {error_count} errors"
        )

        return {'updated': updated_count, 'errors': error_count}

    async def _get_active_symbols(self) -> List[str]:
        """Get all symbols that have data coverage."""
        try:
            response = self.data_service.supabase.table(
                'data_coverage'
            ).select('symbol').execute()

            symbols = list(set([record['symbol'] for record in response.data]))
            return symbols

        except Exception as e:
            logger.error(f"Failed to get active symbols: {e}")
            return self.TOP_SYMBOLS  # Fallback to top symbols

    async def _get_coverage_record(self, symbol: str, interval: str) -> Optional[dict]:
        """Get coverage metadata for a symbol/interval."""
        try:
            response = self.data_service.supabase.table('data_coverage').select('*').eq(
                'symbol', symbol
            ).eq(
                'interval', interval
            ).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to get coverage for {symbol} {interval}: {e}")
            return None

    async def prewarm_single_symbol(
        self,
        symbol: str,
        interval: str = '5m',
        days: int = 60
    ):
        """
        Pre-warm a single symbol (useful for on-demand warming).

        Args:
            symbol: Stock ticker
            interval: Bar interval
            days: Days of history to fetch

        Example:
            # User requested chart for COIN, warm it up
            await service.prewarm_single_symbol('COIN', '5m', 60)
        """
        logger.info(f"🔥 Pre-warming single symbol: {symbol} {interval} ({days} days)")

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            bars = await self.data_service.get_bars(
                symbol=symbol,
                interval=interval,
                start_date=start_date,
                end_date=end_date
            )

            logger.info(f"✅ Pre-warmed {symbol} {interval}: {len(bars)} bars")

            return {
                'symbol': symbol,
                'interval': interval,
                'bars_stored': len(bars),
                'success': True
            }

        except Exception as e:
            logger.error(f"❌ Failed to pre-warm {symbol} {interval}: {e}")

            return {
                'symbol': symbol,
                'interval': interval,
                'bars_stored': 0,
                'success': False,
                'error': str(e)
            }


# Helper function for scripts
async def run_prewarming():
    """Run pre-warming from command line."""
    service = DataPrewarmingService()
    stats = await service.prewarm_top_symbols()
    return stats


if __name__ == "__main__":
    # Allow running directly for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(run_prewarming())
