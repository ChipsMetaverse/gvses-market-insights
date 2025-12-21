# Trendline Root Cause Analysis - ACTUAL ISSUE FOUND

**Date**: December 1, 2025
**Status**: ROOT CAUSE IDENTIFIED

---

## 🎯 The Real Problem

The `interval` parameter is completely ignored throughout the entire data fetching pipeline, causing the API to always return daily/hourly data instead of the requested timeframe.

### Evidence

**1. Debug logs from pattern detection (interval=1m):**
```
🔧 PatternDetector initialized with timeframe: 1m, candles: 65
🔧 [TRENDLINE] timeframe=1m, extend_right_days=1
🔧 [TRENDLINE] Bar calculation: time_interval=3600s, extension_seconds=86400s, bars=24
```

**Problem**: `time_interval=3600s` = 1 HOUR, not 1 minute!

**2. Candle data analysis:**
- Requested: `interval=1m` (1-minute bars)
- Received: 65 candles with 1-hour intervals
- This means the API returned ~2.7 days of hourly data instead of 1 day of minute data

---

## 🔍 Code Path Analysis

### Call Chain
```
mcp_server.py:1606
  → MarketServiceWrapper.get_stock_history(symbol, days=7, interval="1m")
    → Line 149: Cache lookup with hardcoded timeframe="1d" ❌
    → Line 174: Alpaca with no interval parameter ❌
    → Line 208: _get_ohlcv(symbol, range_str) - no interval passed ❌
      → market_service.py:373 get_ohlcv(symbol, range_str)
        → Lines 400-409: interval_map hardcoded to daily/weekly only ❌
```

### Critical Bugs Found

#### Bug 1: `market_service_factory.py` Line 149
```python
cached_candles = await db_service.get_market_candles(
    symbol=symbol.upper(),
    timeframe="1d",  # ← HARDCODED! Should be 'interval'
    start_time=datetime.now(timezone.utc) - timedelta(days=days),
    limit=days * 2
)
```

#### Bug 2: `market_service_factory.py` Line 174
```python
candles = await get_ohlcv_from_alpaca(mapped_symbol, days)
# ← Missing interval parameter!
```

#### Bug 3: `market_service_factory.py` Line 208
```python
candles = await self._get_ohlcv(mapped_symbol, range_str)
# ← Doesn't pass interval, only range_str
```

#### Bug 4: `market_service.py` Lines 400-409
```python
interval_map = {
    "1D": "1d",  # Daily only
    "5D": "1d",
    "1M": "1d",
    "3M": "1d",
    "6M": "1d",
    "YTD": "1d",
    "1Y": "1d",
    "5Y": "1wk"
}
# ← NO INTRADAY INTERVALS AT ALL!
```

---

## 💡 Why Trendlines Were Off-Screen

1. **Frontend requests**: `interval=1m` for 1-minute chart
2. **Backend returns**: Hourly or daily bars (ignoring interval)
3. **Pattern detector receives**: 65 hourly bars spanning ~2.7 days
4. **Trendline builder**:
   - Detects timeframe as "1m" ✅
   - Sets `extend_right_days=1` ✅
   - But calculates `time_interval=3600s` from actual candle data ❌
   - Extends trendline 24 hourly bars = 1 day ✅
   - But those 24 bars span from Nov 24 → Dec 3 (8 days!) ❌
5. **Frontend displays**: Only 4 hours of current session
6. **Result**: Trendlines span 8 days, chart shows 4 hours → ALL OFF-SCREEN

---

## ✅ The Fix

### Phase 1: Fix Data Fetching (CRITICAL)

**File**: `backend/services/market_service_factory.py`

**Change 1**: Pass interval to cache lookup (line 149)
```python
cached_candles = await db_service.get_market_candles(
    symbol=symbol.upper(),
    timeframe=interval,  # ← Use actual interval parameter
    start_time=datetime.now(timezone.utc) - timedelta(days=days),
    limit=days * 2
)
```

**Change 2**: Pass interval to Alpaca (line 174)
```python
candles = await get_ohlcv_from_alpaca(mapped_symbol, days, interval)  # ← Add interval
```

**Change 3**: Pass interval to Yahoo MCP (line 208)
```python
candles = await self._get_ohlcv(mapped_symbol, range_str, interval)  # ← Add interval
```

**Change 4**: Pass interval to cache storage (lines 177, 211)
```python
asyncio.create_task(self._cache_candles(symbol.upper(), interval, candles, "alpaca"))  # ← Use interval
```

**File**: `backend/services/market_service.py`

**Change 5**: Update `get_ohlcv` signature (line 373)
```python
async def get_ohlcv(symbol: str, range_str: str, interval: str = "1d") -> List[Dict[str, Any]]:
```

**Change 6**: Pass interval to MCP call (line 419)
```python
params = {
    "symbol": symbol,
    "period": period,
    "interval": interval  # ← ADD THIS
}
```

**Change 7**: Update `get_ohlcv_from_alpaca` to accept interval
```python
async def get_ohlcv_from_alpaca(symbol: str, days: int, interval: str = "1d") -> List[Dict[str, Any]]:
```

### Phase 2: Already Fixed ✅
- Timeframe-aware trendline extension (already implemented)
- Key levels timeframe-aware extension (already implemented)
- PatternDetector storing timeframe (already implemented)

---

## 🧪 Testing Plan

### Step 1: Implement Data Fetching Fix
- Update all 7 locations identified above
- Restart backend server

### Step 2: Test API Response
```bash
curl "http://localhost:8000/api/pattern-detection?symbol=TSLA&interval=1m" | python3 -c "
import sys, json
data = json.load(sys.stdin)
candles = data.get('patterns', {}).get('candles', [])
if len(candles) >= 2:
    interval = candles[-1]['time'] - candles[-2]['time']
    print(f'Candle interval: {interval} seconds')
    print(f'Expected for 1m: 60 seconds')
    print(f'Match: {\"✅\" if interval == 60 else \"❌\"}'
)
"
```

**Expected output**: `Candle interval: 60 seconds`

### Step 3: Test Trendline Coordinates
```bash
curl "http://localhost:8000/api/pattern-detection?symbol=TSLA&interval=1m" | jq '.trendlines[0]'
```

**Expected**:
- Start time: Within last 6.5 hours (1 trading day)
- End time: Within next 24 hours
- Total span: ~30 hours maximum

### Step 4: Visual Verification
- Take screenshot of 1m chart
- Verify trendlines are visible on screen
- Test all 12 timeframes

---

## ⏱️ Impact Assessment

### Before Fix
- ❌ All intraday intervals (1m, 5m, 15m, 30m, 1H, 2H, 4H) return daily/hourly data
- ❌ Pattern detection works on wrong timeframe data
- ❌ All trendlines off-screen for intraday charts
- ❌ Key levels (PDH, PDL, BL, SH, BTD) span weeks instead of hours

### After Fix
- ✅ Each interval returns correct granularity data
- ✅ Pattern detection analyzes appropriate timeframe
- ✅ Trendlines span ±1-2 days (visible on intraday charts)
- ✅ Key levels span appropriate timeframe
- ✅ All 12 timeframes work correctly

---

## 📝 Lessons Learned

1. **Visual verification is critical** - Console logs claimed success but trendlines were invisible
2. **Debug the full data pipeline** - The issue wasn't in trendline calculation, but in data fetching
3. **Check function signatures** - Multiple functions were missing the interval parameter
4. **Test with real data** - Analyzing actual candle intervals revealed the true problem

---

## 🚀 Next Steps

1. **[NOW]** Implement Phase 1 data fetching fixes
2. **[TEST]** Verify API returns correct candle intervals
3. **[TEST]** Verify trendline coordinates are reasonable
4. **[VISUAL]** Screenshot all 12 timeframes
5. **[DOCUMENT]** Update verification documents with accurate results

---

**Status**: Ready to implement Phase 1 fixes
**Estimated Time**: 45 minutes coding + 30 minutes testing
**Confidence**: HIGH - Root cause definitively identified through debug logging
