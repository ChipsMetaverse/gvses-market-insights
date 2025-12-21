# 🔍 Timeframe Display Investigation

**Date**: November 29, 2025
**Issue**: Chart timeframes not displaying accurate historical data ranges

---

## 📊 Test Results Summary

### 1Y Timeframe Investigation

#### Backend API (✅ **WORKING CORRECTLY**)
```bash
curl "http://localhost:8000/api/intraday?symbol=TSLA&interval=1d&startDate=2024-11-29&endDate=2025-11-29"
```

**Results**:
- **Total Bars**: 272
- **First Bar**: `2024-11-29T05:00:00+00:00` (Nov 29, 2024)
- **Last Bar**: `2025-11-28T14:30:00+00:00` (Nov 28, 2025)
- **✅ Covers full year**: Nov 2024 → Nov 2025

#### Frontend Configuration (✅ **CORRECT**)

From `TradingDashboardSimple.tsx`:
```typescript
timeframeToDays('1Y') = { fetch: 365, display: 365 }
timeframeToInterval('1Y') = '1d'
```

**Passed to Chart**:
- `initialDays`: 365
- `interval`: '1d'
- `displayDays`: 365

---

## 🐛 Issues Identified

### Issue #1: Future Date in API Request

**Console Log Evidence**:
```
[HOOK] 📡 Fetching data from 2024-11-30T01:58:29.045Z to 2025-11-30T01:58:29.045Z
```

**Problem**: End date is **Nov 30, 2025** (tomorrow), not Nov 29, 2025 (today)

**Location**: `useInfiniteChartData.ts` lines 164-167
```typescript
const endDate = new Date()
const startDate = new Date()
startDate.setDate(startDate.getDate() - initialDays)
```

**Impact**: Requesting 1 day of future data that doesn't exist

---

### Issue #2: Chart Only Displays 2025 Data

**Visual Evidence**: Screenshot `1Y-timeframe-test.png`
- X-axis shows: "**2025**, Mar, May, Jul, Sep, Nov, 26"
- Missing: All of Nov-Dec 2024 data

**Expected**: Should show "**2024**, Dec, **2025**, Mar, May, Jul, Sep, Nov"

**Data Received**: 272 bars spanning Nov 2024 - Nov 2025 ✅
**Data Displayed**: Only 2025 portion ❌

**Potential Causes**:
1. `applyTimeframeZoom` calculating wrong visible range
2. Chart initialization race condition
3. Data filtering after receipt
4. TradingView axis labeling issue

**Location**: `TradingChart.tsx` lines 288-305 (`applyTimeframeZoom`)

---

### Issue #3: Fluctuating Bar Counts

**Console Log Sequence**:
```
[HOOK] ✅ Received 271 bars from api
📊 Near left edge, loading more data...
[CHART] 💾 Setting data: 292 bars
📊 Near left edge, loading more data...
[CHART] 💾 Setting data: 313 bars
```

**Problem**: Lazy loading triggering multiple times immediately after initial load

**Impact**:
- Extra API calls
- Data changing during chart render
- Possible race conditions

**Root Cause**: Edge detection threshold (`0.15`) triggering on initial viewport

---

### Issue #4: React 18 Strict Mode Churn

**Console Evidence**:
```
[CHART] 🧹 Cleanup function running
[CHART] 🏗️ Chart initialization effect running
[CHART] 🧹 Cleanup function running
[CHART] 🏗️ Chart initialization effect running
[Error: Object is disposed]
```

**Problem**: Multiple mount/unmount cycles causing:
- Chart disposal errors
- Data setting during unmounted state
- Performance overhead

---

## 🔬 Root Cause Analysis

### Primary Issue: Visible Range Calculation

**Code**: `TradingChart.tsx:288-305`
```typescript
const applyTimeframeZoom = useCallback((data: any[]) => {
  if (!chartRef.current || !displayDays || data.length === 0) return

  const timeScale = chartRef.current.timeScale()
  const latestTime = data[data.length - 1].time  // Nov 28, 2025

  // Calculate start time based on displayDays
  const startTime = (latestTime as number) - displayDays * 24 * 60 * 60
  // startTime = Nov 28, 2024 (for displayDays=365)

  timeScale.setVisibleRange({
    from: startTime as any,
    to: latestTime,
  })
}, [displayDays])
```

**Expected**:
- From: Nov 28, 2024
- To: Nov 28, 2025

**Actual Chart Display**: Only shows 2025

**Hypothesis**: TradingView Lightweight Charts might have:
1. Timezone conversion issues
2. Minimum visible bar requirements
3. Auto-fitting logic overriding `setVisibleRange`

---

## 🧪 Additional Testing Needed

### Test Plan

1. **Intraday Timeframes (1H, 15m, 5m)**
   - Verify PDH/PDL display (✅ already confirmed working on 1H)
   - Check date ranges are accurate
   - Verify bar counts match expectations

2. **Daily Timeframe (1D)**
   - Not in dropdown menu, but used by large timeframes
   - Test with default selection

3. **Large Timeframes (2Y, 3Y, 5Y, MAX)**
   - Verify historical data display
   - Check if same 2024 data truncation occurs

4. **Lazy Loading Edge Cases**
   - Test with `edgeThreshold` = 0 (disable auto-load)
   - Verify manual scroll triggers correctly
   - Check deduplication working

---

## 💡 Recommended Fixes

### Fix #1: Correct End Date Calculation

**File**: `frontend/src/hooks/useInfiniteChartData.ts:164-167`

**Current**:
```typescript
const endDate = new Date()  // May include hours/timezone offset
```

**Suggested**:
```typescript
const endDate = new Date()
endDate.setHours(0, 0, 0, 0)  // Normalize to midnight UTC
```

---

### Fix #2: Investigate Visible Range Setting

**Options**:

**A. Remove applyTimeframeZoom entirely** (let TradingView auto-fit):
```typescript
// Comment out or remove applyTimeframeZoom call
// Let chart show full data range automatically
```

**B. Use fitContent() instead of setVisibleRange**:
```typescript
const timeScale = chartRef.current.timeScale()
timeScale.fitContent()  // Auto-fit to all data
```

**C. Add logging to debug**:
```typescript
console.log('Setting visible range:', {
  from: new Date(startTime * 1000).toISOString(),
  to: new Date(latestTime * 1000).toISOString(),
  dataLength: data.length,
  firstBar: new Date(data[0].time * 1000).toISOString(),
  lastBar: new Date(data[data.length - 1].time * 1000).toISOString()
})
```

---

### Fix #3: Adjust Lazy Loading Threshold

**File**: `frontend/src/components/TradingChart.tsx:558`

**Current**:
```typescript
edgeThreshold: 0.15,  // 15% from edge triggers load
```

**Suggested**:
```typescript
edgeThreshold: 0.05,  // 5% - only at extreme edge
```

Or add delay before first trigger:
```typescript
const [allowLazyLoad, setAllowLazyLoad] = useState(false)

useEffect(() => {
  // Wait 2 seconds after initial load before enabling lazy loading
  const timer = setTimeout(() => setAllowLazyLoad(true), 2000)
  return () => clearTimeout(timer)
}, [])
```

---

## 📝 Next Steps

1. ✅ **Verify backend working** - COMPLETE
2. ✅ **Test 1Y timeframe** - COMPLETE
3. ⏳ **Test other large timeframes** (2Y, 3Y, MAX)
4. ⏳ **Test intraday timeframes** (5m, 15m, 30m)
5. ⏳ **Test daily 1D display**
6. ⏳ **Implement fixes** based on test results
7. ⏳ **Verify with screenshots** using Playwright MCP

---

## 🎯 Success Criteria

- [ ] All timeframes show correct date ranges
- [ ] 1Y shows data from Nov 2024 - Nov 2025
- [ ] Intraday shows recent data only (1-7 days)
- [ ] No excessive lazy loading triggers
- [ ] PDH/PDL display on intraday intervals
- [ ] Smooth chart interactions without errors

---

**Status**: Investigation in progress
**Next Action**: Continue testing remaining timeframes
