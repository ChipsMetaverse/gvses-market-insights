import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import time


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


def get_quote(symbol: str) -> Dict[str, Any]:
    """Get current quote for a symbol"""
    
    # Check cache
    cached = cache.get(f"quote_{symbol}")
    if cached:
        return cached
    
    # In production, fetch from real API
    # For now, generate mock data
    base_price = 100 + hash(symbol) % 400
    
    quote = {
        "symbol": symbol.upper(),
        "company_name": f"{symbol.upper()} Corporation",
        "exchange": "NASDAQ",
        "currency": "USD",
        "last": base_price + random.uniform(-2, 2),
        "change_abs": random.uniform(-5, 5),
        "change_pct": random.uniform(-3, 3),
        "open": base_price + random.uniform(-3, 3),
        "high": base_price + random.uniform(2, 8),
        "low": base_price + random.uniform(-8, -2),
        "prev_close": base_price,
        "volume": random.randint(1000000, 50000000),
        "avg_volume_3m": random.randint(5000000, 30000000),
        "market_cap": random.randint(1000000000, 500000000000),
        "pe_ttm": random.uniform(10, 40),
        "dividend_yield_pct": random.uniform(0, 4),
        "beta": random.uniform(0.5, 2.0),
        "week52_high": base_price + random.uniform(20, 50),
        "week52_low": base_price + random.uniform(-50, -20),
        "is_open": is_market_open()
    }
    
    # Adjust change based on last vs prev_close
    quote["change_abs"] = round(quote["last"] - quote["prev_close"], 2)
    quote["change_pct"] = round((quote["change_abs"] / quote["prev_close"]) * 100, 2)
    
    cache.set(f"quote_{symbol}", quote)
    return quote


def get_ohlcv(symbol: str, range_str: str) -> List[Dict[str, Any]]:
    """Get OHLCV data for a symbol and time range"""
    
    # Check cache
    cache_key = f"ohlcv_{symbol}_{range_str}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Determine number of candles based on range
    from services.chart_service import get_lookback_days, range_to_interval
    
    lookback_days = get_lookback_days(range_str)
    interval = range_to_interval(range_str)
    
    # Calculate number of candles
    candles_per_day = {
        "1m": 390,    # Trading minutes in a day
        "5m": 78,
        "15m": 26,
        "1h": 7,      # Trading hours
        "1d": 1,
        "1w": 0.2
    }
    
    num_candles = int(lookback_days * candles_per_day.get(interval, 1))
    num_candles = min(num_candles, 1000)  # Limit for performance
    
    # Generate mock candles
    candles = []
    base_price = 100 + hash(symbol) % 400
    current_time = int(datetime.now().timestamp())
    
    # Time increment in seconds
    time_increments = {
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "1h": 3600,
        "1d": 86400,
        "1w": 604800
    }
    time_increment = time_increments.get(interval, 3600)
    
    for i in range(num_candles):
        candle_time = current_time - (num_candles - i - 1) * time_increment
        
        # Generate realistic OHLC
        open_price = base_price + random.uniform(-10, 10) + (i - num_candles/2) * 0.1
        close_price = open_price + random.uniform(-2, 2)
        high_price = max(open_price, close_price) + random.uniform(0, 1)
        low_price = min(open_price, close_price) - random.uniform(0, 1)
        
        candles.append({
            "time": candle_time,
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": random.randint(100000, 5000000)
        })
        
        base_price = close_price  # Next candle starts where this one closed
    
    cache.set(cache_key, candles)
    return candles


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