from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .http_mcp_client import get_http_mcp_client as get_direct_mcp_client  # Using HTTP for better performance

logger = logging.getLogger(__name__)


async def get_related_news(symbol: str, limit: int = 6) -> dict:
    """Get related news - REAL DATA ONLY"""
    
    try:
        # Get real news from MCP server  
        client = await get_direct_mcp_client()
        # Get market news (MCP server handles symbol-specific news internally)
        result = await client.call_tool("get_market_news", {
            "limit": limit
        })
        
        logger.info(f"MCP news result type: {type(result)}")
        logger.info(f"MCP raw result keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
        
        # Handle MCP response format: result.result.content[0].text contains JSON string
        news_items = []
        if result and isinstance(result, dict):
            # Extract the actual data from MCP response structure
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if content and len(content) > 0 and "text" in content[0]:
                    import json
                    json_text = content[0]["text"]
                    logger.info(f"Parsing JSON text: {json_text[:200]}...")
                    news_data = json.loads(json_text)
                    news_items = news_data.get("articles", [])
                    logger.info(f"Extracted {len(news_items)} news articles")
            # Fallback for direct format
            elif "articles" in result:
                news_items = result["articles"]
            elif isinstance(result, list):
                news_items = result
        
        if news_items and len(news_items) > 0:
            # Map MCP news format to our format
            items = []
            
            # Default image URLs for different news categories
            image_urls = {
                "earnings": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&h=225&fit=crop",
                "analysis": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=225&fit=crop",
                "partnership": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=400&h=225&fit=crop",
                "trading": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=400&h=225&fit=crop",
                "interview": "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=225&fit=crop",
                "charts": "https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=400&h=225&fit=crop",
                "esg": "https://images.unsplash.com/photo-1569163139394-de4798aa62b6?w=400&h=225&fit=crop",
                "institutional": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=225&fit=crop",
                "default": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=225&fit=crop"
            }
            
            # Filter CNBC news for symbol relevance or supplement with Yahoo Finance
            symbol_lower = symbol.lower()
            relevant_cnbc_news = []
            
            for i, news_item in enumerate(news_items):
                title_lower = news_item.get("title", "").lower()
                description_lower = news_item.get("description", "").lower()
                
                # Check if CNBC article mentions the symbol
                if (symbol_lower in title_lower or 
                    symbol_lower in description_lower or 
                    len(relevant_cnbc_news) < 2):  # Always keep some CNBC news
                    relevant_cnbc_news.append(news_item)
            
            # If we have very few symbol-relevant CNBC articles, get specific news from Yahoo Finance
            if len(relevant_cnbc_news) < 3:
                try:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        # Yahoo Finance symbol-specific news
                        yahoo_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={symbol}&newsCount={limit-len(relevant_cnbc_news)}"
                        headers = {"User-Agent": "Mozilla/5.0 (compatible; MarketBot/1.0)"}
                        response = await client.get(yahoo_url, headers=headers, timeout=10.0)
                        
                        if response.status_code == 200:
                            yahoo_data = response.json()
                            yahoo_news = yahoo_data.get("news", [])
                            
                            # Add Yahoo Finance news to supplement CNBC
                            for yahoo_item in yahoo_news:
                                relevant_cnbc_news.append({
                                    "title": yahoo_item.get("title", ""),
                                    "description": yahoo_item.get("summary", ""),
                                    "source": "Yahoo Finance", 
                                    "publishedAt": yahoo_item.get("providerPublishTime", ""),
                                    "url": yahoo_item.get("link", "")
                                })
                                
                except Exception as e:
                    logger.warning(f"Failed to fetch Yahoo Finance supplement: {e}")
                    
            # Use the relevant news (CNBC + Yahoo Finance supplement)
            news_items = relevant_cnbc_news[:limit]
            
            for i, news_item in enumerate(news_items[:limit]):
                # Determine category for image
                title_lower = news_item.get("title", "").lower()
                image_category = "default"
                if "earnings" in title_lower or "revenue" in title_lower:
                    image_category = "earnings"
                elif "analyst" in title_lower or "upgrade" in title_lower or "downgrade" in title_lower:
                    image_category = "analysis"
                elif "partner" in title_lower or "deal" in title_lower:
                    image_category = "partnership"
                elif "option" in title_lower or "trading" in title_lower:
                    image_category = "trading"
                elif "ceo" in title_lower or "interview" in title_lower:
                    image_category = "interview"
                elif "technical" in title_lower or "chart" in title_lower:
                    image_category = "charts"
                elif "esg" in title_lower or "sustain" in title_lower:
                    image_category = "esg"
                elif "fund" in title_lower or "institution" in title_lower:
                    image_category = "institutional"
                
                published_at = news_item.get("publishedAt", news_item.get("published_at", datetime.now().isoformat()))
                description = news_item.get("description", news_item.get("summary", ""))
                url = news_item.get("url", news_item.get("link", "#"))
                
                items.append({
                    # Standard format (for dashboard)
                    "id": f"{symbol}-news-{i+1}",
                    "title": news_item.get("title", ""),
                    "source": news_item.get("source", news_item.get("publisher", "Unknown")),
                    "published_at": published_at,
                    "url": url,
                    "image_url": news_item.get("image", news_item.get("urlToImage", image_urls.get(image_category, image_urls["default"]))),
                    "description": description,
                    "tickers": news_item.get("tickers", [symbol]),
                    # Frontend-compatible aliases
                    "link": url,
                    "published": published_at,
                    "summary": description,
                    "time": news_item.get("time", "")
                })
            
            return {"articles": items, "items": items}  # Return both for compatibility
        else:
            # No news available - return empty list instead of fake news
            logger.info(f"No news available for {symbol}")
            return {"articles": [], "items": []}
            
    except Exception as e:
        logger.error(f"Failed to fetch real news for {symbol}: {e}")
        # Return empty news list instead of fake data
        return {"articles": [], "items": []}


async def fetch_news_from_provider(symbol: str, limit: int = 6) -> List[Dict[str, Any]]:
    """Fetch news from actual news provider - REAL DATA ONLY"""
    result = await get_related_news(symbol, limit)
    return result["items"]