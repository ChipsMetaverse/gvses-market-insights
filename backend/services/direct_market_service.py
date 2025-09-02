"""
Direct Market Data Service
===========================
Fast production service that makes direct HTTP calls to Yahoo Finance API.
Bypasses MCP subprocess overhead for sub-second performance.
"""

import httpx
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import re

logger = logging.getLogger(__name__)


class DirectMarketDataService:
    """Direct service for fast Yahoo Finance API calls without MCP overhead."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.timeout = 10.0  # 10 second timeout for fast responses
    
    async def get_stock_price(self, symbol: str) -> dict:
        """Get stock price with direct Yahoo Finance API call."""
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol.upper()}"
                response = await client.get(url, headers=self.headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('chart', {}).get('result', [])
                    
                    if result:
                        meta = result[0].get('meta', {})
                        return {
                            "symbol": symbol.upper(),
                            "price": meta.get('regularMarketPrice', 0),
                            "change": meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0),
                            "change_percent": ((meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0)) / meta.get('previousClose', 1)) * 100,
                            "previous_close": meta.get('previousClose', 0),
                            "open": meta.get('regularMarketOpen', 0),
                            "day_low": meta.get('regularMarketDayLow', 0),
                            "day_high": meta.get('regularMarketDayHigh', 0),
                            "volume": meta.get('regularMarketVolume', 0),
                            "timestamp": datetime.now().isoformat(),
                            "data_source": "yahoo_direct"
                        }
                
                raise ValueError(f"No data returned for {symbol}")
                
        except Exception as e:
            logger.error(f"Error fetching direct stock price for {symbol}: {e}")
            raise
    
    async def get_stock_history(self, symbol: str, days: int = 50) -> dict:
        """Get stock history with direct Yahoo Finance API call."""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            period1 = int(start_date.timestamp())
            period2 = int(end_date.timestamp())
            
            async with httpx.AsyncClient() as client:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol.upper()}"
                params = {
                    'period1': period1,
                    'period2': period2,
                    'interval': '1d'
                }
                response = await client.get(url, headers=self.headers, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('chart', {}).get('result', [])
                    
                    if result:
                        quotes = result[0].get('indicators', {}).get('quote', [{}])[0]
                        timestamps = result[0].get('timestamp', [])
                        
                        candles = []
                        for i, timestamp in enumerate(timestamps):
                            if (quotes.get('open', [None] * len(timestamps))[i] is not None and
                                quotes.get('close', [None] * len(timestamps))[i] is not None):
                                
                                candles.append({
                                    'date': datetime.fromtimestamp(timestamp).isoformat().split('T')[0],
                                    'time': timestamp,
                                    'open': quotes.get('open', [])[i],
                                    'high': quotes.get('high', [])[i], 
                                    'low': quotes.get('low', [])[i],
                                    'close': quotes.get('close', [])[i],
                                    'volume': quotes.get('volume', [])[i] or 0
                                })
                        
                        return {
                            "symbol": symbol.upper(),
                            "candles": candles,
                            "period": f"{days}D",
                            "data_source": "yahoo_direct"
                        }
                
                raise ValueError(f"No history data returned for {symbol}")
                
        except Exception as e:
            logger.error(f"Error fetching direct stock history for {symbol}: {e}")
            raise
    
    async def get_stock_news(self, symbol: str, limit: int = 10) -> dict:
        """Get stock news with direct API calls."""
        try:
            async with httpx.AsyncClient() as client:
                # Yahoo Finance news endpoint
                url = f"https://query2.finance.yahoo.com/v1/finance/search"
                params = {
                    'q': symbol.upper(),
                    'quotesCount': 1,
                    'newsCount': limit,
                    'enableFuzzyQuery': False,
                    'quotesQueryId': 'tss_match_phrase_query',
                    'multiQuoteQueryId': 'multi_quote_single_token_query',
                    'newsQueryId': 'news_cie_vespa',
                    'enableCb': True,
                    'enableNavLinks': True,
                    'enableEnhancedTrivialQuery': True
                }
                
                response = await client.get(url, headers=self.headers, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    news_items = data.get('news', [])
                    
                    articles = []
                    for item in news_items:
                        articles.append({
                            "title": item.get('title', ''),
                            "link": item.get('link', ''),
                            "source": item.get('publisher', 'Yahoo Finance'),
                            "published": item.get('providerPublishTime', ''),
                            "summary": item.get('summary', '')
                        })
                    
                    return {
                        "symbol": symbol.upper(),
                        "articles": articles,
                        "total": len(articles),
                        "data_source": "yahoo_direct"
                    }
                
                return {
                    "symbol": symbol.upper(),
                    "articles": [],
                    "total": 0,
                    "data_source": "yahoo_direct"
                }
                
        except Exception as e:
            logger.error(f"Error fetching direct stock news for {symbol}: {e}")
            return {
                "symbol": symbol.upper(),
                "articles": [],
                "total": 0,
                "data_source": "yahoo_direct",
                "error": str(e)
            }
    
    async def get_comprehensive_stock_data(self, symbol: str) -> dict:
        """Get comprehensive stock data with direct API calls."""
        try:
            # Get price and history data concurrently
            tasks = [
                self.get_stock_price(symbol),
                self.get_stock_history(symbol, 30)  # 30 days for technical levels
            ]
            
            price_data, history_data = await asyncio.gather(*tasks, return_exceptions=True)
            
            if isinstance(price_data, Exception):
                price_data = {"error": str(price_data)}
            if isinstance(history_data, Exception):
                history_data = {"candles": []}
            
            # Calculate technical levels
            technical_levels = {}
            candles = history_data.get('candles', [])
            if candles and len(candles) > 0:
                recent_candles = candles[-20:]  # Last 20 days
                if recent_candles:
                    highs = [c.get('high', 0) for c in recent_candles if c.get('high')]
                    lows = [c.get('low', 0) for c in recent_candles if c.get('low')]
                    
                    if highs and lows:
                        recent_high = max(highs)
                        recent_low = min(lows)
                        
                        # Use frontend-compatible field names
                        technical_levels = {
                            "qe_level": round(recent_high * 0.98, 2),  # Quick Entry
                            "st_level": round((recent_high + recent_low) / 2, 2),  # Swing Trade  
                            "ltb_level": round(recent_low * 1.02, 2)  # Load The Boat
                        }
            
            return {
                "symbol": symbol.upper(),
                "price_data": price_data,
                "technical_levels": technical_levels,
                "data_source": "yahoo_direct"
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive data for {symbol}: {e}")
            return {
                "symbol": symbol.upper(),
                "price_data": {},
                "technical_levels": {},
                "data_source": "yahoo_direct",
                "error": str(e)
            }
    
    async def warm_up(self):
        """Pre-warm the service with a test call."""
        try:
            logger.info("Warming up direct market service...")
            result = await self.get_stock_price("SPY")
            if result and "price" in result:
                logger.info(f"Direct market service ready - SPY price: ${result.get('price', 'N/A')}")
            else:
                logger.warning(f"Direct market service warm-up returned unexpected result: {result}")
        except Exception as e:
            logger.warning(f"Direct market service warm-up failed: {e}")
            # Don't re-raise - allow service to initialize even if warm-up fails
            logger.info("Direct market service initialized despite warm-up failure")