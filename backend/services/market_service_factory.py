"""
Market Service Factory
======================
Hybrid factory that provides BOTH Direct API and MCP services for optimal performance.
- Direct API: Fast Yahoo Finance HTTP calls for price/history queries
- MCP: Comprehensive news from CNBC + Yahoo, Alpaca data support
"""

import logging
import os
from typing import Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class MarketServiceWrapper:
    """
    Simple wrapper around the original market_service.py functions.
    Provides a consistent interface for the factory pattern.
    Includes intelligent crypto symbol detection.
    """
    
    # Popular cryptocurrency symbols that users expect to map to -USD pairs
    CRYPTO_SYMBOLS = {
        'BTC': 'BTC-USD',    # Bitcoin
        'ETH': 'ETH-USD',    # Ethereum
        'ADA': 'ADA-USD',    # Cardano
        'DOT': 'DOT-USD',    # Polkadot
        'SOL': 'SOL-USD',    # Solana
        'MATIC': 'MATIC-USD', # Polygon
        'AVAX': 'AVAX-USD',  # Avalanche
        'LTC': 'LTC-USD',    # Litecoin
        'XRP': 'XRP-USD',    # Ripple
        'DOGE': 'DOGE-USD',  # Dogecoin
        'SHIB': 'SHIB-USD',  # Shiba Inu
        'UNI': 'UNI-USD',    # Uniswap
        'LINK': 'LINK-USD',  # Chainlink
        'BCH': 'BCH-USD',    # Bitcoin Cash
        'XLM': 'XLM-USD',    # Stellar
    }
    
    def _map_crypto_symbol(self, symbol: str) -> tuple[str, str]:
        """
        Map crypto symbols to their -USD pairs for accurate pricing.
        
        Returns:
            tuple: (mapped_symbol, asset_type)
        """
        upper_symbol = symbol.upper()
        
        # If already in crypto format, keep as is
        if '-USD' in upper_symbol:
            return upper_symbol, 'crypto'
        
        # Check if it's a known crypto that should map to -USD
        if upper_symbol in self.CRYPTO_SYMBOLS:
            mapped_symbol = self.CRYPTO_SYMBOLS[upper_symbol]
            logger.info(f"Mapping crypto symbol {symbol} -> {mapped_symbol}")
            return mapped_symbol, 'crypto'
        
        # Not a crypto, treat as stock
        return upper_symbol, 'stock'
    
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
        """Get stock price - includes crypto symbol mapping and intelligent routing."""
        
        # Map crypto symbols to proper format
        mapped_symbol, asset_type = self._map_crypto_symbol(symbol)
        
        # Try Alpaca first for real-time quotes (professional-grade) - but only for stocks
        if asset_type == 'stock':
            try:
                # Check if we can use Alpaca
                from services.market_service import get_quote_from_alpaca, ALPACA_AVAILABLE
                
                if ALPACA_AVAILABLE:
                    logger.info(f"Using Alpaca for {mapped_symbol} quote")
                    quote = await get_quote_from_alpaca(mapped_symbol)
                    quote["data_source"] = "alpaca"
                    quote["asset_type"] = asset_type
                    return quote
            except Exception as e:
                logger.warning(f"Alpaca quote failed: {e}, falling back to Yahoo Finance")
        
        # Use Yahoo Finance (supports both stocks and crypto)
        logger.info(f"Using Yahoo Finance for {mapped_symbol} quote (asset_type: {asset_type})")
        quote = await self._get_quote(mapped_symbol)
        
        # Normalize field names from MCP format to Direct format
        # MCP returns: last, prev_close, change_pct
        # Direct/endpoint expects: price, previous_close, change_percent
        if "last" in quote and "price" not in quote:
            quote["price"] = quote["last"]
        if "prev_close" in quote and "previous_close" not in quote:
            quote["previous_close"] = quote["prev_close"]
        if "change_pct" in quote and "change_percent" not in quote:
            quote["change_percent"] = quote["change_pct"]
        
        quote["data_source"] = "yahoo_mcp"
        quote["asset_type"] = asset_type
        
        # If we mapped a crypto symbol, update the response to show original symbol
        if mapped_symbol != symbol.upper():
            quote["original_symbol"] = symbol.upper()
            quote["mapped_from"] = f"{symbol.upper()} -> {mapped_symbol}"
        
        return quote
    
    async def get_stock_history(self, symbol: str, days: int = 50) -> dict:
        """Get stock history - includes crypto symbol mapping and intelligent routing."""
        
        # Map crypto symbols to proper format
        mapped_symbol, asset_type = self._map_crypto_symbol(symbol)
        
        # Try Alpaca first for chart data (professional-grade) - but only for stocks
        if asset_type == 'stock':
            try:
                # Check if we can use Alpaca
                from services.market_service import get_ohlcv_from_alpaca, ALPACA_AVAILABLE
                
                if ALPACA_AVAILABLE:
                    logger.info(f"Using Alpaca for {mapped_symbol} chart data")
                    candles = await get_ohlcv_from_alpaca(mapped_symbol, days)
                    
                    return {
                        "symbol": symbol.upper(),
                        "candles": candles,
                        "period": f"{days}D",
                        "data_source": "alpaca",
                        "asset_type": asset_type
                    }
            except Exception as e:
                logger.warning(f"Alpaca chart data failed: {e}, falling back to Yahoo Finance")
        
        # Use Yahoo Finance (supports both stocks and crypto)
        logger.info(f"Using Yahoo Finance for {mapped_symbol} chart data (asset_type: {asset_type})")
        
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
        
        candles = await self._get_ohlcv(mapped_symbol, range_str)
        result = {
            "symbol": symbol.upper(),
            "candles": candles,
            "period": range_str,
            "data_source": "yahoo_mcp",
            "asset_type": asset_type
        }
        
        # If we mapped a crypto symbol, include mapping info
        if mapped_symbol != symbol.upper():
            result["original_symbol"] = symbol.upper()
            result["mapped_from"] = f"{symbol.upper()} -> {mapped_symbol}"
        
        return result
    
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
            # Get quote and history - request 6M for enough data for advanced TA (200+ candles)
            quote = await self._get_quote(symbol)
            candles = await self._get_ohlcv(symbol, "6M")  # Get 6 months for advanced TA
            
            # Calculate technical levels with advanced TA or fallback
            technical_levels = await self._calculate_technical_levels(symbol, candles, quote)
            
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
    
    async def _calculate_technical_levels(self, symbol: str, candles: list, quote: dict) -> dict:
        """
        Calculate technical levels with advanced TA module or fallback to simple calculations.
        Implements Day 3.1 of integration plan.
        """
        import asyncio
        import sys
        import os
        
        # Add parent directory to path to import advanced_technical_analysis
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            # Try to use advanced technical analysis with timeout
            from advanced_technical_analysis import AdvancedTechnicalAnalysis
            
            # Extract price and volume data for advanced TA
            prices = [c.get('close', c.get('c', 0)) for c in candles[-200:]]  # Last 200 candles
            volumes = [c.get('volume', c.get('v', 0)) for c in candles[-200:]]  # Last 200 volumes
            current_price = quote.get('price', quote.get('last', 0))
            
            # Check if we have enough data
            if len(prices) >= 50 and current_price > 0:
                # Apply 3-second timeout for advanced calculations
                async def calculate_with_timeout():
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        None,
                        AdvancedTechnicalAnalysis.calculate_advanced_levels,
                        prices,
                        volumes,
                        current_price
                    )
                
                try:
                    result = await asyncio.wait_for(calculate_with_timeout(), timeout=3.0)
                    
                    # Ensure consistent field names (sell_high_level, buy_low_level, btd_level, retest_level)
                    return {
                        "sell_high_level": result.get("sell_high_level", current_price * 1.03),
                        "buy_low_level": result.get("buy_low_level", current_price * 0.96),
                        "btd_level": result.get("btd_level", current_price * 0.92),
                        "retest_level": result.get("retest_level", current_price * 0.98),
                        "ma_20": result.get("ma_20", current_price * 0.99),
                        "ma_50": result.get("ma_50", current_price * 0.97),
                        "ma_200": result.get("ma_200", current_price * 0.93),
                        "recent_high": result.get("recent_high", current_price * 1.05),
                        "recent_low": result.get("recent_low", current_price * 0.95),
                        "fib_levels": result.get("fib_levels", {}),
                        "volume_profile": result.get("volume_profile"),
                        "calculation_method": "advanced"
                    }
                except asyncio.TimeoutError:
                    logger.warning(f"Advanced TA calculation timed out for {symbol}, using fallback")
            else:
                logger.info(f"Insufficient data for advanced TA on {symbol} (only {len(prices)} candles)")
        
        except ImportError as e:
            logger.warning(f"Advanced TA module not available: {e}")
        except Exception as e:
            logger.error(f"Error in advanced TA calculation: {e}")
        
        # Fallback to simple calculations (original inline logic)
        current_price = quote.get('price', quote.get('last', 0))
        
        if current_price > 0:
            # Simple percentage-based levels
            return {
                "sell_high_level": round(current_price * 1.03, 2),  # 3% above for sell high
                "buy_low_level": round(current_price * 0.96, 2),  # 4% below for buy low
                "btd_level": round(current_price * 0.92, 2), # 8% below for buy the dip
                "retest_level": round(current_price * 0.98, 2), # 2% below for retest
                "ma_20": round(current_price * 0.99, 2),
                "ma_50": round(current_price * 0.97, 2),
                "ma_200": round(current_price * 0.93, 2),
                "recent_high": round(current_price * 1.05, 2),
                "recent_low": round(current_price * 0.95, 2),
                "fib_levels": {},
                "volume_profile": None,
                "calculation_method": "simple"
            }
        else:
            # No price data available
            return {
                "sell_high_level": 0,
                "buy_low_level": 0,
                "btd_level": 0,
                "retest_level": 0,
                "ma_20": 0,
                "ma_50": 0,
                "ma_200": 0,
                "recent_high": 0,
                "recent_low": 0,
                "fib_levels": {},
                "volume_profile": None,
                "calculation_method": "none"
            }
    
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


class HybridMarketService:
    """
    Hybrid service that intelligently uses BOTH Direct and MCP services.
    - Direct API for fast price/history queries
    - MCP for comprehensive news (CNBC + Yahoo)
    - Best of both worlds: speed AND comprehensive data
    """
    
    def __init__(self):
        self.direct_service = None
        self.mcp_service = None
        self.direct_available = False
        self.mcp_available = False
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize both services, allowing graceful degradation if one fails."""
        # Initialize Direct service
        try:
            from .direct_market_service import DirectMarketDataService
            self.direct_service = DirectMarketDataService()
            self.direct_available = True
            logger.info("Direct market service initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Direct service: {e}")
            self.direct_available = False
        
        # Initialize MCP service
        try:
            self.mcp_service = MarketServiceWrapper()
            self.mcp_available = True
            logger.info("MCP market service initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize MCP service: {e}")
            self.mcp_available = False
        
        if not self.direct_available and not self.mcp_available:
            raise RuntimeError("Failed to initialize any market service")
    
    async def get_stock_price(self, symbol: str) -> dict:
        """Get stock price - prefer MCP/Alpaca for accurate data, fallback to Direct."""
        # Try MCP/Alpaca first (has better data quality including open price)
        if self.mcp_available:
            try:
                result = await self.mcp_service.get_stock_price(symbol)
                logger.info(f"Stock price fetched via {result.get('data_source', 'MCP')}")
                return result
            except Exception as e:
                logger.warning(f"MCP/Alpaca price fetch failed: {e}")
                if self.direct_available:
                    return await self.direct_service.get_stock_price(symbol)
                raise
        elif self.direct_available:
            return await self.direct_service.get_stock_price(symbol)
        else:
            raise RuntimeError("No market service available")
    
    async def get_stock_history(self, symbol: str, days: int = 50) -> dict:
        """Get stock history - prefer MCP/Alpaca for accurate data, fallback to Direct."""
        # Try MCP/Alpaca first (has better data quality)
        if self.mcp_available:
            try:
                result = await self.mcp_service.get_stock_history(symbol, days)
                logger.info(f"Stock history fetched via {result.get('data_source', 'MCP')}")
                return result
            except Exception as e:
                logger.warning(f"MCP/Alpaca history fetch failed: {e}")
                if self.direct_available:
                    return await self.direct_service.get_stock_history(symbol, days)
                raise
        elif self.direct_available:
            return await self.direct_service.get_stock_history(symbol, days)
        else:
            raise RuntimeError("No market service available")
    
    async def get_stock_news(self, symbol: str, limit: int = 10) -> dict:
        """Get stock news - prefer MCP for CNBC + Yahoo, fallback to Direct."""
        if self.mcp_available:
            try:
                return await self.mcp_service.get_stock_news(symbol, limit)
            except Exception as e:
                logger.warning(f"MCP news fetch failed: {e}")
                if self.direct_available:
                    return await self.direct_service.get_stock_news(symbol, limit)
                raise
        elif self.direct_available:
            return await self.direct_service.get_stock_news(symbol, limit)
        else:
            raise RuntimeError("No market service available")
    
    async def get_comprehensive_stock_data(self, symbol: str) -> dict:
        """Get comprehensive data - prefer MCP/Alpaca for accurate data, fallback to Direct."""
        results = {}
        
        # Try MCP/Alpaca first (has complete data including open price and year high/low)
        if self.mcp_available:
            try:
                data = await self.mcp_service.get_comprehensive_stock_data(symbol)
                results = data
                logger.info(f"Comprehensive data fetched via {data.get('data_source', 'MCP')}")
            except Exception as e:
                logger.warning(f"MCP/Alpaca comprehensive data failed: {e}")
                if self.direct_available:
                    data = await self.direct_service.get_comprehensive_stock_data(symbol)
                    results = data
        elif self.direct_available:
            data = await self.mcp_service.get_comprehensive_stock_data(symbol)
            results = data
        
        # Try to enhance with MCP news if available and not already included
        if self.mcp_available and "news" not in results:
            try:
                news_data = await self.mcp_service.get_stock_news(symbol, 5)
                results["news"] = news_data.get("articles", [])
            except Exception as e:
                logger.warning(f"Failed to add MCP news to comprehensive data: {e}")
        
        return results
    
    async def get_market_overview(self) -> dict:
        """Get market overview - delegate to MCP service which has Alpaca-first implementation."""
        if self.mcp_available:
            try:
                return await self.mcp_service.get_market_overview()
            except Exception as e:
                logger.error(f"MCP market overview failed: {e}")
                raise
        else:
            raise RuntimeError("Market overview not available - MCP service required")
    
    async def search_assets(self, query: str, limit: int = 20) -> list:
        """Search for stock symbols using Alpaca API with fallback to MCP."""
        # First try Alpaca via the market service's search function
        try:
            from services.market_service import search_assets_with_alpaca, ALPACA_AVAILABLE
            
            if ALPACA_AVAILABLE:
                logger.info(f"Using Alpaca for symbol search: '{query}'")
                results = await search_assets_with_alpaca(query, limit)
                return results
        except Exception as e:
            logger.warning(f"Alpaca symbol search failed: {e}, falling back to MCP")
        
        # If MCP service is available, try it as fallback (though it may not have search_assets)
        if self.mcp_available and hasattr(self.mcp_service, 'search_assets'):
            try:
                return await self.mcp_service.search_assets(query, limit)
            except Exception as e:
                logger.warning(f"MCP symbol search failed: {e}")
        
        # If neither works, return empty results
        logger.warning(f"No symbol search service available for query: '{query}'")
        return []
    
    async def warm_up(self):
        """Warm up both services, don't fail if one doesn't work."""
        tasks = []
        
        if self.direct_available and self.direct_service:
            tasks.append(self._warm_up_direct())
        
        if self.mcp_available and self.mcp_service:
            tasks.append(self._warm_up_mcp())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"Hybrid service warm-up complete - Direct: {self.direct_available}, MCP: {self.mcp_available}")
    
    async def _warm_up_direct(self):
        """Warm up Direct service."""
        try:
            await self.direct_service.warm_up()
        except Exception as e:
            logger.warning(f"Direct service warm-up failed: {e}")
    
    async def _warm_up_mcp(self):
        """Warm up MCP service."""
        try:
            await self.mcp_service.warm_up()
        except Exception as e:
            logger.warning(f"MCP service warm-up failed: {e}")
    
    def get_service_status(self) -> dict:
        """Get status of both services for health checks."""
        return {
            "direct": "operational" if self.direct_available else "unavailable",
            "mcp": "operational" if self.mcp_available else "unavailable",
            "mode": "hybrid"
        }


class MarketServiceFactory:
    """
    Factory that provides the HybridMarketService with BOTH Direct and MCP capabilities.
    No more either/or - we use both services intelligently!
    """
    
    _instance = None
    _service_mode = None
    
    @classmethod
    def get_service(cls, force_refresh: bool = False):
        """
        Get the hybrid market service that uses both Direct and MCP.
        
        Args:
            force_refresh: Force creation of new instance
            
        Returns:
            HybridMarketService with both Direct and MCP capabilities
        """
        if cls._instance is None or force_refresh:
            logger.info("Initializing Hybrid market service with both Direct and MCP capabilities")
            cls._instance = HybridMarketService()
            cls._service_mode = "Hybrid (Direct + MCP)"
        
        return cls._instance
    
    @classmethod
    async def initialize_service(cls):
        """
        Initialize and warm up the appropriate service.
        Should be called during app startup.
        """
        service = cls.get_service()
        logger.info(f"Attempting to warm up service in {cls._service_mode} mode...")
        
        try:
            await service.warm_up()
            logger.info(f"Market service initialized and warmed up successfully in {cls._service_mode} mode")
        except Exception as e:
            logger.warning(f"Market service warm-up failed in {cls._service_mode} mode: {e}")
            logger.info("Market service initialized but warm-up failed - service may have cold start")
        
        return service
    
    @classmethod
    def get_service_mode(cls) -> str:
        """
        Get the current service mode for health checks.
        """
        if cls._service_mode is None:
            cls._service_mode = "Hybrid (Direct + MCP)"
        
        return cls._service_mode
    
    @classmethod
    def get_service_status(cls) -> dict:
        """
        Get detailed status of both services.
        """
        if cls._instance and hasattr(cls._instance, 'get_service_status'):
            return cls._instance.get_service_status()
        return {
            "direct": "unknown",
            "mcp": "unknown",
            "mode": "not_initialized"
        }