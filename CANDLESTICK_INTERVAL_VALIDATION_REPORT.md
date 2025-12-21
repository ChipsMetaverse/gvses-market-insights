# Candlestick Interval Validation Report

## Executive Summary

**CRITICAL BUG FOUND**: Several timeframe buttons (30m, 2H, 4H) are displayed in the UI but are NOT properly mapped to API intervals, causing them to fallback to daily ('1d') data.

### Quick Summary Table

| Button | Frontend Mapping | Backend Support | Current Behavior | Expected Behavior |
|--------|-----------------|-----------------|------------------|-------------------|
| 1m | ✅ '1m' | ✅ YES | CORRECT ✓ | 1-minute candles |
| 5m | ✅ '5m' | ✅ YES | CORRECT ✓ | 5-minute candles |
| 15m | ✅ '15m' | ✅ YES | CORRECT ✓ | 15-minute candles |
| **30m** | ❌ fallback to '1d' | ✅ YES | **INCORRECT** ❌ | 30-minute candles |
| 1H | ✅ '1h' | ✅ YES | CORRECT ✓ | 1-hour candles |
| **2H** | ❌ fallback to '1d' | ❌ NO | **INCORRECT** ❌ | 2-hour candles (NOT SUPPORTED) |
| **4H** | ❌ fallback to '1d' | ✅ YES | **INCORRECT** ❌ | 4-hour candles |
| 1D | ✅ '1d' | ✅ YES | CORRECT ✓ | daily candles |

**Recommended Action**:
1. Add 30m and 4H mappings (Alpaca-supported)
2. Remove 2H button (NOT Alpaca-supported)

## Test Methodology

Tested each timeframe button at http://localhost:5174/demo by:
1. Clicking the timeframe button
2. Intercepting the API request to `/api/stock-history`
3. Capturing the `interval=` parameter
4. Comparing with expected behavior

## Results

| Timeframe Button | Expected Interval | Actual Interval | Status |
|-----------------|-------------------|-----------------|--------|
| 1m | 1m | 1m | ✅ CORRECT |
| 5m | 5m | 5m | ✅ CORRECT |
| 15m | 15m | 15m | ✅ CORRECT |
| 30m | 30m | **1d** | ❌ INCORRECT |
| 1H | 1h | 1h | ✅ CORRECT |
| 2H | 2h | **1d** | ❌ INCORRECT |
| 4H | 4h | **1d** | ❌ INCORRECT |
| 1D | 1d | 1d | ✅ CORRECT |

## Root Cause Analysis

### File: `/frontend/src/components/TradingDashboardSimple.tsx`

**Lines 161-178**: The `timeframeToInterval()` function mapping is incomplete:

```typescript
const timeframeToInterval = (timeframe: TimeRange): string => {
  const map: Record<TimeRange, string> = {
    // Intraday - Alpaca-native intervals only
    '1m': '1m',
    '5m': '5m',
    '15m': '15m',

    // Hours
    '1H': '1h',
    // ❌ MISSING: '30m', '2H', '4H'

    // Daily and long-term - Use daily interval
    '1D': '1d',
    '1Y': '1d',
    'YTD': '1d',
    'MAX': '1d'
  };
  return map[timeframe] || '1d';  // ⚠️ Unmapped timeframes fallback to '1d'
};
```

### Impact

When users click **30m, 2H, or 4H** buttons:
1. The button visual state changes (appears selected)
2. The UI updates to show the timeframe label
3. **BUT** the chart fetches daily ('1d') data instead
4. Users see daily candles when expecting 30-minute, 2-hour, or 4-hour candles

This creates a **misleading user experience** where the UI suggests one thing but displays another.

## Backend Interval Support Analysis

### Alpaca Markets API Support

Based on `/backend/services/alpaca_intraday_service.py`:

**Supported Intervals** (lines 201-211):
- ✅ 1Min ('1m')
- ✅ 5Min ('5m')
- ✅ 15Min ('15m')
- ✅ 30Min ('30m')
- ✅ 1Hour ('1h')
- ✅ 4Hour ('4h')
- ✅ 1Day ('1d')
- ✅ 1Week ('1w')
- ✅ 1Month ('1mo')

**NOT Supported**:
- ❌ 2Hour ('2h') - Not in Alpaca's TimeFrame mapping

### Verification Results

| Interval | Alpaca Support | Backend Implementation | Frontend Mapping |
|----------|---------------|----------------------|------------------|
| 30m | ✅ YES | ✅ YES | ❌ MISSING |
| 2h | ❌ NO | ❌ NO | ❌ MISSING |
| 4h | ✅ YES | ✅ YES | ❌ MISSING |

## Fix Required

### Option 1: Add Supported Intervals Only (RECOMMENDED)

Add mappings for **30m and 4h** only (Alpaca-supported):

```typescript
const timeframeToInterval = (timeframe: TimeRange): string => {
  const map: Record<TimeRange, string> = {
    // Intraday
    '1m': '1m',
    '5m': '5m',
    '15m': '15m',
    '30m': '30m',  // ✅ ADD THIS (Alpaca supported)

    // Hours
    '1H': '1h',
    '4H': '4h',    // ✅ ADD THIS (Alpaca supported)

    // Daily and long-term
    '1D': '1d',
    '1Y': '1d',
    'YTD': '1d',
    'MAX': '1d'
  };
  return map[timeframe] || '1d';
};
```

**Also**: Remove the **2H button** from the UI since it's not supported by Alpaca:

```typescript
// In TradingDashboardSimple.tsx line 2140
options={['1m', '5m', '15m', '30m', '1H', '4H', '1D', '1Y', 'YTD', 'MAX']}
// ✅ Added: 30m, 4H
// ❌ Removed: 2H (not supported)
```

### Option 2: Implement 2H via Client-Side Aggregation

If 2H functionality is required:
1. Fetch 1H data from backend
2. Aggregate every 2 bars on the frontend
3. Display as 2H candles

This adds complexity but maintains the feature.

### Alternative Solutions

If certain intervals are NOT supported by Alpaca:

**Option 1**: Remove unsupported timeframe buttons from the UI
```typescript
options={['1m', '5m', '15m', '1H', '1D', '1Y', 'YTD', 'MAX']}
// Remove: 30m, 2H, 4H if not supported
```

**Option 2**: Implement client-side aggregation
- Fetch smaller interval data (e.g., fetch 15m data for 30m display)
- Aggregate on the frontend to create larger candles
- More complex but provides full flexibility

**Option 3**: Add backend aggregation service
- Backend fetches fine-grained data
- Aggregates to requested interval
- Returns properly formatted candles

## Recommended Action

1. **Immediate Fix**: Add the three missing mappings to `timeframeToInterval()`
2. **Verification**: Test each interval with backend to confirm Alpaca support
3. **Fallback Plan**: If intervals not supported, remove those buttons from UI

## Testing Protocol

After implementing the fix, verify:
1. Click each timeframe button
2. Inspect Network tab for `/api/stock-history` request
3. Confirm `interval=` parameter matches button label
4. Verify candle timestamps have correct spacing:
   - 30m candles: 1800 second intervals
   - 2H candles: 7200 second intervals
   - 4H candles: 14400 second intervals

## Priority

**HIGH** - This directly impacts user trust and data accuracy.

Users currently clicking 30m, 2H, or 4H are seeing daily candles but thinking they're seeing intraday data. This could lead to incorrect trading decisions.

---

**Report Generated**: December 20, 2025
**Test Environment**: http://localhost:5174/demo
**Backend**: http://localhost:8000
**Symbol Tested**: TSLA
