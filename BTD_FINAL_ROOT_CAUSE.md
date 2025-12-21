# BTD (200 SMA) Investigation - FINAL ROOT CAUSE
**Date:** December 14, 2025
**Status:** ✅ ROOT CAUSE IDENTIFIED

---

## Executive Summary

The BTD horizontal line ($346.08) doesn't match the TradingView 200 SMA indicator ($368.34) because **two different data services are being used**:

1. **Pattern Detection** (`/api/pattern-detection`): Uses `MarketServiceFactory` → Alpaca API → **249 candles** → BTD = $346.08 ❌
2. **Stock History** (`/api/stock-history`): Uses `HistoricalDataService` with 3-tier caching → **275 cached candles** → 200 SMA = $368.34 ✅
3. **Frontend Chart**: Calls `/api/stock-history` → Gets 275 candles → TradingView calculates 200 SMA = $368.34 ✅

---

## The Problem

### Architecture Mismatch

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Chart                           │
│  Calls: /api/stock-history                                   │
│  Uses: HistoricalDataService (3-tier cache)                  │
│  Gets: 275 candles (from cache)                              │
│  200 SMA: $368.34 ✅                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┴──────────────────────┐
        │                                             │
        ▼                                             ▼
┌──────────────────┐                     ┌────────────────────┐
│ TradingView      │                     │ BTD Horizontal     │
│ 200 SMA          │                     │ Line               │
│ Indicator        │                     │ Source: Pattern    │
│ $368.34 ✅       │                     │ Detection          │
└──────────────────┘                     └────────────────────┘
                                                     │
                                                     ▼
                                         ┌────────────────────┐
                                         │ Pattern Detection  │
                                         │ Uses: MarketService│
                                         │ Factory (no cache) │
                                         │ Gets: 249 candles  │
                                         │ BTD: $346.08 ❌    │
                                         └────────────────────┘
```

### Code Paths

**Path 1: Frontend Chart → TradingView 200 SMA**
```python
# mcp_server.py line 938
@app.get("/api/stock-history")
async def get_stock_history(symbol, days=30, interval="1d"):
    from services.historical_data_service import get_historical_data_service
    data_service = get_historical_data_service()  # 3-tier cache!
    bars = await data_service.get_bars(symbol, interval, start_date, end_date)
    # Returns 275 candles from cache → TradingView → 200 SMA = $368.34 ✅
```

**Path 2: Pattern Detection → BTD Calculation**
```python
# mcp_server.py line 1609
service = MarketServiceFactory.get_service()
history = await service.get_stock_history(symbol, days=365, interval="1d")
# Returns 249 candles from Alpaca → BTD = $346.08 ❌
```

---

## Technical Details

### HistoricalDataService (stock-history endpoint)
- **File**: `services/historical_data_service.py`
- **Caching**: 3-tier (Redis → Supabase → Alpaca)
- **Current State**: Has 275 candles cached from earlier fetch
- **Date Range**: Dec 16, 2024 - Dec 12, 2025
- **200 SMA**: $368.34 ✅

### MarketServiceFactory (pattern-detection endpoint)
- **File**: `services/market_service_factory.py`
- **Caching**: Supabase only (currently returning 404)
- **Current State**: Fetches fresh from Alpaca API
- **Date Range**: Dec 14, 2024 - Dec 14, 2025 (365 days back from today)
- **Candles**: 249 trading days
- **200 SMA**: $346.08 ❌

---

## Why Different Candle Counts?

### Frontend (275 candles)
- Cached data from **earlier fetch** when "365 days" meant different date range
- Start date: **Dec 16, 2024** (from when cache was populated)
- End date: **Dec 12, 2025**
- Trading days: **275**

### Backend Pattern Detection (249 candles)
- Fresh Alpaca data with current "365 days back"
- Start date: **Dec 14, 2024** (365 days from today, Dec 14, 2025)
- End date: **Dec 14, 2025**
- Trading days: **249**

**Difference**: 26 candles = ~1 month of trading days

---

## Solutions

### Option 1: Use Same Data Service (RECOMMENDED ✅)
Change pattern detection to use `HistoricalDataService` instead of `MarketServiceFactory`:

```python
# In mcp_server.py line 1608-1610
# OLD:
service = MarketServiceFactory.get_service()
history = await service.get_stock_history(symbol_upper, days=days, interval=interval)

# NEW:
from services.historical_data_service import get_historical_data_service
data_service = get_historical_data_service()
end_dt = datetime.now(timezone.utc)
start_dt = end_dt - timedelta(days=days)
bars = await data_service.get_bars(symbol_upper, interval, start_dt, end_dt)
history = {"candles": bars, "data_source": "historical_data_service"}
```

**Pros:**
- ✅ Guarantees frontend and backend use SAME data
- ✅ Leverages 3-tier caching for performance
- ✅ Future-proof - all endpoints use same service

**Cons:**
- ⚠️ Requires code changes to pattern detection
- ⚠️ Need to test all timeframes (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)

### Option 2: Clear Cache
Clear Redis and Supabase cache for TSLA to force fresh fetch:

**Pros:**
- ✅ Quick temporary fix
- ✅ No code changes

**Cons:**
- ❌ Temporary - will drift again over time
- ❌ Loses performance benefits of caching
- ❌ Doesn't fix root architectural issue

### Option 3: Synchronize Data Fetching
Make both services fetch exact same date range at same time:

**Pros:**
- ✅ Minimal code changes

**Cons:**
- ❌ Complex synchronization logic
- ❌ Still maintains dual architecture
- ❌ Fragile - prone to drift

---

## Recommendation

**Implement Option 1**: Migrate pattern detection to use `HistoricalDataService`.

This aligns the entire backend on a single data service architecture, ensuring:
1. Frontend chart and backend calculations always use same data
2. Better performance through 3-tier caching
3. Simpler architecture - one data service to maintain
4. No cache synchronization issues

---

## Files to Modify (Option 1)

1. **`backend/mcp_server.py`** lines 1608-1622
   - Replace `MarketServiceFactory` with `get_historical_data_service()`
   - Convert bars response to expected format

2. **`backend/key_levels.py`** lines 216-235 (BTD calculation)
   - No changes needed - already correct

---

## Verification Steps

After implementing fix:
1. Clear all caches (Redis + Supabase) for clean slate
2. Call `/api/stock-history?symbol=TSLA&days=365&interval=1d`
3. Call `/api/pattern-detection?symbol=TSLA&interval=1d`
4. Verify both return **same number of candles** from **same date range**
5. Verify BTD value matches TradingView 200 SMA ($368.34)
6. Take screenshot to confirm visual alignment

---

**Status:** READY FOR IMPLEMENTATION
**Priority:** HIGH - Affects trading decision accuracy
**Estimated Effort:** 30 minutes (code + testing)
