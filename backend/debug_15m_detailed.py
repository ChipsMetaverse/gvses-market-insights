#!/usr/bin/env python3
"""
Deep debug for 15m interval - detailed HTF analysis
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
candles = data.get('candles', data)

print(f"15m Candle Data: {len(candles)} bars\n")

# Convert to expected format
formatted_candles = []
for c in candles:
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

# Create pivot detector
pivot_detector = MTFPivotDetector(left_bars=2, right_bars=2)

# Resample to 4H
htf_high, htf_low, htf_timestamps = pivot_detector.resample_to_higher_timeframe(
    formatted_candles,
    htf_interval_seconds=14400
)

print(f"=== HTF (4H) Analysis ===")
print(f"HTF bars: {len(htf_high)}")
print(f"Adaptive spacing: max(3, int(0.05 * {len(htf_high)})) = {max(3, int(0.05 * len(htf_high)))}")
print()

# Step 1: Find raw pivots before filters
raw_highs, raw_lows = pivot_detector.find_pivots_single_tf(
    htf_high, htf_low, htf_timestamps
)
print(f"Raw pivots (no filters): {len(raw_highs)} highs, {len(raw_lows)} lows")

# Step 2: Apply only spacing filter
pivot_detector_copy = MTFPivotDetector(left_bars=2, right_bars=2)
highs_after_spacing, lows_after_spacing = pivot_detector_copy.detect_pivots_with_filters(
    htf_high, htf_low, htf_timestamps,
    apply_spacing=True,
    apply_percent_filter=False,
    apply_trend_filter=False
)
print(f"After spacing filter: {len(highs_after_spacing)} highs, {len(lows_after_spacing)} lows")

# Step 3: Apply spacing + percent filter
highs_after_percent, lows_after_percent = pivot_detector.detect_pivots_with_filters(
    htf_high, htf_low, htf_timestamps,
    apply_spacing=True,
    apply_percent_filter=True,
    apply_trend_filter=False
)
print(f"After spacing + percent filter: {len(highs_after_percent)} highs, {len(lows_after_percent)} lows")

print(f"\n=== Issue Analysis ===")
print(f"The problem: With only {len(htf_high)} HTF bars, even with adaptive spacing,")
print(f"we're getting {len(highs_after_percent)} highs and {len(lows_after_percent)} lows after filters.")
print(f"This is insufficient to build 2-touch or 3-touch trendlines.")
print()

# Try MTF with current filters
mtf_highs, mtf_lows = pivot_detector.find_htf_pivots_confirmed_ltf(
    htf_high, htf_low, htf_timestamps,
    highs, lows, timestamps
)
print(f"MTF confirmed pivots (HTF→LTF): {len(mtf_highs)} highs, {len(mtf_lows)} lows")

# Try direct single TF on 15m data
print(f"\n=== Alternative: Single TF on 15m Data ===")
direct_highs, direct_lows = pivot_detector.detect_pivots_with_filters(
    highs, lows, timestamps,
    apply_spacing=True,
    apply_percent_filter=True,
    apply_trend_filter=False
)
print(f"Direct 15m pivots: {len(direct_highs)} highs, {len(direct_lows)} lows")
print(f"Adaptive spacing for 15m: max(3, int(0.05 * {len(highs)})) = {max(3, int(0.05 * len(highs)))}")

# Try trendlines on direct 15m pivots
trendline_builder = TrendlineBuilder(touch_tolerance_percent=0.005)
for min_touches in [3, 2]:
    support = trendline_builder.build_support_line(direct_lows, lows, min_touches=min_touches)
    resistance = trendline_builder.build_resistance_line(direct_highs, highs, min_touches=min_touches)

    support_status = f"✅ {support.touches} touches" if support else "❌ None"
    resistance_status = f"✅ {resistance.touches} touches" if resistance else "❌ None"

    print(f"\nDirect 15m trendlines (min_touches={min_touches}):")
    print(f"  Support: {support_status}")
    print(f"  Resistance: {resistance_status}")

print(f"\n=== Recommendation ===")
print(f"The MTF path is failing because 15m → 4H resampling creates only {len(htf_high)} HTF bars,")
print(f"which produces too few pivots after filters.")
print(f"Solution: Lower the MTF threshold from 'len(htf_high) >= 5' to 'len(htf_high) >= 20'")
print(f"This will force 15m to use the single TF path, which has {len(highs)} bars to work with.")
