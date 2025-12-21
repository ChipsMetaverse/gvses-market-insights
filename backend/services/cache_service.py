"""
Redis Cache Service for Intraday Data

Provides caching layer for frequently accessed intraday market data.
Reduces API calls and improves response times for popular symbols.

Features:
- Automatic cache warming for top symbols
- TTL-based expiration (1 hour for current day, longer for historical)
- Cache key structure: symbol:interval:days
- Handles cache misses gracefully
- Provides cache hit/miss metrics
"""

import os
import json
import logging
from typing import Optional, Dict, List, Callable
from datetime import datetime, timedelta
import redis

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for intraday market data."""

    # Popular symbols to pre-cache (top 20 most requested)
    TOP_SYMBOLS = [
        'TSLA', 'AAPL', 'NVDA', 'SPY', 'MSFT',
        'GOOGL', 'AMZN', 'META', 'AMD', 'PLTR',
        'QQQ', 'NFLX', 'COIN', 'DIS', 'BABA',
        'BA', 'F', 'GE', 'GM', 'INTC'
    ]

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize Redis cache client.

        Args:
            redis_url: Redis connection URL (defaults to localhost)
        """
        if redis_url is None:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.client.ping()
            logger.info(f"✅ Redis cache connected: {redis_url}")

            # Initialize metrics
            self.hits = 0
            self.misses = 0

        except redis.ConnectionError as e:
            logger.warning(f"⚠️ Redis unavailable: {e}. Caching disabled.")
            self.client = None

    def get(
        self,
        symbol: str,
        interval: str,
        days: int,
        fetch_fn: Callable[[], List[Dict]]
    ) -> List[Dict]:
        """
        Get data from cache or fetch if cache miss.

        Args:
            symbol: Stock ticker
            interval: Bar interval (e.g., '5Min')
            days: Lookback period
            fetch_fn: Function to call on cache miss (returns data)

        Returns:
            List of OHLCV dictionaries
        """
        cache_key = self._make_key(symbol, interval, days)

        # Try cache first
        if self.client:
            try:
                cached_data = self.client.get(cache_key)
                if cached_data:
                    self.hits += 1
                    logger.info(f"💾 Cache HIT: {cache_key}")
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Cache read error for {cache_key}: {e}")

        # Cache miss - fetch fresh data
        self.misses += 1
        logger.info(f"🔄 Cache MISS: {cache_key} - fetching from source")

        data = fetch_fn()

        # Store in cache
        if self.client and data:
            try:
                ttl = self._calculate_ttl(interval, days)
                self.client.setex(
                    cache_key,
                    ttl,
                    json.dumps(data)
                )
                logger.info(f"💾 Cached {len(data)} bars for {cache_key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"Cache write error for {cache_key}: {e}")

        return data

    def warm_cache(
        self,
        symbols: Optional[List[str]] = None,
        fetch_fn: Optional[Callable[[str, str, int], List[Dict]]] = None
    ):
        """
        Pre-populate cache with popular symbols.

        Args:
            symbols: List of symbols to cache (defaults to TOP_SYMBOLS)
            fetch_fn: Function to fetch data (symbol, interval, days) -> data
        """
        if not self.client or not fetch_fn:
            logger.info("Cache warming skipped (no Redis or fetch function)")
            return

        symbols = symbols or self.TOP_SYMBOLS

        logger.info(f"🔥 Warming cache for {len(symbols)} symbols...")

        # Cache configurations: (interval, days)
        configs = [
            ('5Min', 60),   # Last 60 days of 5-minute data
            ('1Hour', 365), # Last year of hourly data
            ('1Day', 1095), # Last 3 years of daily data
        ]

        warmed = 0
        for symbol in symbols:
            for interval, days in configs:
                try:
                    cache_key = self._make_key(symbol, interval, days)

                    # Only warm if not already cached
                    if not self.client.exists(cache_key):
                        data = fetch_fn(symbol, interval, days)
                        if data:
                            ttl = self._calculate_ttl(interval, days)
                            self.client.setex(cache_key, ttl, json.dumps(data))
                            warmed += 1
                            logger.debug(f"  ✓ Cached {symbol} {interval} ({len(data)} bars)")

                except Exception as e:
                    logger.warning(f"  ✗ Failed to warm {symbol} {interval}: {e}")

        logger.info(f"✅ Cache warming complete: {warmed} entries added")

    def invalidate(self, symbol: str, interval: Optional[str] = None):
        """
        Invalidate cache for a symbol (useful after corporate actions).

        Args:
            symbol: Stock ticker
            interval: Specific interval to invalidate (None = all intervals)
        """
        if not self.client:
            return

        try:
            if interval:
                # Invalidate specific interval
                pattern = f"{symbol}:{interval}:*"
            else:
                # Invalidate all intervals for symbol
                pattern = f"{symbol}:*"

            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
                logger.info(f"🗑️ Invalidated {len(keys)} cache entries for {symbol}")

        except Exception as e:
            logger.warning(f"Cache invalidation error for {symbol}: {e}")

    def get_stats(self) -> Dict:
        """
        Get cache performance statistics.

        Returns:
            Dictionary with cache metrics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        stats = {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2),
            'redis_connected': self.client is not None
        }

        if self.client:
            try:
                info = self.client.info('stats')
                stats.update({
                    'total_commands': info.get('total_commands_processed', 0),
                    'used_memory_human': self.client.info('memory').get('used_memory_human', 'N/A')
                })
            except Exception:
                pass

        return stats

    def clear_all(self):
        """Clear entire cache (use with caution!)."""
        if self.client:
            try:
                self.client.flushdb()
                logger.warning("🗑️ Entire cache cleared!")
            except Exception as e:
                logger.error(f"Cache clear failed: {e}")

    def _make_key(self, symbol: str, interval: str, days: int) -> str:
        """Generate cache key from parameters."""
        return f"{symbol.upper()}:{interval}:{days}"

    def _calculate_ttl(self, interval: str, days: int) -> int:
        """
        Calculate appropriate TTL (time-to-live) for cached data.

        Args:
            interval: Bar interval
            days: Data range

        Returns:
            TTL in seconds
        """
        # Current day data: 1 hour TTL (updates frequently)
        if days <= 1:
            return 3600  # 1 hour

        # Recent data (< 7 days): 4 hour TTL
        if days <= 7:
            return 14400  # 4 hours

        # Historical data (> 7 days): 24 hour TTL (stable, rarely changes)
        return 86400  # 24 hours


# Singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create singleton cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
