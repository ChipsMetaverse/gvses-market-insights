# Infinite Scroll Investigation - TSLA Chart

**Date**: December 2, 2025
**Status**: ⚠️ **ISSUE IDENTIFIED - NEEDS FIX**

## Problem Statement

When scrolling left on the chart (panning back in time), no additional historical data is loaded. The chart shows only the initially loaded data range and doesn't automatically fetch older bars when the user scrolls to the left edge.

## Expected Behavior

According to TradingView Lightweight Charts "Infinite History" pattern:
1. Load initial dataset (e.g., 60 days or 200 bars)
2. Subscribe to `timeScale().subscribeVisibleLogicalRangeChange()`
3. When user scrolls left and visible range approaches left edge (< 10 logical units from start)
4. Fetch older historical data (e.g., 30 more days)
5. Prepend new data to existing dataset using `series.setData()`
6. Chart should display seamlessly without jumping

## Current Implementation Analysis

### ✅ What's Working

1. **useInfiniteChartData Hook** (`/frontend/src/hooks/useInfiniteChartData.ts`)
   - Comprehensive lazy loading hook exists
   - Has `loadMore()` function for fetching older data
   - Has `checkEdgeProximity()` function to detect left edge
   - Has `attachToChart()` function to subscribe to visible range changes
   - Properly deduplicates data and sorts by timestamp

2. **TradingChart Component Integration**
   - Hook is imported and initialized (line 24, 79-86)
   - `attachToChart()` is called when chart is created (line 755)
   - Hook is enabled for intraday intervals (line 68, 85)

### ❌ What's Not Working

Looking at the Playwright test console logs:
```
[HOOK] 🚀 loadInitial called, initialDays: 7
[HOOK] 📡 Fetching data from 2025-11-26T00:00:00.000Z to 2025-12-03T00:00:00.000Z
[HOOK] ✅ Received 86 bars from api in 885.61 ms
```

**No "📊 Near left edge, loading more data..." message appears when scrolling left!**

This indicates the edge detection is not triggering.

## Root Cause Analysis

### Potential Issues

#### Issue #1: Visible Logical Range Detection

The `checkEdgeProximity()` function (useInfiniteChartData.ts:297-331) calculates:
```typescript
const leftDistance = (visibleRange.from as number) - dataRange.from
const threshold = visibleSpan * edgeThreshold  // edgeThreshold = 0.15 (15%)

if (leftDistance < threshold && hasMore) {
  console.log('📊 Near left edge, loading more data...')
  loadMore()
}
```

The issue might be:
1. **Logical vs Time coordinates**: The function compares time-based ranges but TradingView uses logical coordinates internally
2. **visibleRange.from** might not be in the correct format
3. **Threshold calculation** might not match the actual visible bars

#### Issue #2: subscribeVisibleLogicalRangeChange Not Firing

Looking at `attachToChart()` (useInfiniteChartData.ts:336-357):
```typescript
timeScale.subscribeVisibleLogicalRangeChange(handleVisibleRangeChange)
```

This subscription should fire whenever the user pans or zooms the chart. If it's not firing:
- The chart reference might be stale
- The subscription might be getting unsubscribed too early
- There might be a React closure issue

#### Issue #3: Logical Range vs Time Range Confusion

TradingView Lightweight Charts uses:
- **Logical coordinates** (0, 1, 2, ...) for bar indices
- **Time coordinates** (Unix timestamps) for actual data points

The `subscribeVisibleLogicalRangeChange` callback receives:
```typescript
logicalRange: { from: Logical, to: Logical }  // Bar indices (0-based)
```

But the code is comparing with:
```typescript
dataRange = {
  from: data[0].time as number,  // Unix timestamp
  to: data[data.length - 1].time as number  // Unix timestamp
}
```

**This is comparing apples to oranges!**

## The Fix

### Step 1: Use Logical Coordinates Properly

Update `checkEdgeProximity()` to work with logical indices:

```typescript
const checkEdgeProximity = useCallback((logicalRange: { from: number; to: number } | null) => {
  if (!logicalRange || !chartRef.current || !data.length || !enabled || isLoadingRef.current) {
    return
  }

  // logicalRange.from is the leftmost visible bar index (logical coordinate)
  // If it's close to 0 (first bar), we need to load more data

  const threshold = 10  // When < 10 bars from left edge, load more

  if (logicalRange.from < threshold && hasMore) {
    console.log(`📊 Near left edge (${logicalRange.from} bars from start), loading more data...`)
    loadMore()
  }
}, [data, enabled, hasMore, loadMore])
```

### Step 2: Pass Logical Range to Handler

Update `attachToChart()`:

```typescript
const handleVisibleRangeChange = (logicalRange: { from: number; to: number } | null) => {
  checkEdgeProximity(logicalRange)
}

timeScale.subscribeVisibleLogicalRangeChange(handleVisibleRangeChange)
```

### Step 3: Add Debug Logging

Add console logs to understand what's happening:

```typescript
const handleVisibleRangeChange = (logicalRange: { from: number; to: number } | null) => {
  console.log('[LAZY LOAD] Visible range changed:', logicalRange)
  checkEdgeProximity(logicalRange)
}
```

## Testing Plan

1. Navigate to http://localhost:5174/demo
2. Click "1m" button to switch to 1-minute timeframe
3. Wait for initial data to load (should see ~100-300 bars)
4. Drag chart left (pan backwards in time)
5. **Expected**: When approaching left edge, see console log: "📊 Near left edge..."
6. **Expected**: New data loads, chart updates with older bars
7. **Expected**: Can continue scrolling left indefinitely (until no more data)

## Success Criteria

- ✅ Console shows "📊 Near left edge..." when scrolling left
- ✅ API request for older data (`/api/intraday?...`) appears in Network tab
- ✅ Chart displays older bars seamlessly without jumping
- ✅ Can scroll back multiple times to load progressively older data
- ✅ No duplicate bars or timestamp conflicts

## Implementation Priority

**HIGH** - This is a core UX feature for intraday charts. Without infinite scroll:
- Users can only see 1-7 days of 1m/5m data
- Cannot analyze historical patterns
- Chart feels limited and frustrating
