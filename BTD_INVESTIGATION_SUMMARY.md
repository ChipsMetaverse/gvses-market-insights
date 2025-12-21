# BTD (200 SMA) Investigation Summary
**Date:** December 14, 2025
**Issue:** BTD horizontal line doesn't match TradingView's 200 SMA indicator

---

## Problem Statement

User reported that the BTD horizontal line (from backend) does not match the purple 200 Daily SMA line (from TradingView chart indicator).

- **Backend BTD value:** $346.08
- **Frontend 200 SMA (TradingView):** $368.34
- **Discrepancy:** $22.26 (6.4%)

---

## Changes Made

###  1. Label Standardization ✅
**File:** `backend/key_levels.py` line 240
**Change:** Label now always shows "BTD (200 SMA)" regardless of actual period used
**Result:** SUCCESS - Label correctly displays "200 SMA" on all timeframes

### 2. Data Fetch Adjustment
**File:** `backend/mcp_server.py` line 1602
**Changes attempted:**
- Started at: 200 days → 138 trading candles
- Increased to: 1000 days → 687 trading candles
- Adjusted to: 365 days → 249 trading candles
- **Current:** 700 days → 481 trading candles

### 3. Removed PatternDetector Candle Limit ✅
**File:** `backend/pattern_detection.py` line 395
**Change:** Removed `candles[-200:]` limit, now uses all fetched candles
**Result:** SUCCESS - All fetched candles are passed to key levels calculation

###  4. BTD Calculation Method
**File:** `backend/key_levels.py` lines 216-235
**Method:** Uses last 200 candles from available dataset
**Formula:** `sum(last_200_closing_prices) / 200`

---

## Current Backend Calculation

```
Total candles fetched: 481 (from 700 calendar days)
Date range: Jan 15, 2024 to Dec 11, 2025
BTD uses: Last 200 candles (candles[281:481])
BTD date range: Feb 27, 2025 to Dec 11, 2025
First close in BTD window: $292.98
Last close in BTD window: $458.96
**Calculated BTD: $346.08**
```

---

## Investigation Findings

### Root Cause
The backend and frontend are calculating 200 SMA from **different datasets**:

1. **Backend:**
   - Fetches 481 candles (700 calendar days)
   - Takes last 200 candles: Feb 27, 2025 - Dec 11, 2025
   - Calculates SMA: $346.08

2. **Frontend (suspected):**
   - May be displaying different time range
   - TradingView 200 SMA indicator: $368.34
   - Suggests using candles from earlier date range (possibly including more historical data from 2024)

### Key Insight
The 200 SMA value is **highly sensitive to which 200 candles are used**:
- Last 200 from 249 candles (Dec 2024 start): Would give different value
- Last 200 from 481 candles (Jan 2024 start): Currently $346.08
- Using all 481 candles: $290.11 (too low - incorrect calculation)

---

## Attempted Solutions

### ❌ Approach 1: Use ALL candles
- Changed to average ALL 481 candles
- Result: $290.11 (too low - not a true "200 SMA")
- **Rejected:** Doesn't match definition of 200-period SMA

### ❌ Approach 2: Increase data fetch
- Increased from 365 to 700 calendar days
- Result: Still $346.08 (same 200 candles)
- **Issue:** More data doesn't change which 200 candles are selected

### ❓ Current Status
- Backend: Correctly calculating 200 SMA as $346.08
- Frontend: Showing 200 SMA as $368.34
- **Gap remains:** Need to identify frontend's actual data range

---

## Next Steps

### Option A: Verify Frontend Data Range
1. Check what date range the TradingView chart is actually displaying
2. Verify which candles the TradingView 200 SMA indicator is using
3. Match backend fetch to exact frontend range

### Option B: Accept Different Calculation Windows
1. Backend uses most recent 200 candles (standard definition)
2. Frontend may use different window based on visible chart range
3. Document that BTD represents "backend-calculated 200 SMA" vs "chart-displayed 200 SMA"

### Option C: Make Backend Match Frontend Dynamically
1. Frontend sends start_date/end_date with pattern-detection API call
2. Backend calculates 200 SMA from those exact candles
3. Guarantees perfect alignment

---

## Technical Details

### BTD Calculation Code
```python
# Current implementation (key_levels.py:216-235)
period = min(200, len(candles))  # Use 200 or fewer if not enough data
selected_candles = candles[-period:]  # Last N candles
closing_prices = [candle['close'] for candle in selected_candles]
sma_value = sum(closing_prices) / len(closing_prices)
```

### Data Fetch Configuration
```python
# mcp_server.py:1594-1605
days_map = {
    "1d": 700,   # Daily: 700 days → ~481 trading candles
    # ... other timeframes
}
```

---

## Files Modified

1. `backend/key_levels.py` - BTD calculation and labeling
2. `backend/mcp_server.py` - Data fetch configuration
3. `backend/pattern_detection.py` - Removed 200-candle limit

---

## Recommendations

**Immediate Action:**
1. Take screenshot of frontend chart showing:
   - Time range selector setting
   - Date range actually displayed on chart
   - TradingView 200 SMA value and where it appears on chart
   - BTD horizontal line position

2. Compare frontend's actual data range with backend's calculation window

**Long-term Solution:**
Implement Option C - have frontend pass desired date range to pattern-detection endpoint for guaranteed alignment.

---

**Status:** INVESTIGATION IN PROGRESS
**Last Updated:** Dec 14, 2025 23:06 PST
