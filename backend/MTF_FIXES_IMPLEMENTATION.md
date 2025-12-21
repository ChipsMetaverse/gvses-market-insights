# MTF Trendline Fixes - Implementation Plan

## Date: November 30, 2025

## Issues Identified

### 1. Pink Resistance Trendline is Horizontal (CRITICAL BUG)
**Problem**: Resistance line appears horizontal instead of diagonal
**Root Cause**: In `trendline_builder.py` lines 159-162, using `p1.index` and `p2.index` as endpoints
**Example**: touching_indices = [33, 44, 102, 108] but line uses pivots 33-44 (18 days) instead of 33-108 (full range)
**Fix**: Use `min(touching_indices)` and `max(touching_indices)` to get actual first/last pivot that touches the line

### 2. Diagonal Trendlines Don't Extend to Right
**Problem**: Support and resistance lines end in the middle of chart instead of extending to current date
**Current**: end_time is the last pivot's timestamp
**Fix**: Extend lines to the last candle timestamp (or add 30 days into future)

### 3. BL/SH Don't Span Full Chart Width
**Problem**: Key levels should extend across entire visible chart range
**Current**: They do extend start→end of data, but should be more explicit
**Fix**: Ensure start_time = first candle time, end_time = last candle time (or +30 days)

### 4. BTD Should Be 200-Day MA
**Problem**: BTD currently calculated as secondary pivot low
**Spec**: User wants BTD = 200-day moving average (horizontal line)
**Fix**: Calculate 200-day SMA from closing prices

## Implementation Plan

### Phase 1: Fix Resistance/Support Trendline Endpoints
**File**: `backend/trendline_builder.py`

**Changes**:
1. In `build_support_line()` and `build_resistance_line()`:
   - After finding best line, get first and last pivots from `touching_indices`
   - Use those pivots' indices and prices as start/end points
   - This ensures line spans the full extent of all touching pivots

**Code Location**: Lines 155-168 (resistance), lines 92-105 (support)

### Phase 2: Extend Trendlines to Right
**File**: `backend/pattern_detection.py`

**Changes**:
1. After getting trendline from builder, extend the end time:
   - Calculate slope from trendline
   - Project price forward to last candle + 30 days
   - Update end timestamp and price

**Code Location**: Lines 740-760 (where trendlines are converted to dict)

### Phase 3: Ensure Key Levels Span Full Width
**File**: `backend/key_levels.py`

**Changes**:
1. In `levels_to_api_format()`:
   - Use `candles[0]['time']` as start_time
   - Use `candles[-1]['time'] + 30*86400` as end_time (extend 30 days)

**Code Location**: Lines 280-282

### Phase 4: Change BTD to 200-Day MA
**File**: `backend/key_levels.py`

**Changes**:
1. Replace `_calculate_btd()` method:
   - Calculate 200-period SMA from closing prices
   - Return horizontal line at SMA value
   - Label as "BTD (200 MA)"

**Code Location**: Lines 191-260

## Expected Results

### After Fix 1 (Resistance Trendline):
```json
{
  "type": "resistance",
  "start": {"time": 1751515200, "price": 318.45},  // Pivot 33
  "end": {"time": 1763875200, "price": 427.89},    // Pivot 108 (last touching pivot)
  "touches": 4,
  "pivot_indices": [33, 44, 102, 108]
}
```

### After Fix 2 (Right Extension):
```json
{
  "type": "resistance",
  "start": {"time": 1751515200, "price": 318.45},
  "end": {"time": 1766941200, "price": 445.32},    // Extended 30 days past last candle
  "touches": 4,
  "pivot_indices": [33, 44, 102, 108]
}
```

### After Fix 3 (Key Level Width):
```json
{
  "type": "key_level",
  "label": "BL",
  "start": {"time": 1747281600, "price": 382.78},  // First candle
  "end": {"time": 1766941200, "price": 382.78},    // Last candle + 30 days
  "color": "#4caf50"
}
```

### After Fix 4 (BTD as 200 MA):
```json
{
  "type": "key_level",
  "label": "BTD (200 MA)",
  "start": {"time": 1747281600, "price": 389.45},  // 200-day SMA value
  "end": {"time": 1766941200, "price": 389.45},
  "color": "#2196f3",
  "style": "dashed"
}
```

## Testing Plan

1. **Test All Timeframes**: Run pattern detection for 1Y, 2Y, 3Y, YTD, MAX
2. **Visual Verification**: Use Playwright to capture screenshots showing:
   - Resistance line is now diagonal (not horizontal)
   - Support and resistance extend to right edge
   - BL/SH span full chart width
   - BTD appears as 200 MA horizontal line
3. **API Response Check**: Verify timestamps and prices are correct

## Success Criteria

✅ Resistance trendline is diagonal following actual pivot structure
✅ Both diagonal trendlines extend to right edge of chart
✅ BL and SH span entire chart width
✅ BTD shows as 200-day MA horizontal line
✅ All changes work across all timeframes (1Y, 2Y, 3Y, YTD, MAX)
✅ No regression in existing functionality

---

**Status**: Ready to implement
**Priority**: HIGH - User identified these as critical issues
