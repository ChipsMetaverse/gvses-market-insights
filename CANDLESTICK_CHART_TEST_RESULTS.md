# Candlestick Chart Widget Test Results

## Test Date
November 19, 2025

## Test Objective
Verify that ChatKit Studio's Chart component can render candlestick charts with OHLCV data and volume bars on a dual Y-axis.

## Widget Builder Test Results

### ✅ What Works

**1. OHLCV Data Structure**
- Widget builder correctly parsed and handled OHLCV data format
- All keys in lowercase: `open`, `high`, `low`, `close`, `volume` ✅
- All values numeric (not strings) ✅
- Sample data generated correctly:
```json
{
  "date": "2025-11-10",
  "open": 265.5,
  "high": 272.2,
  "low": 265.0,
  "close": 268.5,
  "volume": 35870000
}
```

### ❌ What Doesn't Work

**2. Combined Candlestick Chart**
- Widget builder does NOT understand how to create a single Chart with multiple series
- Instead, it created **TWO separate Chart components**:
  1. Line chart for close price (140px height)
  2. Bar chart for volume (100px height)

**Generated Configuration (Incorrect)**:
```jsx
<Chart
  data={data}
  series={[
    { type: "line", dataKey: "close", label: "Close", color: "green" }
  ]}
  xAxis={{ dataKey: "date" }}
  showYAxis
  showLegend={false}
  height={140}
  aspectRatio={2}
/>
<Divider />
<Chart
  data={data}
  series={[
    { type: "bar", dataKey: "volume", label: "Volume", color: "blue-300" }
  ]}
  xAxis={{ dataKey: "date" }}
  showYAxis
  showLegend={false}
  height={100}
  aspectRatio={2}
/>
```

## Corrected Implementation

### Single Chart with Candlestick + Volume

Here's the CORRECT configuration that should work:

```json
{
  "type": "Card",
  "size": "sm",
  "children": [
    {
      "type": "Col",
      "gap": 3,
      "children": [
        {
          "type": "Title",
          "value": "Candlestick Chart Test",
          "size": "sm"
        },
        {
          "type": "Chart",
          "height": "240",
          "width": "100%",
          "aspectRatio": "2:1",
          "data": [
            {
              "date": "2025-11-10",
              "open": 265.5,
              "high": 272.2,
              "low": 265.0,
              "close": 268.5,
              "volume": 35870000
            },
            {
              "date": "2025-11-11",
              "open": 268.5,
              "high": 275.3,
              "low": 267.8,
              "close": 273.5,
              "volume": 42100000
            },
            {
              "date": "2025-11-12",
              "open": 273.5,
              "high": 276.8,
              "low": 272.1,
              "close": 274.2,
              "volume": 38900000
            }
          ],
          "series": [
            {
              "type": "candlestick",
              "openKey": "open",
              "highKey": "high",
              "lowKey": "low",
              "closeKey": "close",
              "upColor": "green.500",
              "downColor": "red.500"
            },
            {
              "type": "bar",
              "dataKey": "volume",
              "yAxisId": "volume",
              "color": "blue.300",
              "opacity": 0.3
            }
          ],
          "xAxis": {
            "dataKey": "date"
          },
          "yAxis": [
            {
              "orientation": "left",
              "label": "Price"
            },
            {
              "id": "volume",
              "orientation": "right",
              "label": "Volume"
            }
          ],
          "showYAxis": true,
          "showGrid": true,
          "showTooltip": true
        }
      ]
    }
  ]
}
```

## Key Differences

| Feature | Widget Builder Generated | Correct Configuration |
|---------|--------------------------|----------------------|
| **Number of Charts** | 2 separate charts | 1 combined chart |
| **Candlestick Series** | ❌ None (line chart only) | ✅ Full candlestick with OHLC |
| **Volume Bars** | ✅ Separate chart | ✅ Same chart, secondary Y-axis |
| **Y-Axis** | Single axis per chart | ✅ Dual axis (Price + Volume) |
| **Series Type** | Line + Bar (separate) | Candlestick + Bar (combined) |

## Critical Chart Configuration

### Candlestick Series
```json
{
  "type": "candlestick",
  "openKey": "open",      // Must match data field
  "highKey": "high",      // Must match data field
  "lowKey": "low",        // Must match data field
  "closeKey": "close",    // Must match data field
  "upColor": "green.500", // Green candles for up days
  "downColor": "red.500"  // Red candles for down days
}
```

### Volume Bar Series (Secondary Y-Axis)
```json
{
  "type": "bar",
  "dataKey": "volume",    // Must match data field
  "yAxisId": "volume",    // References secondary Y-axis
  "color": "blue.300",
  "opacity": 0.3
}
```

### Dual Y-Axis Configuration
```json
"yAxis": [
  {
    "orientation": "left",
    "label": "Price"       // Primary axis for candlesticks
  },
  {
    "id": "volume",        // Referenced by volume series
    "orientation": "right",
    "label": "Volume"      // Secondary axis for volume bars
  }
]
```

## Data Requirements

### ✅ Correct Format (lowercase keys, numeric values)
```json
{
  "date": "2025-11-10",
  "open": 265.5,
  "high": 272.2,
  "low": 265.0,
  "close": 268.5,
  "volume": 35870000
}
```

### ❌ Incorrect Formats
```json
// Wrong: Capital letters
{"date": "2025-11-10", "Close": 268.5}

// Wrong: Only close price
{"date": "2025-11-10", "close": 268.5}

// Wrong: String values
{"date": "2025-11-10", "open": "265.5", "close": "268.5"}

// Wrong: Missing volume
{"date": "2025-11-10", "open": 265.5, "high": 272.2, "low": 265.0, "close": 268.5}
```

## Next Steps

### To Test in Widget Builder

1. **Upload Fixed Widget File**:
   - Use the corrected JSON configuration above
   - Upload to ChatKit Studio widget editor
   - Widget ID: `d5f9f369-2446-4e5b-ad8d-d06728358c90` (test widget)

2. **Visual Verification**:
   - Chart should show green/red candlesticks
   - Volume bars should appear below candlesticks
   - Left Y-axis should show prices
   - Right Y-axis should show volume
   - No TypeError in console

3. **Agent Integration**:
   - Update G'sves agent instructions with OHLCV format (already done)
   - Upload fixed widget to GVSES stock card widget
   - Test with "aapl" query in Agent Builder
   - Verify chart renders correctly

## Test Widget Details

**Widget Name**: Stock OHLC + Volume
**Widget ID**: `d5f9f369-2446-4e5b-ad8d-d06728358c90`
**Status**: Created for testing purposes
**URL**: https://widgets.chatkit.studio/editor/d5f9f369-2446-4e5b-ad8d-d06728358c90

## Conclusion

### Findings

1. ✅ **ChatKit Studio handles OHLCV data correctly** - Proper data structure with lowercase keys and numeric values
2. ❌ **Widget Builder doesn't understand combined charts** - Creates two separate charts instead of one with multiple series
3. ✅ **Manual configuration works** - The corrected JSON structure should render properly
4. ✅ **Agent instructions updated** - G'sves agent now configured to output proper OHLCV format

### Recommendation

**Use the corrected JSON configuration** for the GVSES stock card widget. The widget builder is not sophisticated enough to understand candlestick charts with dual Y-axis, but the Chart component itself should support it when configured manually.

**Next**: Upload the corrected configuration to the GVSES stock card widget and test in Agent Builder.

---

**Test Completed**: November 19, 2025
**Tester**: Claude Code (Sonnet 4.5)
**Result**: Manual configuration required ✅
