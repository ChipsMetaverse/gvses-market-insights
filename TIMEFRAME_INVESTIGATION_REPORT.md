# Timeframe Investigation Report
## Commits Analyzed: e6a6d01 & f0d1529

### Executive Summary
**CRITICAL FINDING:** The frontend `timeframeToDays` mapping was CORRECT at both commits (`'1D': 1`). The issue is NOT with the original code - it's a **semantic misunderstanding** between:

1. **Frontend Timeframe Button "1D"** = User expects 3 years of daily candles
2. **Backend Days Parameter** = Currently treated as "number of days to fetch"
3. **Yahoo Finance Range String** = "1D" means "today's data only"

---

## Original Implementation (e6a6d01 & f0d1529)

### Frontend: `TradingDashboardSimple.tsx`
```typescript
const timeframeToDays = (timeframe: TimeRange): number => {
  const map: Record<TimeRange, number> = {
    // Intraday (all map to 1 day of data)
    '10S': 1, '30S': 1, '1m': 1, '3m': 1, '5m': 1,
    '10m': 1, '15m': 1, '30m': 1,
    // Hours (2-7 days for sufficient context)
    '1H': 2, '2H': 3, '3H': 3, '4H': 5, '6H': 5, '8H': 7, '12H': 7,
    // Days
    '1D': 1,     // ❌ This was CORRECT for intraday, WRONG for daily chart
    '2D': 2,
    '3D': 3,
    '5D': 5,
    '1W': 7,
    // Months
    '1M': 30, '6M': 180,
    // Years
    '1Y': 365, '2Y': 730, '3Y': 1095, '5Y': 1825,
    'MAX': 3650
  };
  return map[timeframe] || 30;
};
```

### Backend: `market_service_factory.py` (lines 184-197)
```python
# Map days to range string for Yahoo
if days <= 1:
    range_str = "1D"      # ❌ Returns TODAY ONLY
elif days <= 5:
    range_str = "5D"
elif days <= 30:
    range_str = "1M"
elif days <= 90:
    range_str = "3M"
elif days <= 180:
    range_str = "6M"
elif days <= 365:
    range_str = "1Y"
else:
    range_str = "5Y"

candles = await self._get_ohlcv(mapped_symbol, range_str)
```

---

## The Real Problem

### Scenario: User clicks "1D" button
1. **Frontend:** `timeframeToDays('1D')` returns `1`
2. **Frontend:** Calls API with `days=1`
3. **Backend:** Receives `days=1`, maps to `range_str="1D"`
4. **Yahoo Finance:** Returns only today's trading data (partial day)
5. **Alpaca (Production):** Returns 0 candles (incomplete trading day)
6. **Result:** Chart fails with "No historical data available"

### What User Expected: "1D" = Daily Chart View
- **Display:** 3 years of data (1095 days)
- **Candle Size:** 1 day per candle
- **NOT:** 1 day of trading data

---

## Why Local Worked vs Production Failed

### Local (Working)
- Falls back to **Yahoo Finance**
- Yahoo's `range_str="1D"` returns *some* data even for partial days
- User saw partial success

### Production (Failing)
- Uses **Alpaca API**
- Alpaca is strict: `days=1` for an incomplete trading day = 0 candles
- Chart displays "No historical data available"

---

## My Incorrect Fix (commits 8fb104f-45db7f5)
```typescript
// Changed all short timeframes to request 7 days
'1D': 7,  // ❌ WRONG - This is a hack, not a fix
```

**Why This Was Wrong:**
- Treated the symptom (Alpaca returning 0 candles) not the cause
- User expected 3 YEARS of data for "1D", not 7 DAYS
- Misunderstood the purpose of timeframe buttons

---

## Correct Understanding

### Two Different Concepts Mixed Together

#### 1. **Intraday Timeframes** (candle size < 1 day)
```
'10S', '30S', '1m', '5m', '15m', '30m', '1H', '4H'
```
- Should fetch **recent data only** (1-7 days)
- High-resolution view of recent price action
- Correct: `'1m': 7` (7 days of 1-minute candles)

#### 2. **Daily+ Timeframes** (candle size >= 1 day)
```
'1D', '2D', '1W', '1M', '1Y'
```
- Should fetch **historical data** (years)
- Long-term price trends
- Correct: `'1D': 1095` (3 years of 1-day candles)

---

## Correct Fix Required

### Option 1: Separate Timeframe Semantics
```typescript
const timeframeToDays = (timeframe: TimeRange): number => {
  const map: Record<TimeRange, number> = {
    // Intraday - recent data only
    '10S': 1, '30S': 1, '1m': 1, '5m': 1,
    '15m': 7, '30m': 7, '1H': 7, '4H': 7,
    
    // Daily+ - historical data
    '1D': 1095,   // ✅ 3 years
    '1W': 1095,   // ✅ 3 years
    '1M': 3650,   // ✅ 10 years
    '1Y': 3650,   // ✅ 10 years
    'MAX': 7300   // ✅ 20 years
  };
  return map[timeframe] || 365;
};
```

### Option 2: Rename Buttons (Clearer UX)
```
Instead of: '1D', '1W', '1M', '1Y'
Use:        'Day', 'Week', 'Month', 'Year' (implicit: "show N years of data")
```

---

## Action Items

### 1. Revert My Changes
```bash
git checkout 6a4bc5f -- frontend/src/components/TradingDashboardSimple.tsx
```

### 2. Apply Correct Fix
Update `timeframeToDays` to distinguish intraday vs daily+ timeframes:
- Intraday: 1-7 days of data
- Daily+: 3+ years of data

### 3. Test Both Scenarios
```bash
# Daily chart (should show 3 years)
curl "http://localhost:8000/api/stock-history?symbol=TSLA&days=1095"

# Intraday chart (should show 7 days)
curl "http://localhost:8000/api/stock-history?symbol=TSLA&days=7"
```

---

## Conclusion

**The original code (`'1D': 1`) was semantically incorrect** because:
- "1D" button means "show me a daily chart" (long-term view)
- NOT "show me 1 day of data" (short-term view)

**My fix (`'1D': 7`) was even worse** because:
- Still didn't match user expectations (3 years, not 7 days)
- Was a workaround for Alpaca, not a real solution

**The correct fix:**
- `'1D': 1095` (3 years of daily candles)
- Aligns with user's mental model
- Works with both Alpaca and Yahoo Finance
