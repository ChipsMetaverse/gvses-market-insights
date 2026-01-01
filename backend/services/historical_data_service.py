"""
Historical Data Service - Database-Backed Market Data Management

Implements competitor-inspired 3-tier caching architecture:
  L1: Redis (2ms) - Hot data: last 30 days, popular symbols
  L2: Supabase (20ms) - All historical data, persistent storage
  L3: Alpaca API (300-500ms) - Fetch missing data only

Architecture based on research:
- TradingView: Pre-load data, serve from cache
- Webull: Database-first approach
- Robinhood: Multi-layer caching

Key Benefits:
- 99% reduction in API calls after initial load
- Sub-200ms response for cached symbols
- Automatic gap detection and backfill
- Scales to 100+ symbols within free tier limits
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from supabase import create_client, Client
import redis

from services.alpaca_intraday_service import get_alpaca_service
from services.cache_service import get_cache_service
from services.http_mcp_client import get_http_mcp_client as get_direct_mcp_client  # Using HTTP for better performance

logger = logging.getLogger(__name__)


class HistoricalDataService:
    """
    Manages historical market data with 3-tier caching strategy.

    Workflow:
    1. Check Redis (L1) - fastest, but limited capacity
    2. Check Supabase (L2) - persistent, unlimited history
    3. Fetch from Alpaca API (L3) - only for missing data
    4. Store in L2 + L1 for future requests
    """

    def __init__(self):
        """Initialize connections to all three tiers."""
        # Supabase (L2 - persistent storage)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")

        self.supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase connected (L2 storage)")

        # Redis (L1 - hot cache)
        self.cache_service = get_cache_service()
        logger.info("✅ Redis connected (L1 cache)")

        # Alpaca API (L3 - data source)
        self.alpaca_service = get_alpaca_service()
        logger.info("✅ Alpaca service initialized (L3 source)")

        # Metrics
        self.metrics = {
            'redis_hits': 0,
            'db_hits': 0,
            'api_calls': 0,
            'total_requests': 0
        }

    async def get_bars(
        self,
        symbol: str,
        interval: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Main entry point for fetching historical data.

        Args:
            symbol: Stock ticker (e.g., 'AAPL', 'TSLA')
            interval: Bar interval ('1m', '5m', '1h', '1d', etc.)
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            List of OHLCV dictionaries sorted by timestamp ascending
        """
        self.metrics['total_requests'] += 1
        symbol_upper = symbol.upper()

        logger.info(
            f"📊 get_bars: {symbol_upper} {interval} "
            f"{start_date.date()} to {end_date.date()}"
        )

        # L1: Check Redis cache
        cache_key = self._make_cache_key(symbol_upper, interval, start_date, end_date)
        cached_bars = self._get_from_redis(cache_key)

        if cached_bars:
            self.metrics['redis_hits'] += 1
            logger.info(f"💾 L1 HIT (Redis): {cache_key}")
            return cached_bars

        # L2: Check Supabase database
        db_bars = await self._fetch_from_database(
            symbol_upper, interval, start_date, end_date
        )

        # Check if we have complete coverage
        coverage = await self._check_coverage(
            symbol_upper, interval, start_date, end_date
        )

        if coverage['is_complete']:
            # We have all requested data in database
            self.metrics['db_hits'] += 1
            logger.info(
                f"💾 L2 HIT (Supabase): {symbol_upper} {interval} "
                f"({len(db_bars)} bars, complete)"
            )

            # Cache in Redis for next time
            self._store_in_redis(cache_key, db_bars)
            return db_bars

        # L3: Fetch missing data from Alpaca API
        logger.info(
            f"🔄 L2 PARTIAL: {symbol_upper} {interval} "
            f"({len(coverage['gaps'])} gaps to fill)"
        )

        all_bars = await self._fill_gaps(
            symbol_upper, interval, db_bars, coverage['gaps'], start_date, end_date
        )

        # Cache complete dataset
        self._store_in_redis(cache_key, all_bars)

        return all_bars

    async def _fetch_from_database(
        self,
        symbol: str,
        interval: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Query Supabase for bars in the requested range.
        
        Uses pagination to bypass Supabase's 1000 row server-side limit.

        Returns:
            List of bars from database (may be incomplete)
        """
        try:
            # FIX: Supabase has a server-side max of 1000 rows that .limit() cannot override
            # Must use pagination with .range() to fetch all data
            all_bars = []
            page_size = 1000  # Supabase max per request
            offset = 0
            
            while True:
                response = self.supabase.table('historical_bars').select('*').eq(
                    'symbol', symbol
                ).eq(
                    'interval', interval
                ).gte(
                    'timestamp', start_date.isoformat()
                ).lte(
                    'timestamp', end_date.isoformat()
                ).order('timestamp', desc=False).range(offset, offset + page_size - 1).execute()

                bars = response.data if response.data else []
                all_bars.extend(bars)
                
                # If we got fewer than page_size, we've reached the end
                if len(bars) < page_size:
                    break
                    
                offset += page_size
                
                # Safety limit to prevent infinite loops
                if offset > 50000:
                    logger.warning(f"⚠️ Pagination limit reached for {symbol} {interval}")
                    break

            logger.info(
                f"📚 DB query: {symbol} {interval} → {len(all_bars)} bars (paginated)"
            )
            # #region agent log - DISABLED (hardcoded path causes production errors)
            # import json as _json
            # _db_dates = sorted([b.get('timestamp','')[:10] for b in all_bars]) if all_bars else []
            # _june_2025_count = len([b for b in all_bars if b.get('timestamp','').startswith('2025-06')])
            # with open('/Volumes/WD My Passport 264F Media/claude-voice-mcp/.cursor/debug.log', 'a') as _f:
            #     _f.write(_json.dumps({"location":"historical_data_service.py:_fetch_from_database","message":"Supabase PAGINATED query result","data":{"symbol":symbol,"interval":interval,"bar_count":len(all_bars),"first_date":_db_dates[0] if _db_dates else None,"last_date":_db_dates[-1] if _db_dates else None,"june_2025_bars":_june_2025_count,"pages_fetched":offset//page_size + 1},"timestamp":__import__('time').time()*1000,"sessionId":"debug-session","runId":"pagination-fix","hypothesisId":"F"}) + '\n')
            # #endregion

            return all_bars

        except Exception as e:
            logger.error(f"❌ Database query error: {e}")
            return []

    async def _check_coverage(
        self,
        symbol: str,
        interval: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Determine what data we have vs what we need.

        Returns:
            {
                'is_complete': bool,  # Do we have all requested data?
                'gaps': [{'start': datetime, 'end': datetime}],  # Missing ranges
                'coverage_record': dict  # Metadata from data_coverage table
            }
        """
        try:
            # Query coverage metadata
            response = self.supabase.table('data_coverage').select('*').eq(
                'symbol', symbol
            ).eq(
                'interval', interval
            ).execute()

            if not response.data or len(response.data) == 0:
                # No data at all - need to fetch entire range
                logger.debug(f"📊 No coverage data for {symbol} {interval}")
                return {
                    'is_complete': False,
                    'gaps': [{'start': start_date, 'end': end_date}],
                    'coverage_record': None
                }

            coverage_record = response.data[0]
            earliest_db = datetime.fromisoformat(coverage_record['earliest_bar'])
            latest_db = datetime.fromisoformat(coverage_record['latest_bar'])

            # Determine gaps
            gaps = []

            # Need older data?
            if start_date < earliest_db:
                gaps.append({
                    'start': start_date,
                    'end': min(earliest_db - timedelta(seconds=1), end_date)
                })
                logger.debug(
                    f"📊 Gap (older): {start_date.date()} to {earliest_db.date()}"
                )

            # Need newer data?
            if end_date > latest_db:
                gaps.append({
                    'start': max(latest_db + timedelta(seconds=1), start_date),
                    'end': end_date
                })
                logger.debug(
                    f"📊 Gap (newer): {latest_db.date()} to {end_date.date()}"
                )

            is_complete = len(gaps) == 0

            return {
                'is_complete': is_complete,
                'gaps': gaps,
                'coverage_record': coverage_record
            }

        except Exception as e:
            logger.error(f"❌ Coverage check error: {e}")
            # Assume incomplete and fetch entire range
            return {
                'is_complete': False,
                'gaps': [{'start': start_date, 'end': end_date}],
                'coverage_record': None
            }

    async def _fetch_from_yahoo_mcp(
        self,
        symbol: str,
        interval: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Fetch historical data from Yahoo Finance via MCP server (fallback source).

        Args:
            symbol: Ticker symbol
            interval: Bar interval
            start_date: Start of range
            end_date: End of range

        Returns:
            List of bars in Alpaca format (with 'timestamp', 'open', 'high', 'low', 'close', 'volume')
        """
        try:
            # Calculate days parameter for Yahoo Finance
            days = (end_date - start_date).days + 1

            # Map internal interval format to Yahoo Finance API format
            # Yahoo Finance uses different interval codes than our internal system
            yahoo_interval_map = {
                '1w': '1wk',    # Weekly: '1w' → '1wk'
                '1mo': '1mo',   # Monthly: same
                '1d': '1d',     # Daily: same
                '1h': '1h',     # Hourly: same
                '15m': '15m',   # 15-min: same
                '5m': '5m',     # 5-min: same
                '1min': '1m',   # 1-min: '1min' → '1m'
            }
            yahoo_interval = yahoo_interval_map.get(interval, interval)

            logger.info(
                f"🌐 L3 FALLBACK (Yahoo via MCP): {symbol} {interval} → {yahoo_interval} "
                f"{start_date.date()} to {end_date.date()} ({days} days)"
            )

            # Get MCP client (HTTPMCPClient via HTTP on port 3001)
            client = await get_direct_mcp_client()

            # Call Yahoo Finance via MCP with absolute dates (supports decades of data)
            params = {
                "symbol": symbol,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "interval": yahoo_interval  # Use converted Yahoo format
            }

            result = await client.call_tool("get_stock_history", params)

            # Handle MCP response format (STDIO)
            # Response structure: {"result": {"content": [{"type": "text", "text": "{...JSON...}"}]}}
            candles = []
            if result and isinstance(result, dict):
                if "result" in result and isinstance(result["result"], dict):
                    result_data = result["result"]
                    # STDIO format: result.result.content[0].text contains JSON string
                    if "content" in result_data and isinstance(result_data["content"], list):
                        content = result_data["content"]
                        if content and len(content) > 0 and "text" in content[0]:
                            # Parse the JSON string inside the text field
                            data_json = json.loads(content[0]["text"])
                            candles = data_json.get("candles", data_json.get("data", []))
                            logger.info(f"📦 Extracted {len(candles)} candles from STDIO format")
                    # HTTP format: result.result directly contains the data
                    elif "candles" in result_data or "data" in result_data:
                        candles = result_data.get("candles", result_data.get("data", []))
                        logger.info(f"📦 Extracted {len(candles)} candles from HTTP format")

            # Convert Yahoo Finance format to Alpaca format
            bars = []
            logger.info(f"🔍 Parsing {len(candles)} candles from Yahoo MCP")
            logger.info(f"🔍 Date range filter: {start_date.date()} to {end_date.date()}")

            for candle in candles:
                # Yahoo MCP returns: {date: ISO string, open, high, low, close, volume}
                # Convert to Alpaca format: {timestamp: ISO string, ...}
                timestamp_str = candle.get("date") or candle.get("time")
                if timestamp_str:
                    # Parse ISO string or unix timestamp
                    if isinstance(timestamp_str, str):
                        timestamp_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        timestamp_dt = datetime.fromtimestamp(timestamp_str)

                    # Remove timezone for comparison (start_date/end_date are naive)
                    timestamp_dt_naive = timestamp_dt.replace(tzinfo=None)

                    # Debug: Log first few dates
                    if len(bars) < 3:
                        logger.info(
                            f"🔍 Candle date: {timestamp_dt_naive.date()}, "
                            f"In range? {start_date.date() <= timestamp_dt_naive.date() <= end_date.date()}"
                        )

                    # Filter to requested range (compare dates only, not times)
                    if start_date.date() <= timestamp_dt_naive.date() <= end_date.date():
                        bars.append({
                            "timestamp": timestamp_dt.isoformat(),
                            "open": float(candle.get("open", 0)),
                            "high": float(candle.get("high", 0)),
                            "low": float(candle.get("low", 0)),
                            "close": float(candle.get("close", 0)),
                            "volume": int(candle.get("volume", 0)),
                            "data_source": "yahoo_finance"
                        })

            logger.info(
                f"✅ Yahoo MCP SUCCESS: {symbol} {interval} → {len(bars)} bars"
            )

            return bars

        except Exception as e:
            logger.error(
                f"❌ Yahoo MCP FAILED: {symbol} {interval} "
                f"{start_date.date()} to {end_date.date()}: {e}"
            )
            return []

    async def _fill_gaps(
        self,
        symbol: str,
        interval: str,
        existing_bars: List[Dict],
        gaps: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Fetch missing data from Alpaca API (with Yahoo Finance fallback) and merge with existing bars.

        Args:
            symbol: Ticker symbol
            interval: Bar interval
            existing_bars: Bars already in database
            gaps: List of missing date ranges
            start_date: Original requested start
            end_date: Original requested end

        Returns:
            Complete dataset (existing + newly fetched)
        """
        all_new_bars = []

        # Alpaca IEX feed limit: ~5 years / 1900 days (data since ~2020)
        ALPACA_MAX_DAYS = 1900
        alpaca_cutoff_date = datetime.now() - timedelta(days=ALPACA_MAX_DAYS)

        for gap in gaps:
            try:
                # Calculate days to fetch
                days = (gap['end'] - gap['start']).days + 1

                # Force Yahoo MCP for weekly intervals (Alpaca IEX doesn't support 1Week)
                if interval == '1w':
                    logger.info(
                        f"🌐 L3 FETCH (Yahoo MCP - weekly interval): {symbol} {interval} "
                        f"{gap['start'].date()} to {gap['end'].date()} ({days} days)"
                    )

                    start_time = datetime.now()
                    new_bars = await self._fetch_from_yahoo_mcp(
                        symbol=symbol,
                        interval=interval,
                        start_date=gap['start'],
                        end_date=gap['end']
                    )
                    duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

                    if new_bars:
                        logger.info(
                            f"✅ L3 SUCCESS (Yahoo): {symbol} {interval} "
                            f"→ {len(new_bars)} bars in {duration_ms}ms"
                        )

                        await self._store_bars(symbol, interval, new_bars)
                        all_new_bars.extend(new_bars)

                        await self._log_api_call(
                            provider='yahoo_finance',
                            symbol=symbol,
                            interval=interval,
                            start_date=gap['start'],
                            end_date=gap['end'],
                            bars_fetched=len(new_bars),
                            duration_ms=duration_ms,
                            success=True
                        )
                    else:
                        logger.warning(
                            f"⚠️ Yahoo MCP returned no data for weekly {symbol} "
                            f"{gap['start'].date()} to {gap['end'].date()}"
                        )

                        await self._log_api_call(
                            provider='yahoo_finance',
                            symbol=symbol,
                            interval=interval,
                            start_date=gap['start'],
                            end_date=gap['end'],
                            bars_fetched=0,
                            duration_ms=duration_ms,
                            success=False,
                            error_message="No weekly data returned"
                        )

                    continue  # Skip Alpaca attempt for weekly data

                # Route to appropriate data source based on date range
                # For gaps older than Alpaca's limit (~2020), use Yahoo Finance directly
                if gap['start'] < alpaca_cutoff_date:
                    logger.info(
                        f"🌐 L3 FETCH (Yahoo MCP - pre-{alpaca_cutoff_date.year} data): {symbol} {interval} "
                        f"{gap['start'].date()} to {gap['end'].date()} ({days} days)"
                    )

                    # Use Yahoo Finance MCP for historical data
                    start_time = datetime.now()
                    new_bars = await self._fetch_from_yahoo_mcp(
                        symbol=symbol,
                        interval=interval,
                        start_date=gap['start'],
                        end_date=gap['end']
                    )
                    duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

                    if new_bars:
                        logger.info(
                            f"✅ L3 SUCCESS (Yahoo): {symbol} {interval} "
                            f"→ {len(new_bars)} bars in {duration_ms}ms"
                        )

                        # Store in database
                        await self._store_bars(symbol, interval, new_bars)
                        all_new_bars.extend(new_bars)

                        # Log successful Yahoo API call
                        await self._log_api_call(
                            provider='yahoo_finance',
                            symbol=symbol,
                            interval=interval,
                            start_date=gap['start'],
                            end_date=gap['end'],
                            bars_fetched=len(new_bars),
                            duration_ms=duration_ms,
                            success=True
                        )
                    else:
                        logger.warning(
                            f"⚠️ Yahoo MCP returned no data for {symbol} {interval} "
                            f"{gap['start'].date()} to {gap['end'].date()}"
                        )

                        # Log failed Yahoo attempt
                        await self._log_api_call(
                            provider='yahoo_finance',
                            symbol=symbol,
                            interval=interval,
                            start_date=gap['start'],
                            end_date=gap['end'],
                            bars_fetched=0,
                            duration_ms=duration_ms,
                            success=False,
                            error_message="No data returned"
                        )

                    # Skip Alpaca attempt for old data
                    continue

                logger.info(
                    f"🌐 L3 FETCH (Alpaca): {symbol} {interval} "
                    f"{gap['start'].date()} to {gap['end'].date()} ({days} days)"
                )

                # Call Alpaca API for recent data (post-2020)
                start_time = datetime.now()
                new_bars = self.alpaca_service.get_bars(
                    symbol=symbol,
                    interval=interval,
                    days=days
                )
                duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

                self.metrics['api_calls'] += 1

                # Filter bars to gap range (Alpaca might return more)
                # Fix: Convert timezone-aware timestamps to naive for comparison
                filtered_bars = []

                # Convert gap start/end to naive (they may be timezone-aware)
                gap_start_naive = gap['start'].replace(tzinfo=None) if gap['start'].tzinfo else gap['start']
                gap_end_naive = gap['end'].replace(tzinfo=None) if gap['end'].tzinfo else gap['end']

                for bar in new_bars:
                    bar_time = datetime.fromisoformat(bar['timestamp'])
                    # Remove timezone info to make it naive for comparison
                    bar_time_naive = bar_time.replace(tzinfo=None)
                    if gap_start_naive <= bar_time_naive <= gap_end_naive:
                        filtered_bars.append(bar)

                logger.info(
                    f"✅ L3 SUCCESS: {symbol} {interval} "
                    f"→ {len(filtered_bars)} bars in {duration_ms}ms"
                )

                # Store in database
                if filtered_bars:
                    await self._store_bars(symbol, interval, filtered_bars)
                    all_new_bars.extend(filtered_bars)

                # Log API call
                await self._log_api_call(
                    provider='alpaca',
                    symbol=symbol,
                    interval=interval,
                    start_date=gap['start'],
                    end_date=gap['end'],
                    bars_fetched=len(filtered_bars),
                    duration_ms=duration_ms,
                    success=True
                )

            except Exception as e:
                logger.error(
                    f"❌ L3 FAILED (Alpaca): {symbol} {interval} "
                    f"{gap['start'].date()} to {gap['end'].date()}: {e}"
                )

                # Log failed Alpaca API call
                await self._log_api_call(
                    provider='alpaca',
                    symbol=symbol,
                    interval=interval,
                    start_date=gap['start'],
                    end_date=gap['end'],
                    bars_fetched=0,
                    duration_ms=0,
                    success=False,
                    error_message=str(e)
                )

                # FALLBACK: Try Yahoo Finance via MCP
                try:
                    logger.warning(
                        f"🔄 Attempting Yahoo Finance fallback for {symbol} {interval}"
                    )

                    start_time = datetime.now()
                    yahoo_bars = await self._fetch_from_yahoo_mcp(
                        symbol=symbol,
                        interval=interval,
                        start_date=gap['start'],
                        end_date=gap['end']
                    )
                    duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

                    if yahoo_bars:
                        logger.info(
                            f"✅ FALLBACK SUCCESS: {symbol} {interval} "
                            f"→ {len(yahoo_bars)} bars from Yahoo Finance in {duration_ms}ms"
                        )

                        # Store in database
                        await self._store_bars(symbol, interval, yahoo_bars)
                        all_new_bars.extend(yahoo_bars)

                        # Log successful Yahoo API call
                        await self._log_api_call(
                            provider='yahoo_finance',
                            symbol=symbol,
                            interval=interval,
                            start_date=gap['start'],
                            end_date=gap['end'],
                            bars_fetched=len(yahoo_bars),
                            duration_ms=duration_ms,
                            success=True
                        )
                    else:
                        logger.error(
                            f"❌ FALLBACK FAILED: Yahoo Finance returned no data for {symbol}"
                        )

                        # Log failed Yahoo API call
                        await self._log_api_call(
                            provider='yahoo_finance',
                            symbol=symbol,
                            interval=interval,
                            start_date=gap['start'],
                            end_date=gap['end'],
                            bars_fetched=0,
                            duration_ms=duration_ms,
                            success=False,
                            error_message="No data returned"
                        )

                except Exception as yahoo_error:
                    logger.error(
                        f"❌ BOTH SOURCES FAILED: {symbol} {interval} - "
                        f"Alpaca: {e}, Yahoo: {yahoo_error}"
                    )

                    # Log failed Yahoo attempt
                    await self._log_api_call(
                        provider='yahoo_finance',
                        symbol=symbol,
                        interval=interval,
                        start_date=gap['start'],
                        end_date=gap['end'],
                        bars_fetched=0,
                        duration_ms=0,
                        success=False,
                        error_message=str(yahoo_error)
                    )

        # Merge existing + new bars, deduplicate, and sort
        # For daily bars: merge by DATE to handle different timestamp conventions
        # For intraday bars: merge by full TIMESTAMP

        if interval == '1d':
            # Daily bars: Use DATE as key (handles 05:00 UTC vs 14:30 UTC issue)
            bars_by_date = {}

            # Add existing bars first (from database)
            for bar in existing_bars:
                date = bar['timestamp'][:10]  # Extract "YYYY-MM-DD"
                bars_by_date[date] = bar

            # Add new bars (from API) - these override database bars if same date
            for bar in all_new_bars:
                date = bar['timestamp'][:10]
                bars_by_date[date] = bar  # Newer API data overwrites older DB data

            # Convert to list and normalize timestamps to BusinessDay format
            all_bars = []
            for date, bar in bars_by_date.items():
                bar = bar.copy()
                bar['timestamp'] = date  # Normalize to "YYYY-MM-DD" for Lightweight Charts
                all_bars.append(bar)

            all_bars.sort(key=lambda x: x['timestamp'])

            logger.info(
                f"📊 Daily bars merged: {len(existing_bars)} DB + {len(all_new_bars)} API "
                f"→ {len(all_bars)} unique dates"
            )
        else:
            # Intraday bars: Use full timestamp as key
            bars_by_timestamp = {}

            # Add existing bars first (from database)
            for bar in existing_bars:
                bars_by_timestamp[bar['timestamp']] = bar

            # Add new bars (from API) - these override database bars if duplicate timestamp
            for bar in all_new_bars:
                bars_by_timestamp[bar['timestamp']] = bar

            # Convert back to list and sort
            all_bars = list(bars_by_timestamp.values())
            all_bars.sort(key=lambda x: x['timestamp'])

        return all_bars

    def _normalize_daily_timestamp(self, timestamp_str: str) -> str:
        """
        Normalize daily bar timestamps to canonical format (BusinessDay: YYYY-MM-DD).

        Problem: Different data sources use different daily timestamp conventions:
        - Alpaca: Market open (14:30 UTC = 9:30 ET)
        - Yahoo: Midnight exchange day (05:00 UTC = 00:00 ET)

        This causes duplicate bars for the same trading day.

        Solution: Extract trading date only for daily bars.

        Args:
            timestamp_str: ISO timestamp string

        Returns:
            Canonical timestamp: "YYYY-MM-DD" for daily bars
        """
        try:
            # Handle both ISO format and simple date format
            if len(timestamp_str) == 10:  # Already YYYY-MM-DD
                return timestamp_str
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            # Return just the date in YYYY-MM-DD format (BusinessDay)
            return dt.date().isoformat()
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse timestamp {timestamp_str}: {e}")
            return timestamp_str  # Return original if parsing fails

    async def _store_bars(self, symbol: str, interval: str, bars: List[Dict]):
        """
        Store bars in Supabase database.

        For daily bars (interval='1d'), normalizes timestamps to BusinessDay format
        to prevent duplicates from different timestamp conventions.

        Uses upsert to handle duplicates gracefully.
        Trigger will automatically update data_coverage table.
        """
        if not bars:
            return

        try:
            # Prepare data for insert
            records = []
            for bar in bars:
                # Normalize daily timestamps to prevent duplicates
                timestamp = bar['timestamp']
                if interval == '1d':
                    timestamp = self._normalize_daily_timestamp(timestamp)

                records.append({
                    'symbol': symbol,
                    'interval': interval,
                    'timestamp': timestamp,
                    'open': float(bar['open']),
                    'high': float(bar['high']),
                    'low': float(bar['low']),
                    'close': float(bar['close']),
                    'volume': int(bar['volume']),
                    'trade_count': bar.get('trade_count'),
                    'vwap': bar.get('vwap'),
                    'data_source': bar.get('data_source', 'alpaca')
                })

            logger.info(
                f"💾 Storing {len(records)} bars for {symbol} {interval} "
                f"({'normalized to BusinessDay' if interval == '1d' else 'as-is'})"
            )

            # Upsert (insert or update if exists)
            # Now that daily timestamps are normalized, upsert will properly deduplicate
            response = self.supabase.table('historical_bars').upsert(records).execute()

        except Exception as e:
            logger.error(f"❌ Failed to store bars: {e}")

    async def _log_api_call(
        self,
        provider: str,
        symbol: str,
        interval: str,
        start_date: datetime,
        end_date: datetime,
        bars_fetched: int,
        duration_ms: int,
        success: bool,
        error_message: str = None
    ):
        """Log API call to database for monitoring."""
        try:
            self.supabase.table('api_call_log').insert({
                'provider': provider,
                'symbol': symbol,
                'interval': interval,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'bars_fetched': bars_fetched,
                'duration_ms': duration_ms,
                'success': success,
                'error_message': error_message
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to log API call: {e}")

    def _make_cache_key(
        self,
        symbol: str,
        interval: str,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """Generate Redis cache key."""
        return f"bars:{symbol}:{interval}:{start_date.date()}:{end_date.date()}"

    def _get_from_redis(self, cache_key: str) -> Optional[List[Dict]]:
        """Retrieve data from Redis cache (L1)."""
        if not self.cache_service.client:
            return None

        try:
            cached = self.cache_service.client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")

        return None

    def _store_in_redis(self, cache_key: str, bars: List[Dict]):
        """Store data in Redis cache with 1-hour TTL."""
        if not self.cache_service.client or not bars:
            return

        try:
            self.cache_service.client.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(bars)
            )
            logger.debug(f"💾 Cached in Redis: {cache_key}")
        except Exception as e:
            logger.warning(f"Redis set error: {e}")

    def get_metrics(self) -> Dict:
        """Get cache performance metrics."""
        total = self.metrics['total_requests']
        if total == 0:
            return self.metrics

        return {
            **self.metrics,
            'redis_hit_rate': round(self.metrics['redis_hits'] / total * 100, 2),
            'db_hit_rate': round(self.metrics['db_hits'] / total * 100, 2),
            'api_call_rate': round(self.metrics['api_calls'] / total * 100, 2)
        }


# Singleton instance
_historical_data_service: Optional[HistoricalDataService] = None


def get_historical_data_service() -> HistoricalDataService:
    """Get or create singleton historical data service instance."""
    global _historical_data_service
    if _historical_data_service is None:
        _historical_data_service = HistoricalDataService()
    return _historical_data_service
