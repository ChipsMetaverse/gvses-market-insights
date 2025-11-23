# GVSES Widget - Required Code Changes

## Overview
This document shows the exact code changes needed to add the missing features identified in the comparison with Jeeves 2.0.

---

## Change 1: Add After-Hours Price Display

**Location:** After the price change badge section, before the first Divider

**Current Code (lines in price section):**
```json
{
  "type": "Row",
  "align": "center",
  "children": [
    {
      "type": "Col",
      "gap": 1,
      "children": [
        {
          "type": "Title",
          "value": "$189.32",
          "size": "3xl",
          "weight": "bold"
        },
        {
          "type": "Row",
          "gap": 2,
          "children": [
            {
              "type": "Badge",
              "label": "+1.45 (+0.77%)",
              "color": "success",
              "variant": "soft"
            }
          ]
        }
      ]
    },
    // ... rest of section
  ]
}
```

**NEW Code to Add:**
```json
{
  "type": "Row",
  "align": "center",
  "children": [
    {
      "type": "Col",
      "gap": 1,
      "children": [
        {
          "type": "Title",
          "value": "$189.32",
          "size": "3xl",
          "weight": "bold"
        },
        {
          "type": "Row",
          "gap": 2,
          "children": [
            {
              "type": "Badge",
              "label": "+1.45 (+0.77%)",
              "color": "success",
              "variant": "soft"
            }
          ]
        },
        // ⭐ NEW: After-hours price display
        {
          "type": "Row",
          "gap": 2,
          "align": "center",
          "children": [
            {
              "type": "Caption",
              "value": "After Hours:",
              "color": "secondary"
            },
            {
              "type": "Text",
              "value": "$272.82",
              "size": "sm",
              "weight": "semibold"
            },
            {
              "type": "Badge",
              "label": "+0.41 (+0.15%)",
              "color": "success",
              "variant": "soft",
              "size": "sm"
            }
          ]
        }
      ]
    },
    // ... rest of section
  ]
}
```

---

## Change 2: Expand Timeframe Buttons (5 → 8 buttons)

**Current Code:**
```json
{
  "type": "Row",
  "gap": 2,
  "children": [
    { "type": "Button", "key": "1D", "label": "1D", "size": "sm", "pill": true, "variant": "solid", ... },
    { "type": "Button", "key": "1W", "label": "1W", "size": "sm", "pill": true, "variant": "outline", ... },
    { "type": "Button", "key": "1M", "label": "1M", "size": "sm", "pill": true, "variant": "outline", ... },
    { "type": "Button", "key": "3M", "label": "3M", "size": "sm", "pill": true, "variant": "outline", ... },
    { "type": "Button", "key": "1Y", "label": "1Y", "size": "sm", "pill": true, "variant": "outline", ... }
  ]
}
```

**NEW Code (Add 3 more buttons):**
```json
{
  "type": "Row",
  "gap": 2,
  "children": [
    { "type": "Button", "key": "1D", "label": "1D", "size": "sm", "pill": true, "variant": "solid", ... },
    { "type": "Button", "key": "5D", "label": "5D", "size": "sm", "pill": true, "variant": "outline", ... },  // ⭐ NEW
    { "type": "Button", "key": "1M", "label": "1M", "size": "sm", "pill": true, "variant": "outline", ... },
    { "type": "Button", "key": "3M", "label": "3M", "size": "sm", "pill": true, "variant": "outline", ... },
    { "type": "Button", "key": "6M", "label": "6M", "size": "sm", "pill": true, "variant": "outline", ... },  // ⭐ NEW
    { "type": "Button", "key": "YTD", "label": "YTD", "size": "sm", "pill": true, "variant": "outline", ... },  // ⭐ NEW
    { "type": "Button", "key": "1Y", "label": "1Y", "size": "sm", "pill": true, "variant": "outline", ... },
    { "type": "Button", "key": "5Y", "label": "5Y", "size": "sm", "pill": true, "variant": "outline", ... },  // ⭐ NEW
    { "type": "Button", "key": "max", "label": "MAX", "size": "sm", "pill": true, "variant": "outline", ... }  // ⭐ NEW
  ]
}
```

---

## Change 3: Redesign Quick Stats Section (3-Column Table)

**Current Code (1 row with 3 stats):**
```json
{
  "type": "Row",
  "align": "stretch",
  "children": [
    {
      "type": "Col",
      "children": [
        { "type": "Caption", "value": "Open" },
        { "type": "Text", "value": "$187.80", "weight": "semibold" }
      ]
    },
    { "type": "Spacer" },
    {
      "type": "Col",
      "children": [
        { "type": "Caption", "value": "Volume" },
        { "type": "Text", "value": "42.3M", "weight": "semibold" }
      ]
    },
    { "type": "Spacer" },
    {
      "type": "Col",
      "children": [
        { "type": "Caption", "value": "Day Range" },
        { "type": "Text", "value": "$186.90 – $190.12", "weight": "semibold" }
      ]
    }
  ]
}
```

**NEW Code (3-column table with 7 stats):**
```json
{
  "type": "Col",
  "gap": 2,
  "children": [
    // Row 1: Open | Volume | Market Cap
    {
      "type": "Row",
      "align": "stretch",
      "children": [
        {
          "type": "Col",
          "flex": 1,
          "children": [
            { "type": "Caption", "value": "Open", "size": "xs" },
            { "type": "Text", "value": "271.06", "size": "sm", "weight": "semibold" }
          ]
        },
        {
          "type": "Col",
          "flex": 1,
          "children": [
            { "type": "Caption", "value": "Volume", "size": "xs" },
            { "type": "Text", "value": "47.4M", "size": "sm", "weight": "semibold" }
          ]
        },
        {
          "type": "Col",
          "flex": 1,
          "children": [
            { "type": "Caption", "value": "Market Cap (TTM)", "size": "xs" },  // ⭐ NEW
            { "type": "Text", "value": "3.01T", "size": "sm", "weight": "semibold" }
          ]
        }
      ]
    },
    // Row 2: Day Low | Year Low | EPS
    {
      "type": "Row",
      "align": "stretch",
      "children": [
        {
          "type": "Col",
          "flex": 1,
          "children": [
            { "type": "Caption", "value": "Day Low", "size": "xs" },
            { "type": "Text", "value": "269.60", "size": "sm", "weight": "semibold" }
          ]
        },
        {
          "type": "Col",
          "flex": 1,
          "children": [
            { "type": "Caption", "value": "Year Low", "size": "xs" },  // ⭐ NEW
            { "type": "Text", "value": "169.21", "size": "sm", "weight": "semibold" }
          ]
        },
        {
          "type": "Col",
          "flex": 1,
          "children": [
            { "type": "Caption", "value": "EPS (TTM)", "size": "xs" },  // ⭐ NEW
            { "type": "Text", "value": "6.59", "size": "sm", "weight": "semibold" }
          ]
        }
      ]
    },
    // Row 3: Day High | Year High | P/E Ratio
    {
      "type": "Row",
      "align": "stretch",
      "children": [
        {
          "type": "Col",
          "flex": 1,
          "children": [
            { "type": "Caption", "value": "Day High", "size": "xs" },
            { "type": "Text", "value": "275.93", "size": "sm", "weight": "semibold" }
          ]
        },
        {
          "type": "Col",
          "flex": 1,
          "children": [
            { "type": "Caption", "value": "Year High", "size": "xs" },  // ⭐ NEW
            { "type": "Text", "value": "277.32", "size": "sm", "weight": "semibold" }
          ]
        },
        {
          "type": "Col",
          "flex": 1,
          "children": [
            { "type": "Caption", "value": "P/E Ratio (TTM)", "size": "xs" },  // ⭐ NEW
            { "type": "Text", "value": "30.28", "size": "sm", "weight": "semibold" }
          ]
        }
      ]
    }
  ]
}
```

---

## Schema Changes Required

### Before (Current Schema):
```json
{
  "company": "Apple Inc.",
  "symbol": "AAPL",
  "timestamp": "Nov 16, 2025 • 10:15 AM ET",
  "price": {
    "current": "189.32",
    "changeLabel": "+1.45 (+0.77%)",
    "changeColor": "success"
  },
  "timeframes": ["1D", "1W", "1M", "3M", "1Y"],
  "selectedTimeframe": "1D",
  "chartImage": "https://upload.wikimedia.org/wikipedia/commons/7/75/Candlesticks.png"
  // ... rest of schema
}
```

### After (Updated Schema):
```json
{
  "company": "Apple Inc.",
  "symbol": "AAPL",
  "timestamp": "Nov 16, 2025 • 10:15 AM ET",
  "price": {
    "current": "189.32",
    "changeLabel": "+1.45 (+0.77%)",
    "changeColor": "success",
    // ⭐ NEW: After-hours data
    "afterHours": {
      "price": "272.82",
      "changeLabel": "+0.41 (+0.15%)",
      "changeColor": "success"
    }
  },
  // ⭐ NEW: Expanded timeframes
  "timeframes": ["1D", "5D", "1M", "3M", "6M", "YTD", "1Y", "5Y", "max"],
  "selectedTimeframe": "1D",
  "chartImage": "https://upload.wikimedia.org/wikipedia/commons/7/75/Candlesticks.png",
  // ⭐ NEW: Extended stats
  "stats": {
    "open": "271.06",
    "volume": "47.4M",
    "dayLow": "269.60",
    "dayHigh": "275.93",
    "yearLow": "169.21",      // NEW
    "yearHigh": "277.32",     // NEW
    "marketCap": "3.01T",     // NEW
    "eps": "6.59",            // NEW
    "peRatio": "30.28"        // NEW
  }
  // ... rest of schema
}
```

---

## Summary of Changes

### Priority 1 (Critical):
1. ✅ **After-Hours Price** - Added 3-item row with caption, price, and badge
2. ✅ **Extended Stats** - Redesigned to 3x3 table (9 stats total)
   - Added: Market Cap (TTM), Year Low, Year High, EPS (TTM), P/E Ratio (TTM)

### Priority 2 (Enhanced):
3. ✅ **Additional Timeframes** - Expanded from 5 to 8 buttons
   - Added: 5D, 6M, YTD, 5Y, max

### Visual Changes:
- After-hours row uses smaller text (Caption + Text size="sm") to differentiate from main price
- Stats section now uses 3-column grid layout for better information density
- Maintained all existing sections (Pattern Detection, News, Events)

---

## Next Steps:

1. Click "Schema" tab in ChatKit Studio
2. Update schema JSON with new fields
3. Click back to editor view
4. Insert new code sections in appropriate locations
5. Test preview to verify layout
6. Download updated widget

---

## Testing Checklist:

- [ ] After-hours price displays correctly
- [ ] 8 timeframe buttons fit in one row
- [ ] 3-column stats table aligns properly
- [ ] Mobile responsive layout works
- [ ] All existing sections (patterns, news, events) still render
- [ ] Schema validation passes
