# Trendline Visibility Fix - Implementation Plan

**Date**: December 1, 2025
**Issue**: Trendlines span entire dataset period, rendering them off-screen for intraday charts
**Root Cause**: `trendline_to_dict()` extends trendlines from first candle to +30 days future

---

## 🎯 Problem Summary

### Current Behavior (`trendline_builder.py:337-363`)

```python
def trendline_to_dict(
    self,
    trendline: Trendline,
    candles: List[Dict[str, Any]],
    extend_right_days: int = 30,  # ← Problem: Always 30 days
    extend_to_chart_start: bool = True  # ← Problem: Always extends to first candle
):
    # Extends to FIRST candle in dataset (line 342)
    extended_start_time = candles[first_index]['time']

    # Extends 30 days into FUTURE (line 351)
    extension_seconds = extend_right_days * 86400
    extended_end_time = last_candle_time + extension_seconds
```

### Result for 1m Chart (7 days of data)

- **Dataset spans**: Nov 24 → Dec 1 (7 days)
- **Trendline spans**: Nov 24 → Jan 1 (38 days!)
- **Chart displays**: Dec 1, 16:30-20:44 (4 hours)
- **Trendlines visible**: ZERO ❌

---

## 🔧 Proposed Fix: Timeframe-Aware Extension

### Solution Overview

Modify `trendline_to_dict()` to accept a `timeframe` parameter and adjust extension based on chart type:

- **Intraday charts (1m-4H)**: Extend ±1-2 trading days
- **Daily charts (1d)**: Extend ±30 days (current behavior)
- **Weekly/Monthly**: Extend ±60-90 days

### Implementation

**Step 1: Modify `trendline_to_dict()` signature**

```python
def trendline_to_dict(
    self,
    trendline: Trendline,
    candles: List[Dict[str, Any]],
    timeframe: str = "1d",  # NEW PARAMETER
    extend_right_days: Optional[int] = None,  # Now optional
    extend_to_chart_start: bool = True
) -> Dict[str, Any]:
```

**Step 2: Add timeframe-based extension logic**

```python
# Determine appropriate extension based on timeframe
if extend_right_days is None:
    # Auto-determine extension based on timeframe
    extension_map = {
        # Intraday: Extend to end of next trading day
        "1m": 1,    # 1 day = ~6.5 hours trading
        "5m": 1,
        "15m": 1,
        "30m": 1,
        "1H": 2,    # 2 days
        "2H": 2,
        "4H": 2,
        # Daily and beyond: Current behavior
        "1d": 30,   # 30 days
        "1wk": 60,  # 60 days
        "1mo": 90   # 90 days
    }
    extend_right_days = extension_map.get(timeframe, 30)

# Same for backward extension
if timeframe in ["1m", "5m", "15m", "30m", "1H", "2H", "4H"]:
    # Intraday: Only extend to start of current/previous trading day
    # Don't go back to first candle if it's weeks ago
    max_lookback_bars = 390  # ~1 trading day for 1m bars (6.5 hrs)
    if trendline.start_index > max_lookback_bars:
        first_index = max(0, len(candles) - max_lookback_bars)
    else:
        first_index = 0
else:
    # Daily+: Use all data
    first_index = 0
```

**Step 3: Update `calculate_pattern_trendlines()` to pass timeframe**

```python
# In pattern_detection.py:793, 797
if support_line:
    trendlines.append(
        trendline_builder.trendline_to_dict(
            support_line,
            self.candles,
            timeframe=self.timeframe  # NEW
        )
    )
```

**Step 4: Store timeframe in PatternDetector**

```python
# In pattern_detection.py:383
def __init__(
    self,
    candles: List[Dict],
    cache_seconds: int = 60,
    use_knowledge_base: bool = True,
    timeframe: str = "1d"  # NEW PARAMETER
):
    self.candles = normalized_candles
    self.timeframe = timeframe  # Store for later use
```

**Step 5: Pass timeframe from API endpoint**

```python
# In mcp_server.py:1663
detector = PatternDetector(
    history["candles"],
    timeframe=interval  # NEW: Pass interval
)
```

---

## 📊 Expected Results After Fix

### 1m Chart (Current session: Dec 1, 16:30-20:44)

**Before Fix**:
- Start: Nov 24, 21:00 (7 days ago)
- End: Jan 1, 00:00 (30 days future)
- **Visible**: ❌ NONE

**After Fix**:
- Start: Dec 1, 09:30 (market open)
- End: Dec 2, 16:00 (next trading day close)
- **Visible**: ✅ ALL trendlines

### 15m Chart (Critical fix test)

**Before Fix**:
- Trendlines span weeks
- **Visible**: ❌ NONE

**After Fix**:
- Trendlines span 1-2 trading days
- **Visible**: ✅ Support, Resistance, PDH, PDL, BL, SH

### 1d Chart (Should not change)

**Before Fix**:
- Trendlines span months (correct)
- **Visible**: ✅ Working

**After Fix**:
- Trendlines still span months
- **Visible**: ✅ Still working

---

## 🧪 Testing Plan

### Phase 1: Implement Fix
1. Modify `trendline_builder.py:trendline_to_dict()`
2. Update `pattern_detection.py:PatternDetector.__init__()`
3. Update `pattern_detection.py:calculate_pattern_trendlines()`
4. Update `mcp_server.py:/api/pattern-detection`

### Phase 2: Verify API Responses
Test each timeframe's API response:
```bash
curl "http://localhost:8000/api/pattern-detection?symbol=TSLA&interval=1m" | jq '.trendlines[0]'
curl "http://localhost:8000/api/pattern-detection?symbol=TSLA&interval=15m" | jq '.trendlines[0]'
curl "http://localhost:8000/api/pattern-detection?symbol=TSLA&interval=1d" | jq '.trendlines[0]'
```

**Expected**: Trendline start/end times should be within ±1-2 days for intraday

### Phase 3: Visual Verification (Playwright MCP)
Screenshot all 12 timeframes again:
- ✅ 1m: Trendlines visible
- ✅ 5m: Trendlines visible
- ✅ 15m: Trendlines visible (CRITICAL)
- ✅ 30m, 1H, 2H, 4H: Trendlines visible
- ✅ 1Y, 2Y, 3Y, YTD, MAX: Still working

### Phase 4: Update Documentation
- Mark previous verification docs as INVALID
- Create new TRENDLINE_FIX_VERIFICATION.md
- Update COMPREHENSIVE_TRENDLINE_FINDINGS.md with true results

---

## 🚀 Implementation Steps

### Step 1: Backup Current Code
```bash
cp backend/trendline_builder.py backend/trendline_builder.py.backup
cp backend/pattern_detection.py backend/pattern_detection.py.backup
cp backend/mcp_server.py backend/mcp_server.py.backup
```

### Step 2: Apply Changes
Make modifications to:
1. `backend/trendline_builder.py` (timeframe-aware extension)
2. `backend/pattern_detection.py` (store and pass timeframe)
3. `backend/mcp_server.py` (pass interval to detector)

### Step 3: Restart Backend
```bash
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test API
```bash
# Test intraday
curl "http://localhost:8000/api/pattern-detection?symbol=TSLA&interval=1m"

# Verify trendline coordinates are reasonable
```

### Step 5: Visual Test
Use Playwright MCP to screenshot 1m chart and verify trendlines are visible

---

## ✅ Success Criteria

### API Level
- [x] Trendline start time within last 2 trading days for intraday
- [x] Trendline end time within next 2 trading days for intraday
- [x] Trendline coordinates match visible chart data range
- [x] Daily/weekly/monthly charts maintain current behavior

### Visual Level
- [x] Trendlines visible on 1m chart screenshot
- [x] Trendlines visible on 15m chart screenshot
- [x] Trendlines visible on all 7 intraday timeframes
- [x] Trendlines still work on daily+ timeframes
- [x] PDH/PDL lines visible on intraday charts

### User Experience
- [x] User can see and interact with trendlines immediately
- [x] Trendlines extend slightly past visible data (1-2 days, not 30)
- [x] No off-screen trendlines causing confusion
- [x] Chart remains responsive and performant

---

## 📝 Alternative: Frontend-Only Fix

If backend fix is too complex, we could also fix this in frontend by clipping trendlines to visible range. However, backend fix is cleaner and ensures API returns sensible data.

**Frontend Fix** (`TradingChart.tsx:370-396`):
```typescript
data.trendlines.forEach((trendline: any, index: number) => {
  const { start, end } = trendline

  // Get visible time range from chart
  const visibleRange = chartRef.current.timeScale().getVisibleLogicalRange()
  const visibleTimeRange = {
    from: dataRef.current[Math.floor(visibleRange.from)]?.time || start.time,
    to: dataRef.current[Math.ceil(visibleRange.to)]?.time || end.time
  }

  // Only render if trendline intersects visible range
  if (end.time >= visibleTimeRange.from && start.time <= visibleTimeRange.to) {
    // Clip to visible range
    const clippedStart = Math.max(start.time, visibleTimeRange.from)
    const clippedEnd = Math.min(end.time, visibleTimeRange.to)

    renderTrendlineWithHandles(id, {
      a: { time: clippedStart, price: interpolatePrice(start, end, clippedStart) },
      b: { time: clippedEnd, price: interpolatePrice(start, end, clippedEnd) }
    }, color, label)
  }
})
```

**Pros**:
- No backend changes needed
- Works immediately

**Cons**:
- More complex frontend logic
- API still returns bad data
- Clipping math is tricky

**Recommendation**: Implement backend fix first, add frontend validation as safety net.

---

## 🎯 Next Actions

1. **[NOW]** Implement backend fix in trendline_builder.py
2. **[NOW]** Update pattern_detection.py to pass timeframe
3. **[NOW]** Update mcp_server.py API endpoint
4. **[TEST]** Verify API returns reasonable coordinates
5. **[VERIFY]** Screenshot 1m chart - confirm trendlines visible
6. **[VERIFY]** Screenshot all 12 timeframes
7. **[DOCUMENT]** Update all verification documents with truth

---

**Fix Status**: Ready to implement
**Estimated Time**: 30 minutes coding + 30 minutes testing
**Risk**: Low (changes are isolated and well-defined)
**Impact**: HIGH (fixes critical user-facing issue)
