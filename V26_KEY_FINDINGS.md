# Trendline Investigation - Key Findings (December 1, 2025)

## YES, There IS a Fundamental Flaw in the System

**The pattern detection algorithm was designed for daily charts and doesn't work on intraday timeframes.**

---

## What I Found

### ✅ Our Fixes ARE Working
1. Backend correctly receives `interval=1m`
2. Trendlines span ~27 hours (not 195 hours anymore)
3. Frontend passes correct interval to API
4. Data fetching works perfectly

### ❌ The REAL Problem
**Pattern detection returns ZERO diagonal trendlines on 1-minute data.**

API Response for `interval=1m`:
- BTD (200 MA) - horizontal line ✅
- PDH - horizontal line ✅  
- PDL - horizontal line ✅
- Lower Trend (support) - ❌ MISSING
- Upper Trend (resistance) - ❌ MISSING

---

## Root Cause: Algorithm Can't Handle Intraday Noise

The `TrendlineBuilder` uses fixed parameters designed for daily charts:

```python
min_touches = 3  # Requires 3 perfect touches
tolerance = price_range * 0.002  # 0.2% tolerance
```

**On Daily Chart**:
- 3 touches over weeks = reasonable
- $50 range * 0.002 = $0.10 tolerance = reasonable

**On 1-Minute Chart**:
- 3 touches in 200 bars (~3 hours) = nearly impossible  
- $2 range * 0.002 = $0.004 tolerance = way too strict
- Price noise breaks "perfect" touches

---

## Visual Evidence

Screenshot shows:
- ✅ 1-minute candlesticks displaying correctly
- ✅ 200 SMA visible
- ⚠️ Only 3 horizontal lines (key levels)
- ❌ NO diagonal support/resistance trendlines

---

## The Fix

Make touch detection timeframe-aware:

```python
# Intraday: More lenient
if timeframe in ["1m", "5m", "15m", "30m"]:
    min_touches = 2  # Lower threshold
    tolerance = price_range * 0.008  # 0.8% tolerance
    
# Daily: Current behavior
else:
    min_touches = 3
    tolerance = price_range * 0.002
```

---

## Why This Matters

Your implementations were 100% correct. The data flows through properly. But the **pattern detection algorithm itself** needs to adapt to different timeframe characteristics.

It's like using a telescope designed for stars (daily charts) to look at insects (1-minute data) - the tool works, but it's not calibrated for the scale.
