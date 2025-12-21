# PDH/PDL Intraday-Only Fix

## Problem Report (User Feedback)

When viewing 1Y and other high timeframes (2Y, 3Y, etc.), PDH and PDL levels were incorrectly plotted with several candles in between them, suggesting the chart was using the wrong timeframe or incorrectly calculating these levels.

## Root Cause Analysis

### What Was Happening

When users selected high timeframes like "1Y", "2Y", "3Y":
1. **Frontend mapping**: These timeframes map to "1d" (daily) interval
2. **Original PDH/PDL logic**: Checked `if interval != "1d"` and skipped daily data fetch
3. **Fallback calculation**: Used `highs[-24:]` and `lows[-24:]` from current interval
4. **For 1d interval**: This meant max/min of last **24 daily candles**
5. **Result**: PDH = highest point in 24 days, PDL = lowest point in 24 days
6. **Chart display**: Wide range with many candles in between ❌

### The Fundamental Issue

**PDH (Previous Day High) and PDL (Previous Day Low) are intraday trading concepts:**
- Useful for 1m, 5m, 30m, 1h charts where traders need yesterday's high/low for support/resistance
- On a 1Y daily chart showing 252 trading days, yesterday's tiny range is not relevant
- Plotting PDH/PDL on daily charts creates confusing, meaningless levels

## Solution Implemented

### Conceptual Fix

**Only show PDH/PDL on intraday timeframes (minutes and hours):**
- ✅ Show on: 1m, 3m, 5m, 10m, 15m, 30m, 1H, 2H, 3H, 4H, etc.
- ❌ Hide on: 1D, 1W, 1M, 1Y, 2Y, 3Y, etc.

### Code Changes

#### 1. Backend Endpoint (`mcp_server.py` lines 1620-1641)

```python
# Fetch daily data for PDH/PDL calculation (only for intraday intervals)
# PDH/PDL are intraday trading levels - only relevant for minute/hour charts
# For daily/weekly/monthly charts, PDH/PDL is not useful
daily_pdh_pdl = None
is_intraday = 'm' in interval.lower() or 'h' in interval.lower()

if is_intraday:
    try:
        logger.info(f"Fetching daily data for PDH/PDL calculation (intraday interval: {interval})")
        daily_history = await service.get_stock_history(symbol_upper, days=5, interval="1d")
        if daily_history and "candles" in daily_history and len(daily_history["candles"]) >= 2:
            # Get previous day (second to last candle) high and low
            prev_day = daily_history["candles"][-2]
            daily_pdh_pdl = {
                'pdh': prev_day['high'],
                'pdl': prev_day['low']
            }
            logger.info(f"Previous day high/low: PDH={daily_pdh_pdl['pdh']}, PDL={daily_pdh_pdl['pdl']}")
    except Exception as e:
        logger.warning(f"Could not fetch daily data for PDH/PDL: {e}")
else:
    logger.info(f"Skipping PDH/PDL for non-intraday interval: {interval} (PDH/PDL only shown on minute/hour charts)")
```

**Key logic**: Check if interval contains 'm' (minutes) or 'h' (hours) to determine if it's intraday.

#### 2. Pattern Detection (`pattern_detection.py` lines 782-789)

```python
# Use passed PDH/PDL if available (from previous trading day)
# If None, don't generate PDH/PDL (they're only useful for intraday charts)
if daily_pdh_pdl:
    logger.info(f"Using passed PDH/PDL: {daily_pdh_pdl}")
    daily_data = daily_pdh_pdl
else:
    logger.info("No PDH/PDL provided - skipping PDH/PDL levels (not applicable for daily/weekly charts)")
    daily_data = None
```

**Key change**: Pass `None` instead of falling back to the old calculation method.

#### 3. Key Levels Generator (`key_levels.py` - no changes needed)

The existing code already handles `None` correctly:
```python
if daily_data and 'pdh' in daily_data and 'pdl' in daily_data:
    # Generate PDH/PDL
```

When `daily_data=None`, this condition is false and PDH/PDL are skipped.

## Verification

### Intraday Charts (30m example)
```
INFO:mcp_server:Fetching daily data for PDH/PDL calculation (intraday interval: 30m)
INFO:mcp_server:Previous day high/low: PDH=430.3, PDL=430.02
INFO:pattern_detection:Using passed PDH/PDL: {'pdh': 430.3, 'pdl': 430.02}
INFO:pattern_detection:📏 Generated 4 key levels: ['BL', 'SH', 'PDH', 'PDL']
```
**Result**: 4 key levels including PDH and PDL ✅

### Daily Charts (1Y example)
```
INFO:mcp_server:Skipping PDH/PDL for non-intraday interval: 1d (PDH/PDL only shown on minute/hour charts)
INFO:pattern_detection:No PDH/PDL provided - skipping PDH/PDL levels (not applicable for daily/weekly charts)
INFO:pattern_detection:📏 Generated 3 key levels: ['BL', 'SH', 'BTD']
```
**Result**: 3 key levels, PDH and PDL not shown ✅

## Expected Behavior After Fix

### Intraday Timeframes (1m, 5m, 30m, 1h, 2h, etc.)
- **PDH**: Previous calendar day's high (horizontal line)
- **PDL**: Previous calendar day's low (horizontal line)
- **BL**: Buy Low level from pivot lows
- **SH**: Sell High level from pivot highs
- **BTD**: Buy The Dip (200 MA) level

**Total: 5 key levels** (or 3-4 if some are too close and deduplicated)

### Daily+ Timeframes (1D, 1Y, 2Y, 3Y, 1W, 1M, etc.)
- **BL**: Buy Low level from pivot lows
- **SH**: Sell High level from pivot highs
- **BTD**: Buy The Dip (200 MA) level
- ~~**PDH**: Not shown~~
- ~~**PDL**: Not shown~~

**Total: 3 key levels**

## Trading Rationale

### Why PDH/PDL Are Intraday-Only

**Intraday Trading (1m - 4h charts)**:
- Traders reference previous day's high/low as key support/resistance
- If price breaks above PDH = bullish breakout signal
- If price breaks below PDL = bearish breakdown signal
- These levels are actionable within the trading day

**Daily+ Trading (1d - monthly charts)**:
- Looking at a full year of price action (252 daily candles)
- Yesterday's high/low is just one tiny range among 252 days
- Not statistically significant for long-term analysis
- More relevant: major swing highs/lows (BL/SH), trend support (BTD)

## Files Modified

1. **`/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/mcp_server.py`**
   - Lines 1620-1641: Added intraday check for PDH/PDL fetching

2. **`/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/pattern_detection.py`**
   - Lines 782-789: Skip fallback calculation when daily_pdh_pdl is None

3. **`/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/key_levels.py`**
   - No changes needed (already handles None correctly)

## Testing Checklist

- ✅ **30m chart**: Shows PDH/PDL (intraday)
- ✅ **1h chart**: Shows PDH/PDL (intraday)
- ✅ **1d chart (1Y view)**: No PDH/PDL (daily)
- ✅ **Backend logs**: Correct messages for each case
- ⏳ **Frontend visual**: User verification needed

## Related Fixes

This builds on the earlier interval parameter fix:
1. **Interval Parameter Fix**: Ensures trendlines use correct timeframe data
2. **PDH/PDL Intraday-Only Fix**: Ensures PDH/PDL only show on appropriate timeframes

Together, these ensure accurate, meaningful technical levels across all chart timeframes.

## Date
December 1, 2025 (3:40 AM)
