"""
Fallback Price Data
===================
Provides fallback prices when market data APIs are unavailable.
Used for demonstration and when markets are closed.

Note: These are sample prices for demo purposes only.
Update with real data when markets open.
"""

from datetime import datetime

# Last known closing prices (update these with real data)
FALLBACK_PRICES = {
    "TSLA": {
        "price": 428.75,
        "previous_close": 425.30,
        "change": 3.45,
        "change_percent": 0.81,
        "volume": 125842000,
        "last_updated": "2025-01-17 16:00:00"
    },
    "AAPL": {
        "price": 235.85,
        "previous_close": 234.12,
        "change": 1.73,
        "change_percent": 0.74,
        "volume": 45234000,
        "last_updated": "2025-01-17 16:00:00"
    },
    "NVDA": {
        "price": 589.45,
        "previous_close": 585.20,
        "change": 4.25,
        "change_percent": 0.73,
        "volume": 52341000,
        "last_updated": "2025-01-17 16:00:00"
    },
    "SPY": {
        "price": 582.15,
        "previous_close": 580.45,
        "change": 1.70,
        "change_percent": 0.29,
        "volume": 65432000,
        "last_updated": "2025-01-17 16:00:00"
    },
    "PLTR": {
        "price": 82.35,
        "previous_close": 81.20,
        "change": 1.15,
        "change_percent": 1.42,
        "volume": 45123000,
        "last_updated": "2025-01-17 16:00:00"
    },
    "META": {
        "price": 638.50,
        "previous_close": 635.20,
        "change": 3.30,
        "change_percent": 0.52,
        "volume": 12345000,
        "last_updated": "2025-01-17 16:00:00"
    },
    "GOOGL": {
        "price": 192.45,
        "previous_close": 191.20,
        "change": 1.25,
        "change_percent": 0.65,
        "volume": 23456000,
        "last_updated": "2025-01-17 16:00:00"
    },
    "MSFT": {
        "price": 445.30,
        "previous_close": 443.15,
        "change": 2.15,
        "change_percent": 0.49,
        "volume": 18765000,
        "last_updated": "2025-01-17 16:00:00"
    },
    "AMZN": {
        "price": 218.75,
        "previous_close": 217.30,
        "change": 1.45,
        "change_percent": 0.67,
        "volume": 34567000,
        "last_updated": "2025-01-17 16:00:00"
    },
    "BTC-USD": {
        "price": 102450.00,
        "previous_close": 101230.00,
        "change": 1220.00,
        "change_percent": 1.21,
        "volume": 28563000000,
        "last_updated": "2025-01-17 16:00:00"
    }
}


def get_fallback_price(symbol: str) -> dict:
    """
    Get fallback price data for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        dict with price data or None if not available
    """
    symbol_upper = symbol.upper()
    
    # Handle crypto mapping
    if symbol_upper == "BTC":
        symbol_upper = "BTC-USD"
    
    fallback = FALLBACK_PRICES.get(symbol_upper)
    
    if not fallback:
        return None
    
    return {
        "symbol": symbol.upper(),
        "company_name": symbol.upper(),
        "exchange": "NASDAQ",
        "currency": "USD",
        "last": fallback["price"],
        "price": fallback["price"],
        "change_abs": fallback["change"],
        "change_pct": fallback["change_percent"],
        "open": fallback["previous_close"],
        "high": fallback["price"] * 1.02,
        "low": fallback["previous_close"] * 0.98,
        "prev_close": fallback["previous_close"],
        "previous_close": fallback["previous_close"],
        "volume": fallback["volume"],
        "avg_volume_3m": fallback["volume"],
        "market_cap": 0,
        "pe_ttm": 0,
        "dividend_yield_pct": 0,
        "beta": 1.0,
        "week52_high": fallback["price"] * 1.25,
        "week52_low": fallback["previous_close"] * 0.75,
        "is_open": False,
        "change_percent": fallback["change_percent"],
        "data_source": "fallback_demo",
        "asset_type": "crypto" if "-USD" in symbol_upper else "stock",
        "note": "Fallback demo data - markets closed or API unavailable"
    }

