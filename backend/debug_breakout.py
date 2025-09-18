#!/usr/bin/env python3
"""
Debug script to understand breakout detection
"""

import json
from pathlib import Path
from pattern_detection import PatternDetector

# Load the support_breakout fixture
fixture_path = Path("fixtures/support_breakout.json")
with open(fixture_path, 'r') as f:
    fixture = json.load(f)

print("Candle analysis for breakout:")
print("=" * 50)

for i, candle in enumerate(fixture["candles"]):
    print(f"Index {i}: Open={candle['open']}, Close={candle['close']}, Volume={candle['volume']}")

print("\n" + "=" * 50)
print("Looking for breakout at index 8:")
print(f"Index 7: Close = {fixture['candles'][7]['close']}")
print(f"Index 8: Close = {fixture['candles'][8]['close']}")
print(f"Index 8: Volume = {fixture['candles'][8]['volume']}")

# Calculate average volume for first 8 candles
avg_vol = sum(c['volume'] for c in fixture['candles'][:8]) / 8
print(f"Avg volume (first 8): {avg_vol}")
print(f"Volume ratio at index 8: {fixture['candles'][8]['volume'] / avg_vol:.2f}x")

print("\n" + "=" * 50)
print("Running pattern detection:")

detector = PatternDetector(fixture["candles"])
results = detector.detect_all_patterns()

print(f"Support levels: {results['active_levels']['support']}")
print(f"Resistance levels: {results['active_levels']['resistance']}")

# Check for any resistance around 100
print(f"\nNeed resistance around 100 for breakout detection")
print(f"Current resistance levels: {results['active_levels']['resistance']}")

# Check breakout patterns
breakout_patterns = [p for p in results["detected"] if "breakout" in p["type"] or "breakdown" in p["type"]]
print(f"\nBreakout/Breakdown patterns: {len(breakout_patterns)}")
for pattern in breakout_patterns:
    print(f"  - {pattern['type']} at candle {pattern['start_candle']}-{pattern['end_candle']}")
    print(f"    Description: {pattern['description']}")
    print(f"    Confidence: {pattern['confidence']}%")