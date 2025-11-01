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
    """Get related news - REAL DATA ONLY, TICKER-SPECIFIC - aggregates Yahoo Finance + CNBC"""
    
    try:
        # Aggregate news from MULTIPLE sources for comprehensive coverage
        all_articles = []
        sources_used = []
        
        # SOURCE 1: Yahoo Finance (TICKER-SPECIFIC)
        try:
            from .direct_market_service import DirectMarketDataService
            direct_service = DirectMarketDataService()
            yahoo_result = await direct_service.get_stock_news(symbol, limit)
            
            if yahoo_result and yahoo_result.get("articles") and len(yahoo_result["articles"]) > 0:
                yahoo_articles = yahoo_result["articles"]
                all_articles.extend(yahoo_articles)
                sources_used.append(f"Yahoo Finance ({len(yahoo_articles)} articles)")
                logger.info(f"✅ Yahoo Finance: {len(yahoo_articles)} {symbol}-specific articles")
        except Exception as e:
            logger.warning(f"Yahoo Finance news failed for {symbol}: {e}")
        
        # SOURCE 2: CNBC (TICKER-SPECIFIC via web scraping)
        try:
            import httpx
            from bs4 import BeautifulSoup
            
            # CNBC ticker-specific news via search
            cnbc_url = f"https://www.cnbc.com/search/?query={symbol}&qsearchterm={symbol}"
            async with httpx.AsyncClient() as client:
                response = await client.get(cnbc_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }, timeout=5.0)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    cnbc_articles = []
                    
                    # Extract search results
                    for result in soup.select('.SearchResult-searchResult')[:3]:  # Max 3 CNBC articles
                        title_elem = result.select_one('.SearchResult-searchResultTitle')
                        link_elem = result.select_one('a')
                        date_elem = result.select_one('.SearchResult-publishedDate')
                        
                        if title_elem and link_elem:
                            article = {
                                "title": title_elem.get_text(strip=True),
                                "link": link_elem.get('href', ''),
                                "source": "CNBC",
                                "published": date_elem.get_text(strip=True) if date_elem else "",
                                "summary": ""
                            }
                            cnbc_articles.append(article)
                    
                    if cnbc_articles:
                        all_articles.extend(cnbc_articles)
                        sources_used.append(f"CNBC ({len(cnbc_articles)} articles)")
                        logger.info(f"✅ CNBC: {len(cnbc_articles)} {symbol}-specific articles")
        except Exception as e:
            logger.warning(f"CNBC news failed for {symbol}: {e}")
        
        # If we have enough articles from Yahoo + CNBC, return them
        if len(all_articles) >= limit:
            logger.info(f"✅ Aggregated {len(all_articles)} ticker-specific articles from: {', '.join(sources_used)}")
            return {
                "articles": all_articles[:limit],
                "items": all_articles[:limit],
                "sources": sources_used,
                "data_source": "multi_source_aggregated"
            }
        
        # Fallback to MCP server ONLY if we have insufficient articles
        try:
            client = await get_direct_mcp_client()
            result = await client.call_tool("get_market_news", {
                "limit": limit  # Note: MCP get_market_news ignores symbol parameter
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
                        logger.info(f"Extracted {len(news_items)} MCP fallback articles")
                # Fallback for direct format
                elif "articles" in result:
                    news_items = result["articles"]
                elif isinstance(result, list):
                    news_items = result
            
            # Append MCP articles (generic market news) to supplement ticker-specific news
            if news_items and len(news_items) > 0:
                for item in news_items[:limit - len(all_articles)]:
                    all_articles.append({
                        "title": item.get("title", ""),
                        "link": item.get("url", item.get("link", "")),
                        "source": item.get("source", "Market News"),
                        "published": item.get("publishedAt", item.get("published_at", "")),
                        "summary": item.get("summary", item.get("description", ""))
                    })
                sources_used.append(f"MCP Fallback ({len(news_items)} articles)")
        except Exception as e:
            logger.warning(f"MCP fallback also failed: {e}")
        
        # Return all aggregated articles from all sources
        if len(all_articles) > 0:
            logger.info(f"✅ Final aggregated news: {len(all_articles)} articles from {', '.join(sources_used)}")
            return {
                "articles": all_articles[:limit],
                "items": all_articles[:limit],
                "sources": sources_used,
                "data_source": "multi_source_aggregated"
            }
        else:
            # No articles from any source
            logger.warning(f"⚠️  No news articles found for {symbol} from any source")
            return {
                "articles": [],
                "items": [],
                "sources": [],
                "data_source": "none"
            }
            
    except Exception as e:
        logger.error(f"❌ Failed to fetch news for {symbol}: {e}")
        # Return empty news list instead of fake data
        return {"articles": [], "items": [], "sources": [], "data_source": "error"}


async def fetch_news_from_provider(symbol: str, limit: int = 6) -> List[Dict[str, Any]]:
    """Fetch news from actual news provider - REAL DATA ONLY"""
    result = await get_related_news(symbol, limit)
    return result["items"]