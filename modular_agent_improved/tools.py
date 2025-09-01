"""
tools.py - Production-ready market data tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connects to your production backend (https://gvses-market-insights.fly.dev)
for real market data. Each function matches the ElevenLabs Server Tools
configuration and returns properly formatted responses.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx

# Production backend URL
BACKEND_URL = "https://gvses-market-insights.fly.dev"

async def get_stock_price(symbol: str) -> Dict[str, Any]:
    """Fetch real-time stock, cryptocurrency, or index prices."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/api/stock-price",
            params={"symbol": symbol.upper()}
        )
        response.raise_for_status()
        return response.json()

async def get_stock_news(symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve latest news headlines for a symbol."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/api/stock-news",
            params={"symbol": symbol.upper(), "limit": limit}
        )
        response.raise_for_status()
        return response.json()

async def get_market_overview() -> Dict[str, Any]:
    """Get snapshot of major indices and top market movers."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/api/market-overview")
        response.raise_for_status()
        return response.json()

async def get_stock_history(symbol: str, days: int = 30) -> Dict[str, Any]:
    """Get historical price data for charting."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/api/stock-history",
            params={"symbol": symbol.upper(), "days": days}
        )
        response.raise_for_status()
        return response.json()

async def get_comprehensive_stock_data(symbol: str) -> Dict[str, Any]:
    """Get comprehensive stock information including fundamentals."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/api/comprehensive-stock-data",
            params={"symbol": symbol.upper()}
        )
        response.raise_for_status()
        return response.json()

async def get_market_movers() -> Dict[str, Any]:
    """Get top gainers, losers, and most active stocks."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/api/market-movers")
        response.raise_for_status()
        return response.json()

async def get_analyst_ratings(symbol: str) -> Dict[str, Any]:
    """Get analyst ratings and price targets."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/api/analyst-ratings",
            params={"symbol": symbol.upper()}
        )
        response.raise_for_status()
        return response.json()

async def get_options_chain(symbol: str) -> Dict[str, Any]:
    """Get options chain data for a symbol."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/api/options-chain",
            params={"symbol": symbol.upper()}
        )
        response.raise_for_status()
        return response.json()

# OpenAI function schemas for all tools
FUNCTION_SCHEMAS = [
    {
        "name": "get_stock_price",
        "description": "Fetch real-time stock, cryptocurrency, or index prices",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock/crypto symbol (e.g., AAPL, TSLA, BTC-USD)"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_stock_news",
        "description": "Retrieve latest news headlines for a symbol",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of news items",
                    "default": 5
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_market_overview",
        "description": "Get snapshot of major indices and top market movers",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_stock_history",
        "description": "Get historical price data for charting",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days of history",
                    "default": 30
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_comprehensive_stock_data",
        "description": "Get comprehensive stock information including fundamentals",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_market_movers",
        "description": "Get top gainers, losers, and most active stocks",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_analyst_ratings",
        "description": "Get analyst ratings and price targets",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_options_chain",
        "description": "Get options chain data for a symbol",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            },
            "required": ["symbol"]
        }
    }
]

async def main():
    """Test the tools with real data."""
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else "TSLA"
    
    print(f"Testing tools for {symbol}...\n")
    
    try:
        price = await get_stock_price(symbol)
        print("Price:", json.dumps(price, indent=2))
        
        news = await get_stock_news(symbol, limit=3)
        print("\nNews:", json.dumps(news[:2], indent=2))  # Show first 2 items
        
        overview = await get_market_overview()
        print("\nMarket Overview:", json.dumps(overview, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())