from typing import List, Dict, Any
from datetime import datetime, timedelta
import random


def get_related_news(symbol: str, limit: int = 6) -> dict:
    """Get related news with image URLs
    
    In production, this would fetch from a real news API.
    For now, returns mock data with realistic structure.
    """
    
    # Mock news items
    mock_news = [
        {
            "title": f"{symbol} Reports Strong Q4 Earnings Beat, Raises Guidance",
            "source": "MarketWatch",
            "description": "Company exceeds analyst expectations with 15% revenue growth year-over-year",
            "image_category": "earnings"
        },
        {
            "title": f"Analysts Upgrade {symbol} Price Target Following Product Launch",
            "source": "Reuters",
            "description": "Multiple Wall Street firms raise price targets after successful new product rollout",
            "image_category": "analysis"
        },
        {
            "title": f"{symbol} Announces Strategic Partnership to Expand Market Reach",
            "source": "Bloomberg",
            "description": "Partnership expected to accelerate growth in international markets",
            "image_category": "partnership"
        },
        {
            "title": f"Options Activity Suggests Bullish Sentiment for {symbol}",
            "source": "Benzinga",
            "description": "Unusual call volume indicates institutional buying interest",
            "image_category": "trading"
        },
        {
            "title": f"{symbol} CEO Discusses Innovation Strategy in Exclusive Interview",
            "source": "CNBC",
            "description": "Leadership outlines vision for AI integration and market expansion",
            "image_category": "interview"
        },
        {
            "title": f"Technical Analysis: {symbol} Breaks Key Resistance Level",
            "source": "TradingView",
            "description": "Stock shows strong momentum after clearing 200-day moving average",
            "image_category": "charts"
        },
        {
            "title": f"{symbol} Included in S&P 500 ESG Index",
            "source": "Financial Times",
            "description": "Recognition for sustainability initiatives drives investor interest",
            "image_category": "esg"
        },
        {
            "title": f"Hedge Funds Increase {symbol} Stakes in Q4 Filings",
            "source": "Seeking Alpha",
            "description": "13F filings reveal significant position increases by major funds",
            "image_category": "institutional"
        }
    ]
    
    # Placeholder images by category
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
    
    # Select random news items
    selected_news = random.sample(mock_news, min(limit, len(mock_news)))
    
    # Build news items
    items = []
    for i, news in enumerate(selected_news):
        # Generate realistic timestamps
        hours_ago = random.randint(1, 48)
        published_at = datetime.now() - timedelta(hours=hours_ago)
        
        items.append({
            "id": f"{symbol}-news-{i+1}",
            "title": news["title"],
            "source": news["source"],
            "published_at": published_at.isoformat(),
            "url": f"https://example.com/news/{symbol.lower()}-{i+1}",
            "image_url": image_urls.get(news["image_category"], image_urls["default"]),
            "description": news.get("description"),
            "tickers": [symbol]
        })
    
    # Sort by published date (most recent first)
    items.sort(key=lambda x: x["published_at"], reverse=True)
    
    return {"items": items}


def fetch_news_from_provider(symbol: str, limit: int = 6) -> List[Dict[str, Any]]:
    """Fetch news from actual news provider
    
    This would integrate with NewsAPI, Alpha Vantage, or similar.
    Currently returns mock data.
    """
    # In production, this would make actual API calls
    # Example:
    # response = requests.get(f"https://newsapi.org/v2/everything?q={symbol}")
    # return normalize_news_response(response.json())
    
    return get_related_news(symbol, limit)["items"]