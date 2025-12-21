# PDH/PDL Not Displaying - Investigation Report

## Date
December 1, 2025 (4:35 AM)

## User Report
User reported that PDH/PDL levels are "still not right" on the 1H chart, specifically noting:
- "there aren't 24 candles in between the PDH and PDL levels which indicates something is wrong"
- Provided screenshot showing only ONE visible horizontal line on chart
- Despite previous fix removing duplicate frontend calculation

## Investigation via Playwright MCP

### Visual Evidence
Screenshot taken at 1H timeframe shows:
- **Only ONE horizontal dotted line visible** around $430
- Expected to see TWO distinct lines for PDH and PDL
- Chart price range: ~$380-$500 ($120 total range)

### API Response Verification
Pattern detection API (`/api/pattern-detection?symbol=TSLA&interval=1h`) returns:
```json
{
  "PDH": {
    "price": 430.3,
    "label": "PDH",
    "color": "#ff9800"
  },
  "PDL": {
    "price": 430.02,
    "label": "PDL",
    "color": "#ff9800"
  }
}
```

**Issue**: PDH and PDL are only **$0.28 apart** (0.065% difference)

### Console Log Analysis
Frontend logs repeatedly show:
```
[AUTO-TRENDLINES] ✅ Drew key_level: PDH (#ff9800)
[AUTO-TRENDLINES] ✅ Drew key_level: PDL (#ff9800)
```

**Problem**: Logs claim both lines are drawn, but only one is visible on chart.

### Backend Calculation Verification
Backend logs show:
```
INFO:mcp_server:Fetching daily data for PDH/PDL calculation (intraday interval: 1h)
INFO:mcp_server:Previous day high/low: PDH=430.3, PDL=430.02
INFO:pattern_detection:Using passed PDH/PDL: {'pdh': 430.3, 'pdl': 430.02}
```

### Comparison with Other Key Levels
Current values from API:
- **SH (Sell High)**: $474.07
- **BL (Buy Low)**: $382.78
- **PDH (Previous Day High)**: $430.30
- **PDL (Previous Day Low)**: $430.02

Percentage differences:
- PDH vs SH: 9.2% difference ✅ (passes 1% deduplication threshold)
- PDL vs BL: 12.3% difference ✅ (passes 1% deduplication threshold)

**Conclusion**: The 1% deduplication filter in `key_levels.py` is NOT removing PDH/PDL.

## Root Cause Analysis

### Daily Data Discrepancy
Fetching daily history directly shows:
```
2025-11-26: High=$426.935, Low=$416.98, Close=$426.51
2025-11-28: High=$432.85, Low=$426.245, Close=$430.14 (Alpaca data)
2025-11-28: High=$432.93, Low=$426.2, Close=$430.17 (Yahoo data)
```

Using `candles[-2]` (second-to-last) gives:
- High: $432.85
- Low: $426.245
- **Range: $6.60** (normal daily range for TSLA)

But pattern detection reports:
- PDH: $430.30
- PDL: $430.02
- **Range: $0.28** (abnormally tight)

### The Problem
**The PDH/PDL values ($430.30/$430.02) don't match ANY of the daily candles in the last 5 days!**

This suggests:
1. **Stale/cached data** - Pattern detection is using old daily data
2. **Wrong data source** - Different data between pattern detection and stock history endpoints
3. **Incorrect array indexing** - `[-2]` might not be selecting the right "previous day"

### November 28, 2025 Context
- November 28 was **Thanksgiving** (market closed)
- Current date: November 30 (Saturday, market closed)
- Last trading day: November 29 (Friday)
- Previous trading day: November 27 (Wednesday)

The `[-2]` index would give Nov 28 (Thanksgiving), which might have limited after-hours trading or be incorrect altogether.

## Code Analysis

### Backend: mcp_server.py (lines 1620-1641)
```python
if is_intraday:
    daily_history = await service.get_stock_history(symbol_upper, days=5, interval="1d")
    if daily_history and "candles" in daily_history and len(daily_history["candles"]) >= 2:
        # Get previous day (second to last candle) high and low
        prev_day = daily_history["candles"][-2]
        daily_pdh_pdl = {
            'pdh': prev_day['high'],
            'pdl': prev_day['low']
        }
```

**Issue**: Uses `[-2]` which assumes:
- Arrays are always sorted chronologically
- Second-to-last = previous trading day
- Doesn't account for market holidays or data source inconsistencies

### Backend: key_levels.py (lines 70-89)
```python
if daily_data and 'pdh' in daily_data and 'pdl' in daily_data:
    # Only add PDH if different from SH (>1%)
    if sh_level and abs(daily_data['pdh'] - sh_level['price']) / sh_level['price'] > 0.01:
        levels['PDH'] = { ... }

    # Only add PDL if different from BL (>1%)
    if bl_level and abs(daily_data['pdl'] - bl_level['price']) / bl_level['price'] > 0.01:
        levels['PDL'] = { ... }
```

**Status**: This 1% deduplication is working correctly - PDH and PDL pass the threshold and are included in the response.

## Why Only One Line Appears

Despite API returning both PDH ($430.30) and PDL ($430.02), only one line is visible because:

1. **Lines are too close together**: $0.28 separation on a $120 price range = 0.23%
2. **Canvas rendering overlap**: TradingView Lightweight Charts renders both lines at nearly the same pixel coordinates
3. **Same color**: Both use `#ff9800` (orange)
4. **Same style**: Both use dotted lines

The lines are **actually being drawn**, but they appear as a single line due to overlap.

## The Real Problem

**The backend is calculating the wrong "previous day" data**, resulting in:
- Incorrect PDH/PDL values that don't match actual daily candles
- Abnormally tight range ($0.28 instead of expected $5-10 for TSLA)
- User confusion because the levels don't represent the actual previous trading day

## Expected vs Actual

### What User Expects (1H chart)
- PDH: Previous trading day's high (~$432.85)
- PDL: Previous trading day's low (~$426.20)
- Range: ~$6-7 (24+ hourly candles between them)
- Visual: Two clearly separated orange dotted lines

### What's Actually Displayed
- PDH: $430.30 (incorrect/cached value)
- PDL: $430.02 (incorrect/cached value)
- Range: $0.28 (< 1 hourly candle)
- Visual: Appears as single line due to overlap

## Recommended Fix

### Option 1: Fix "Previous Day" Logic
Instead of using `candles[-2]`, implement proper previous trading day detection:
```python
# Find most recent complete trading day (not today)
today = datetime.now().date()
prev_day_candle = None
for candle in reversed(daily_history["candles"]):
    candle_date = parse_timestamp(candle['timestamp']).date()
    if candle_date < today:
        prev_day_candle = candle
        break
```

### Option 2: Use Last Complete Candle
Always use `[-1]` instead of `[-2]` to get the most recent complete daily candle:
```python
prev_day = daily_history["candles"][-1]  # Most recent day
```

### Option 3: Add Data Validation
Verify the PDH/PDL range is reasonable:
```python
pdh_pdl_range = prev_day['high'] - prev_day['low']
avg_price = (prev_day['high'] + prev_day['low']) / 2
range_percent = pdh_pdl_range / avg_price

# Reject if range is < 0.5% (likely bad data)
if range_percent < 0.005:
    logger.warning(f"PDH/PDL range too tight ({pdh_pdl_range:.2f}, {range_percent:.1%}), skipping")
    daily_pdh_pdl = None
```

## Files Involved

1. `/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/mcp_server.py` (lines 1620-1641)
   - PDH/PDL daily data fetching logic

2. `/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/key_levels.py` (lines 70-89)
   - PDH/PDL deduplication logic (working correctly)

3. `/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/components/TradingChart.tsx`
   - Frontend rendering (working correctly after duplicate calculation removal)

## Related Documentation

- `PDH_PDL_DUPLICATE_CALCULATION_FIX.md` - Previous fix removing frontend calculation
- `PDH_PDL_INTRADAY_ONLY_FIX.md` - Earlier fix making PDH/PDL intraday-only

## Next Steps

1. Fix the "previous day" selection logic in `mcp_server.py`
2. Add validation to reject unrealistic PDH/PDL ranges
3. Add more detailed logging to show which daily candle is being used
4. Verify fix with Playwright MCP showing two distinct lines
5. Update documentation with correct implementation

## Testing Checklist

- [ ] Backend logs show correct previous day being selected
- [ ] PDH/PDL values match actual daily candle high/low
- [ ] Visual verification shows two distinct orange dotted lines on 1H chart
- [ ] Lines are appropriately spaced (not overlapping)
- [ ] Works correctly across market holidays and weekends
