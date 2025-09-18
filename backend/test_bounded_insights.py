#!/usr/bin/env python3
"""Test the bounded LLM insights feature (Day 4.2)."""

import asyncio
from services.agent_orchestrator import get_orchestrator

async def test_bounded_insights():
    orchestrator = get_orchestrator()
    
    # Test contexts with different market scenarios
    test_cases = [
        {
            'name': 'Bullish momentum',
            'context': {
                'symbol': 'TSLA',
                'price_data': {
                    'price': 425.50,
                    'change': 15.20,
                    'change_percent': 3.70
                },
                'technical_levels': {
                    'se_level': 430,
                    'buy_low_level': 380,
                    'btd_level': 350,
                    'retest_level': 410
                }
            }
        },
        {
            'name': 'Bearish pressure',
            'context': {
                'symbol': 'AAPL',
                'price_data': {
                    'price': 230.00,
                    'change': -5.50,
                    'change_percent': -2.34
                },
                'technical_levels': {
                    'se_level': 240,
                    'buy_low_level': 228,
                    'btd_level': 220,
                    'retest_level': 235
                }
            }
        },
        {
            'name': 'Consolidation',
            'context': {
                'symbol': 'NVDA',
                'price_data': {
                    'price': 950.25,
                    'change': 2.15,
                    'change_percent': 0.23
                },
                'technical_levels': {
                    'se_level': 960,
                    'buy_low_level': 940,
                    'btd_level': 920,
                    'retest_level': 950
                }
            }
        }
    ]
    
    print("Testing Bounded LLM Insights (Day 4.2)")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Symbol: {test['context']['symbol']}")
        print(f"Price: ${test['context']['price_data']['price']:.2f}")
        print(f"Change: {test['context']['price_data']['change_percent']:.2f}%")
        print("-" * 40)
        
        try:
            # Test with different character limits
            for max_chars in [150, 250, 400]:
                insight = await orchestrator._generate_bounded_insight(
                    test['context'], 
                    max_chars=max_chars
                )
                print(f"\n[Max {max_chars} chars] (Actual: {len(insight)} chars)")
                print(f"Insight: {insight}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing fallback insights (when LLM unavailable)")
    print("=" * 60)
    
    # Test fallback directly
    for test in test_cases:
        print(f"\nFallback for: {test['name']}")
        fallback = orchestrator._generate_fallback_insight(test['context'], 200)
        print(f"Fallback ({len(fallback)} chars): {fallback}")

if __name__ == "__main__":
    asyncio.run(test_bounded_insights())