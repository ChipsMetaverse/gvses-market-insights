#!/usr/bin/env python3
"""Test the ideal response formatter with real market data."""

import asyncio
from services.market_service_factory import MarketServiceFactory
from response_formatter import MarketResponseFormatter

async def test_ideal_format():
    # Get market service
    service = MarketServiceFactory.get_service()
    
    print("Fetching real market data for AAPL...")
    
    # Fetch comprehensive data
    comp_data = await service.get_comprehensive_stock_data('AAPL')
    price_data = comp_data.get('price_data', {})
    technical_levels = comp_data.get('technical_levels', {})
    
    # Fetch news
    news_result = await service.get_stock_news('AAPL', limit=5)
    news_items = news_result.get('articles', [])
    
    # Mock after-hours data (not available in current API)
    after_hours = {
        'price': price_data.get('price', 0) + 0.50,
        'change': 0.50,
        'change_percent': 0.21,
        'volume': 1500000
    }
    
    # Format using ideal formatter
    company_name = "Apple Inc."
    formatted_response = MarketResponseFormatter.format_stock_snapshot_ideal(
        'AAPL',
        company_name,
        price_data,
        news_items,
        technical_levels,
        after_hours
    )
    
    print("\n" + "="*60)
    print("IDEAL FORMATTED RESPONSE:")
    print("="*60)
    print(formatted_response)
    print("\n" + "="*60)
    print(f"Total length: {len(formatted_response)} characters")
    
    # Check key sections are present
    sections = [
        "## Here's your real-time",
        "Market Snapshot & Context",
        "Key Headlines",
        "Technical Overview & Forecasts",
        "Broader Trends & Forecasts",
        "Summary Table",
        "Strategic Insights",
        "Would you like me to dive deeper",
        "Disclaimer"
    ]
    
    print("\nSection Check:")
    for section in sections:
        present = "✓" if section in formatted_response else "✗"
        print(f"  {present} {section}")

if __name__ == "__main__":
    asyncio.run(test_ideal_format())