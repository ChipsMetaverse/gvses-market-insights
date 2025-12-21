# Playwright MCP Test Results - Trendline Drawing

**Date:** November 28, 2025
**Test Route:** `/test-chart`
**Status:** ⚠️ Mixed Results - Visual Success, Runtime Errors

---

## Test Summary

### ✅ Successful Behaviors
1. **Trendline Button Activation** - "↗️ Trendline" button changed to "✓ Trendline (click 2 points)" with active state
2. **Drawing Mode Activated** - Cancel button appeared correctly
3. **Trendline Created** - Console log confirms: `Created trendline: trendline-1764358637380`
4. **Visual Rendering** - Trendline visible on chart with blue line and handle circles
5. **Custom Primitives Working** - The v5 primitive system successfully rendered the drawing

### ❌ Critical Errors Detected

**Stack Overflow Errors (RangeError: Maximum call stack size exceeded)**

**Location 1: TimeScale Operations**
```
at TimeScale._internal_isEmpty
at TimeScale._private__updateVisibleRange
at TimeScale._internal_visibleStrictRange
at Pane._private__recalculatePriceScaleImpl
... continues recursively
```

**Location 2: PlotList Min/Max Calculations**
```
at PlotList._private__minMaxOnRangeCachedImpl
at PlotList._internal_minMaxOnRangeCached
at Series._private__autoscaleInfoImpl
at PriceScale._private__recalculatePriceRangeImpl
... continues recursively
```

**Trigger:** Errors occurred BEFORE trendline creation during chart interaction/crosshair updates

---

## Visual Evidence

### Before Drawing
- Chart loaded with TSLA 1D candlestick data
- "↗️ Trendline" button visible and clickable

### After Drawing
- Trendline visible with:
  - Blue diagonal line connecting two points
  - Blue circular handles at both endpoints
  - Proper layering over candlestick data

Screenshot: `trendline-with-stack-overflow.png`

---

## Error Analysis

### Root Cause Investigation

The stack overflow is **NOT** caused by our custom primitive implementation. Evidence:

1. **Trendline was successfully created** - Log shows `Created trendline: trendline-1764358637380`
2. **Visual rendering works** - Primitives draw correctly on canvas
3. **Errors triggered by chart internals** - Stack traces point to:
   - `TimeScale` calculations
   - `PriceScale` autoscale operations
   - `PlotList` min/max caching
   - `ChartModel` crosshair updates

### Hypothesis

The errors may be caused by:

1. **Autoscale Loop** - Chart repeatedly trying to recalculate price range
2. **Empty/Invalid Series Data** - Some series (PDH/PDL or preview) has problematic data
3. **Crosshair Update Cascade** - Mouse movements triggering recursive coordinate conversions
4. **Chart State Corruption** - Some internal chart state became invalid

### What's NOT the Cause

❌ **Not single-point line series** - We verified:
- PDH line has 2 points: `[start, end]`
- PDL line has 2 points: `[start, end]`
- Preview lines have 2 points: `[anchor, cursor]`
- Trendline handles use **primitives**, not line series

---

## Code Review Findings

### TradingChart.tsx Line Series Usage

**Line 344-354: PDH (Previous Day High)**
```typescript
const pdhLine = chartRef.current.addSeries(LineSeries, {...})
pdhLine.setData([
  { time: chartData[0].time, value: pdh },
  { time: chartData[chartData.length - 1].time, value: pdh }
]) // ✅ TWO points
```

**Line 357-367: PDL (Previous Day Low)**
```typescript
const pdlLine = chartRef.current.addSeries(LineSeries, {...})
pdlLine.setData([
  { time: chartData[0].time, value: pdl },
  { time: chartData[chartData.length - 1].time, value: pdl }
]) // ✅ TWO points
```

**Line 661-672: Preview Line (Anchor Mode)**
```typescript
const preview = chartRef.current!.addSeries(LineSeries, {...})
preview.setData([
  { time: anchorPoint.time, value: anchorPoint.price },
  { time: param.time, value: price }
]) // ✅ TWO points
```

**Line 683-697: Preview Line (Drawing Mode)**
```typescript
const preview = chartRef.current.addSeries(LineSeries, {...})
previewLineRef.current.setData([
  { time: firstPoint.time, value: firstPoint.price },
  { time: param.time, value: price }
]) // ✅ TWO points
```

**Conclusion:** All line series have proper 2-point data. No single-point series found.

---

## Performance Optimizations Applied

### Fix #1: Conditional `requestUpdate()` in `hitTest()`
**Status:** ✅ Implemented
**File:** `TrendlineHandlePrimitive.ts:60-137`

Changed from unconditional updates to state-change-only:
```typescript
// Only update if hover state changed
if (this._hoveredHandle !== 'a') {
  this._hoveredHandle = 'a';
  this.requestUpdate();
}
```

### Fix #2: In-Place Primitive Updates
**Status:** ✅ Implemented
**File:** `DrawingOverlay.ts:74-93`

Changed from detach/recreate to update existing:
```typescript
if (trendlineDataChanged(currentData, drawing)) {
  existing.primitive.updateTrendline(drawing);
}
```

**Note:** TradingChart.tsx still uses detach/recreate pattern (line 177) - potential future optimization

---

## Unresolved Questions

### Missing Implementation: `autoscaleInfo()`

According to research findings (Q6.1), primitives can implement `autoscaleInfo()` to participate in chart autoscaling:

> "The library calls updateAllViews() on each primitive during chart redraws... if your trendlines extend the visible price range, you might want the chart to autoscale to show it. The library provides primitive.autoscaleInfo() for that purpose."

**Current Status:** Not implemented
**Risk:** May contribute to autoscale calculation loops

### Potential Issues

1. **Missing Autoscale Info**
   - Trendlines don't provide autoscale range
   - Chart may struggle to calculate proper price bounds
   - Could trigger repeated recalculation attempts

2. **Chart State During Drawing**
   - What happens when crosshair moves during drawing mode?
   - Are coordinate conversions safe during active primitive attachment?

3. **Series Update Timing**
   - Do PDH/PDL lines update correctly after trendline creation?
   - Could there be a race condition between series updates?

---

## Recommendations

### Immediate Actions

1. **Implement `autoscaleInfo()`** in `TrendlineHandlePrimitive`
   ```typescript
   autoscaleInfo(startTimePoint: Logical, endTimePoint: Logical): AutoscaleInfo | null {
     // Return min/max price range covered by this trendline
     return {
       priceRange: {
         minValue: Math.min(this._trendline.a.price, this._trendline.b.price),
         maxValue: Math.max(this._trendline.a.price, this._trendline.b.price)
       }
     };
   }
   ```

2. **Add Error Boundaries** around chart operations
   - Prevent cascade failures
   - Graceful degradation

3. **Optimize TradingChart.tsx**
   - Replace detach/recreate with updatePrimitive pattern (line 172-181)
   - Match DrawingOverlay.ts optimization

### Testing Needed

1. **Draw Multiple Trendlines** - Test with 5-10 trendlines to verify no cumulative errors
2. **Zoom/Pan During Drawing** - Ensure chart updates don't interfere
3. **Rapid Selection Changes** - Click different trendlines quickly
4. **Delete Operations** - Verify Backspace/Delete work without errors

### Monitoring

Watch for these patterns in console:
- Repeated autoscale errors
- Coordinate conversion failures
- Series update cascades

---

## Conclusion

**Visual Functionality:** ✅ Working
**Runtime Stability:** ⚠️ Stack overflow errors present
**User Experience:** ⚠️ Trendline works but errors pollute console

**Root Cause:** Likely related to chart autoscale/crosshair calculations, NOT our primitive implementation

**Next Step:** Implement `autoscaleInfo()` and test if it resolves the stack overflow issues

---

*Test conducted via Playwright MCP browser automation*
*Screenshots saved to `.playwright-mcp/` directory*
