"""
Market Service Factory
======================
Hybrid factory that intelligently routes between Direct API and MCP services.
- Direct API Mode (Production): Fast Yahoo Finance HTTP calls, sub-second responses
- MCP Mode (Development): Full MCP capabilities, AI tooling benefits
"""

import logging
import os
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


class MarketServiceFactory:
    """
    Hybrid factory that intelligently routes between Direct API and MCP services.
    Routes based on USE_MCP environment variable for optimal performance.
    """
    
    _instance = None
    _service_mode = None
    
    @classmethod
    def get_service(cls, force_refresh: bool = False):
        """
        Get the appropriate market service based on environment.
        
        Args:
            force_refresh: Force creation of new instance
            
        Returns:
            DirectMarketDataService (fast) or MarketServiceWrapper (MCP)
        """
        if cls._instance is None or force_refresh:
            use_mcp = os.getenv('USE_MCP', 'true').lower() == 'true'
            
            if use_mcp:
                logger.info("Initializing MCP-based market service (Development Mode)")
                cls._instance = MarketServiceWrapper()
                cls._service_mode = "MCP (Yahoo Finance + CNBC)"
            else:
                logger.info("Initializing Direct API market service (Production Mode)")
                try:
                    from .direct_market_service import DirectMarketDataService
                    cls._instance = DirectMarketDataService()
                    cls._service_mode = "Direct (Yahoo Finance)"
                    logger.info("DirectMarketDataService initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize DirectMarketDataService: {e}")
                    logger.info("Falling back to MCP service")
                    cls._instance = MarketServiceWrapper()
                    cls._service_mode = "MCP (Yahoo Finance + CNBC) - Fallback"
        
        return cls._instance
    
    @classmethod
    async def initialize_service(cls):
        """
        Initialize and warm up the appropriate service.
        Should be called during app startup.
        """
        try:
            service = cls.get_service()
            logger.info(f"Attempting to warm up service in {cls._service_mode} mode...")
            await service.warm_up()
            logger.info(f"Market service initialized successfully in {cls._service_mode} mode")
            return service
        except Exception as e:
            logger.error(f"Failed to initialize market service in {cls._service_mode} mode: {e}")
            raise  # Re-raise to handle in startup event
    
    @classmethod
    def get_service_mode(cls) -> str:
        """
        Get the current service mode for health checks.
        """
        if cls._service_mode is None:
            use_mcp = os.getenv('USE_MCP', 'true').lower() == 'true'
            cls._service_mode = "MCP (Yahoo Finance + CNBC)" if use_mcp else "Direct (Yahoo Finance)"
        
        return cls._service_mode