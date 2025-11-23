# GVSES Widget Transform Requirements

**Date:** November 17, 2025
**Status:** 🔧 **TRANSFORM REQUIRED**
**Test File:** `backend/test_widget_data_shape.py`

---

## Executive Summary

The GVSES_Market_Data_Server tool output **does NOT match** the widget template expectations. A **Transform node is REQUIRED** in the Agent Builder workflow to reshape the data before rendering.

**Critical Issues Found:** 4
**Formatting Issues:** 0 (all formatting correct)
**Status:** Blocking widget rendering until Transform implemented

---

## ❌ Critical Data Mismatches

### Issue 1: Missing `company` Field

**Widget Expects:**
```json
{
  "company": "Apple Inc"
}
```

**Tool Returns:**
```json
{
  "price_data": {
    "company_name": "Apple Inc.",
    "symbol": "AAPL",
    ...
  }
}
```

**Transform Required:**
```javascript
{
  "company": tool_output.price_data.company_name
}
```

---

### Issue 2: News Missing `time` Field

**Widget Expects:**
```json
{
  "news": [
    {
      "title": "Apple Hits $4T...",
      "source": "GOBankingRates",
      "time": "2h",
      "url": "https://..."
    }
  ]
}
```

**Tool Returns:**
```json
{
  "news": [
    {
      "title": "Apple Hits $4T...",
      "source": "GOBankingRates",
      "published": 1763334848,  // Unix timestamp
      "link": "https://..."      // Not "url"
    }
  ]
}
```

**Transform Required:**
```javascript
{
  "news": tool_output.news.map(article => ({
    "title": article.title,
    "source": article.source,
    "time": formatRelativeTime(article.published),  // Convert timestamp to "2h", "5h", "1d"
    "url": article.link  // Rename "link" to "url"
  }))
}
```

**Helper Function Needed:**
```javascript
function formatRelativeTime(unixTimestamp) {
  const now = Math.floor(Date.now() / 1000);
  const diff = now - unixTimestamp;

  if (diff < 3600) return Math.floor(diff / 60) + "m";
  if (diff < 86400) return Math.floor(diff / 3600) + "h";
  return Math.floor(diff / 86400) + "d";
}
```

---

### Issue 3: News `url` vs `link` Field Name

**Widget Expects:** `url`
**Tool Returns:** `link`

**Transform Required:**
```javascript
{
  "url": article.link
}
```

---

### Issue 4: Patterns Wrong Data Type

**Widget Expects:**
```json
{
  "patterns": [
    {
      "type": "doji",
      "confidence": 75,
      "signal": "neutral",
      ...
    }
  ]
}
```

**Tool Returns:**
```json
{
  "patterns": {
    "detected": [
      {
        "type": "doji",
        "confidence": 75,
        "signal": "neutral",
        ...
      }
    ],
    "active_levels": { ... },
    "summary": { ... }
  }
}
```

**Transform Required:**
```javascript
{
  "patterns": tool_output.patterns.detected  // Extract the "detected" array
}
```

---

## ✅ Fields That Match (No Transform Needed)

| Field | Tool Output | Widget Expects | Status |
|-------|-------------|----------------|--------|
| `symbol` | ✅ "AAPL" | string | ✅ Match |
| `news[]` | ✅ Array of 5 items | array | ✅ Match |
| `news[].title` | ✅ String | string | ✅ Match |
| `news[].source` | ✅ String | string | ✅ Match |
| `price_data.*` | ✅ Present | (not used directly) | ✅ OK |
| `technical_levels.*` | ✅ Present | (mapped separately) | ✅ OK |
| `sentiment.*` | ✅ Present | object | ✅ Match |

---

## 🔧 Complete Transform Node Configuration

### Transform Node (JavaScript)

Add this Transform node AFTER the GVSES_Market_Data_Server tool call and BEFORE the G'sves agent output node:

```javascript
// Transform GVSES tool output to match widget template
const toolOutput = context.tool_result;  // Or however Agent Builder accesses tool output

// Helper function: Convert Unix timestamp to relative time
function formatRelativeTime(unixTimestamp) {
  const now = Math.floor(Date.now() / 1000);
  const diff = now - unixTimestamp;

  if (diff < 60) return "Just now";
  if (diff < 3600) return Math.floor(diff / 60) + "m";
  if (diff < 86400) return Math.floor(diff / 3600) + "h";
  if (diff < 604800) return Math.floor(diff / 86400) + "d";
  return new Date(unixTimestamp * 1000).toLocaleDateString();
}

// Transform the data
const widgetData = {
  // FIX 1: Extract company name from nested object
  company: toolOutput.price_data?.company_name || "Unknown Company",

  // Keep symbol as-is (already matches)
  symbol: toolOutput.symbol,

  // Map price_data (widget template uses "price" object)
  price: {
    current: toolOutput.price_data?.last || 0,
    change: toolOutput.price_data?.change_abs || 0,
    changePercent: toolOutput.price_data?.change_pct || 0,
    previousClose: toolOutput.price_data?.prev_close || 0
  },

  // Map technical levels (widget expects "sh", "bl", "btd")
  technical: {
    position: toolOutput.sentiment?.label || "Neutral",
    color: toolOutput.sentiment?.label === "Bullish" ? "success" :
           toolOutput.sentiment?.label === "Bearish" ? "danger" : "warning",
    levels: {
      sh: "$" + (toolOutput.technical_levels?.sell_high_level || 0).toFixed(2),
      bl: "$" + (toolOutput.technical_levels?.buy_low_level || 0).toFixed(2),
      now: "$" + (toolOutput.price_data?.last || 0).toFixed(2),
      btd: "$" + (toolOutput.technical_levels?.btd_level || 0).toFixed(2)
    }
  },

  // Map stats (widget expects formatted strings with units)
  stats: {
    open: "$" + (toolOutput.price_data?.open || 0).toFixed(2),
    volume: formatVolume(toolOutput.price_data?.volume),
    marketCap: formatMarketCap(toolOutput.price_data?.market_cap),
    dayLow: "$" + (toolOutput.price_data?.low || 0).toFixed(2),
    dayHigh: "$" + (toolOutput.price_data?.high || 0).toFixed(2),
    yearLow: "$" + (toolOutput.price_data?.week52_low || 0).toFixed(2),
    yearHigh: "$" + (toolOutput.price_data?.week52_high || 0).toFixed(2),
    eps: "$" + (toolOutput.price_data?.earnings_per_share || 0).toFixed(2),
    peRatio: (toolOutput.price_data?.pe_ttm || 0).toFixed(1)
  },

  // FIX 2 & 3: Transform news array (fix "time" and "url" fields)
  news: (toolOutput.news || []).map(article => ({
    title: article.title,
    source: article.source,
    time: formatRelativeTime(article.published),  // FIX 2: Add formatted time
    url: article.link  // FIX 3: Rename "link" to "url"
  })),

  // FIX 4: Extract patterns array from nested object
  patterns: toolOutput.patterns?.detected || [],

  // Keep sentiment as-is (already matches)
  sentiment: toolOutput.sentiment,

  // Optional: Map events if available
  events: toolOutput.events || []
};

// Helper functions
function formatVolume(vol) {
  if (!vol) return "0";
  if (vol >= 1e9) return (vol / 1e9).toFixed(1) + "B";
  if (vol >= 1e6) return (vol / 1e6).toFixed(1) + "M";
  if (vol >= 1e3) return (vol / 1e3).toFixed(1) + "K";
  return vol.toString();
}

function formatMarketCap(cap) {
  if (!cap) return "0";
  if (cap >= 1e12) return "$" + (cap / 1e12).toFixed(2) + "T";
  if (cap >= 1e9) return "$" + (cap / 1e9).toFixed(1) + "B";
  if (cap >= 1e6) return "$" + (cap / 1e6).toFixed(1) + "M";
  return "$" + cap.toString();
}

// Return transformed data for widget rendering
return widgetData;
```

---

## 📊 Validation Test Results

### Test Command
```bash
cd backend && python3 test_widget_data_shape.py
```

### Results Summary
```
================================================================================
📋 VALIDATION SUMMARY
================================================================================

⚠️  4 ISSUES FOUND:

   • company: MISSING (expected string)
   • news[0].time: MISSING (expected string)
   • news[0].url: MISSING (expected string)
   • patterns: Expected array, got dict

🔧 TRANSFORM REQUIRED: Tool output needs reshaping to match widget template expectations
```

### Formatting Validation
```
================================================================================
💰 FORMATTING VALIDATION (Critical for Widget Display)
================================================================================

✅ ALL FORMATTING CORRECT: Values already formatted with $ and units
```

**Note:** The tool already returns properly formatted values with `$` symbols and units (M/B/T), so no additional formatting is needed in the Transform node for technical levels and stats.

---

## 🚀 Implementation Steps

### Step 1: Add Transform Node in Agent Builder

1. **Navigate to your Agent Builder workflow**
2. **Locate the flow:** GVSES_Market_Data_Server tool → G'sves agent
3. **Insert Transform node** between them:
   ```
   GVSES_Market_Data_Server → [Transform Node] → G'sves agent (widget output)
   ```

### Step 2: Configure Transform Node

1. **Click "Add Node" → "Transform"**
2. **Paste the complete Transform code** (from section above)
3. **Set input variable:** `tool_result` or whatever variable holds the tool output
4. **Set output variable:** `widgetData`

### Step 3: Update Widget Template Reference

In the G'sves agent node configuration:
- **Input:** Use `widgetData` (from Transform) instead of raw `tool_result`
- **Output format:** Widget (GVSES stock card fixed)

### Step 4: Test the Workflow

1. **Publish workflow**
2. **Test in ChatKit:** Ask "What's the latest on AAPL?"
3. **Verify widget renders** with all sections populated
4. **Check all 4 fixed fields:**
   - ✅ Company name displays correctly
   - ✅ News shows "2h", "5h" (not timestamps)
   - ✅ News links work (url field present)
   - ✅ Patterns array renders (not nested object)

---

## 🧪 Edge Case Handling

The Transform handles these scenarios:

### Missing Data Fields
```javascript
company: toolOutput.price_data?.company_name || "Unknown Company"
```
Uses optional chaining (`?.`) and fallbacks to prevent errors.

### Empty News Array
```javascript
news: (toolOutput.news || []).map(...)
```
Defaults to empty array if news is null/undefined.

### Missing Pattern Data
```javascript
patterns: toolOutput.patterns?.detected || []
```
Returns empty array if patterns missing.

### Zero Values
All numeric fields handle `0` gracefully:
```javascript
current: toolOutput.price_data?.last || 0
```

---

## 📋 Pre-Flight Checklist

Before deploying to production:

- [ ] Transform node added to workflow
- [ ] Transform code pasted and validated
- [ ] Input/output variables configured correctly
- [ ] Workflow published successfully
- [ ] Test query executed ("What's the latest on AAPL?")
- [ ] Widget renders inline in chat (not JSON)
- [ ] Company name displays correctly
- [ ] News items show relative time ("2h", "5h")
- [ ] News links are clickable
- [ ] Patterns section populated with array
- [ ] All interactive elements functional
- [ ] Error scenarios tested (invalid symbol, etc.)

---

## 🔍 Debugging Tips

### If Widget Still Shows JSON Text

**Possible Causes:**
1. Transform node not connected properly in workflow
2. Output format not set to "Widget" in G'sves node
3. Widget file not uploaded to G'sves node
4. Workflow not published

**Solution:**
- Check workflow connections in visual editor
- Verify G'sves node "Output format" = Widget
- Re-upload GVSES-stock-card-fixed-.widget if needed
- Republish workflow

### If Widget Renders Blank

**Possible Causes:**
1. Transform returning undefined/null
2. Variable name mismatch (widgetData vs tool_result)
3. Jinja2 template variables not matching transformed data

**Solution:**
- Add console.log in Transform to debug output
- Check browser console for widget rendering errors
- Verify Jinja2 template variables match transformed object keys

### If Some Fields Missing

**Possible Causes:**
1. Tool returned null for that field
2. Transform mapping incorrect
3. Widget template referencing wrong key

**Solution:**
- Run test_widget_data_shape.py to see actual tool output
- Verify Transform handles null/undefined gracefully
- Check widget template uses correct variable names

---

## 📚 Related Documentation

- **Test Script:** `backend/test_widget_data_shape.py`
- **Widget Template:** `.playwright-mcp/GVSES-stock-card-fixed-.widget`
- **Deep Research Report:** `results.md`
- **Jinja2 Fix Guide:** `AGENT_BUILDER_JINJA_FIX.md`
- **Label Update Report:** `CHATKIT_LABEL_UPDATE_COMPLETE.md`

---

## ✅ Success Criteria

The widget is successfully integrated when:

1. ✅ Company name displays at top of card
2. ✅ News section shows "2h ago", "5h ago" (not Unix timestamps)
3. ✅ News items clickable with working URLs
4. ✅ Patterns section shows array of detected patterns
5. ✅ All technical levels (SH/BL/BTD) display with $ formatting
6. ✅ Statistics show units (47.4M volume, $4.03T market cap)
7. ✅ Interactive elements functional (timeframe buttons, etc.)
8. ✅ No console errors when rendering
9. ✅ Widget renders inline in chat (not separate modal/iframe)
10. ✅ Error states handled gracefully (invalid symbol shows message)

---

**Status:** Ready for Agent Builder implementation
**Next Step:** Add Transform node to workflow and test end-to-end

---

*Document created: November 17, 2025*
*Based on: test_widget_data_shape.py validation results*
*GVSES Widget Data Shape Validation Complete*
