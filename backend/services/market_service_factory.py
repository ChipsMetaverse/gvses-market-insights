"""
Market Service Factory
======================
Simple factory that returns the MCP-based market service.
MCP handles all data sources (Yahoo Finance, CNBC, etc).
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MarketServiceWrapper:
    """
    Simple wrapper around the original market_service.py functions.
    Provides a consistent interface for the factory pattern.
    """
    
    def __init__(self):
        # Import the original MCP-based functions
        from services.market_service import (
            get_quote,
            get_ohlcv,
            humanize_market_cap,
            build_summary_table
        )
        from services.news_service import get_related_news
        
        # Store references to the functions
        self._get_quote = get_quote
        self._get_ohlcv = get_ohlcv
        self._get_news = get_related_news
        self.humanize_market_cap = humanize_market_cap
        self.build_summary_table = build_summary_table
    
    async def get_stock_price(self, symbol: str) -> dict:
        """Get stock price - uses Alpaca for quotes, Yahoo for fallback."""
        
        # Try Alpaca first for real-time quotes (professional-grade)
        try:
            # Check if we can use Alpaca
            from services.market_service import get_quote_from_alpaca, ALPACA_AVAILABLE
            
            if ALPACA_AVAILABLE:
                logger.info(f"Using Alpaca for {symbol} quote")
                quote = await get_quote_from_alpaca(symbol)
                quote["data_source"] = "alpaca"
                return quote
        except Exception as e:
            logger.warning(f"Alpaca quote failed: {e}, falling back to Yahoo Finance")
        
        # Fallback to Yahoo Finance via MCP
        logger.info(f"Using Yahoo Finance for {symbol} quote")
        quote = await self._get_quote(symbol)
        quote["data_source"] = "yahoo_mcp"
        return quote
    
    async def get_stock_history(self, symbol: str, days: int = 50) -> dict:
        """Get stock history - uses Alpaca for chart data, Yahoo for fallback."""
        
        # Try Alpaca first for chart data (professional-grade)
        try:
            # Check if we can use Alpaca
            from services.market_service import get_ohlcv_from_alpaca, ALPACA_AVAILABLE
            
            if ALPACA_AVAILABLE:
                logger.info(f"Using Alpaca for {symbol} chart data")
                candles = await get_ohlcv_from_alpaca(symbol, days)
                
                return {
                    "symbol": symbol.upper(),
                    "candles": candles,
                    "period": f"{days}D",
                    "data_source": "alpaca"
                }
        except Exception as e:
            logger.warning(f"Alpaca chart data failed: {e}, falling back to Yahoo Finance")
        
        # Fallback to Yahoo Finance via MCP
        logger.info(f"Using Yahoo Finance for {symbol} chart data")
        
        # Map days to range string for Yahoo
        if days <= 1:
            range_str = "1D"
        elif days <= 5:
            range_str = "5D" 
        elif days <= 30:
            range_str = "1M"
        elif days <= 90:
            range_str = "3M"
        elif days <= 180:
            range_str = "6M"
        elif days <= 365:
            range_str = "1Y"
        else:
            range_str = "5Y"
        
        candles = await self._get_ohlcv(symbol, range_str)
        return {
            "symbol": symbol.upper(),
            "candles": candles,
            "period": range_str,
            "data_source": "yahoo_mcp"
        }
    
    async def get_stock_news(self, symbol: str, limit: int = 10) -> dict:
        """Get stock news via MCP (includes CNBC and Yahoo)."""
        news = await self._get_news(symbol, limit)
        
        # Handle the "items" field from get_related_news
        articles = news.get("articles", news.get("news", news.get("items", [])))
        
        # Ensure consistent format
        return {
            "symbol": symbol.upper(),
            "articles": articles,
            "total": len(articles),
            "data_sources": ["Yahoo Finance", "CNBC"],  # MCP provides both
            "data_source": "mcp"
        }
    
    async def get_comprehensive_stock_data(self, symbol: str) -> dict:
        """Get comprehensive stock data via MCP."""
        try:
            # Get quote and history
            quote = await self._get_quote(symbol)
            candles = await self._get_ohlcv(symbol, "1M")
            
            # Calculate technical levels
            technical_levels = {}
            if candles and len(candles) > 0:
                recent_candles = candles[-20:]  # Last 20 days
                if recent_candles:
                    highs = [c.get('high', 0) for c in recent_candles if c.get('high')]
                    lows = [c.get('low', 0) for c in recent_candles if c.get('low')]
                    
                    if highs and lows:
                        recent_high = max(highs)
                        recent_low = min(lows)
                        
                        technical_levels = {
                            "qe_level": round(recent_high * 0.98, 2),
                            "st_level": round((recent_high + recent_low) / 2, 2),
                            "ltb_level": round(recent_low * 1.02, 2)
                        }
            
            return {
                "symbol": symbol.upper(),
                "price_data": quote,
                "technical_levels": technical_levels,
                "data_source": "mcp"
            }
        except Exception as e:
            logger.error(f"Error getting comprehensive data: {e}")
            return {
                "symbol": symbol.upper(),
                "price_data": {},
                "technical_levels": {},
                "data_source": "error",
                "error": str(e)
            }
    
    async def warm_up(self):
        """Pre-warm MCP connection."""
        try:
            logger.info("Warming up MCP-based market service...")
            await self._get_quote("SPY")
            logger.info("Market service ready")
        except Exception as e:
            logger.warning(f"Market service warm-up failed: {e}")
    
    async def get_market_overview(self) -> dict:
        """Get market overview using Alpaca ETF proxies with MCP fallback."""
        from datetime import datetime
        
        # ETF proxy symbols for market indices
        ETF_PROXIES = {
            "SPY": "sp500",    # S&P 500
            "QQQ": "nasdaq",   # NASDAQ
            "DIA": "dow",      # Dow Jones
            "VXX": "vix"       # Volatility Index
        }
        
        # Try Alpaca first for real-time ETF data
        try:
            from services.market_service import ALPACA_AVAILABLE, get_alpaca_service
            
            if ALPACA_AVAILABLE:
                logger.info("Using Alpaca for market overview (ETF proxies)")
                
                # Get Alpaca service instance
                alpaca_service = get_alpaca_service()
                
                # Fetch batch snapshots for all ETF proxies
                symbols = list(ETF_PROXIES.keys())
                snapshots = await alpaca_service.get_batch_snapshots(symbols)
                
                # Build indices data from ETF snapshots
                indices = {}
                for etf_symbol, index_name in ETF_PROXIES.items():
                    if etf_symbol in snapshots and "error" not in snapshots[etf_symbol]:
                        snapshot = snapshots[etf_symbol]
                        
                        # Get current price from latest trade
                        current_price = 0
                        if "latest_trade" in snapshot:
                            current_price = snapshot["latest_trade"]["price"]
                        elif "daily_bar" in snapshot:
                            current_price = snapshot["daily_bar"]["close"]
                        
                        # Calculate change from previous close
                        prev_close = 0
                        change = 0
                        change_percent = 0
                        
                        if "previous_daily_bar" in snapshot:
                            prev_close = snapshot["previous_daily_bar"]["close"]
                            if current_price and prev_close:
                                change = round(current_price - prev_close, 2)
                                change_percent = round((change / prev_close) * 100, 2)
                        
                        indices[index_name] = {
                            "value": current_price,
                            "change": change,
                            "change_percent": change_percent
                        }
                    else:
                        logger.warning(f"No Alpaca data for {etf_symbol}")
                
                # If we got at least some indices data, return it
                if indices:
                    # Try to get movers from MCP
                    movers = {}
                    try:
                        from mcp_client import get_mcp_client
                        client = get_mcp_client()
                        
                        if not client._initialized:
                            await client.start()
                        
                        # Get CNBC pre-market movers
                        cnbc_movers = await client.call_tool("get_cnbc_movers", {})
                        if cnbc_movers:
                            movers = cnbc_movers
                    except Exception as e:
                        logger.warning(f"Failed to get CNBC movers: {e}")
                    
                    return {
                        "indices": indices,
                        "movers": movers,
                        "data_source": "alpaca",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
        
        except Exception as e:
            logger.warning(f"Alpaca market overview failed: {e}, falling back to MCP")
        
        # Fallback to MCP market overview
        try:
            logger.info("Using MCP for market overview (Yahoo Finance)")
            from mcp_client import get_mcp_client
            client = get_mcp_client()
            
            if not client._initialized:
                await client.start()
            
            # Get comprehensive market overview from MCP
            overview = await client.call_tool("get_market_overview", {})
            
            if overview:
                overview["data_source"] = "yahoo_mcp"
                return overview
            
        except Exception as e:
            logger.error(f"MCP market overview failed: {e}")
        
        # Return error if both methods fail
        raise ValueError("Unable to fetch market overview from any source")


class MarketServiceFactory:
    """
    Simple factory for the market service.
    Always returns the MCP-based service.
    """
    
    _instance = None
    
    @classmethod
    def get_service(cls, force_refresh: bool = False):
        """
        Get the market service (MCP-based).
        
        Args:
            force_refresh: Force creation of new instance
            
        Returns:
            MarketServiceWrapper that uses MCP
        """
        if cls._instance is None or force_refresh:
            logger.info("Initializing MCP-based market service")
            cls._instance = MarketServiceWrapper()
        
        return cls._instance
    
    @classmethod
    async def initialize_service(cls):
        """
        Initialize and warm up the service.
        Should be called during app startup.
        """
        service = cls.get_service()
        await service.warm_up()
        return service
    
    @classmethod
    def get_service_mode(cls) -> str:
        """
        Get the current service mode for health checks.
        """
        return "MCP (Yahoo Finance + CNBC)"