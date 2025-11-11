"""
Forex Currency Pairs
Static list of major, cross, and exotic forex pairs for search
"""

from typing import List, Dict, Any

# Comprehensive forex pairs list
# Symbol format: "EURUSD=X" (Yahoo Finance format)
FOREX_PAIRS = [
    # Major Pairs (USD-based)
    {"symbol": "EURUSD=X", "name": "EUR/USD", "base": "EUR", "quote": "USD", "category": "major", "description": "Euro vs US Dollar"},
    {"symbol": "GBPUSD=X", "name": "GBP/USD", "base": "GBP", "quote": "USD", "category": "major", "description": "British Pound vs US Dollar"},
    {"symbol": "USDJPY=X", "name": "USD/JPY", "base": "USD", "quote": "JPY", "category": "major", "description": "US Dollar vs Japanese Yen"},
    {"symbol": "USDCHF=X", "name": "USD/CHF", "base": "USD", "quote": "CHF", "category": "major", "description": "US Dollar vs Swiss Franc"},
    {"symbol": "AUDUSD=X", "name": "AUD/USD", "base": "AUD", "quote": "USD", "category": "major", "description": "Australian Dollar vs US Dollar"},
    {"symbol": "USDCAD=X", "name": "USD/CAD", "base": "USD", "quote": "CAD", "category": "major", "description": "US Dollar vs Canadian Dollar"},
    {"symbol": "NZDUSD=X", "name": "NZD/USD", "base": "NZD", "quote": "USD", "category": "major", "description": "New Zealand Dollar vs US Dollar"},

    # Cross Pairs (Non-USD)
    {"symbol": "EURGBP=X", "name": "EUR/GBP", "base": "EUR", "quote": "GBP", "category": "cross", "description": "Euro vs British Pound"},
    {"symbol": "EURJPY=X", "name": "EUR/JPY", "base": "EUR", "quote": "JPY", "category": "cross", "description": "Euro vs Japanese Yen"},
    {"symbol": "GBPJPY=X", "name": "GBP/JPY", "base": "GBP", "quote": "JPY", "category": "cross", "description": "British Pound vs Japanese Yen"},
    {"symbol": "EURCHF=X", "name": "EUR/CHF", "base": "EUR", "quote": "CHF", "category": "cross", "description": "Euro vs Swiss Franc"},
    {"symbol": "EURAUD=X", "name": "EUR/AUD", "base": "EUR", "quote": "AUD", "category": "cross", "description": "Euro vs Australian Dollar"},
    {"symbol": "EURCAD=X", "name": "EUR/CAD", "base": "EUR", "quote": "CAD", "category": "cross", "description": "Euro vs Canadian Dollar"},
    {"symbol": "GBPCHF=X", "name": "GBP/CHF", "base": "GBP", "quote": "CHF", "category": "cross", "description": "British Pound vs Swiss Franc"},
    {"symbol": "GBPAUD=X", "name": "GBP/AUD", "base": "GBP", "quote": "AUD", "category": "cross", "description": "British Pound vs Australian Dollar"},
    {"symbol": "GBPCAD=X", "name": "GBP/CAD", "base": "GBP", "quote": "CAD", "category": "cross", "description": "British Pound vs Canadian Dollar"},
    {"symbol": "AUDCAD=X", "name": "AUD/CAD", "base": "AUD", "quote": "CAD", "category": "cross", "description": "Australian Dollar vs Canadian Dollar"},
    {"symbol": "AUDJPY=X", "name": "AUD/JPY", "base": "AUD", "quote": "JPY", "category": "cross", "description": "Australian Dollar vs Japanese Yen"},
    {"symbol": "AUDCHF=X", "name": "AUD/CHF", "base": "AUD", "quote": "CHF", "category": "cross", "description": "Australian Dollar vs Swiss Franc"},
    {"symbol": "NZDJPY=X", "name": "NZD/JPY", "base": "NZD", "quote": "JPY", "category": "cross", "description": "New Zealand Dollar vs Japanese Yen"},
    {"symbol": "CADJPY=X", "name": "CAD/JPY", "base": "CAD", "quote": "JPY", "category": "cross", "description": "Canadian Dollar vs Japanese Yen"},
    {"symbol": "CHFJPY=X", "name": "CHF/JPY", "base": "CHF", "quote": "JPY", "category": "cross", "description": "Swiss Franc vs Japanese Yen"},

    # Exotic Pairs
    {"symbol": "USDTRY=X", "name": "USD/TRY", "base": "USD", "quote": "TRY", "category": "exotic", "description": "US Dollar vs Turkish Lira"},
    {"symbol": "USDMXN=X", "name": "USD/MXN", "base": "USD", "quote": "MXN", "category": "exotic", "description": "US Dollar vs Mexican Peso"},
    {"symbol": "USDZAR=X", "name": "USD/ZAR", "base": "USD", "quote": "ZAR", "category": "exotic", "description": "US Dollar vs South African Rand"},
    {"symbol": "USDBRL=X", "name": "USD/BRL", "base": "USD", "quote": "BRL", "category": "exotic", "description": "US Dollar vs Brazilian Real"},
    {"symbol": "USDINR=X", "name": "USD/INR", "base": "USD", "quote": "INR", "category": "exotic", "description": "US Dollar vs Indian Rupee"},
    {"symbol": "USDKRW=X", "name": "USD/KRW", "base": "USD", "quote": "KRW", "category": "exotic", "description": "US Dollar vs South Korean Won"},
    {"symbol": "USDSGD=X", "name": "USD/SGD", "base": "USD", "quote": "SGD", "category": "exotic", "description": "US Dollar vs Singapore Dollar"},
    {"symbol": "USDHKD=X", "name": "USD/HKD", "base": "USD", "quote": "HKD", "category": "exotic", "description": "US Dollar vs Hong Kong Dollar"},
    {"symbol": "USDRUB=X", "name": "USD/RUB", "base": "USD", "quote": "RUB", "category": "exotic", "description": "US Dollar vs Russian Ruble"},
    {"symbol": "USDPLN=X", "name": "USD/PLN", "base": "USD", "quote": "PLN", "category": "exotic", "description": "US Dollar vs Polish Zloty"},
    {"symbol": "USDSEK=X", "name": "USD/SEK", "base": "USD", "quote": "SEK", "category": "exotic", "description": "US Dollar vs Swedish Krona"},
    {"symbol": "USDNOK=X", "name": "USD/NOK", "base": "USD", "quote": "NOK", "category": "exotic", "description": "US Dollar vs Norwegian Krone"},
    {"symbol": "USDDKK=X", "name": "USD/DKK", "base": "USD", "quote": "DKK", "category": "exotic", "description": "US Dollar vs Danish Krone"},
    {"symbol": "USDCZK=X", "name": "USD/CZK", "base": "USD", "quote": "CZK", "category": "exotic", "description": "US Dollar vs Czech Koruna"},
    {"symbol": "USDHUF=X", "name": "USD/HUF", "base": "USD", "quote": "HUF", "category": "exotic", "description": "US Dollar vs Hungarian Forint"},
    {"symbol": "USDTHB=X", "name": "USD/THB", "base": "USD", "quote": "THB", "category": "exotic", "description": "US Dollar vs Thai Baht"},
]


def search_forex_pairs(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search forex pairs by symbol, name, base currency, or quote currency.

    Args:
        query: Search term (e.g., "eur", "usd", "gbp/usd")
        limit: Maximum number of results to return

    Returns:
        List of matching forex pairs with full metadata
    """
    if not query:
        return FOREX_PAIRS[:limit]

    query_lower = query.lower().strip()
    filtered = []

    for pair in FOREX_PAIRS:
        # Check if query matches symbol, name, base, quote, or description
        symbol_match = query_lower in pair["symbol"].lower()
        name_match = query_lower in pair["name"].lower()
        base_match = query_lower == pair["base"].lower() or query_lower in pair["base"].lower()
        quote_match = query_lower == pair["quote"].lower() or query_lower in pair["quote"].lower()
        desc_match = query_lower in pair["description"].lower()

        if any([symbol_match, name_match, base_match, quote_match, desc_match]):
            filtered.append(pair)

    # Sort by relevance
    # Priority: exact base/quote match > starts with query > contains query
    filtered.sort(key=lambda x: (
        x["base"].lower() != query_lower and x["quote"].lower() != query_lower,  # Exact currency match first
        not x["name"].lower().startswith(query_lower),  # Name starts with query second
        x["symbol"]  # Alphabetical
    ))

    return filtered[:limit]


def get_all_forex_pairs() -> List[Dict[str, Any]]:
    """
    Get all forex pairs.

    Returns:
        Complete list of all forex pairs
    """
    return FOREX_PAIRS


def get_forex_pairs_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Get forex pairs filtered by category.

    Args:
        category: "major", "cross", or "exotic"

    Returns:
        List of forex pairs in the specified category
    """
    return [pair for pair in FOREX_PAIRS if pair["category"] == category]
