# Chart Timeframe Accuracy Report
**Date**: October 31, 2025  
**Testing Tool**: Playwright MCP Server  
**Test Symbol**: TSLA  
**Frontend**: localhost:5174

---

## Executive Summary

✅ **FIXED ISSUES**:
- Pattern detection working (5 patterns displayed)
- Pattern overlays now visible on chart
- Support/Resistance lines displaying correctly
- News panel showing ticker-specific content
- Technical indicators calculating properly

❌ **NEW CRITICAL ISSUE DISCOVERED**:
**Timeframe buttons 1M, 6M, and 1Y are displaying ALL historical data instead of filtering to the selected timeframe.**

---

## Detailed Test Results

### ✅ Working Timeframes

#### 1D Timeframe
- **Status**: ✅ **WORKING**
- **Display**: Shows approximately 1 trading day
- **Data Range**: Single day view with intraday candles
- **Screenshot**: `tsla-1D-initial.png`

#### 5D Timeframe
- **Status**: ✅ **WORKING**  
- **Display**: Shows approximately 5 trading days
- **Data Range**: Limited to last week
- **Screenshot**: `tsla-5D-timeframe.png`
- **Note**: Triggered 7 component re-renders (performance concern)

---

### ❌ Broken Timeframes

#### 1M (1 Month) Timeframe
- **Status**: ❌ **BROKEN**
- **Expected**: Last 30 days of data
- **Actual**: **Showing ALL data from 2020-2025**
- **Data Range**: Entire company history (~5 years)
- **X-Axis Labels**: 2020, 2021, 2022, 2023, 2024, 2025, Sep
- **Screenshot**: `tsla-1M-timeframe.png`
- **Issue**: Data not filtered to 1 month window

#### 6M (6 Months) Timeframe
- **Status**: ❌ **BROKEN**
- **Expected**: Last 180 days of data
- **Actual**: **Showing ALL data from 2020-2025** (identical to 1M)
- **Data Range**: Entire company history (~5 years)
- **X-Axis Labels**: 2020, 2021, 2022, 2023, 2024, 2025, Sep
- **Screenshot**: `tsla-6M-timeframe.png`
- **Issue**: Data not filtered to 6 month window

#### 1Y (1 Year) Timeframe
- **Status**: ❌ **BROKEN**
- **Expected**: Last 365 days of data
- **Actual**: **Showing ALL data from 2020-2025** (identical to 1M and 6M)
- **Data Range**: Entire company history (~5 years)
- **X-Axis Labels**: 2020, 2021, 2022, 2023, 2024, 2025, Sep
- **Screenshot**: `tsla-1Y-timeframe.png`
- **Issue**: Data not filtered to 1 year window

---

## Root Cause Analysis

### Suspected Issue Location

The timeframe filtering logic is failing for medium-range timeframes (1M, 6M, 1Y). This suggests:

1. **Frontend Data Slicing Logic**:
   - File: `frontend/src/components/TradingChart.tsx` or `frontend/src/hooks/useIndicatorState.ts`
   - The chart is receiving the full dataset but not applying the timeframe filter
   - Lightweight Charts `setVisibleTimeRange` may not be called correctly

2. **Backend Data Fetching**:
   - File: `backend/services/direct_market_service.py`
   - The `timeframeToDays()` function may not be mapping 1M/6M/1Y correctly
   - Backend might be sending full dataset regardless of timeframe

3. **Chart Initialization**:
   - The chart might be auto-fitting to all available data instead of respecting the timeframe selection

---

## Evidence

### Console Logs Analysis

When switching timeframes, the following patterns were observed:

```
1. Multiple re-renders on timeframe change:
   - 1D → 5D: Only 1 re-render ✅
   - 5D → 1M: 7 re-renders ❌ (Performance issue)
   
2. Chart initialization logs show:
   - "Enhanced chart control initialized"
   - "Chart ready for enhanced agent control"
   - "Chart snapshot captured for TSLA"
   
3. No errors in console for 1M/6M/1Y
   - This suggests data is loading, but filtering is not applied
```

### Visual Comparison

| Timeframe | Expected Data | Actual Data | Status |
|-----------|---------------|-------------|---------|
| 1D | ~1 day | ~1 day | ✅ PASS |
| 5D | ~5 days | ~5 days | ✅ PASS |
| **1M** | **~30 days** | **~5 years** | ❌ FAIL |
| **6M** | **~180 days** | **~5 years** | ❌ FAIL |
| **1Y** | **~365 days** | **~5 years** | ❌ FAIL |
| 2Y | ~730 days | Not tested | ⚠️  UNKNOWN |
| 3Y | ~1095 days | Not tested | ⚠️  UNKNOWN |
| YTD | Year-to-date | Not tested | ⚠️  UNKNOWN |
| MAX | All data | Not tested | ⚠️  UNKNOWN |

---

## Files to Investigate

### Priority 1: Frontend Data Filtering

```typescript
// frontend/src/hooks/useIndicatorState.ts
function timeframeToDays(timeframe: string): number {
  const map: Record<string, number> = {
    '1D': 200,  // ✅ Fixed for technical indicators
    '5D': 200,  // ✅ Fixed
    '1M': 200,  // ❓ Should this request 200 days but display 30?
    '6M': 200,  // ❓ Should this request 200+ days but display 180?
    '1Y': 365,  // ❓ Correct request, but display filtering missing?
    // ...
  };
  return map[timeframe] || 200;
}
```

**Issue**: This function returns the days to FETCH, but there may be no logic to FILTER/DISPLAY only the requested range.

### Priority 2: Chart Visible Range

```typescript
// frontend/src/components/TradingChart.tsx
// Look for where setVisibleTimeRange or setVisibleLogicalRange is called
// This should be triggered on timeframe change
```

### Priority 3: Timeframe Mapping

```typescript
// frontend/src/components/TradingDashboardSimple.tsx
// Check how timeframe buttons trigger data updates
// Verify the timeframe value is passed correctly to the chart
```

---

## Recommended Fix

### Step 1: Add Timeframe-Based Data Filtering

In `TradingChart.tsx`, after data is loaded, apply the timeframe filter:

```typescript
useEffect(() => {
  if (chartData && chartData.length > 0 && chartInstance) {
    // Calculate visible range based on timeframe
    const now = Math.floor(Date.now() / 1000);
    const timeframeInSeconds = {
      '1D': 86400,
      '5D': 5 * 86400,
      '1M': 30 * 86400,
      '6M': 180 * 86400,
      '1Y': 365 * 86400,
      '2Y': 730 * 86400,
      '3Y': 1095 * 86400,
    }[selectedTimeframe] || null;

    if (timeframeInSeconds) {
      const fromTime = now - timeframeInSeconds;
      chartInstance.timeScale().setVisibleLogicalRange({
        from: chartData.findIndex(d => d.time >= fromTime),
        to: chartData.length - 1
      });
    } else {
      // For MAX/YTD, show all data
      chartInstance.timeScale().fitContent();
    }
  }
}, [chartData, selectedTimeframe, chartInstance]);
```

### Step 2: Prevent Auto-Fit on Data Load

```typescript
// Disable automatic "fit all data" behavior
chartInstance.timeScale().applyOptions({
  fixLeftEdge: false,
  fixRightEdge: false,
  lockVisibleTimeRangeOnResize: true,
});
```

### Step 3: Test All Timeframes

After implementing the fix, verify:
- 1M shows only last 30 days
- 6M shows only last 180 days  
- 1Y shows only last 365 days
- MAX shows all historical data

---

## Performance Issues Noted

### Excessive Re-renders

**Observation**: Switching from 5D → 1M triggered **7 component re-renders**:

```
- [LOG] TradingDashboardSimple rendering... (x7)
- [LOG] useOpenAIRealtimeConversation HOOK CALLED (x7)
- [LOG] Component rendered with isConnected: false (x7)
- [LOG] Voice provider switched from chatkit to: chatkit (x5)
```

**Impact**: Performance degradation, especially on slower devices

**Recommendation**: 
1. Memoize expensive components with `React.memo()`
2. Use `useMemo` for chart data transformations
3. Debounce timeframe changes to prevent rapid re-renders

---

## User Impact

### Trader Experience Levels

#### Beginner Trader
- **Issue**: Sees full 5-year history when selecting "1 Month"
- **Confusion**: Cannot see recent price action clearly
- **Expected**: Zoomed view of last 30 days for short-term analysis

#### Intermediate Trader
- **Issue**: Technical analysis on wrong timeframe
- **Impact**: MA200 shown on 1M chart (should only appear on 200+ day view)
- **Expected**: Appropriate indicators for selected timeframe

#### Advanced/Seasoned Trader
- **Issue**: Cannot perform multi-timeframe analysis
- **Impact**: Unable to compare 1M vs 6M vs 1Y trends side-by-side
- **Expected**: Accurate timeframe filtering for strategy backtesting

---

## Test Coverage

### ✅ Tested
- 1D timeframe
- 5D timeframe
- 1M timeframe
- 6M timeframe
- 1Y timeframe
- Pattern detection overlay
- News panel accuracy
- Technical indicators (MA20, MA50, MA200, RSI, MACD, Bollinger Bands)

### ⚠️  Not Tested (Recommended)
- 2Y timeframe
- 3Y timeframe
- YTD timeframe
- MAX timeframe
- Different symbols (AAPL, NVDA, SPY, PLTR)
- Switching symbols while on broken timeframes
- Chart zoom/pan behavior on broken timeframes

---

## Success Criteria for Fix

✅ **Definition of Done**:

1. **1M Timeframe**:
   - X-axis shows dates spanning approximately 30 days
   - Most recent data point is current date
   - Oldest data point is ~30 days ago
   - Chart is appropriately zoomed to show 1-month trend

2. **6M Timeframe**:
   - X-axis shows dates spanning approximately 180 days
   - Data range: Current date to ~6 months ago
   - Chart shows clear quarterly trends

3. **1Y Timeframe**:
   - X-axis shows dates spanning approximately 365 days
   - Data range: Current date to ~1 year ago
   - Annual trend clearly visible

4. **Performance**:
   - Timeframe changes trigger ≤2 re-renders (acceptable threshold)
   - No visible lag when switching timeframes

5. **Consistency**:
   - All symbols (TSLA, AAPL, NVDA, SPY, PLTR) behave identically
   - Pattern overlays remain visible and accurate on all timeframes

---

## Next Steps

1. **Immediate Priority**: Fix 1M/6M/1Y timeframe filtering
2. **Test remaining timeframes**: 2Y, 3Y, YTD, MAX
3. **Performance optimization**: Reduce re-renders on timeframe change
4. **Cross-symbol testing**: Verify fix works for all tickers
5. **User acceptance testing**: Validate with Playwright MCP from trader perspectives

---

## Related Issues

- ✅ FIXED: Technical indicators 500 error
- ✅ FIXED: Pattern detection empty results
- ✅ FIXED: News content not ticker-specific
- ✅ FIXED: Pattern overlays not visible
- ❌ **NEW**: Timeframe filtering not working for 1M/6M/1Y

---

**Report Generated by**: Playwright MCP Automated Testing  
**Status**: ❌ CRITICAL BUG - Medium-range timeframes not filtering data correctly  
**Priority**: HIGH - Impacts all user experience levels  
**Estimated Fix Time**: 1-2 hours

