#!/usr/bin/env python3
"""Simple test of the ideal formatter with mock data."""

from response_formatter import MarketResponseFormatter

# Mock data
price_data = {
    'symbol': 'AAPL',
    'price': 230.50,
    'change': 2.34,
    'change_percent': 1.02,
    'open': 228.00,
    'day_high': 231.50,
    'day_low': 227.50,
    'volume': 45000000
}

technical_levels = {
    'btd_level': 212.06,      # Buy the Dip
    'buy_low_level': 221.28,  # Buy Low
    'retest_level': 225.89,   # Retest
    'se_level': 237.42        # Sell High
}

news_items = [
    {'title': 'Apple Announces New AI Features', 'source': 'CNBC'},
    {'title': 'Strong iPhone Sales in Q4', 'source': 'Yahoo Finance'}
]

after_hours = {
    'price': 231.00,
    'change': 0.50,
    'change_percent': 0.22,
    'volume': 2000000
}

llm_insight = "AAPL showing strong momentum above Buy Low level at $221.28, approaching Sell High resistance at $237.42."

# Format the response
formatted = MarketResponseFormatter.format_stock_snapshot_ideal(
    symbol='AAPL',
    company_name='Apple Inc.',
    price_data=price_data,
    news=news_items,
    technical_levels=technical_levels,
    after_hours=after_hours
)

print("="*60)
print("FORMATTED RESPONSE WITH TRADING LEVELS:")
print("="*60)
print(formatted)
print("="*60)

# Check for key trading levels
levels_check = {
    'BTD (Buy the Dip)': 'Buy the Dip' in formatted or 'BTD' in formatted,
    'Buy Low': 'Buy Low' in formatted,
    'Sell High': 'Sell High' in formatted,
    'Retest': 'Retest' in formatted
}

print("\nTRADING LEVELS CHECK:")
for level, found in levels_check.items():
    status = "✅" if found else "❌"
    print(f"{status} {level}: {'Found' if found else 'Not found'}")

if all(levels_check.values()):
    print("\n🎉 All trading levels are correctly displayed!")
else:
    print("\n⚠️ Some trading levels are missing from the output.")