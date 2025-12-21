"""
Test MTF Pivot Detector on Real TSLA Data
Compares old 5-bar window approach with new 2-2 window + filters
"""

import asyncio
import numpy as np
from pivot_detector_mtf import MTFPivotDetector
from pattern_detection import PatternDetector
from typing import Dict, Any
import json


async def fetch_tsla_data() -> Dict[str, Any]:
    """Fetch real TSLA 1H data from API"""
    import aiohttp

    async with aiohttp.ClientSession() as session:
        url = "http://localhost:8000/api/stock-history"
        params = {"symbol": "TSLA", "days": 30}  # 30 days of 1H data

        async with session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"API returned {response.status}")
            data = await response.json()
            return data


def extract_price_arrays(candles: list) -> Dict[str, np.ndarray]:
    """Extract OHLC arrays from candle data"""
    timestamps = np.array([c['time'] for c in candles])
    opens = np.array([c['open'] for c in candles])
    highs = np.array([c['high'] for c in candles])
    lows = np.array([c['low'] for c in candles])
    closes = np.array([c['close'] for c in candles])

    return {
        'timestamps': timestamps,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes
    }


def test_old_algorithm(data: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """Test current 5-bar window algorithm"""
    detector = PatternDetector()

    # Use existing _find_swing_points method
    swing_highs = detector._find_swing_points(data['high'], is_high=True, window=5)
    swing_lows = detector._find_swing_points(data['low'], is_high=False, window=5)

    return {
        'algorithm': 'Old (5-bar window)',
        'swing_high_count': len(swing_highs),
        'swing_low_count': len(swing_lows),
        'total_swings': len(swing_highs) + len(swing_lows),
        'swing_highs': swing_highs[:10],  # First 10 for inspection
        'swing_lows': swing_lows[:10]
    }


def test_new_algorithm(data: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """Test new 2-2 window + filters algorithm"""
    detector = MTFPivotDetector(left_bars=2, right_bars=2)

    # Test 1: Basic pivot detection (no filters)
    pivot_highs_raw, pivot_lows_raw = detector.find_pivots_single_tf(
        data['high'],
        data['low'],
        data['timestamps']
    )

    # Test 2: With all filters
    pivot_highs_filtered, pivot_lows_filtered = detector.detect_pivots_with_filters(
        data['high'],
        data['low'],
        data['timestamps'],
        apply_spacing=True,
        apply_percent_filter=True,
        apply_trend_filter=True
    )

    return {
        'algorithm': 'New (2-2 window + filters)',
        'raw_pivot_high_count': len(pivot_highs_raw),
        'raw_pivot_low_count': len(pivot_lows_raw),
        'raw_total': len(pivot_highs_raw) + len(pivot_lows_raw),
        'filtered_pivot_high_count': len(pivot_highs_filtered),
        'filtered_pivot_low_count': len(pivot_lows_filtered),
        'filtered_total': len(pivot_highs_filtered) + len(pivot_lows_filtered),
        'pivot_highs_sample': [
            {'index': p.index, 'price': p.price}
            for p in pivot_highs_filtered[:5]
        ],
        'pivot_lows_sample': [
            {'index': p.index, 'price': p.price}
            for p in pivot_lows_filtered[:5]
        ]
    }


async def main():
    """Main test runner"""
    print("=" * 60)
    print("Testing MTF Pivot Detector on TSLA 1H Data")
    print("=" * 60)

    # Fetch data
    print("\n1. Fetching TSLA data from API...")
    try:
        api_data = await fetch_tsla_data()
        candles = api_data.get('candles', [])

        if not candles:
            print("ERROR: No candles returned from API")
            return

        print(f"   ✓ Loaded {len(candles)} candles")

        # Extract arrays
        data = extract_price_arrays(candles)
        print(f"   ✓ Price range: ${data['low'].min():.2f} - ${data['high'].max():.2f}")

    except Exception as e:
        print(f"   ✗ Failed to fetch data: {e}")
        return

    # Test old algorithm
    print("\n2. Testing OLD algorithm (5-bar window)...")
    old_results = test_old_algorithm(data)
    print(f"   Algorithm: {old_results['algorithm']}")
    print(f"   Swing Highs: {old_results['swing_high_count']}")
    print(f"   Swing Lows: {old_results['swing_low_count']}")
    print(f"   Total Swings: {old_results['total_swings']}")

    # Test new algorithm
    print("\n3. Testing NEW algorithm (2-2 window + filters)...")
    new_results = test_new_algorithm(data)
    print(f"   Algorithm: {new_results['algorithm']}")
    print(f"   Raw Pivots (no filters): {new_results['raw_total']}")
    print(f"     - Pivot Highs: {new_results['raw_pivot_high_count']}")
    print(f"     - Pivot Lows: {new_results['raw_pivot_low_count']}")
    print(f"   Filtered Pivots: {new_results['filtered_total']}")
    print(f"     - Pivot Highs: {new_results['filtered_pivot_high_count']}")
    print(f"     - Pivot Lows: {new_results['filtered_pivot_low_count']}")

    # Show sample pivots
    if new_results['pivot_highs_sample']:
        print("\n   Sample Pivot Highs (first 5):")
        for p in new_results['pivot_highs_sample']:
            print(f"     Bar {p['index']}: ${p['price']:.2f}")

    if new_results['pivot_lows_sample']:
        print("\n   Sample Pivot Lows (first 5):")
        for p in new_results['pivot_lows_sample']:
            print(f"     Bar {p['index']}: ${p['price']:.2f}")

    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    print(f"Old Algorithm Total Swings: {old_results['total_swings']}")
    print(f"New Algorithm Total Pivots: {new_results['filtered_total']}")

    reduction = old_results['total_swings'] - new_results['filtered_total']
    reduction_pct = (reduction / old_results['total_swings']) * 100 if old_results['total_swings'] > 0 else 0

    print(f"\nReduction: {reduction} swings ({reduction_pct:.1f}%)")

    if new_results['filtered_total'] <= 10:
        print("✓ SUCCESS: New algorithm produces significantly fewer pivots")
    else:
        print("⚠ WARNING: Still producing many pivots, may need stricter filters")

    # Save detailed results
    results = {
        'test_date': '2025-11-30',
        'symbol': 'TSLA',
        'timeframe': '1H',
        'candle_count': len(candles),
        'old_algorithm': old_results,
        'new_algorithm': new_results,
        'reduction': {
            'absolute': reduction,
            'percentage': reduction_pct
        }
    }

    with open('/tmp/pivot_detection_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n✓ Detailed results saved to /tmp/pivot_detection_test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
