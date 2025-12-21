"""
Alpaca Market Data Service
Provides real-time and historical market data using Alpaca Markets API
"""

import os
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables before accessing them
load_dotenv()
from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import (
    StockBarsRequest,
    StockQuotesRequest,
    StockTradesRequest,
    StockSnapshotRequest,
    CryptoLatestQuoteRequest,
    CryptoBarsRequest
)
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.requests import GetOrdersRequest, GetAssetsRequest
from alpaca.trading.enums import QueryOrderStatus, AssetClass, AssetStatus, AssetExchange
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT_THRESHOLD = 180  # Alpaca allows 200 requests per minute
RATE_LIMIT_WINDOW = 60  # 60 seconds
REQUEST_TRACKING = {
    'count': 0,
    'window_start': time.time()
}


class AlpacaService:
    """Service for fetching market data from Alpaca Markets."""
    
    def __init__(self):
        """Initialize Alpaca clients with API credentials from environment."""
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.is_available = False
        self.request_count = 0
        self.window_start = time.time()
        
        if not self.api_key or not self.secret_key:
            logger.warning("Alpaca API credentials not found in environment - service will be unavailable")
            return
        
        try:
            # Initialize clients
            self.trading_client = TradingClient(
                api_key=self.api_key,
                secret_key=self.secret_key,
                paper=True  # Always use paper trading for safety
            )

            self.data_client = StockHistoricalDataClient(
                api_key=self.api_key,
                secret_key=self.secret_key
            )

            self.crypto_client = CryptoHistoricalDataClient(
                api_key=self.api_key,
                secret_key=self.secret_key
            )

            self.is_available = True
            logger.info("Alpaca service initialized successfully (stocks + crypto)")
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca clients: {e}")
            self.is_available = False
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_time = time.time()
        
        # Reset counter if window has elapsed
        if current_time - self.window_start > RATE_LIMIT_WINDOW:
            self.request_count = 0
            self.window_start = current_time
        
        # Check if we're approaching the limit
        if self.request_count >= RATE_LIMIT_THRESHOLD:
            logger.warning(f"Alpaca rate limit approaching: {self.request_count}/{RATE_LIMIT_THRESHOLD}")
            return False
        
        return True
    
    def _increment_request_count(self):
        """Increment the request counter."""
        self.request_count += 1
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        try:
            account = self.trading_client.get_account()
            return {
                "status": account.status,
                "buying_power": float(account.buying_power),
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "pattern_day_trader": account.pattern_day_trader,
                "trading_blocked": account.trading_blocked,
                "account_blocked": account.account_blocked,
            }
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            return {"error": str(e)}
    
    @lru_cache(maxsize=100)
    def _get_cached_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Cache quotes for 1 minute to reduce API calls."""
        return None
    
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get latest quote for a stock symbol."""
        try:
            request = StockQuotesRequest(symbol_or_symbols=symbol)
            quotes = self.data_client.get_stock_latest_quote(request)
            
            if symbol in quotes:
                quote = quotes[symbol]
                return {
                    "symbol": symbol,
                    "ask_price": float(quote.ask_price) if quote.ask_price else None,
                    "bid_price": float(quote.bid_price) if quote.bid_price else None,
                    "ask_size": quote.ask_size,
                    "bid_size": quote.bid_size,
                    "timestamp": quote.timestamp.isoformat() if quote.timestamp else None,
                    "source": "alpaca"
                }
            return {"error": f"No quote data for {symbol}"}
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return {"error": str(e)}
    
    async def get_stock_bars(
        self, 
        symbol: str, 
        timeframe: str = "1Day",
        days_back: int = 30,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get historical bars for a stock symbol."""
        try:
            # Map timeframe strings to Alpaca TimeFrame
            timeframe_map = {
                "1Min": TimeFrame.Minute,
                "5Min": TimeFrame(5, "Min"),
                "15Min": TimeFrame(15, "Min"),
                "30Min": TimeFrame(30, "Min"),
                "1Hour": TimeFrame.Hour,
                "4Hour": TimeFrame(4, "Hour"),
                "1Day": TimeFrame.Day,
                "1Week": TimeFrame.Week,
                "1Month": TimeFrame.Month
            }
            
            tf = timeframe_map.get(timeframe, TimeFrame.Day)

            # Calculate start date
            start_date = datetime.now() - timedelta(days=days_back)
            logger.info(f"[ALPACA DEBUG] Requesting {symbol} bars from {start_date.strftime('%Y-%m-%d')} ({days_back} days back, timeframe={timeframe})")

            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=start_date,
                limit=limit
            )

            bars_response = self.data_client.get_stock_bars(request)

            if symbol in bars_response.data:
                bars = bars_response.data[symbol]
                logger.info(f"[ALPACA DEBUG] Alpaca API returned {len(bars)} bars for {symbol}")
                return {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "bars": [
                        {
                            "timestamp": bar.timestamp.isoformat(),
                            "open": float(bar.open),
                            "high": float(bar.high),
                            "low": float(bar.low),
                            "close": float(bar.close),
                            "volume": bar.volume,
                            "trade_count": bar.trade_count,
                            "vwap": float(bar.vwap) if bar.vwap else None
                        }
                        for bar in bars
                    ],
                    "source": "alpaca"
                }
            return {"error": f"No bar data for {symbol}"}
        except Exception as e:
            logger.error(f"Error fetching bars for {symbol}: {e}")
            return {"error": str(e)}
    
    async def get_batch_snapshots(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive snapshots for multiple stock symbols."""
        try:
            # Alpaca API accepts multiple symbols in a single request
            request = StockSnapshotRequest(symbol_or_symbols=symbols)
            snapshots = self.data_client.get_stock_snapshot(request)
            
            results = {}
            for symbol in symbols:
                if symbol in snapshots:
                    snapshot = snapshots[symbol]
                    result = {
                        "symbol": symbol,
                        "source": "alpaca"
                    }
                    
                    # Add latest trade
                    if snapshot.latest_trade:
                        result["latest_trade"] = {
                            "price": float(snapshot.latest_trade.price),
                            "size": snapshot.latest_trade.size,
                            "timestamp": snapshot.latest_trade.timestamp.isoformat()
                        }
                    
                    # Add latest quote
                    if snapshot.latest_quote:
                        result["latest_quote"] = {
                            "ask_price": float(snapshot.latest_quote.ask_price) if snapshot.latest_quote.ask_price else None,
                            "bid_price": float(snapshot.latest_quote.bid_price) if snapshot.latest_quote.bid_price else None,
                            "ask_size": snapshot.latest_quote.ask_size,
                            "bid_size": snapshot.latest_quote.bid_size
                        }
                    
                    # Add daily bar
                    if snapshot.daily_bar:
                        result["daily_bar"] = {
                            "open": float(snapshot.daily_bar.open),
                            "high": float(snapshot.daily_bar.high),
                            "low": float(snapshot.daily_bar.low),
                            "close": float(snapshot.daily_bar.close),
                            "volume": snapshot.daily_bar.volume,
                            "timestamp": snapshot.daily_bar.timestamp.isoformat()
                        }
                    
                    # Add previous daily bar
                    if snapshot.previous_daily_bar:
                        result["previous_daily_bar"] = {
                            "open": float(snapshot.previous_daily_bar.open),
                            "high": float(snapshot.previous_daily_bar.high),
                            "low": float(snapshot.previous_daily_bar.low),
                            "close": float(snapshot.previous_daily_bar.close),
                            "volume": snapshot.previous_daily_bar.volume,
                            "timestamp": snapshot.previous_daily_bar.timestamp.isoformat()
                        }
                    
                    results[symbol] = result
                else:
                    results[symbol] = {"error": f"No snapshot data for {symbol}"}
            
            return results
        except Exception as e:
            logger.error(f"Error fetching batch snapshots: {e}")
            return {symbol: {"error": str(e)} for symbol in symbols}
    
    async def get_snapshot(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive snapshot data for a symbol."""
        try:
            request = StockSnapshotRequest(symbol_or_symbols=symbol)
            snapshots = self.data_client.get_stock_snapshot(request)
            
            if symbol in snapshots:
                snapshot = snapshots[symbol]
                
                result = {
                    "symbol": symbol,
                    "source": "alpaca"
                }
                
                # Add latest trade
                if snapshot.latest_trade:
                    result["latest_trade"] = {
                        "price": float(snapshot.latest_trade.price),
                        "size": snapshot.latest_trade.size,
                        "timestamp": snapshot.latest_trade.timestamp.isoformat()
                    }
                
                # Add latest quote
                if snapshot.latest_quote:
                    result["latest_quote"] = {
                        "ask_price": float(snapshot.latest_quote.ask_price) if snapshot.latest_quote.ask_price else None,
                        "bid_price": float(snapshot.latest_quote.bid_price) if snapshot.latest_quote.bid_price else None,
                        "ask_size": snapshot.latest_quote.ask_size,
                        "bid_size": snapshot.latest_quote.bid_size
                    }
                
                # Add minute bar
                if snapshot.minute_bar:
                    result["minute_bar"] = {
                        "open": float(snapshot.minute_bar.open),
                        "high": float(snapshot.minute_bar.high),
                        "low": float(snapshot.minute_bar.low),
                        "close": float(snapshot.minute_bar.close),
                        "volume": snapshot.minute_bar.volume,
                        "timestamp": snapshot.minute_bar.timestamp.isoformat()
                    }
                
                # Add daily bar
                if snapshot.daily_bar:
                    result["daily_bar"] = {
                        "open": float(snapshot.daily_bar.open),
                        "high": float(snapshot.daily_bar.high),
                        "low": float(snapshot.daily_bar.low),
                        "close": float(snapshot.daily_bar.close),
                        "volume": snapshot.daily_bar.volume,
                        "timestamp": snapshot.daily_bar.timestamp.isoformat()
                    }
                
                # Add previous daily bar
                if snapshot.previous_daily_bar:
                    result["previous_daily_bar"] = {
                        "open": float(snapshot.previous_daily_bar.open),
                        "high": float(snapshot.previous_daily_bar.high),
                        "low": float(snapshot.previous_daily_bar.low),
                        "close": float(snapshot.previous_daily_bar.close),
                        "volume": snapshot.previous_daily_bar.volume,
                        "timestamp": snapshot.previous_daily_bar.timestamp.isoformat()
                    }
                
                return result
            
            return {"error": f"No snapshot data for {symbol}"}
        except Exception as e:
            logger.error(f"Error fetching snapshot for {symbol}: {e}")
            return {"error": str(e)}
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions."""
        try:
            positions = self.trading_client.get_all_positions()
            return [
                {
                    "symbol": pos.symbol,
                    "qty": float(pos.qty),
                    "avg_entry_price": float(pos.avg_entry_price),
                    "market_value": float(pos.market_value),
                    "cost_basis": float(pos.cost_basis),
                    "unrealized_pl": float(pos.unrealized_pl),
                    "unrealized_plpc": float(pos.unrealized_plpc),
                    "current_price": float(pos.current_price) if pos.current_price else None,
                    "side": pos.side
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    async def get_orders(self, status: str = "all", limit: int = 50) -> List[Dict[str, Any]]:
        """Get orders with specified status."""
        try:
            status_map = {
                "all": QueryOrderStatus.ALL,
                "open": QueryOrderStatus.OPEN,
                "closed": QueryOrderStatus.CLOSED
            }
            
            request = GetOrdersRequest(
                status=status_map.get(status.lower(), QueryOrderStatus.ALL),
                limit=limit
            )
            
            orders = self.trading_client.get_orders(request)
            
            return [
                {
                    "id": order.id,
                    "symbol": order.symbol,
                    "qty": float(order.qty) if order.qty else None,
                    "notional": float(order.notional) if order.notional else None,
                    "side": order.side,
                    "type": order.type,
                    "time_in_force": order.time_in_force,
                    "limit_price": float(order.limit_price) if order.limit_price else None,
                    "stop_price": float(order.stop_price) if order.stop_price else None,
                    "status": order.status,
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                    "filled_qty": float(order.filled_qty) if order.filled_qty else None,
                    "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None
                }
                for order in orders
            ]
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []
    
    async def search_assets(self, query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """Search for assets (stocks) that match the query string."""
        try:
            # Create search request
            search_params = GetAssetsRequest(
                asset_class=AssetClass.US_EQUITY,
                status=AssetStatus.ACTIVE
            )
            
            # Get all active US equity assets
            assets = self.trading_client.get_all_assets(search_params)
            
            # Filter by query if provided
            if query:
                query_lower = query.lower().strip()
                filtered_assets = []
                
                for asset in assets:
                    # Search in symbol and name
                    symbol_match = query_lower in asset.symbol.lower()
                    name_match = asset.name and query_lower in asset.name.lower()
                    
                    if symbol_match or name_match:
                        filtered_assets.append(asset)
                
                # Sort by relevance - exact symbol matches first
                filtered_assets.sort(key=lambda x: (
                    x.symbol.lower() != query_lower,  # Exact symbol match first
                    not x.symbol.lower().startswith(query_lower),  # Symbol starts with query second
                    x.symbol  # Alphabetical for the rest
                ))
                
                assets = filtered_assets[:limit]
            else:
                # If no query, just return first N assets
                assets = list(assets)[:limit]
            
            # Format results
            results = []
            for asset in assets:
                results.append({
                    "symbol": asset.symbol,
                    "name": asset.name or asset.symbol,
                    "exchange": asset.exchange.value if asset.exchange else "UNKNOWN",
                    "asset_class": asset.asset_class.value if asset.asset_class else "us_equity",
                    "tradable": asset.tradable,
                    "status": asset.status.value if asset.status else "active"
                })
            
            logger.info(f"Found {len(results)} assets for query '{query}'")
            return results

        except Exception as e:
            logger.error(f"Error searching assets with query '{query}': {e}")
            return []

    async def search_crypto_assets(self, query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """Search for crypto assets that match the query string."""
        try:
            # Create search request for crypto assets
            search_params = GetAssetsRequest(
                asset_class=AssetClass.CRYPTO,
                status=AssetStatus.ACTIVE
            )

            # Get all active crypto assets
            assets = self.trading_client.get_all_assets(search_params)

            # Filter by query if provided
            if query:
                query_lower = query.lower().strip()
                filtered_assets = []

                for asset in assets:
                    # Search in symbol (e.g., "BTC/USD")
                    symbol_match = query_lower in asset.symbol.lower()
                    # Extract base currency (BTC from "BTC/USD")
                    base_currency = asset.symbol.split('/')[0].lower() if '/' in asset.symbol else asset.symbol.lower()
                    base_match = query_lower in base_currency

                    if symbol_match or base_match:
                        filtered_assets.append(asset)

                # Sort by relevance - exact base currency match first
                filtered_assets.sort(key=lambda x: (
                    x.symbol.split('/')[0].lower() != query_lower,  # Exact base currency match first
                    not x.symbol.lower().startswith(query_lower),  # Symbol starts with query second
                    x.symbol  # Alphabetical for the rest
                ))

                assets = filtered_assets[:limit]
            else:
                # If no query, return first N assets
                assets = list(assets)[:limit]

            # Format results
            results = []
            for asset in assets:
                results.append({
                    "symbol": asset.symbol,
                    "name": asset.name or asset.symbol,
                    "exchange": asset.exchange.value if asset.exchange else "CRYPTO",
                    "asset_class": "crypto",
                    "tradable": asset.tradable,
                    "status": asset.status.value if asset.status else "active",
                    "source": "alpaca"
                })

            logger.info(f"Found {len(results)} crypto assets for query '{query}'")
            return results

        except Exception as e:
            logger.error(f"Error searching crypto assets with query '{query}': {e}")
            return []

    async def get_crypto_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest crypto quote (bid/ask)."""
        try:
            request = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = self.crypto_client.get_crypto_latest_quote(request)

            if symbol in quotes:
                quote = quotes[symbol]
                return {
                    "symbol": symbol,
                    "bid_price": float(quote.bid_price),
                    "ask_price": float(quote.ask_price),
                    "bid_size": float(quote.bid_size),
                    "ask_size": float(quote.ask_size),
                    "timestamp": quote.timestamp.isoformat(),
                    "data_source": "alpaca_crypto"
                }
            else:
                logger.warning(f"No crypto quote found for {symbol}")
                return None

        except Exception as e:
            logger.error(f"Error getting crypto quote for {symbol}: {e}")
            return None

    async def get_market_status(self) -> Dict[str, Any]:
        """Check if market is open."""
        try:
            clock = self.trading_client.get_clock()
            return {
                "is_open": clock.is_open,
                "next_open": clock.next_open.isoformat() if clock.next_open else None,
                "next_close": clock.next_close.isoformat() if clock.next_close else None,
                "timestamp": clock.timestamp.isoformat() if clock.timestamp else None
            }
        except Exception as e:
            logger.error(f"Error fetching market status: {e}")
            return {"error": str(e)}


# Singleton instance
_alpaca_service: Optional[AlpacaService] = None


def get_alpaca_service() -> Optional[AlpacaService]:
    """Get or create the singleton Alpaca service instance.
    
    Returns None if Alpaca credentials are missing or service initialization fails.
    """
    global _alpaca_service
    
    if _alpaca_service is None:
        try:
            _alpaca_service = AlpacaService()
            if not _alpaca_service.is_available:
                logger.warning("Alpaca service is not available - credentials missing or initialization failed")
                return None
        except Exception as e:
            logger.error(f"Failed to create Alpaca service: {e}")
            return None
    
    # Check if rate limit is exceeded
    if _alpaca_service and not _alpaca_service._check_rate_limit():
        logger.warning("Alpaca rate limit exceeded - returning None to trigger fallback")
        return None
    
    return _alpaca_service