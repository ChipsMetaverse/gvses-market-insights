"""
Comprehensive Market Data Service
Provides all market data functionality to match ChatGPT's capabilities
"""

import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import logging
from services.sentiment_scorer import SentimentScorer

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching comprehensive market data."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def get_comprehensive_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get all available data for a stock."""
        async with httpx.AsyncClient() as client:
            # Fetch multiple data sources in parallel
            tasks = [
                self.get_stock_quote(client, symbol),
                self.get_stock_news(client, symbol),
                self.get_analyst_ratings(client, symbol),
                self.get_key_statistics(client, symbol),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine all data
            data = {
                "symbol": symbol.upper(),
                "timestamp": datetime.now().isoformat(),
            }
            
            # Add quote data
            if not isinstance(results[0], Exception):
                data.update(results[0])
            
            # Add news
            if not isinstance(results[1], Exception):
                data["news"] = results[1]
            
            # Add analyst ratings
            if not isinstance(results[2], Exception):
                data["analyst_ratings"] = results[2]
            
            # Add key statistics
            if not isinstance(results[3], Exception):
                data["statistics"] = results[3]
            
            # Add technical levels
            data["technical_levels"] = self.calculate_technical_levels(data.get("price", 0))

            # Calculate sentiment score
            try:
                price_data = {
                    'changePercent': data.get('change_percent', 0),
                    'price': data.get('price', 0),
                }

                volume_data = {
                    'current_volume': data.get('volume', 0),
                    'avg_volume': data.get('avg_volume', 0),
                }

                # Format news for sentiment analysis
                news_articles = []
                if "news" in data:
                    news_articles = [
                        {
                            'title': news_item.get('title', ''),
                            'summary': '',  # Yahoo news doesn't provide summary in this endpoint
                        }
                        for news_item in data["news"]
                    ]

                # Calculate sentiment (technical_indicators=None for now)
                sentiment_data = SentimentScorer.calculate_sentiment_score(
                    price_data=price_data,
                    technical_indicators=None,
                    news_articles=news_articles if news_articles else None,
                    volume_data=volume_data if volume_data['current_volume'] > 0 else None
                )

                data["sentiment"] = sentiment_data

            except Exception as e:
                logger.error(f"Error calculating sentiment for {symbol}: {e}")
                # Add default sentiment on error
                data["sentiment"] = SentimentScorer._default_sentiment()

            return data
    
    async def get_stock_quote(self, client: httpx.AsyncClient, symbol: str) -> Dict[str, Any]:
        """Get detailed quote data."""
        try:
            # Chart API for price data
            chart_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol.upper()}"
            chart_response = await client.get(chart_url, headers=self.headers, timeout=10.0)
            
            # Quote API for detailed data
            quote_url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol.upper()}"
            quote_response = await client.get(quote_url, headers=self.headers, timeout=10.0)
            
            data = {}
            
            if chart_response.status_code == 200:
                chart_data = chart_response.json()
                result = chart_data.get("chart", {}).get("result", [{}])[0]
                meta = result.get("meta", {})
                
                current_price = meta.get("regularMarketPrice", 0)
                prev_close = meta.get("chartPreviousClose", meta.get("previousClose", current_price))
                
                data.update({
                    "price": round(current_price, 2),
                    "change": round(current_price - prev_close, 2),
                    "change_percent": round((current_price - prev_close) / prev_close * 100 if prev_close else 0, 2),
                    "previous_close": round(prev_close, 2),
                    "open": round(meta.get("regularMarketOpen", 0), 2),
                    "day_low": round(meta.get("regularMarketDayLow", 0), 2),
                    "day_high": round(meta.get("regularMarketDayHigh", 0), 2),
                    "volume": meta.get("regularMarketVolume", 0),
                })
            
            if quote_response.status_code == 200:
                quotes = quote_response.json().get("quoteResponse", {}).get("result", [])
                if quotes:
                    quote_data = quotes[0]
                    data.update({
                        "company_name": quote_data.get("longName", symbol.upper()),
                        "market_cap": quote_data.get("marketCap", 0),
                        "pe_ratio": round(quote_data.get("trailingPE", 0), 2),
                        "forward_pe": round(quote_data.get("forwardPE", 0), 2),
                        "eps": round(quote_data.get("epsTrailingTwelveMonths", 0), 2),
                        "dividend_yield": round(quote_data.get("dividendYield", 0) * 100 if quote_data.get("dividendYield") else 0, 2),
                        "beta": round(quote_data.get("beta", 0), 2),
                        "year_low": round(quote_data.get("fiftyTwoWeekLow", 0), 2),
                        "year_high": round(quote_data.get("fiftyTwoWeekHigh", 0), 2),
                        "avg_volume": quote_data.get("averageDailyVolume3Month", 0),
                        "shares_outstanding": quote_data.get("sharesOutstanding", 0),
                    })
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return {}
    
    async def get_stock_news(self, client: httpx.AsyncClient, symbol: str) -> List[Dict[str, Any]]:
        """Get latest news for a stock."""
        try:
            # Using Yahoo Finance news API
            url = f"https://query2.finance.yahoo.com/v1/finance/search?q={symbol}&newsCount=5"
            response = await client.get(url, headers=self.headers, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                news_items = data.get("news", [])
                
                return [
                    {
                        "title": item.get("title", ""),
                        "publisher": item.get("publisher", ""),
                        "link": item.get("link", ""),
                        "published": item.get("providerPublishTime", 0),
                    }
                    for item in news_items[:5]
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    async def get_analyst_ratings(self, client: httpx.AsyncClient, symbol: str) -> Dict[str, Any]:
        """Get analyst ratings and price targets."""
        try:
            # This would typically use a premium API, but we'll provide structured mock data
            # In production, integrate with services like Alpha Vantage, IEX Cloud, or Polygon.io
            
            return {
                "consensus": "Buy",
                "rating_distribution": {
                    "strong_buy": 15,
                    "buy": 20,
                    "hold": 10,
                    "sell": 3,
                    "strong_sell": 1
                },
                "price_targets": {
                    "average": 245.50,
                    "high": 280.00,
                    "low": 210.00,
                    "current": 231.59
                },
                "recent_ratings": [
                    {
                        "firm": "Morgan Stanley",
                        "rating": "Overweight",
                        "price_target": 250.00,
                        "date": "2025-08-15"
                    },
                    {
                        "firm": "Goldman Sachs",
                        "rating": "Buy",
                        "price_target": 265.00,
                        "date": "2025-08-14"
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error fetching analyst ratings for {symbol}: {e}")
            return {}
    
    async def get_key_statistics(self, client: httpx.AsyncClient, symbol: str) -> Dict[str, Any]:
        """Get key financial statistics."""
        try:
            url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=defaultKeyStatistics,financialData,summaryDetail"
            response = await client.get(url, headers=self.headers, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("quoteSummary", {}).get("result", [{}])[0]
                
                key_stats = result.get("defaultKeyStatistics", {})
                financial = result.get("financialData", {})
                summary = result.get("summaryDetail", {})
                
                return {
                    "profit_margin": self._get_raw_value(financial.get("profitMargins")),
                    "operating_margin": self._get_raw_value(financial.get("operatingMargins")),
                    "roe": self._get_raw_value(financial.get("returnOnEquity")),
                    "roa": self._get_raw_value(financial.get("returnOnAssets")),
                    "revenue_growth": self._get_raw_value(financial.get("revenueGrowth")),
                    "earnings_growth": self._get_raw_value(financial.get("earningsGrowth")),
                    "debt_to_equity": self._get_raw_value(financial.get("debtToEquity")),
                    "current_ratio": self._get_raw_value(financial.get("currentRatio")),
                    "quick_ratio": self._get_raw_value(financial.get("quickRatio")),
                    "peg_ratio": self._get_raw_value(key_stats.get("pegRatio")),
                    "price_to_book": self._get_raw_value(key_stats.get("priceToBook")),
                    "enterprise_value": self._get_raw_value(key_stats.get("enterpriseValue")),
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching key statistics for {symbol}: {e}")
            return {}
    
    def _get_raw_value(self, data: Any) -> Optional[float]:
        """Extract raw value from Yahoo Finance response."""
        if isinstance(data, dict):
            return data.get("raw")
        return None
    
    def calculate_technical_levels(self, current_price: float) -> Dict[str, Any]:
        """Calculate technical trading levels."""
        if not current_price:
            return {}
        
        # Calculate Fibonacci levels (simplified)
        year_range = current_price * 0.3  # Approximate 30% range
        high = current_price + year_range / 2
        low = current_price - year_range / 2
        
        fib_levels = {
            "0%": round(high, 2),
            "23.6%": round(high - (high - low) * 0.236, 2),
            "38.2%": round(high - (high - low) * 0.382, 2),
            "50%": round(high - (high - low) * 0.5, 2),
            "61.8%": round(high - (high - low) * 0.618, 2),
            "100%": round(low, 2),
        }
        
        # Calculate trading levels
        return {
            "load_the_boat": round(current_price * 0.95, 2),  # 5% below current
            "swing_trade": round(current_price * 0.98, 2),    # 2% below current
            "quick_entry": round(current_price * 1.01, 2),    # 1% above current
            "resistance_1": round(current_price * 1.03, 2),
            "resistance_2": round(current_price * 1.05, 2),
            "support_1": round(current_price * 0.97, 2),
            "support_2": round(current_price * 0.95, 2),
            "fibonacci_levels": fib_levels,
        }
    
    async def get_market_movers(self) -> Dict[str, Any]:
        """Get market movers - gainers, losers, most active."""
        try:
            async with httpx.AsyncClient() as client:
                # Fetch trending tickers
                url = "https://query1.finance.yahoo.com/v1/finance/trending/US"
                response = await client.get(url, headers=self.headers, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    trending = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])
                    
                    return {
                        "trending": trending[:10],
                        "timestamp": datetime.now().isoformat()
                    }
                
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching market movers: {e}")
            return {}
    
    async def get_options_chain(self, symbol: str) -> Dict[str, Any]:
        """Get options chain data."""
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://query2.finance.yahoo.com/v7/finance/options/{symbol}"
                response = await client.get(url, headers=self.headers, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    option_chain = data.get("optionChain", {}).get("result", [{}])[0]
                    
                    if option_chain:
                        options_data = option_chain.get("options", [{}])[0]
                        
                        return {
                            "expiration_dates": option_chain.get("expirationDates", []),
                            "strikes": option_chain.get("strikes", []),
                            "calls": self._format_options(options_data.get("calls", [])),
                            "puts": self._format_options(options_data.get("puts", [])),
                        }
                
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {e}")
            return {}
    
    def _format_options(self, options: List[Dict]) -> List[Dict]:
        """Format options data for display."""
        formatted = []
        for option in options[:10]:  # Limit to top 10
            formatted.append({
                "strike": option.get("strike"),
                "last_price": option.get("lastPrice"),
                "bid": option.get("bid"),
                "ask": option.get("ask"),
                "volume": option.get("volume"),
                "open_interest": option.get("openInterest"),
                "implied_volatility": option.get("impliedVolatility"),
            })
        return formatted