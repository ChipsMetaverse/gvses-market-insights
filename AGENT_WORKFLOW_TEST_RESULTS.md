# Agent Builder Workflow Test Results

**Date**: November 17, 2025
**Status**: ⚠️ Partial Success - Schema Validation Error

---

## Test Summary

**Query**: "What's TSLA trading at?"

**Workflow Execution**:
✅ Start node → Success
✅ Intent Classifier → Success (`{"intent":"market_data","symbol":"TSLA","confidence":"high"}`)
✅ Transform node → Success (mapped intent, symbol, confidence)
✅ G'sves Agent → **Partial Success** (called tools, returned data, but schema mismatch)
❌ End node → **Failed** (CEL expression error)

---

## Error Details

```
Workflow failed: Error evaluating CEL expression:
("no such member in mapping: 'selectedTimeframe'", <class 'KeyError'>, None).
(code: user_error)
```

**Root Cause**: Agent output JSON is missing the `selectedTimeframe` field, which is **required** by the widget schema (line 329 of .widget file).

---

## Agent Output Analysis

### What Worked ✅
The agent successfully:
1. Called MCP tools (get_stock_quote)
2. Retrieved real TSLA data:
   - Company: "Tesla, Inc."
   - Symbol: "TSLA"
   - Current price: "$408.92"
   - Change: "+4.57 USD" (success color)
   - After-hours: "$410.13" (+1.21)
   - Stats: open, dayLow, dayHigh, yearLow, yearHigh, volume, marketCap
3. Returned valid JSON structure

### What Failed ❌

**Missing Required Field**:
```json
"selectedTimeframe": "1D"  // ← MISSING (required by schema)
```

**Incorrect Fields**:
```json
"timeframes": ["Real-time", "Post-market"]  // ← WRONG
// Should be: ["1D", "5D", "1M", "3M", "6M", "1Y", "YTD", "MAX"]

"chartData": []  // ← EMPTY
// Should contain 100+ historical data points from getStockHistory

"technical": {
  "position": "",  // ← EMPTY (should be "Bullish", "Bearish", or "Neutral")
  "color": "secondary",
  "levels": {
    "sh": "",   // ← EMPTY (should be price like "$450.00")
    "bl": "",   // ← EMPTY
    "now": "",  // ← EMPTY
    "btd": ""   // ← EMPTY
  }
}

"events": []  // ← EMPTY (should have earnings dates, FOMC, etc.)
```

---

## Widget Schema Requirements

From `.widget` file analysis:

### Required Fields (line 329):
- `company` ✅
- `symbol` ✅
- `timestamp` ✅
- `price` ✅ (with current, changeLabel, changeColor)
- `timeframes` ⚠️ (present but wrong values)
- **`selectedTimeframe`** ❌ **MISSING**
- `chartData` ⚠️ (present but empty)
- `stats` ✅ (all 9 fields present)
- `technical` ⚠️ (present but empty levels)

### CEL Expression That Failed:
```jinja
{% if selectedTimeframe == tf %}\"solid\"{% else %}\"outline\"{% endif %}
```
This expression compares `selectedTimeframe` to each timeframe button to highlight the selected one. Since `selectedTimeframe` doesn't exist in the output, the CEL expression throws KeyError.

---

## Fix Strategy

### Solution: Update G'sves Agent Instructions

The agent instructions need to be more explicit about the **exact schema requirements**:

1. **Add `selectedTimeframe` field** (default: `"1D"`)
2. **Fix `timeframes` array** to use standard values: `["1D", "5D", "1M", "3M", "6M", "1Y", "YTD", "MAX"]`
3. **Populate `chartData`** by calling `getStockHistory` tool with proper parameters
4. **Calculate technical levels** (sh, bl, now, btd) based on price data
5. **Add `events` array** with upcoming earnings/FOMC dates

### Updated Instructions Template

```markdown
## CRITICAL OUTPUT REQUIREMENTS

You MUST include these exact fields in your JSON output:

1. **selectedTimeframe** (REQUIRED):
   - Type: string
   - Default value: "1D"
   - Valid values: "1D", "5D", "1M", "3M", "6M", "1Y", "YTD", "MAX"

2. **timeframes** (REQUIRED):
   - Type: array of strings
   - MUST be exactly: ["1D", "5D", "1M", "3M", "6M", "1Y", "YTD", "MAX"]
   - Do NOT use: ["Real-time", "Post-market"]

3. **chartData** (REQUIRED):
   - Type: array of {date: string, Close: number}
   - MUST call getStockHistory(symbol, 100, "1d") to populate
   - MUST have 100+ data points
   - Example: [{"date": "2025-11-17", "Close": 408.92}, ...]

4. **technical.levels** (REQUIRED):
   - sh, bl, now, btd MUST be price strings, NOT empty strings
   - Calculate based on recent price data
   - Example: {"sh": "$450.00", "bl": "$425.00", "now": "$408.92", "btd": "$385.00"}

5. **technical.position** (REQUIRED):
   - MUST be "Bullish", "Bearish", or "Neutral" (NOT empty string)

6. **events** (REQUIRED):
   - Type: array
   - Include upcoming earnings, FOMC meetings, etc.
   - If no events, use empty array []
```

---

## Implementation Steps

1. **Update Agent Instructions**:
   - Add explicit field requirements section
   - Include examples for each required field
   - Specify tool calls needed (getStockHistory for chartData)

2. **Test Again**:
   - Send same query: "What's TSLA trading at?"
   - Verify selectedTimeframe is present
   - Verify chartData has 100+ data points
   - Verify technical levels are calculated
   - Verify widget renders without errors

3. **Validate Output**:
   - Check all required fields exist
   - Verify data types match schema
   - Ensure widget template renders visually

---

## Next Steps

1. ✅ Identified root cause: Missing `selectedTimeframe` field
2. ⏳ Update G'sves Agent instructions with explicit schema requirements
3. ⏳ Re-test workflow in Preview mode
4. ⏳ Verify widget renders correctly
5. ⏳ Publish workflow

---

**Created**: November 17, 2025, 10:52 PM
**Priority**: HIGH - Blocking workflow completion
**Estimated Fix Time**: 15-20 minutes (instructions update + retest)
