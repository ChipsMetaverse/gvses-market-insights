"""
Simple test of MTF Pivot Detector using synthetic TSLA-like data
Tests both algorithms without requiring running backend server
"""

import numpy as np
from pivot_detector_mtf import MTFPivotDetector
import json


def generate_tsla_like_data(num_bars: int = 200) -> dict:
    """
    Generate synthetic price data resembling TSLA movement
    Simulates uptrend with pullbacks
    """
    np.random.seed(42)

    # Start at $400, trend up to $450 with volatility
    base_prices = np.linspace(400, 450, num_bars)

    # Add noise and swing structure
    noise = np.random.normal(0, 5, num_bars)
    swings = 10 * np.sin(np.linspace(0, 6 * np.pi, num_bars))

    closes = base_prices + noise + swings

    # Generate OHLC
    highs = closes + np.abs(np.random.normal(0, 2, num_bars))
    lows = closes - np.abs(np.random.normal(0, 2, num_bars))
    opens = closes + np.random.normal(0, 1, num_bars)

    # Ensure OHLC consistency
    for i in range(num_bars):
        high_val = max(opens[i], closes[i], highs[i])
        low_val = min(opens[i], closes[i], lows[i])
        highs[i] = high_val
        lows[i] = low_val

    timestamps = np.arange(num_bars) * 3600  # 1-hour bars

    return {
        'timestamps': timestamps,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes
    }


def find_swings_old_method(data: np.ndarray, is_high: bool, window: int = 5) -> list:
    """
    Old algorithm from pattern_detection.py
    Fixed 5-bar window approach
    """
    swings = []
    for i in range(window, len(data) - window):
        if is_high:
            # Swing high: higher than all surrounding points
            if all(data[i] >= data[i-window:i]) and all(data[i] >= data[i+1:i+window+1]):
                swings.append(i)
        else:
            # Swing low: lower than all surrounding points
            if all(data[i] <= data[i-window:i]) and all(data[i] <= data[i+1:i+window+1]):
                swings.append(i)
    return swings


def main():
    """Test both algorithms"""
    print("=" * 70)
    print("MTF Pivot Detector Test - Synthetic TSLA Data")
    print("=" * 70)

    # Generate data
    print("\n1. Generating synthetic TSLA-like data...")
    data = generate_tsla_like_data(200)
    print(f"   ✓ Generated {len(data['close'])} bars")
    print(f"   ✓ Price range: ${data['low'].min():.2f} - ${data['high'].max():.2f}")

    # Test OLD algorithm
    print("\n2. Testing OLD algorithm (5-bar window)...")
    old_swing_highs = find_swings_old_method(data['high'], is_high=True, window=5)
    old_swing_lows = find_swings_old_method(data['low'], is_high=False, window=5)
    old_total = len(old_swing_highs) + len(old_swing_lows)

    print(f"   Algorithm: 5-bar window (current)")
    print(f"   Swing Highs: {len(old_swing_highs)}")
    print(f"   Swing Lows: {len(old_swing_lows)}")
    print(f"   Total Swings: {old_total}")

    # Test NEW algorithm
    print("\n3. Testing NEW algorithm (2-2 window + filters)...")
    detector = MTFPivotDetector(left_bars=2, right_bars=2)

    # Raw pivots (no filters)
    pivot_highs_raw, pivot_lows_raw = detector.find_pivots_single_tf(
        data['high'],
        data['low'],
        data['timestamps']
    )
    raw_total = len(pivot_highs_raw) + len(pivot_lows_raw)

    print(f"   Raw Pivots (2-2 window, no filters): {raw_total}")
    print(f"     - Pivot Highs: {len(pivot_highs_raw)}")
    print(f"     - Pivot Lows: {len(pivot_lows_raw)}")

    # Filtered pivots
    pivot_highs_filtered, pivot_lows_filtered = detector.detect_pivots_with_filters(
        data['high'],
        data['low'],
        data['timestamps'],
        apply_spacing=True,
        apply_percent_filter=True,
        apply_trend_filter=True,
        trend_direction="auto"
    )
    filtered_total = len(pivot_highs_filtered) + len(pivot_lows_filtered)

    print(f"\n   Filtered Pivots (spacing + % + trend): {filtered_total}")
    print(f"     - Pivot Highs: {len(pivot_highs_filtered)}")
    print(f"     - Pivot Lows: {len(pivot_lows_filtered)}")

    # Show details of filtered pivots
    if pivot_highs_filtered:
        print(f"\n   Pivot Highs Detail:")
        for i, p in enumerate(pivot_highs_filtered[:10]):  # Show first 10
            print(f"     #{i+1}: Bar {p.index}, Price ${p.price:.2f}")

    if pivot_lows_filtered:
        print(f"\n   Pivot Lows Detail:")
        for i, p in enumerate(pivot_lows_filtered[:10]):  # Show first 10
            print(f"     #{i+1}: Bar {p.index}, Price ${p.price:.2f}")

    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)
    print(f"Old Algorithm (5-bar): {old_total} swings")
    print(f"New Algorithm (raw):   {raw_total} pivots")
    print(f"New Algorithm (filtered): {filtered_total} pivots")

    reduction_from_old = old_total - filtered_total
    reduction_pct = (reduction_from_old / old_total) * 100 if old_total > 0 else 0

    print(f"\nReduction from OLD: {reduction_from_old} swings ({reduction_pct:.1f}%)")

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    if filtered_total <= 4:
        print("✓ EXCELLENT: Very few pivots - should produce 1-2 clean trendlines")
    elif filtered_total <= 8:
        print("✓ GOOD: Reasonable number of pivots - should produce 2-3 trendlines")
    elif filtered_total <= 15:
        print("⚠ FAIR: Moderate pivots - may still produce multiple trendlines")
    else:
        print("✗ TOO MANY: Still detecting too many pivots")

    print("\nFilters applied:")
    print(f"  - Left/Right bars: {detector.left_bars}/{detector.right_bars}")
    print(f"  - Min spacing: {detector.min_spacing_bars} bars")
    print(f"  - Min percent move: {detector.min_percent_move * 100}%")
    print(f"  - Trend structure: enabled")

    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    if filtered_total > 10:
        print("To reduce pivot count further, try:")
        print("  1. Increase min_spacing_bars to 10-15")
        print("  2. Increase min_percent_move to 2-3%")
        print("  3. Use stricter trend structure filters")
    elif filtered_total < 4:
        print("Very few pivots detected. Consider:")
        print("  1. Decreasing min_spacing_bars to 3-4")
        print("  2. Decreasing min_percent_move to 0.5%")
    else:
        print("✓ Pivot count looks optimal for 2-3 trendline generation")

    # Save results
    results = {
        'test_type': 'synthetic_tsla',
        'data_points': len(data['close']),
        'price_range': {
            'low': float(data['low'].min()),
            'high': float(data['high'].max())
        },
        'old_algorithm': {
            'window': 5,
            'swing_highs': len(old_swing_highs),
            'swing_lows': len(old_swing_lows),
            'total': old_total
        },
        'new_algorithm': {
            'left_bars': detector.left_bars,
            'right_bars': detector.right_bars,
            'min_spacing': detector.min_spacing_bars,
            'min_percent': detector.min_percent_move,
            'raw_total': raw_total,
            'filtered_total': filtered_total,
            'pivot_highs': len(pivot_highs_filtered),
            'pivot_lows': len(pivot_lows_filtered)
        },
        'reduction': {
            'absolute': reduction_from_old,
            'percentage': reduction_pct
        }
    }

    with open('/tmp/pivot_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n✓ Results saved to /tmp/pivot_test_results.json")


if __name__ == "__main__":
    main()
