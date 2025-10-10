"""
Simplified Market Data Handler for Voice Trading Assistant
Extracted from agent_orchestrator.py for cleaner architecture
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MarketDataHandler:
    """Handles market data requests and formatting."""
    
    def __init__(self, market_service=None):
        """
        Initialize market data handler.
        
        Args:
            market_service: Market service instance for data fetching
        """
        self.market_service = market_service
    
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock price for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Price data dictionary
        """
        if not self.market_service:
            return {"error": "Market service not available"}
        
        try:
            price_data = await self.market_service.get_stock_price(symbol)
            return self._format_price_data(symbol, price_data)
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return {"error": f"Failed to fetch price for {symbol}"}
    
    async def get_stock_news(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get news for a stock symbol.
        
        Args:
            symbol: Stock ticker symbol
            limit: Number of news items to return
            
        Returns:
            List of news items
        """
        if not self.market_service:
            return []
        
        try:
            news = await self.market_service.get_stock_news(symbol)
            return news[:limit] if news else []
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """
        Get market overview including major indices.
        
        Returns:
            Market overview data
        """
        if not self.market_service:
            return {"error": "Market service not available"}
        
        try:
            return await self.market_service.get_market_overview()
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return {"error": "Failed to fetch market overview"}
    
    async def get_stock_history(
        self, 
        symbol: str, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get historical data for a stock.
        
        Args:
            symbol: Stock ticker symbol
            days: Number of days of history
            
        Returns:
            List of historical data points
        """
        if not self.market_service:
            return []
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            history = await self.market_service.get_stock_history(
                symbol=symbol,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            return history if history else []
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            return []
    
    def _format_price_data(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format price data for consistent output.
        
        Args:
            symbol: Stock symbol
            data: Raw price data
            
        Returns:
            Formatted price data
        """
        if not data:
            return {"symbol": symbol, "error": "No data available"}
        
        return {
            "symbol": symbol,
            "price": data.get("current_price", 0),
            "change": data.get("change", 0),
            "change_percent": data.get("change_percent", 0),
            "volume": data.get("volume", 0),
            "market_cap": data.get("market_cap", 0),
            "high": data.get("high", 0),
            "low": data.get("low", 0),
            "open": data.get("open", 0),
            "previous_close": data.get("previous_close", 0),
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }
    
    def format_price_response(self, symbol: str, price_data: Dict[str, Any]) -> str:
        """
        Format price data as human-readable text.
        
        Args:
            symbol: Stock symbol
            price_data: Price data dictionary
            
        Returns:
            Formatted text response
        """
        if "error" in price_data:
            return f"Unable to fetch price for {symbol}"
        
        price = price_data.get("price", 0)
        change = price_data.get("change", 0)
        change_pct = price_data.get("change_percent", 0)
        
        direction = "up" if change > 0 else "down" if change < 0 else "unchanged"
        
        return (
            f"{symbol} is trading at ${price:.2f}, "
            f"{direction} ${abs(change):.2f} ({abs(change_pct):.2f}%) today"
        )
    
    def format_news_response(self, symbol: str, news_items: List[Dict[str, Any]]) -> str:
        """
        Format news items as human-readable text.
        
        Args:
            symbol: Stock symbol
            news_items: List of news items
            
        Returns:
            Formatted text response
        """
        if not news_items:
            return f"No recent news found for {symbol}"
        
        response = f"Latest news for {symbol}:\n"
        for i, item in enumerate(news_items[:3], 1):
            title = item.get("title", "")
            source = item.get("source", "")
            response += f"{i}. {title}"
            if source:
                response += f" ({source})"
            response += "\n"
        
        return response.strip()


# Export main class
__all__ = ['MarketDataHandler']