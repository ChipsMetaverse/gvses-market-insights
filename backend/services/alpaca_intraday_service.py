"""
Alpaca Intraday Data Service - Extended Historical Data (5+ Years)

Provides access to Alpaca Markets API for extended intraday historical data.
Supports 1-minute, 5-minute, and 1-hour bars going back up to 5+ years.

Key Features:
- Free tier access via Alpaca paper trading API
- 5+ years of historical intraday data (IEX feed, since ~2020)
- 200 API calls/minute rate limit
- IEX exchange data (15-minute delayed on free tier)
- Automatic pagination for large date ranges
- Error handling with fallback support
- Requires explicit feed='iex' parameter for free tier access
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Literal
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import logging

logger = logging.getLogger(__name__)

IntervalType = Literal['1Min', '5Min', '15Min', '30Min', '1Hour', '1Day']


class AlpacaIntradayService:
    """Service for fetching extended intraday data from Alpaca Markets API."""

    def __init__(self):
        """Initialize Alpaca client with credentials from environment."""
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')

        if not api_key or not secret_key:
            raise ValueError(
                "Alpaca API credentials not found. "
                "Set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env"
            )

        # Initialize historical data client (free tier uses paper trading API)
        self.client = StockHistoricalDataClient(api_key, secret_key)
        logger.info("✅ Alpaca Intraday Service initialized with free tier access")

    def get_bars(
        self,
        symbol: str,
        interval: IntervalType = '5Min',
        days: int = 60,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Fetch intraday bars from Alpaca.

        Args:
            symbol: Stock ticker symbol (e.g., 'TSLA', 'AAPL')
            interval: Bar interval - '1Min', '5Min', '15Min', '30Min', '1Hour', '1Day'
            days: Number of days to fetch (max 1900 = ~5 years on free tier)
            limit: Optional max number of bars to return (None = all available)

        Returns:
            List of OHLCV dictionaries with format:
            [
                {
                    'timestamp': '2024-01-01T09:30:00Z',
                    'open': 100.5,
                    'high': 101.2,
                    'low': 100.1,
                    'close': 101.0,
                    'volume': 1000000
                },
                ...
            ]

        Raises:
            ValueError: If invalid parameters
            Exception: If API call fails
        """
        try:
            # Validate inputs
            if days > 1900:  # ~5 years (free tier IEX feed limit)
                logger.warning(f"Requested {days} days exceeds 5-year free tier limit. Capping at 1900 days.")
                days = 1900

            # Convert interval string to Alpaca TimeFrame
            timeframe = self._convert_interval_to_timeframe(interval)

            # Calculate start and end dates (timezone-aware for consistency)
            from datetime import timezone
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)

            logger.info(
                f"📊 Fetching {interval} bars for {symbol} "
                f"from {start_date.date()} to {end_date.date()} ({days} days)"
            )

            # Create request
            # IMPORTANT: Use 'iex' feed for free tier / paper trading accounts
            # SIP feed requires additional subscription ($99/month)
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start_date,
                end=end_date,
                limit=limit,  # None = fetch all
                feed='iex'  # Use IEX feed for free tier access
            )

            # Fetch data from Alpaca
            bars_response = self.client.get_stock_bars(request)

            # Extract bars for the symbol
            if symbol not in bars_response.data:
                logger.warning(f"⚠️ No data returned for {symbol}")
                return []

            bars = bars_response.data[symbol]

            # Convert to standard OHLCV format
            result = [
                {
                    'timestamp': bar.timestamp.isoformat(),
                    'open': float(bar.open),
                    'high': float(bar.high),
                    'low': float(bar.low),
                    'close': float(bar.close),
                    'volume': int(bar.volume),
                    'trade_count': int(bar.trade_count) if hasattr(bar, 'trade_count') and bar.trade_count is not None else None,
                    'vwap': float(bar.vwap) if hasattr(bar, 'vwap') and bar.vwap is not None else None,
                }
                for bar in bars
            ]

            logger.info(f"✅ Successfully fetched {len(result)} bars for {symbol}")
            return result

        except Exception as e:
            logger.error(f"❌ Error fetching Alpaca data for {symbol}: {str(e)}")
            raise

    def _normalize_interval(self, interval: str) -> str:
        """
        Normalize interval format to Alpaca format.
        Supports both formats: '1d'/'1Day', '5m'/'5Min', etc.

        Args:
            interval: Interval string (e.g., '1d', '1Day', '5m', '5Min')

        Returns:
            Normalized interval in Alpaca format (e.g., '1Day', '5Min')
        """
        # Mapping from short format to Alpaca format
        format_map = {
            '1m': '1Min',
            '5m': '5Min',
            '15m': '15Min',
            '30m': '30Min',
            '1h': '1Hour',
            '4h': '4Hour',
            '1d': '1Day',
            '1w': '1Week',
            '1mo': '1Month',
            # Also accept Alpaca format as-is
            '1Min': '1Min',
            '5Min': '5Min',
            '15Min': '15Min',
            '30Min': '30Min',
            '1Hour': '1Hour',
            '4Hour': '4Hour',
            '1Day': '1Day',
            '1Week': '1Week',
            '1Month': '1Month',
        }

        normalized = format_map.get(interval)
        if not normalized:
            raise ValueError(
                f"Invalid interval '{interval}'. "
                f"Supported formats: {list(format_map.keys())}"
            )

        return normalized

    def _convert_interval_to_timeframe(self, interval: IntervalType) -> TimeFrame:
        """
        Convert interval string to Alpaca TimeFrame object.

        Args:
            interval: String like '1d', '1Day', '5m', '5Min', etc.

        Returns:
            Alpaca TimeFrame object
        """
        # Normalize interval first
        normalized = self._normalize_interval(interval)

        interval_map = {
            '1Min': TimeFrame(1, TimeFrameUnit.Minute),
            '5Min': TimeFrame(5, TimeFrameUnit.Minute),
            '15Min': TimeFrame(15, TimeFrameUnit.Minute),
            '30Min': TimeFrame(30, TimeFrameUnit.Minute),
            '1Hour': TimeFrame(1, TimeFrameUnit.Hour),
            '4Hour': TimeFrame(4, TimeFrameUnit.Hour),
            '1Day': TimeFrame(1, TimeFrameUnit.Day),
            '1Week': TimeFrame(1, TimeFrameUnit.Week),
            '1Month': TimeFrame(1, TimeFrameUnit.Month),
        }

        return interval_map[normalized]

    def get_latest_bar(self, symbol: str, interval: IntervalType = '1Min') -> Optional[Dict]:
        """
        Get the most recent bar for a symbol.

        Args:
            symbol: Stock ticker
            interval: Bar interval

        Returns:
            Latest OHLCV dictionary or None if no data
        """
        try:
            bars = self.get_bars(symbol, interval, days=1, limit=1)
            return bars[-1] if bars else None
        except Exception as e:
            logger.error(f"Error fetching latest bar for {symbol}: {str(e)}")
            return None

    def health_check(self) -> Dict[str, any]:
        """
        Check if Alpaca API is accessible and working.

        Returns:
            Dictionary with health status
        """
        try:
            # Try fetching a single bar for a liquid stock
            test_bar = self.get_latest_bar('AAPL', '1Min')

            return {
                'status': 'healthy' if test_bar else 'degraded',
                'service': 'Alpaca Markets API',
                'tier': 'Free (IEX feed, 15-min delayed)',
                'capabilities': {
                    'max_history': '5+ years (IEX feed)',
                    'intervals': ['1Min', '5Min', '15Min', '30Min', '1Hour', '1Day'],
                    'rate_limit': '200 calls/minute',
                    'data_feed': 'IEX (free tier)'
                },
                'test_result': test_bar is not None
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'service': 'Alpaca Markets API'
            }


# Singleton instance
_alpaca_service: Optional[AlpacaIntradayService] = None


def get_alpaca_service() -> AlpacaIntradayService:
    """Get or create singleton Alpaca service instance."""
    global _alpaca_service
    if _alpaca_service is None:
        _alpaca_service = AlpacaIntradayService()
    return _alpaca_service
