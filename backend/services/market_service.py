import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import time
import asyncio
import logging

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from mcp_client import get_mcp_client

logger = logging.getLogger(__name__)

# Import Alpaca service for chart data
try:
    from alpaca_service import get_alpaca_service
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logger.warning("Alpaca service not available - will use Yahoo Finance for all data")


# Simple cache implementation
class MarketDataCache:
    def __init__(self, ttl: int = 5):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
        return None
    
    def set(self, key: str, value: Any):
        self.cache[key] = (value, time.time())


cache = MarketDataCache(ttl=5)


async def search_assets_with_alpaca(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search for assets using Alpaca Markets API."""
    
    if not ALPACA_AVAILABLE:
        raise ValueError("Alpaca service not available")
    
    logger.info(f"Searching Alpaca assets for query: '{query}'")
    
    try:
        # Get Alpaca service instance
        alpaca_service = get_alpaca_service()
        
        # Use the search method we just added
        results = await alpaca_service.search_assets(query, limit)
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching Alpaca assets for '{query}': {e}")
        raise


async def get_quote_from_alpaca(symbol: str) -> Dict[str, Any]:
    """Get current quote from Alpaca Markets."""
    
    if not ALPACA_AVAILABLE:
        raise ValueError("Alpaca service not available")
    
    logger.info(f"Fetching Alpaca quote for {symbol}")
    
    try:
        # Get Alpaca service instance
        alpaca_service = get_alpaca_service()
        
        # Get comprehensive snapshot for best price data
        snapshot = await alpaca_service.get_snapshot(symbol.upper())
        
        if "error" in snapshot:
            logger.error(f"Alpaca snapshot error: {snapshot['error']}")
            raise ValueError(f"Alpaca error: {snapshot['error']}")
        
        # Extract price data from snapshot
        quote = {
            "symbol": symbol.upper(),
            "company_name": symbol.upper(),  # Alpaca doesn't provide company name
            "exchange": "NASDAQ",  # Default, Alpaca doesn't specify in snapshot
            "currency": "USD",
            "is_open": True  # Will be updated if market status available
        }
        
        # Get latest trade price
        if "latest_trade" in snapshot:
            quote["last"] = snapshot["latest_trade"]["price"]
        
        # Get daily bar for OHLC
        if "daily_bar" in snapshot:
            daily = snapshot["daily_bar"]
            quote["open"] = daily.get("open", 0)
            quote["high"] = daily.get("high", 0)
            quote["low"] = daily.get("low", 0)
            quote["volume"] = daily.get("volume", 0)
            
            # Use daily close as current if no latest trade
            if "last" not in quote:
                quote["last"] = daily.get("close", 0)
        
        # Calculate change from previous day
        if "previous_daily_bar" in snapshot:
            prev_close = snapshot["previous_daily_bar"].get("close", 0)
            quote["prev_close"] = prev_close
            
            if quote.get("last") and prev_close:
                quote["change_abs"] = round(quote["last"] - prev_close, 2)
                quote["change_pct"] = round((quote["change_abs"] / prev_close) * 100, 2)
            else:
                quote["change_abs"] = 0
                quote["change_pct"] = 0
        else:
            quote["change_abs"] = 0
            quote["change_pct"] = 0
            quote["prev_close"] = quote.get("last", 0)
        
        # Add quote prices if available
        if "latest_quote" in snapshot:
            latest_quote = snapshot["latest_quote"]
            quote["ask"] = latest_quote.get("ask_price")
            quote["bid"] = latest_quote.get("bid_price")
            quote["ask_size"] = latest_quote.get("ask_size")
            quote["bid_size"] = latest_quote.get("bid_size")
        
        # Set defaults for missing fields to match Yahoo format
        quote.setdefault("avg_volume_3m", 0)
        quote.setdefault("market_cap", 0)
        quote.setdefault("pe_ttm", 0)
        quote.setdefault("dividend_yield_pct", 0)
        quote.setdefault("beta", 1.0)
        quote.setdefault("week52_high", 0)
        quote.setdefault("week52_low", 0)
        
        logger.info(f"Alpaca quote for {symbol}: ${quote.get('last', 'N/A')}")
        return quote
        
    except Exception as e:
        logger.error(f"Failed to fetch Alpaca quote for {symbol}: {e}")
        raise ValueError(f"Unable to fetch Alpaca quote: {str(e)}")


async def get_quote(symbol: str) -> Dict[str, Any]:
    """Get current quote for a symbol - REAL DATA ONLY"""
    
    # Check cache
    cached = cache.get(f"quote_{symbol}")
    if cached:
        return cached
    
    try:
        # Get real data from MCP server
        client = get_mcp_client()
        
        # Ensure client is started
        if not client._initialized:
            await client.start()
        
        result = await client.call_tool("get_stock_quote", {"symbol": symbol})
        
        if result and isinstance(result, dict):
            # Map MCP response to our format
            quote = {
                "symbol": symbol.upper(),
                "company_name": result.get("name", f"{symbol.upper()}"),
                "exchange": result.get("exchange", "NASDAQ"),
                "currency": result.get("currency", "USD"),
                "last": result.get("price", result.get("regularMarketPrice", 0)),
                "change_abs": result.get("change", 0),
                "change_pct": result.get("changePercent", 0),
                "open": result.get("open", result.get("regularMarketOpen", 0)),
                "high": result.get("dayHigh", result.get("regularMarketDayHigh", 0)),
                "low": result.get("dayLow", result.get("regularMarketDayLow", 0)),
                "prev_close": result.get("previousClose", result.get("regularMarketPreviousClose", 0)),
                "volume": result.get("volume", result.get("regularMarketVolume", 0)),
                "avg_volume_3m": result.get("averageVolume", 0),
                "market_cap": result.get("marketCap", 0),
                "pe_ttm": result.get("peRatio", result.get("trailingPE", 0)),
                "dividend_yield_pct": result.get("dividendYield", 0),
                "beta": result.get("beta", 1.0),
                "week52_high": result.get("fiftyTwoWeekHigh", result.get("yearHigh", 0)),
                "week52_low": result.get("fiftyTwoWeekLow", result.get("yearLow", 0)),
                "is_open": result.get("marketState", "REGULAR") == "REGULAR"
            }
            
            # Ensure change calculations are correct
            if quote["last"] and quote["prev_close"]:
                quote["change_abs"] = round(quote["last"] - quote["prev_close"], 2)
                quote["change_pct"] = round((quote["change_abs"] / quote["prev_close"]) * 100, 2)
            
            cache.set(f"quote_{symbol}", quote)
            return quote
        else:
            raise ValueError(f"No data received for symbol {symbol}")
            
    except Exception as e:
        logger.error(f"Failed to fetch real market data for {symbol}: {e}")
        raise ValueError(f"Unable to fetch real market data for {symbol}. Please check the symbol and try again.")


async def get_ohlcv_from_alpaca(symbol: str, days: int) -> List[Dict[str, Any]]:
    """Get OHLCV data from Alpaca Markets for chart display."""
    
    if not ALPACA_AVAILABLE:
        raise ValueError("Alpaca service not available")
    
    logger.info(f"Fetching Alpaca OHLCV data for {symbol} - {days} days")
    
    try:
        # Get Alpaca service instance
        alpaca_service = get_alpaca_service()
        
        # Determine timeframe based on days
        if days <= 1:
            timeframe = "15Min"  # Intraday data
        elif days <= 7:
            timeframe = "1Hour"  # Hourly for a week
        else:
            timeframe = "1Day"  # Daily for longer periods
        
        # Fetch bars from Alpaca
        result = await alpaca_service.get_stock_bars(
            symbol=symbol.upper(),
            timeframe=timeframe,
            days_back=days,
            limit=None  # Get all available data
        )
        
        if "error" in result:
            logger.error(f"Alpaca error: {result['error']}")
            raise ValueError(f"Alpaca error: {result['error']}")
        
        # Convert Alpaca format to chart format
        candles = []
        if "bars" in result:
            for bar in result["bars"]:
                # Convert ISO timestamp to Unix timestamp
                from datetime import datetime
                timestamp_str = bar.get("timestamp", "")
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    unix_timestamp = int(dt.timestamp())
                except:
                    unix_timestamp = 0
                
                candles.append({
                    "time": unix_timestamp,
                    "open": bar.get("open", 0),
                    "high": bar.get("high", 0),
                    "low": bar.get("low", 0),
                    "close": bar.get("close", 0),
                    "volume": bar.get("volume", 0)
                })
        
        logger.info(f"Alpaca returned {len(candles)} candles for {symbol}")
        return candles
        
    except Exception as e:
        logger.error(f"Failed to fetch Alpaca OHLCV data for {symbol}: {e}")
        raise ValueError(f"Unable to fetch Alpaca historical data: {str(e)}")


async def get_ohlcv(symbol: str, range_str: str) -> List[Dict[str, Any]]:
    """Get OHLCV data for a symbol and time range - REAL DATA ONLY"""
    
    # Check cache
    cache_key = f"ohlcv_{symbol}_{range_str}"
    cached = cache.get(cache_key)
    if cached:
        logger.info(f"Returning cached OHLCV data for {symbol} {range_str}")
        return cached
    
    logger.info(f"Fetching OHLCV data for {symbol} with range {range_str}")
    try:
        # Map our range format to MCP period format
        # Note: Using 5d for 1D to ensure we get data
        period_map = {
            "1D": "5d",  # Get 5 days of data, filter to 1 day later
            "5D": "5d",
            "1M": "1mo",
            "3M": "3mo",
            "6M": "6mo",
            "YTD": "ytd",
            "1Y": "1y",
            "5Y": "5y"
        }
        
        # Map our range to interval
        # Use defaults that work with Yahoo Finance
        interval_map = {
            "1D": "1d",  # Use default daily interval
            "5D": "1d",  # Daily for 5 days
            "1M": "1d",  # Daily for 1 month
            "3M": "1d",
            "6M": "1d",
            "YTD": "1d",
            "1Y": "1d",
            "5Y": "1wk"
        }
        
        period = period_map.get(range_str, "1mo")
        
        # Get real data from MCP server
        client = get_mcp_client()
        
        # Ensure client is started
        if not client._initialized:
            logger.info("Initializing MCP client for OHLCV")
            await client.start()
        
        # Build parameters - let MCP server use its defaults for interval
        params = {
            "symbol": symbol,
            "period": period
        }
        
        logger.info(f"Calling get_stock_history with params: {params}")
        result = await client.call_tool("get_stock_history", params)
        
        logger.info(f"MCP returned result type: {type(result)}, has data: {result is not None}")
        if result:
            logger.info(f"MCP result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Parse string result if needed
        if result and isinstance(result, str):
            try:
                import json
                result = json.loads(result)
                logger.info(f"Parsed string result to dict: {type(result)}")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse MCP result as JSON: {result[:200]}")
                raise ValueError(f"Invalid response format from MCP server")
        
        if result and isinstance(result, dict):
            # Extract candles from MCP response
            candles = []
            
            # Handle different response formats
            if "data" in result:
                # MCP server format
                data = result["data"]
                for price_data in data:
                    # Convert date string to timestamp if needed
                    date_val = price_data.get("date", 0)
                    if isinstance(date_val, str):
                        from datetime import datetime
                        try:
                            dt = datetime.fromisoformat(date_val.replace('Z', '+00:00'))
                            date_val = int(dt.timestamp())
                        except:
                            date_val = 0
                    candles.append({
                        "time": date_val,
                        "open": price_data.get("open", 0),
                        "high": price_data.get("high", 0),
                        "low": price_data.get("low", 0),
                        "close": price_data.get("close", 0),
                        "volume": price_data.get("volume", 0)
                    })
            elif "prices" in result:
                prices = result["prices"]
                for price_data in prices:
                    candles.append({
                        "time": price_data.get("date", 0),
                        "open": price_data.get("open", 0),
                        "high": price_data.get("high", 0),
                        "low": price_data.get("low", 0),
                        "close": price_data.get("close", 0),
                        "volume": price_data.get("volume", 0)
                    })
            elif "indicators" in result and "quote" in result["indicators"]:
                # Yahoo Finance format
                quotes = result["indicators"]["quote"][0]
                timestamps = result.get("timestamp", [])
                
                for i in range(len(timestamps)):
                    if i < len(quotes.get("open", [])):
                        candles.append({
                            "time": timestamps[i],
                            "open": quotes["open"][i] if quotes["open"][i] else 0,
                            "high": quotes["high"][i] if quotes["high"][i] else 0,
                            "low": quotes["low"][i] if quotes["low"][i] else 0,
                            "close": quotes["close"][i] if quotes["close"][i] else 0,
                            "volume": quotes["volume"][i] if quotes["volume"][i] else 0
                        })
            
            if candles:
                cache.set(cache_key, candles)
                return candles
            else:
                raise ValueError(f"No historical data available for {symbol}")
                
    except Exception as e:
        logger.error(f"Failed to fetch real OHLCV data for {symbol}: {e}")
        raise ValueError(f"Unable to fetch real historical data for {symbol}. Please check the symbol and try again.")


def is_market_open() -> bool:
    """Check if market is currently open"""
    now = datetime.now()
    
    # Simple check: weekday and EST hours
    if now.weekday() >= 5:  # Weekend
        return False
    
    # Convert to EST (simplified, doesn't handle DST perfectly)
    est_hour = (now.hour - 5) % 24
    
    # Market hours: 9:30 AM - 4:00 PM EST
    if 9.5 <= est_hour < 16:
        return True
    
    return False


def humanize_market_cap(value: Optional[float]) -> str:
    """Convert market cap to human readable format"""
    if value is None:
        return "—"
    
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    else:
        return f"${value:,.0f}"


def build_summary_table(quote: Dict[str, Any]) -> dict:
    """Build summary table from quote data"""
    
    rows = []
    
    # Market Cap
    if quote.get("market_cap"):
        rows.append({
            "key": "mkt_cap",
            "label": "Market Cap",
            "value_raw": quote["market_cap"],
            "value_formatted": humanize_market_cap(quote["market_cap"]),
            "tooltip": "Total market value of all shares"
        })
    
    # P/E Ratio
    if quote.get("pe_ttm") is not None:
        rows.append({
            "key": "pe",
            "label": "P/E (TTM)",
            "value_raw": quote["pe_ttm"],
            "value_formatted": f"{quote['pe_ttm']:.2f}",
            "tooltip": "Price to Earnings ratio (trailing twelve months)"
        })
    
    # Dividend Yield
    if quote.get("dividend_yield_pct") is not None:
        rows.append({
            "key": "div_yield",
            "label": "Dividend Yield",
            "value_raw": quote["dividend_yield_pct"],
            "value_formatted": f"{quote['dividend_yield_pct']:.2f}%",
            "tooltip": "Annual dividend as percentage of stock price"
        })
    
    # Beta
    if quote.get("beta") is not None:
        rows.append({
            "key": "beta",
            "label": "Beta",
            "value_raw": quote["beta"],
            "value_formatted": f"{quote['beta']:.2f}",
            "tooltip": "Volatility relative to market"
        })
    
    # Volume
    if quote.get("volume"):
        rows.append({
            "key": "volume",
            "label": "Volume",
            "value_raw": quote["volume"],
            "value_formatted": f"{quote['volume']:,}",
            "delta_pct": ((quote["volume"] / quote.get("avg_volume_3m", quote["volume"])) - 1) * 100 if quote.get("avg_volume_3m") else None,
            "delta_formatted": f"{((quote['volume'] / quote.get('avg_volume_3m', quote['volume'])) - 1) * 100:+.1f}% vs avg" if quote.get("avg_volume_3m") else None,
            "tooltip": "Shares traded today"
        })
    
    # 52 Week Range
    if quote.get("week52_high") and quote.get("week52_low"):
        current_position = (quote["last"] - quote["week52_low"]) / (quote["week52_high"] - quote["week52_low"]) * 100
        rows.append({
            "key": "52w_range",
            "label": "52 Week Range",
            "value_raw": current_position,
            "value_formatted": f"${quote['week52_low']:.2f} - ${quote['week52_high']:.2f}",
            "delta_formatted": f"Currently {current_position:.0f}% of range",
            "tooltip": "Price range over past year"
        })
    
    return {"rows": rows}