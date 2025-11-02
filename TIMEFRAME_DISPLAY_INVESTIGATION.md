# Timeframe Display Issue - Investigation Report

**Date**: January 2025  
**Status**: 🔍 **CRITICAL BUG IDENTIFIED**

---

## 🚨 **ROOT CAUSE IDENTIFIED**

### The Bug

**Location**: `frontend/src/components/TradingChart.tsx` (lines 219-230)

**Problem**: Mismatch between `timeframeToDays()` values and `applyTimeframeZoom()` logic

###Logic Flow (BROKEN):

```
User selects "1M" timeframe
    ↓
timeframeToDays('1M') returns 250 days
    ↓
TradingChart receives days=250
    ↓
applyTimeframeZoom(chartData) checks:
    if (days <= 1) return 86400      // 1D
    if (days <= 5) return 5 * 86400   // 5D
    if (days <= 30) return 30 * 86400  // 1M  ← SHOULD MATCH HERE
    if (days <= 180) return 180 * 86400 // 6M
    if (days <= 365) return 365 * 86400 // 1Y  ← ACTUALLY MATCHES HERE!
    ↓
Since days=250 is NOT <= 30, it skips to 365
    ↓
Chart displays 1 YEAR of data, not 1 MONTH ❌
```

---

## 📊 **Timeframe Mapping Issues**

| User Selects | timeframeToDays() | applyTimeframeZoom() Condition | Actual Display | Expected Display |
|--------------|-------------------|-------------------------------|----------------|------------------|
| **1M** | 250 days | `days <= 365` → 1Y | **1 YEAR** ❌ | 1 MONTH |
| **3M** | 300 days | `days <= 365` → 1Y | **1 YEAR** ❌ | 3 MONTHS |
| **6M** | 380 days | `days <= 730` → 2Y | **2 YEARS** ❌ | 6 MONTHS |
| **1Y** | 365 days | `days <= 365` → 1Y | 1 YEAR ✅ | 1 YEAR |
| **2Y** | 730 days | `days <= 730` → 2Y | 2 YEARS ✅ | 2 YEARS |

**Result**: Users selecting 1M, 3M, or 6M see WAY more data than expected!

---

## 🔍 **Why This Design Exists**

The comment at line 120-121 explains the intent:

```typescript
// Daily+ - Historical data (fetch more than needed for technical indicators)
'1D': 200,   // Fetch 200 days but display 1
```

**Intent**: Fetch extra historical data for technical indicators (MA200, etc.) but only DISPLAY the requested timeframe.

**Problem**: The `applyTimeframeZoom()` function doesn't know the difference between:
- Fetched days (250) 
- Display days (30)

It only receives `days=250` and assumes that's what to display.

---

## 🛠️ **Solution Options**

### Option A: Pass Separate Values (Recommended)
Pass BOTH `fetchDays` and `displayDays` to TradingChart:

```typescript
// TradingDashboardSimple.tsx
const timeframeToDays = (timeframe: TimeRange): { fetch: number, display: number } => {
  const map: Record<TimeRange, { fetch: number, display: number }> = {
    '1D': { fetch: 200, display: 1 },
    '5D': { fetch: 200, display: 5 },
    '1M': { fetch: 250, display: 30 },
    '3M': { fetch: 300, display: 90 },
    '6M': { fetch: 380, display: 180 },
    '1Y': { fetch: 365, display: 365 },
    // ...
  }
  return map[timeframe] || { fetch: 365, display: 365 }
}

// Pass both values
<TradingChart
  fetchDays={timeframeToDays(selectedTimeframe).fetch}
  displayDays={timeframeToDays(selectedTimeframe).display}
  // ...
/>
```

Then in `TradingChart.tsx`:

```typescript
const applyTimeframeZoom = useCallback((chartData: any[]) => {
  // Use displayDays instead of days
  const timeframeInSeconds = displayDays * 86400
  // ...
}, [displayDays])
```

### Option B: Simplify timeframeToDays (Simpler, but less flexible for indicators)
Just return the actual display days:

```typescript
const timeframeToDays = (timeframe: TimeRange): number => {
  const map: Record<TimeRange, number> = {
    '1D': 1,
    '5D': 5,
    '1M': 30,    // Display 30 days, not 250
    '3M': 90,    // Display 90 days, not 300
    '6M': 180,   // Display 180 days, not 380
    '1Y': 365,
    // ...
  }
  return map[timeframe] || 365
}
```

**Tradeoff**: Technical indicators might not have enough historical data for MA200, Bollinger Bands, etc.

### Option C: Fix applyTimeframeZoom Logic (Quick Fix)
Adjust the conditions to match the actual `timeframeToDays` values:

```typescript
const timeframeInSeconds = (() => {
  if (days <= 1) return 86400        // 1D
  if (days <= 5) return 5 * 86400    // 5D
  if (days <= 200) return 30 * 86400  // 1M ← CHANGED from 30 to 200
  if (days <= 300) return 90 * 86400  // 3M ← ADDED
  if (days <= 380) return 180 * 86400 // 6M ← CHANGED from 180 to 380
  if (days <= 730) return 365 * 86400 // 1Y
  if (days <= 1095) return 730 * 86400 // 2Y
  if (days <= 1825) return 1095 * 86400 // 3Y
  return null // MAX/YTD
})()
```

---

## 🧪 **Test Plan**

Test the following across 3 assets (NVDA, TSLA, AAPL):

### Test Cases
1. **1D**: Should show 1 day of data
2. **5D**: Should show 5 days of data
3. **1M**: Should show ~30 days of data (currently shows 1 YEAR ❌)
4. **3M**: Should show ~90 days of data (currently shows 1 YEAR ❌)
5. **6M**: Should show ~180 days of data (currently shows 2 YEARS ❌)
6. **1Y**: Should show 365 days of data ✅
7. **MAX**: Should show all available data ✅

### Verification Method
For each timeframe:
1. Check first visible candle date
2. Check last visible candle date
3. Calculate date range
4. Verify matches expected timeframe

---

## 💡 **Recommended Fix**

**Use Option A (Pass Separate Values)** - This provides the best of both worlds:
- ✅ Technical indicators get enough historical data
- ✅ Users see the correct timeframe
- ✅ No ambiguity in the code
- ✅ Future-proof for adding more sophisticated indicators

**Implementation Priority**: **CRITICAL** - Users are seeing incorrect data ranges

**Estimated Effort**: 1-2 hours

**Files to Modify**:
1. `frontend/src/components/TradingDashboardSimple.tsx`
2. `frontend/src/components/TradingChart.tsx`

---

## 📋 **Implementation Steps**

1. Update `timeframeToDays()` to return `{ fetch, display }`
2. Pass both values as props to `TradingChart`
3. Update `TradingChart` component signature
4. Update `applyTimeframeZoom()` to use `displayDays`
5. Test all timeframes across NVDA, TSLA, AAPL
6. Verify technical indicators still work (MA200, etc.)

---

**End of Investigation Report**

*Critical bug identified. Fix required before production deployment.*

