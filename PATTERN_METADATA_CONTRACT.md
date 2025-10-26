# Pattern Metadata Contract

**Document Version**: 1.0  
**Last Updated**: 2025-10-26  
**Status**: ✅ Implemented & Tested

## Overview

This document defines the contract between the **backend pattern detection system** and the **frontend chart visualization system** for displaying detected chart patterns with interactive overlays.

## Architecture

```
PatternDetector.detect_all_patterns()
    ↓ (returns patterns with metadata)
MarketServiceWrapper._build_chart_metadata_from_pattern()
    ↓ (converts metadata → chart_metadata)
Frontend: drawPatternOverlay()
    ↓ (renders overlays on chart)
enhancedChartControl.drawTrendline() / drawHorizontalLine()
```

## Pattern Metadata Structure

### 1. Candlestick Patterns

**Applies to**: `bullish_engulfing`, `bearish_engulfing`, `doji`, `hammer`, `shooting_star`, `morning_star`, `evening_star`, `three_white_soldiers`, `three_black_crows`, `piercing_line`

**Metadata Fields**:
```typescript
{
  candle?: {
    open: number,
    close: number,
    low: number,
    high: number
  },
  candles?: Array<{
    open: number,
    close: number,
    low: number,
    high: number
  }>,
  horizontal_level: number,  // Stop loss or key level
  prev_candle?: {...},  // For two-candle patterns
  curr_candle?: {...}   // For two-candle patterns
}
```

**Example** (Bullish Engulfing):
```json
{
  "metadata": {
    "prev_candle": {"open": 298.83, "close": 295.14, "low": 291.14, "high": 305.5},
    "curr_candle": {"open": 285.96, "close": 308.58, "low": 281.85, "high": 309.83},
    "horizontal_level": 291.14
  }
}
```

### 2. Structural Patterns (Triangles, Wedges, Channels)

**Applies to**: `ascending_triangle`, `descending_triangle`, `symmetrical_triangle`, `rising_wedge`, `falling_wedge`, `bullish_flag`, `bearish_flag`, `channel`

**Metadata Fields**:
```typescript
{
  upper_trendline?: {
    start_candle: number,
    end_candle: number,
    start_price: number,
    end_price: number
  },
  lower_trendline?: {
    start_candle: number,
    end_candle: number,
    start_price: number,
    end_price: number
  },
  channel_bounds?: {
    upper: number,
    lower: number
  }
}
```

**Example** (Symmetrical Triangle):
```json
{
  "metadata": {
    "upper_trendline": {
      "start_candle": 10,
      "end_candle": 20,
      "start_price": 320.0,
      "end_price": 315.0
    },
    "lower_trendline": {
      "start_candle": 10,
      "end_candle": 20,
      "start_price": 300.0,
      "end_price": 305.0
    }
  }
}
```

### 3. Gap Patterns

**Applies to**: `breakaway_gap`, `exhaustion_gap`, `runaway_gap`

**Metadata Fields**:
```typescript
{
  gap_size: number,
  gap_pct: number,
  prev_candle: {...},
  curr_candle: {...},
  horizontal_level: number  // Previous close (gap level)
}
```

### 4. Head & Shoulders / Double Tops/Bottoms

**Applies to**: `head_and_shoulders`, `inverse_head_shoulders`, `double_top`, `double_bottom`

**Metadata Fields**:
```typescript
{
  neckline?: number,  // Horizontal neckline price
  peaks?: Array<{
    candle: number,
    price: number
  }>,
  troughs?: Array<{
    candle: number,
    price: number
  }>
}
```

## Chart Metadata Generation

The `_build_chart_metadata_from_pattern()` method in `market_service_factory.py` converts pattern `metadata` into frontend-friendly `chart_metadata`:

### Output Schema

```typescript
interface ChartMetadata {
  trendlines?: Array<{
    type: "upper_trendline" | "lower_trendline",
    start: {
      time: number,  // Unix timestamp
      price: number
    },
    end: {
      time: number,
      price: number
    }
  }>,
  levels?: Array<{
    type: "support" | "resistance" | "neckline",
    price: number
  }>
}
```

### Conversion Logic

1. **Trendlines**: If `metadata` contains `upper_trendline` or `lower_trendline`, map the `start_candle`/`end_candle` indices to actual timestamps from the `candles` array.

2. **Levels**: If `metadata` contains `horizontal_level`, create a level with appropriate `type` (support for bullish, resistance for bearish).

3. **Empty Metadata**: Returns `None` if metadata is empty or `None`.

## Frontend Visualization

### Pattern Display (`TradingDashboardSimple.tsx`)

```typescript
// State
const [visiblePatterns, setVisiblePatterns] = useState<Set<string>>(new Set());
const [hoveredPattern, setHoveredPattern] = useState<string | null>(null);

// Drawing Function
const drawPatternOverlay = useCallback((pattern: any) => {
  if (!pattern.chart_metadata) {
    console.log('[Pattern] No chart_metadata');
    return;
  }
  
  const { trendlines, levels } = pattern.chart_metadata;
  
  // Draw trendlines
  trendlines?.forEach((trendline: any) => {
    const color = trendline.type === 'upper_trendline' ? '#ef4444' : '#3b82f6';
    enhancedChartControl.drawTrendline(
      trendline.start.time,
      trendline.start.price,
      trendline.end.time,
      trendline.end.price,
      color
    );
  });
  
  // Draw support/resistance levels
  levels?.forEach((level: any) => {
    const color = level.type === 'support' ? '#10b981' : '#ef4444';
    enhancedChartControl.drawHorizontalLine(level.price, color, level.type);
  });
}, []);
```

### Chart Control (`enhancedChartControl.ts`)

```typescript
// Draw trendline between two points
drawTrendline(startTime: number, startPrice: number, endTime: number, endPrice: number, color: string): string {
  const lineSeries = this.chartRef.addLineSeries({
    color: color,
    lineWidth: 2,
    lineStyle: 0, // Solid
  });
  
  lineSeries.setData([
    { time: startTime, value: startPrice },
    { time: endTime, value: endPrice }
  ]);
  
  this.annotationsMap.set(`trendline_${Date.now()}`, lineSeries);
  return 'Trendline drawn';
}

// Draw horizontal level
drawHorizontalLine(price: number, color: string, label?: string): string {
  const priceLine = this.seriesRef.createPriceLine({
    price: price,
    color: color,
    lineWidth: 2,
    lineStyle: 2, // Dashed
    title: label || `Level ${price.toFixed(2)}`,
  });
  
  this.drawingsMap.set(`horizontal_${Date.now()}`, priceLine);
  return 'Horizontal line drawn';
}
```

## Testing

### Regression Tests

**File**: `backend/tests/test_pattern_metadata.py`

**Test Coverage**:
- ✅ All patterns have `metadata` field
- ✅ Candlestick patterns have `horizontal_level`
- ✅ Structural patterns have trendline or channel data
- ✅ `chart_metadata` is generated from `metadata`
- ✅ `chart_metadata` follows the schema contract
- ✅ End-to-end serialization works correctly

**Run Tests**:
```bash
cd backend
python3 -m pytest tests/test_pattern_metadata.py -v
```

## Pattern Coverage

### ✅ Implemented (Chart Visualization Ready)

**Candlestick Patterns** (9):
- `bullish_engulfing`, `bearish_engulfing`
- `doji`
- `hammer`, `shooting_star`
- `morning_star`, `evening_star`
- `three_white_soldiers`, `three_black_crows`
- `piercing_line`

**Structural Patterns** (9):
- `ascending_triangle`, `descending_triangle`, `symmetrical_triangle`
- `rising_wedge`, `falling_wedge`
- `bullish_flag`, `bearish_flag`
- `channel`
- `double_top`, `double_bottom`

**Head & Shoulders** (2):
- `head_and_shoulders`, `inverse_head_shoulders`

**Gap Patterns** (3):
- `breakaway_gap`, `runaway_gap`, `exhaustion_gap`

**Cup & Handle**:
- `cup_and_handle`

**Trend Acceleration**:
- `trend_acceleration_bullish`, `trend_acceleration_bearish`

### 📝 Low Priority (Minimal/No Metadata)

These patterns are detected but do not yet have rich metadata for visualization. They can be enhanced in future iterations:

- `spinning_top`, `marubozu`, `hanging_man`, `inverted_hammer`
- `three_outside_up`, `three_outside_down`, `three_inside_up`, `three_inside_down`
- `abandoned_baby_bullish`, `abandoned_baby_bearish`
- `pennant`, `rectangle`, `broadening`, `diamond`, `rounding_bottom`

## API Response Example

```json
{
  "symbol": "TSLA",
  "patterns": {
    "detected": [
      {
        "pattern_id": "bullish_engulfing_3_1749475800",
        "pattern_type": "bullish_engulfing",
        "confidence": 95.0,
        "signal": "bullish",
        "description": "Bullish Engulfing - Strong reversal signal",
        "start_candle": 2,
        "end_candle": 3,
        "start_time": 1746019800,
        "end_time": 1746106200,
        "metadata": {
          "prev_candle": {"open": 298.83, "close": 295.14, "low": 291.14, "high": 305.5},
          "curr_candle": {"open": 285.96, "close": 308.58, "low": 281.85, "high": 309.83},
          "horizontal_level": 291.14
        },
        "chart_metadata": {
          "levels": [
            {
              "type": "resistance",
              "price": 291.14
            }
          ]
        },
        "entry_guidance": "Enter on the close of the engulfing bar...",
        "stop_loss_guidance": "Place below the engulfing candle's low...",
        "risk_notes": "Lower reliability when the engulfing candle emerges at resistance..."
      }
    ]
  }
}
```

## Future Enhancements

### Phase 2: Additional Patterns
- Add metadata to low-priority patterns (spinning tops, etc.)
- Implement volume profile overlays
- Add Fibonacci retracement levels to patterns

### Phase 3: Interactive Features
- Pattern editing (adjust trendlines)
- Pattern alerts/notifications
- Historical pattern performance tracking

## Version History

### v1.0 (2025-10-26)
- Initial contract definition
- Implemented metadata for 24+ patterns
- Added comprehensive regression tests
- Documented frontend integration

