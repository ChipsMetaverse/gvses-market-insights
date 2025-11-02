"""
Supabase Market Data Cache Integration
Connects existing backend code to optimized market_data_daily schema
"""

import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseMarketCache:
    """
    Intelligent caching layer for market data using Supabase.
    
    Strategy:
    1. Check cache (market_data_daily) first
    2. If missing, fetch from existing API pipeline
    3. Store in cache for next time
    4. Automatic cache invalidation and refresh
    """
    
    def __init__(self):
        """Initialize Supabase client with service role key"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not found - cache disabled")
            self.enabled = False
            return
        
        try:
            self.client: Client = create_client(supabase_url, supabase_key)
            self.enabled = True
            logger.info("✅ Supabase market cache initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase cache: {e}")
            self.enabled = False
    
    def get_daily_bars(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get daily bars from cache.
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            
        Returns:
            List of OHLCV dicts or None if cache miss
        """
        if not self.enabled:
            return None
        
        try:
            result = self.client.rpc(
                'get_historical_data',
                {
                    'p_symbol': symbol.upper(),
                    'p_start_date': start_date,
                    'p_end_date': end_date
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"✅ Cache HIT for {symbol} ({len(result.data)} records)")
                return result.data
            
            logger.info(f"⚠️ Cache MISS for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Cache read error for {symbol}: {e}")
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get latest price from cache.
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Dict with latest price data or None
        """
        if not self.enabled:
            return None
        
        try:
            result = self.client.rpc(
                'get_latest_price',
                {'p_symbol': symbol.upper()}
            ).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"✅ Latest price cached for {symbol}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error fetching latest price for {symbol}: {e}")
            return None
    
    def store_daily_bars(
        self, 
        symbol: str, 
        bars_data: List[Dict[str, Any]],
        source: str = "alpaca"
    ) -> bool:
        """
        Store daily bars in cache.
        
        Args:
            symbol: Stock ticker
            bars_data: List of bar dicts with keys: date, open, high, low, close, volume
            source: Data source name (default: 'alpaca')
            
        Returns:
            True if stored successfully
        """
        if not self.enabled or not bars_data:
            return False
        
        try:
            # Transform data to match schema
            records = []
            for bar in bars_data:
                # Handle both dict and DataFrame-like objects
                if hasattr(bar, 'to_dict'):
                    bar = bar.to_dict()
                
                record = {
                    'symbol': symbol.upper(),
                    'date': bar.get('date') or bar.get('timestamp'),
                    'open': float(bar['open']),
                    'high': float(bar['high']),
                    'low': float(bar['low']),
                    'close': float(bar['close']),
                    'volume': int(bar['volume']),
                    'adjusted_close': float(bar.get('adjusted_close', bar['close'])),
                    'data_source': source
                }
                records.append(record)
            
            # Upsert to database (insert or update on conflict)
            self.client.table('market_data_daily').upsert(
                records,
                on_conflict='symbol,date'
            ).execute()
            
            logger.info(f"💾 Cached {len(records)} records for {symbol}")
            
            # Update symbol metadata
            self._update_symbol_metadata(symbol, records)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache write error for {symbol}: {e}")
            return False
    
    def _update_symbol_metadata(
        self, 
        symbol: str, 
        records: List[Dict[str, Any]]
    ):
        """Update or create symbol metadata"""
        try:
            dates = [r['date'] for r in records]
            first_date = min(dates)
            last_date = max(dates)
            
            metadata = {
                'symbol': symbol.upper(),
                'asset_type': 'stock',
                'is_active': True,
                'is_tradable': True,
                'first_trade_date': first_date,
                'last_update': last_date,
                'metadata': {
                    'record_count': len(records),
                    'last_sync': datetime.now().isoformat()
                }
            }
            
            self.client.table('symbols').upsert(
                metadata,
                on_conflict='symbol'
            ).execute()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to update symbol metadata: {e}")
    
    def get_cached_symbols(self) -> List[str]:
        """Get list of symbols available in cache"""
        if not self.enabled:
            return []
        
        try:
            result = self.client.table('symbols').select('symbol').eq('is_active', True).execute()
            return [row['symbol'] for row in result.data]
        except Exception as e:
            logger.error(f"❌ Error fetching cached symbols: {e}")
            return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled:
            return {'enabled': False}
        
        try:
            # Get storage stats
            storage = self.client.rpc('storage_stats', {}).execute()
            
            # Get symbol count
            symbols = self.client.table('symbols').select('symbol', count='exact').execute()
            
            # Get record count
            records = self.client.table('market_data_daily').select('symbol', count='exact').execute()
            
            return {
                'enabled': True,
                'total_symbols': symbols.count if hasattr(symbols, 'count') else 0,
                'total_records': records.count if hasattr(records, 'count') else 0,
                'storage': storage.data if storage.data else []
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching cache stats: {e}")
            return {'enabled': True, 'error': str(e)}
    
    def clear_old_data(self, days_to_keep: int = 730):
        """
        Clear data older than specified days (default: 2 years).
        
        Args:
            days_to_keep: Number of days of historical data to retain
        """
        if not self.enabled:
            return
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).date()
            
            result = self.client.table('market_data_daily')\
                .delete()\
                .lt('date', cutoff_date.isoformat())\
                .execute()
            
            logger.info(f"🧹 Cleaned up data older than {cutoff_date}")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning old data: {e}")


# Global cache instance
_cache_instance = None

def get_market_cache() -> SupabaseMarketCache:
    """Get or create global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SupabaseMarketCache()
    return _cache_instance


# Convenience functions for backward compatibility
def get_cached_bars(symbol: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
    """Get bars from cache (convenience function)"""
    return get_market_cache().get_daily_bars(symbol, start_date, end_date)


def cache_bars(symbol: str, bars: List[Dict], source: str = "alpaca") -> bool:
    """Store bars in cache (convenience function)"""
    return get_market_cache().store_daily_bars(symbol, bars, source)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics (convenience function)"""
    return get_market_cache().get_cache_stats()

