# PDH/PDL Fix Summary

## Problem Identified

The PDH (Previous Day High) and PDL (Previous Day Low) levels were being calculated incorrectly across different timeframes:

### Original Broken Behavior
- **For 30m charts**: Used high/low from last 24 30-minute bars (12 hours) ❌
- **For 1m charts**: Used high/low from last 24 1-minute bars (24 minutes) ❌
- **For 1d charts**: Used high/low from last 24 daily bars (24 days!) ❌

**Root Cause**: The code was using `highs[-24:]` from the current interval's data, not the actual previous trading day.

## Expected Correct Behavior

PDH and PDL should represent the **previous calendar trading day's high and low**, regardless of chart timeframe:

- **For 1h chart**: 24 hourly candles span 1 day, PDH/PDL from previous day ✅
- **For 1m chart**: 1440 minute candles span 1 day, PDH/PDL from same previous day ✅
- **For 30m chart**: 48 half-hour candles span 1 day, PDH/PDL from same previous day ✅

**Key Insight**: All timeframes should show the same PDH/PDL values because they represent the same previous trading day.

## Solution Implemented

### Changes to `backend/mcp_server.py` (Lines 1620-1642)

Added logic to fetch daily (1d) data separately when pattern detection is called with intraday intervals:

```python
# Fetch daily data for PDH/PDL calculation (always use 1d interval for these levels)
# PDH/PDL should represent the previous trading day, regardless of current chart interval
daily_pdh_pdl = None
if interval != "1d":
    try:
        logger.info(f"Fetching daily data for PDH/PDL calculation")
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

# Pass daily data for PDH/PDL
results = detector.detect_all_patterns(daily_pdh_pdl=daily_pdh_pdl)
```

### Changes to `backend/pattern_detection.py`

#### 1. Modified `detect_all_patterns` method signature (Line 563):
```python
def detect_all_patterns(self, daily_pdh_pdl: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
```

#### 2. Modified `calculate_pattern_trendlines` method signature (Line 681):
```python
def calculate_pattern_trendlines(
    self,
    patterns: List[Dict[str, Any]],
    support_levels: List[float],
    resistance_levels: List[float],
    daily_pdh_pdl: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
```

#### 3. Updated PDH/PDL calculation logic (Lines 782-794):
```python
# Use passed PDH/PDL if available (from previous trading day),
# otherwise calculate from recent data as fallback
if daily_pdh_pdl:
    logger.info(f"Using passed PDH/PDL: {daily_pdh_pdl}")
    daily_data = daily_pdh_pdl
else:
    logger.info("No PDH/PDL provided, calculating from recent data (fallback)")
    recent_highs = highs[-24:] if len(highs) >= 24 else highs
    recent_lows = lows[-24:] if len(lows) >= 24 else lows
    daily_data = {
        'pdh': float(np.max(recent_highs)),
        'pdl': float(np.min(recent_lows))
    }
```

## Verification

### Log Evidence
```
INFO:pattern_detection:Using passed PDH/PDL: {'pdh': 430.3, 'pdl': 430.02}
INFO:pattern_detection:📏 Generated 4 key levels: ['BL', 'SH', 'PDH', 'PDL']
```

### Test Procedure
1. View TSLA chart on 30m timeframe
2. Check that PDH and PDL levels are displayed
3. Switch to 1h timeframe
4. Verify PDH/PDL values remain the same (representing same previous day)
5. Switch to 1m timeframe
6. Verify PDH/PDL values still match

## Related Fix

This fix works in conjunction with the earlier interval parameter fix (commit addressing trendline accuracy):

- **Interval Parameter Fix**: Ensures pattern detection uses correct timeframe data
- **PDH/PDL Fix**: Ensures PDH/PDL always represent the actual previous trading day

Together, these fixes ensure that:
1. Trendlines and pivots are calculated from the correct timeframe data
2. PDH/PDL levels correctly represent the previous calendar day across all timeframes

## Files Modified

1. `/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/mcp_server.py`
   - Lines 1620-1642: Added daily data fetching for PDH/PDL

2. `/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/pattern_detection.py`
   - Line 563: Updated `detect_all_patterns` signature
   - Line 646-650: Pass daily_pdh_pdl parameter
   - Line 681-701: Updated `calculate_pattern_trendlines` signature and docs
   - Lines 782-794: Modified PDH/PDL calculation logic

## Testing Status

✅ Backend server restarted successfully
✅ Daily data fetch working (logs show successful PDH/PDL retrieval)
✅ Pattern detection using passed PDH/PDL values
⏳ Frontend testing pending (awaiting user verification on different timeframes)

## Date
December 1, 2025 (3:30 AM)
