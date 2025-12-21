#!/usr/bin/env python3
"""
Deep debug for 15m interval failure
"""
import requests
import numpy as np
from datetime import datetime
from pivot_detector_mtf import MTFPivotDetector
from trendline_builder import TrendlineBuilder

# Get 15m data
response = requests.get(
    "http://localhost:8000/api/stock-history",
    params={'symbol': 'TSLA', 'interval': '15m', 'days': 7}
)
data = response.json()
candles = data.get('candles', data)  # Handle both response formats

print(f"15m Candle Data: {len(candles)} bars")

# Convert to expected format for pattern detection
formatted_candles = []
for c in candles:
    # Parse timestamp string to Unix timestamp
    if isinstance(c.get('timestamp'), str):
        dt = datetime.fromisoformat(c['timestamp'].replace('+00:00', ''))
        timestamp = int(dt.timestamp())
    else:
        timestamp = int(c.get('timestamp', c.get('time', 0)))

    formatted_candles.append({
        'time': timestamp,
        'open': float(c['open']),
        'high': float(c['high']),
        'low': float(c['low']),
        'close': float(c['close']),
        'volume': float(c['volume'])
    })

# Extract OHLC
highs = np.array([c['high'] for c in formatted_candles])
lows = np.array([c['low'] for c in formatted_candles])
timestamps = np.array([c['time'] for c in formatted_candles])

# Test pivot detection
pivot_detector = MTFPivotDetector(left_bars=2, right_bars=2)

# Try resampling to 4H
htf_high, htf_low, htf_timestamps = pivot_detector.resample_to_higher_timeframe(
    formatted_candles,
    htf_interval_seconds=14400
)

print(f"HTF (4H) bars after resampling: {len(htf_high)}")
print(f"Condition len(htf_high) >= 5: {len(htf_high) >= 5}")

if len(htf_high) >= 5:
    print("\n=== Using MTF Path ===")
    pivot_highs, pivot_lows = pivot_detector.find_htf_pivots_confirmed_ltf(
        htf_high, htf_low, htf_timestamps,
        highs, lows, timestamps
    )
    print(f"MTF Pivots: {len(pivot_highs)} highs, {len(pivot_lows)} lows")
else:
    print("\n=== Using Single TF Path ===")
    pivot_highs, pivot_lows = pivot_detector.detect_pivots_with_filters(
        highs, lows, timestamps,
        apply_spacing=True,
        apply_percent_filter=True,
        apply_trend_filter=True
    )
    print(f"Single TF Pivots: {len(pivot_highs)} highs, {len(pivot_lows)} lows")

# Calculate adaptive spacing
total_bars = len(highs)
adaptive_spacing = max(3, int(0.05 * total_bars))
print(f"\nAdaptive spacing calculation:")
print(f"  Total bars: {total_bars}")
print(f"  Formula: max(3, int(0.05 * {total_bars})) = {adaptive_spacing}")

# Try trendline building with different min_touches
trendline_builder = TrendlineBuilder(touch_tolerance_percent=0.005)

print(f"\n=== Trendline Building Attempts ===")
for min_touches in [3, 2]:
    support_line = trendline_builder.build_support_line(
        pivot_lows, lows, min_touches=min_touches
    )
    resistance_line = trendline_builder.build_resistance_line(
        pivot_highs, highs, min_touches=min_touches
    )

    support_status = f"✅ {support_line.touches} touches" if support_line else "❌ None"
    resistance_status = f"✅ {resistance_line.touches} touches" if resistance_line else "❌ None"

    print(f"min_touches={min_touches}:")
    print(f"  Support: {support_status}")
    print(f"  Resistance: {resistance_status}")
