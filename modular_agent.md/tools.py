"""
tools.py
~~~~~~~~

This module defines a collection of *synthetic* data fetching functions for use by
the OpenAI agent.  Each function simulates retrieving market data such as
current prices or news headlines.  In your own implementation you should
replace these stubs with real API calls to your backend or external data
providers.

Tools are exposed as asynchronous functions (using `async def`) so they can be
awaited by the agent.  Each function returns a dictionary with the
requested information.  The module also defines a `FUNCTION_SCHEMAS` variable
containing JSON‑serializable schemas for each tool.  These schemas are used by
the OpenAI API to describe the functions available for function calling.

You can run this module directly to see the synthetic outputs by passing a
stock symbol on the command line:

```bash
python -m modular_agent.tools TSLA
```
"""

from __future__ import annotations

import asyncio
import json
import random
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional


# A simple list of fake news stories to return for any symbol.
FAKE_NEWS = [
    {
        "headline": "Company releases groundbreaking product",
        "source": "Reuters",
        "timestamp": datetime.now().isoformat(),
        "sentiment": "positive",
    },
    {
        "headline": "Regulatory concerns weigh on sector",
        "source": "Bloomberg",
        "timestamp": datetime.now().isoformat(),
        "sentiment": "negative",
    },
    {
        "headline": "Analysts see upside potential after earnings beat",
        "source": "CNBC",
        "timestamp": datetime.now().isoformat(),
        "sentiment": "positive",
    },
]


async def get_stock_price(symbol: str) -> Dict[str, Any]:
    """Return a synthetic price quote for a given stock symbol.

    This stub generates a fake price around 100–200 and random daily change.
    Replace this implementation with a call to your own price API.

    :param symbol: Stock ticker symbol (e.g. "TSLA", "AAPL").
    :return: A dictionary containing price information.
    """
    base = random.uniform(100.0, 200.0)
    change = random.uniform(-5.0, 5.0)
    price = round(base + change, 2)
    percent_change = round((change / base) * 100.0, 2)
    volume = random.randint(1_000_000, 10_000_000)
    timestamp = datetime.now().isoformat()
    return {
        "symbol": symbol.upper(),
        "price": price,
        "change": change,
        "percent_change": percent_change,
        "volume": volume,
        "timestamp": timestamp,
    }


async def get_stock_news(symbol: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Return a synthetic list of news headlines for a given symbol.

    This stub simply cycles through the FAKE_NEWS list and prepends the symbol
    to each headline.  Replace this with a call to your own news API.

    :param symbol: Stock ticker symbol.
    :param limit: Maximum number of news items to return.
    :return: A list of dictionaries representing news items.
    """
    items: List[Dict[str, Any]] = []
    for i in range(min(limit, len(FAKE_NEWS))):
        item = FAKE_NEWS[i].copy()
        item["headline"] = f"{symbol.upper()}: {item['headline']}"
        items.append(item)
    return items


async def get_market_overview() -> Dict[str, Any]:
    """Return a synthetic snapshot of the overall market.

    The snapshot includes random index levels and top movers.  In a real
    implementation you might call an API such as your backend's
    `/api/market-overview` endpoint.

    :return: A dictionary with index values and top gainers/losers.
    """
    indices = {
        "S&P 500": round(random.uniform(4000, 4500), 2),
        "NASDAQ": round(random.uniform(13000, 15000), 2),
        "Dow Jones": round(random.uniform(32000, 35000), 2),
    }
    top_gainers = [
        {"symbol": f"GAIN{i}", "change": round(random.uniform(5, 10), 2)}
        for i in range(3)
    ]
    top_losers = [
        {"symbol": f"LOSS{i}", "change": -round(random.uniform(5, 10), 2)}
        for i in range(3)
    ]
    return {
        "indices": indices,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "timestamp": datetime.now().isoformat(),
    }


# Define JSON schema for each function so that the OpenAI agent knows how to
# call them.  See OpenAI function calling docs for details.
FUNCTION_SCHEMAS = [
    {
        "name": "get_stock_price",
        "description": "Get a real‑time quote for a stock or cryptocurrency symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock or crypto ticker symbol (e.g. TSLA, AAPL, BTC‑USD)."
                }
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_stock_news",
        "description": "Retrieve the latest news headlines for a given symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Ticker symbol to fetch news for."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of news items to return.",
                    "default": 3,
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_market_overview",
        "description": "Get a snapshot of major indices and top market movers.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


async def main() -> None:
    """Basic demonstration when running this module directly."""
    symbol = sys.argv[1] if len(sys.argv) > 1 else "TSLA"
    price = await get_stock_price(symbol)
    news = await get_stock_news(symbol)
    overview = await get_market_overview()
    print("Price:", json.dumps(price, indent=2))
    print("News:", json.dumps(news, indent=2))
    print("Overview:", json.dumps(overview, indent=2))


if __name__ == "__main__":
    asyncio.run(main())