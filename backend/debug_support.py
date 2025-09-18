#!/usr/bin/env python3
"""
Debug script to understand support level detection
"""

import json
from pathlib import Path
from pattern_detection import PatternDetector

# Load the support_breakout fixture
fixture_path = Path("fixtures/support_breakout.json")
with open(fixture_path, 'r') as f:
    fixture = json.load(f)

# Create detector
detector = PatternDetector(fixture["candles"])

# Manually check the data
print("Candle data analysis:")
print("=" * 50)

lows = [c['low'] for c in fixture["candles"]]
highs = [c['high'] for c in fixture["candles"]]

print(f"All lows: {lows}")
print(f"Unique lows: {sorted(set(lows))}")
print(f"95 appears {lows.count(95)} times in lows")
print(f"Values close to 95: {[l for l in lows if 94.5 <= l <= 95.5]}")

print("\n" + "=" * 50)
print("Running detection:")

# Run detection
results = detector.detect_all_patterns()

print(f"Support levels detected: {results['active_levels']['support']}")
print(f"Resistance levels detected: {results['active_levels']['resistance']}")

# Check breakout patterns
breakout_patterns = [p for p in results["detected"] if "breakout" in p["type"]]
print(f"\nBreakout patterns: {len(breakout_patterns)}")
for pattern in breakout_patterns:
    print(f"  - {pattern['description']}")

# Let's check what percentiles give us
import numpy as np
print("\n" + "=" * 50)
print("Percentile analysis:")
print(f"0th percentile (min): {np.percentile(lows, 0)}")
print(f"10th percentile: {np.percentile(lows, 10)}")
print(f"25th percentile: {np.percentile(lows, 25)}")

# Count touches manually
level_95 = 95.0
touches = sum(1 for l in lows if abs(l - level_95) / level_95 < 0.02)  # Within 2%
print(f"\nTouches of 95 level (within 2%): {touches}")