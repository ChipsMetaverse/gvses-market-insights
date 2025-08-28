from typing import List, Dict, Any
from models.schemas import TimeRange, CandleInterval


def range_to_interval(range_str: str) -> str:
    """Convert time range to candle interval"""
    mapping = {
        "1D": "1m",
        "5D": "5m",
        "1M": "15m",
        "6M": "1h",
        "YTD": "1h",
        "1Y": "1d",
        "5Y": "1d",
        "MAX": "1w",
    }
    return mapping.get(range_str, "1h")


def build_chart_data(symbol: str, range_str: str, candles: List[Dict[str, Any]]) -> dict:
    """Build chart data from candles"""
    interval = range_to_interval(range_str)
    
    # Process candles
    processed_candles = []
    volume_bars = []
    
    # Handle case where candles is None or empty
    if not candles:
        return {
            "range": range_str,
            "interval": interval,
            "timezone": "UTC",
            "candles": [],
            "volume_bars": None,
            "price_min": None,
            "price_max": None
        }
    
    for candle in candles:
        # Handle both dict and object formats
        if hasattr(candle, '__dict__'):
            candle = candle.__dict__
        
        processed_candle = {
            "time": candle.get("time", candle.get("timestamp", 0)),
            "open": candle.get("open", 0),
            "high": candle.get("high", 0),
            "low": candle.get("low", 0),
            "close": candle.get("close", 0),
            "volume": candle.get("volume")
        }
        processed_candles.append(processed_candle)
        
        if processed_candle["volume"] is not None:
            volume_bars.append({
                "time": processed_candle["time"],
                "value": processed_candle["volume"]
            })
    
    # Calculate price range
    if processed_candles:
        all_highs = [c["high"] for c in processed_candles if c["high"]]
        all_lows = [c["low"] for c in processed_candles if c["low"]]
        price_min = min(all_lows) if all_lows else None
        price_max = max(all_highs) if all_highs else None
    else:
        price_min = None
        price_max = None
    
    return {
        "range": range_str,
        "interval": interval,
        "timezone": "UTC",
        "candles": processed_candles,
        "volume_bars": volume_bars if volume_bars else None,
        "price_min": price_min,
        "price_max": price_max
    }


def get_lookback_days(range_str: str) -> int:
    """Get number of days to look back for a given range"""
    mapping = {
        "1D": 1,
        "5D": 5,
        "1M": 30,
        "6M": 182,
        "YTD": None,  # Calculate based on current date
        "1Y": 365,
        "5Y": 1825,
        "MAX": 7300  # 20 years
    }
    
    if range_str == "YTD":
        from datetime import datetime
        now = datetime.now()
        return (now - datetime(now.year, 1, 1)).days
    
    return mapping.get(range_str, 30)