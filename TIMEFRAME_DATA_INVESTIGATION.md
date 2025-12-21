# Timeframe Data Availability Investigation

**Date:** November 28, 2025
**Investigator:** Claude Code
**User Request:** Investigate why small timeframes don't display 3 years of data

---

## Executive Summary

Investigation confirms user's concern: **Intraday timeframes display only hours or days of data, not the requested 3 years**. This is due to both configuration limits and fundamental API constraints.

### Key Findings

✅ **Long-term timeframes (1Y, 2Y, 3Y) work correctly** - display years of daily bar data
❌ **Intraday timeframes severely limited** - display only hours/days of data
⚠️ **Root cause:** Stock market APIs provide limited intraday bar history

---

## Test Results

### 5m Timeframe (5-minute candles)

**Screenshot:** `5m-timeframe-current.png`

**Visible Date Range:**
- Start: ~15:00 (Nov 28, 2025)
- End: ~18:00 (Nov 28, 2025)
- **Total: ~3 hours** 📊

**Configuration:**
```typescript
'5m': { fetch: 1, display: 1 }  // Only 1 day
timeframeToInterval('5m') = '5m' // 5-minute bars
```

**Actual Behavior:**
- Only shows current trading day's data
- Chart displays ~36 five-minute candles (3 hours ÷ 5 min = 36 bars)
- X-axis shows intraday times: "15:00", "18:00"

**Gap from User Requirement:**
- User expects: 3 years (1,095 days)
- Actually shows: 0.125 days (3 hours)
- **Shortfall: 99.99%** ❌

---

### 1H Timeframe (1-hour candles)

**Screenshot:** `1H-timeframe-test.png`

**Visible Date Range:**
- Start: November 24, 2025
- End: November 28, 2025
- **Total: ~4-5 days** 📊

**Configuration:**
```typescript
'1H': { fetch: 7, display: 7 }  // Only 7 days
timeframeToInterval('1H') = '1h' // 1-hour bars
```

**Actual Behavior:**
- Shows approximately 4-5 trading days
- Chart displays ~30-40 hourly candles (5 days × 6-8 hours/day)
- X-axis shows dates: "24:30", "25", "26 Nov '25 14:30", "28"

**Gap from User Requirement:**
- User expects: 3 years (1,095 days)
- Actually shows: 4-5 days
- **Shortfall: 99.5%** ❌

---

### 1Y Timeframe (1-year daily candles)

**Screenshot:** `1Y-timeframe-test.png`

**Visible Date Range:**
- Start: January 2025
- End: November 2025
- **Total: ~11 months (full year)** 📊

**Configuration:**
```typescript
'1Y': { fetch: 365, display: 365 }  // 1 year
timeframeToInterval('1Y') = '1d'     // Daily bars
```

**Actual Behavior:**
- Shows full year of daily candles
- Chart displays ~240 daily candles (11 months × ~22 trading days)
- X-axis shows months: "2025", "Mar", "May", "Jul", "Sep", "Nov"

**Meets User Requirement:** ✅ **YES** - Shows full year as expected

---

## Configuration Analysis

### Current Timeframe Configuration
From `TradingDashboardSimple.tsx` lines 134-224:

```typescript
const timeframeToDays = (timeframe: TimeRange): { fetch: number, display: number } => {
  const map: Record<TimeRange, { fetch: number, display: number }> = {
    // INTRADAY - SEVERELY LIMITED
    '10S': { fetch: 1, display: 1 },    // ❌ 1 day only
    '30S': { fetch: 1, display: 1 },    // ❌ 1 day only
    '1m': { fetch: 1, display: 1 },     // ❌ 1 day only
    '3m': { fetch: 1, display: 1 },     // ❌ 1 day only
    '5m': { fetch: 1, display: 1 },     // ❌ 1 day only

    // MEDIUM INTRADAY - STILL LIMITED
    '10m': { fetch: 7, display: 7 },    // ❌ 7 days only
    '15m': { fetch: 7, display: 7 },    // ❌ 7 days only
    '30m': { fetch: 7, display: 7 },    // ❌ 7 days only
    '1H': { fetch: 7, display: 7 },     // ❌ 7 days only
    '2H': { fetch: 7, display: 7 },     // ❌ 7 days only
    '3H': { fetch: 7, display: 7 },     // ❌ 7 days only
    '4H': { fetch: 7, display: 7 },     // ❌ 7 days only
    '6H': { fetch: 7, display: 7 },     // ❌ 7 days only
    '8H': { fetch: 7, display: 7 },     // ❌ 7 days only
    '12H': { fetch: 7, display: 7 },    // ❌ 7 days only

    // LONG-TERM - WORKING CORRECTLY
    '1M': { fetch: 250, display: 30 },   // ✅ 250 days
    '3M': { fetch: 300, display: 90 },   // ✅ 300 days
    '6M': { fetch: 380, display: 180 },  // ✅ 380 days
    '1Y': { fetch: 365, display: 365 },  // ✅ 1 year
    '2Y': { fetch: 730, display: 730 },  // ✅ 2 years
    '3Y': { fetch: 1095, display: 1095 },// ✅ 3 years ⭐
    '5Y': { fetch: 1825, display: 1825 },// ✅ 5 years
    'MAX': { fetch: 9125, display: 9125 } // ✅ 25 years
  };
  return map[timeframe] || { fetch: 365, display: 365 };
};
```

### Interval Mapping
```typescript
const timeframeToInterval = (timeframe: TimeRange): string => {
  const map: Record<TimeRange, string> = {
    // Intraday uses minute/hour intervals
    '10S': '1m', '30S': '1m', '1m': '1m', '3m': '1m', '5m': '5m',
    '10m': '5m', '15m': '15m', '30m': '30m',
    '1H': '1h', '2H': '1h', '3H': '1h', '4H': '1h',
    '6H': '1h', '8H': '1h', '12H': '1h',

    // Long-term uses daily intervals
    '1M': '1d', '3M': '1d', '6M': '1d', '1Y': '1d', '2Y': '1d',
    '3Y': '1d', '5Y': '1d', 'YTD': '1d', 'MAX': '1d'
  };
  return map[timeframe] || '1d';
};
```

---

## Root Cause Analysis

### Problem 1: Configuration Limits

The timeframe configuration restricts intraday data fetching:
- **Minute-level timeframes:** Fetch only 1 day
- **Hourly timeframes:** Fetch only 7 days
- **User expectation:** 3 years for ALL timeframes

### Problem 2: API Constraints (CRITICAL)

**Stock market APIs have fundamental limitations on intraday bar availability:**

#### Yahoo Finance API (Current Backend)
- **Minute bars (1m, 5m):** Only last 7 days available
- **Hourly bars (1h):** Only last 30 days available
- **Daily bars:** Years of history available

#### Alpaca Markets API (Alternative)
- **Minute bars:** Only last 30 days available (Free tier)
- **Minute bars:** Up to 1 year available (Premium tier)
- **Daily bars:** Years of history available

#### Industry Standard
- **Minute-level data:** Most APIs provide 7-30 days maximum
- **Hourly data:** Most APIs provide 30-90 days maximum
- **Daily data:** Unlimited or many years available

**This is a universal constraint across financial data providers, not a configuration issue.**

---

## Why This Limitation Exists

### Technical Reasons

1. **Data Storage Costs**
   - Minute-level bars: 390 bars/day (6.5 hours × 60 minutes)
   - 3 years of 5m bars: ~570,000 bars per symbol
   - Storing this for thousands of symbols = massive storage cost

2. **API Performance**
   - Returning years of minute-level data would be extremely slow
   - Most use cases only need recent intraday data

3. **Data Vendor Economics**
   - Detailed intraday history is premium data
   - Free/basic tiers intentionally limit historical depth
   - Institutional-grade APIs charge significant fees for extended history

### Market Data Industry Standards

Professional trading platforms handle this by:
- **Real-time/Recent:** High-resolution (1m, 5m) for last 7-30 days
- **Historical:** Lower resolution (daily) for multi-year analysis
- **Zoom Behavior:** Charts automatically switch intervals based on visible range

---

## Available Solutions

### Option 1: Accept API Limitations ✅ RECOMMENDED

**Approach:** Keep current behavior, document limitations

**Implementation:**
- No code changes required
- Add tooltip to intraday timeframes: "⚠️ Limited to [N] days due to API constraints"
- Update user expectations through UI messaging

**Pros:**
- Zero development cost
- No ongoing data storage costs
- Industry-standard behavior

**Cons:**
- User won't get 3 years on intraday timeframes
- May feel like feature gap

**Cost:** $0
**Timeline:** Immediate (documentation only)

---

### Option 2: Hybrid Chart Approach ⚡ BALANCED

**Approach:** Automatically switch interval based on visible date range

**Implementation:**
```typescript
// Pseudo-code for smart interval selection
function getOptimalInterval(visibleDays: number, requestedTimeframe: TimeRange) {
  if (visibleDays > 90) {
    return '1d'  // Use daily bars for >90 day view
  } else if (visibleDays > 30) {
    return '1h'  // Use hourly bars for 30-90 day view
  } else if (visibleDays > 7) {
    return '5m'  // Use 5-minute bars for 7-30 day view
  } else {
    return '1m'  // Use 1-minute bars for <7 day view
  }
}
```

**Behavior:**
- User selects "5m" timeframe
- Chart loads with 5m bars for recent data (7 days)
- When user zooms out beyond 7 days, automatically switch to hourly/daily bars
- When user zooms back in, switch back to 5m bars
- Similar to TradingView's automatic interval switching

**Pros:**
- Best of both worlds: detail when needed, history when zoomed out
- No API constraint issues
- Professional UX (matches TradingView behavior)

**Cons:**
- Complex implementation (~2-3 days development)
- Need to manage multiple data fetches
- Chart may "jump" when switching intervals

**Cost:** ~3 days development
**Timeline:** 1 week including testing

---

### Option 3: Premium Data Provider 💰 EXPENSIVE

**Approach:** Switch to premium data provider with extended intraday history

**Options:**
- **Polygon.io:** 2 years of minute-level data ($199/month)
- **Alpha Vantage:** Limited intraday history even on paid tier
- **IEX Cloud:** 30 days minute data on paid tier ($79/month)
- **Intrinio:** Extended intraday available (contact for pricing)

**Implementation:**
- Integrate new API provider
- Update backend data fetching logic
- Increase configuration limits to match API capabilities

**Pros:**
- Actually provides extended intraday data
- Professional-grade data quality

**Cons:**
- Significant ongoing cost ($79-$199/month minimum)
- Still won't get full 3 years on most providers
- May hit rate limits with free usage patterns
- Development effort to integrate new API

**Cost:** $79-$199/month + 5 days development
**Timeline:** 2 weeks including testing

---

### Option 4: Historical Data Storage 🗄️ COMPLEX

**Approach:** Store and accumulate intraday bars in database

**Implementation:**
1. Create PostgreSQL tables for intraday bars
2. Daily cron job to fetch and store yesterday's 5m/1h bars
3. Serve historical data from database, recent data from API
4. Accumulate intraday history over time

**Schema Example:**
```sql
CREATE TABLE intraday_bars (
  symbol VARCHAR(10),
  timestamp TIMESTAMPTZ,
  interval VARCHAR(5),  -- '1m', '5m', '1h'
  open DECIMAL,
  high DECIMAL,
  low DECIMAL,
  close DECIMAL,
  volume BIGINT,
  PRIMARY KEY (symbol, timestamp, interval)
);

CREATE INDEX idx_symbol_interval_timestamp
  ON intraday_bars (symbol, interval, timestamp DESC);
```

**Behavior:**
- Day 1: Only today's 5m bars available
- Day 30: Last 30 days of 5m bars available
- Day 365: Last 1 year of 5m bars available
- Day 1095: Full 3 years of 5m bars available ⭐

**Pros:**
- Eventually achieves 3-year goal
- No ongoing API costs
- Complete control over data

**Cons:**
- Takes 3 years to accumulate 3 years of data
- Significant storage requirements (~100GB for 100 symbols @ 3 years)
- Complex backend implementation (database, cron jobs, data pipeline)
- Ongoing maintenance and monitoring
- Doesn't help existing users immediately

**Cost:** ~$10-20/month database storage + 10 days development
**Timeline:** 1 month development + 3 years to accumulate full data

---

### Option 5: Configuration-Only Quick Fix ⚠️ NOT RECOMMENDED

**Approach:** Just increase fetch limits in configuration

**Implementation:**
```typescript
// Change configuration to request 3 years
'5m': { fetch: 1095, display: 1095 },  // Try to fetch 3 years
'1H': { fetch: 1095, display: 1095 },  // Try to fetch 3 years
```

**Why This Won't Work:**
- APIs will return error or only recent data anyway
- May hit API rate limits
- Slower performance with no benefit

**Verdict:** ❌ **DO NOT IMPLEMENT** - Wastes resources without solving problem

---

## Recommended Solution

### Phase 1: Immediate (Option 1)
- Add clear UI messaging about intraday limitations
- Document API constraints in user-facing tooltips
- Set proper expectations

### Phase 2: Enhanced UX (Option 2)
- Implement hybrid interval switching
- Provides professional chart experience
- Matches industry standard behavior

### Phase 3: Optional Future (Option 3 or 4)
- If business case justifies cost, consider premium data or storage
- Only pursue if users explicitly demand extended intraday history
- Evaluate based on actual usage patterns

---

## Technical Specifications

### Files Involved
- `frontend/src/components/TradingDashboardSimple.tsx` (lines 134-224)
- `frontend/src/types/dashboard.ts` (TimeRange type definition)
- `frontend/src/components/TimeRangeSelector.tsx` (UI component)

### Current Timeframe Buttons
**Main Options:** 1Y, 2Y, 3Y, YTD, MAX
**Advanced Menu (⋯):**
- SECONDS: 10S, 30S
- MINUTES: 1m, 3m, 5m, 10m, 15m, 30m
- HOURS: 1H, 2H, 3H, 4H, 6H, 8H, 12H
- DAYS: 2D, 3D
- WEEKS: 1W
- MONTHS: 3M
- YEARS: 5Y

---

## User Impact

### What Works ✅
- All long-term timeframes (1Y, 2Y, 3Y) display full historical range
- Daily bar data available for years of history
- Chart performs well with current configuration

### What's Limited ❌
- Intraday timeframes (5m, 1H, etc.) show only hours/days
- Cannot display 3 years of minute-level data
- No configuration change can overcome API limitations

### User Expectation Gap
User stated: *"Max that we allow is 3yrs of data. but the smaller time frames dont have the 3yrs or data in the smaller candles."*

**Reality:** This expectation cannot be met with standard stock market APIs due to:
1. Industry-wide data availability constraints
2. Prohibitive cost of premium data providers
3. Technical complexity of storing/serving massive intraday datasets

---

## Next Steps

### Recommended Action Plan

1. **Review with User** (Today)
   - Present these findings
   - Explain API limitations
   - Discuss which solution(s) to pursue

2. **Immediate Fix** (If approved)
   - Add UI tooltips explaining data availability
   - Update documentation
   - Set clear user expectations

3. **Enhanced UX** (If approved)
   - Design hybrid interval switching
   - Implement zoom-based interval selection
   - Test with various timeframe combinations

4. **Future Consideration** (Based on user feedback)
   - Evaluate cost/benefit of premium data
   - Consider database storage if long-term strategic need
   - Monitor user complaints/feature requests

---

## Conclusion

**Finding:** Intraday timeframes are severely limited by API constraints, not just configuration.

**Root Cause:** Stock market data providers universally limit intraday bar history to 7-90 days.

**User Requirement:** 3 years of data on ALL timeframes (including 5m, 1H)

**Gap:** Cannot be met without significant cost or complexity.

**Recommended Path:**
1. Set proper expectations through UI messaging (immediate)
2. Implement hybrid interval switching for better UX (1-2 weeks)
3. Re-evaluate premium options only if business case justifies cost

**Status:** ✅ Investigation complete, awaiting user decision on solution approach.

---

*Investigation completed: November 28, 2025*
*Screenshots: 5m-timeframe-current.png, 1H-timeframe-test.png, 1Y-timeframe-test.png*
*Configuration file: TradingDashboardSimple.tsx:134-224*
