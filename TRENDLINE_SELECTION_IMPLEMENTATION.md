# Trendline Selection & Config Popup Implementation Plan

## Current State Analysis

### Existing Infrastructure ✅
1. **TrendlineHandlePrimitive** (frontend/src/drawings/TrendlineHandlePrimitive.ts)
   - Already has `selected` state support (line 321)
   - Visual highlighting with golden color when selected (line 326)
   - Hit testing for handles and line (lines 109-186)

2. **TradingChart State** (frontend/src/components/TradingChart.tsx)
   - `selectedTrendlineId` state already exists (line 103)
   - `deleteSelectedTrendline()` function exists (line 272)
   - Click handler exists (line 764) for drawing mode and drag detection

3. **Types** (frontend/src/drawings/types.ts)
   - `selected?: boolean` field in BaseDrawing interface (line 17)

### New Components Created ✅
1. **TrendlineConfigPopup.tsx** - Popup UI component with:
   - Delete button
   - Extend Left button
   - Extend Right button
   - Positioned near selected trendline
   - Click-outside-to-close behavior

2. **TrendlineConfigPopup.css** - Golden-themed styling matching selection highlight

## Implementation Tasks

### 1. Add Trendline Selection Logic

**File**: `frontend/src/components/TradingChart.tsx`

**Location**: Inside the `subscribeClick` handler (around line 764)

**Changes Needed**:
```typescript
// After checking handles for dragging, add selection logic
// If not clicking on a handle, check if clicking on the trendline line
for (const [id, trendline] of trendlinesRef.current.entries()) {
  const primitive = trendline.primitive;
  const hitResult = primitive.hitTest(param.point.x, param.point.y);

  if (hitResult && hitResult.externalId.includes('-line')) {
    // Clicked on line (not handle) - select it
    setSelectedTrendlineId(id);

    // Update visual to show selection
    const coords = primitive.getTrendline();
    updateTrendlineSelection(id, true);

    console.log('Selected trendline:', id);
    return;
  }
}

// If clicked on empty space, deselect
setSelectedTrendlineId(null);
```

### 2. Add Selection Update Function

**Function to add**:
```typescript
const updateTrendlineSelection = (id: string, isSelected: boolean) => {
  const trendlineVisual = trendlinesRef.current.get(id);
  if (!trendlineVisual) return;

  const primitive = trendlineVisual.primitive;
  const currentData = primitive.getTrendline();

  primitive.updateTrendline({
    ...currentData,
    selected: isSelected
  });
};
```

### 3. Add Popup State and Position Tracking

**State to add**:
```typescript
const [popupPosition, setPopupPosition] = useState<{ x: number; y: number } | null>(null);
```

**Effect to track selected trendline and calculate popup position**:
```typescript
useEffect(() => {
  if (!selectedTrendlineId || !chartRef.current || !candlestickSeriesRef.current) {
    setPopupPosition(null);
    return;
  }

  const trendlineVisual = trendlinesRef.current.get(selectedTrendlineId);
  if (!trendlineVisual) return;

  const trendline = trendlineVisual.primitive.getTrendline();

  // Position popup near the midpoint of the trendline
  const midTime = (trendline.a.time + trendline.b.time) / 2;
  const midPrice = (trendline.a.price + trendline.b.price) / 2;

  const x = chartRef.current.timeScale().timeToCoordinate(midTime);
  const y = candlestickSeriesRef.current.priceToCoordinate(midPrice);

  if (x !== null && y !== null) {
    // Offset popup slightly from the line
    setPopupPosition({ x: x + 20, y: y - 60 });
  }
}, [selectedTrendlineId]);
```

### 4. Add Extension Functions

**Extend Left Function**:
```typescript
const extendTrendlineLeft = () => {
  if (!selectedTrendlineId) return;

  const trendlineVisual = trendlinesRef.current.get(selectedTrendlineId);
  if (!trendlineVisual || !chartRef.current) return;

  const trendline = trendlineVisual.primitive.getTrendline();
  const timeScale = chartRef.current.timeScale();

  // Calculate slope
  const deltaTime = trendline.b.time - trendline.a.time;
  const deltaPrice = trendline.b.price - trendline.a.price;
  const slope = deltaPrice / deltaTime;

  // Extend by 20% of current length
  const extendTime = deltaTime * 0.2;
  const extendPrice = extendTime * slope;

  const newA = {
    time: trendline.a.time - extendTime,
    price: trendline.a.price - extendPrice
  };

  trendlineVisual.primitive.updateTrendline({
    a: newA
  });

  console.log('Extended trendline left:', selectedTrendlineId);
};
```

**Extend Right Function**:
```typescript
const extendTrendlineRight = () => {
  if (!selectedTrendlineId) return;

  const trendlineVisual = trendlinesRef.current.get(selectedTrendlineId);
  if (!trendlineVisual || !chartRef.current) return;

  const trendline = trendlineVisual.primitive.getTrendline();

  // Calculate slope
  const deltaTime = trendline.b.time - trendline.a.time;
  const deltaPrice = trendline.b.price - trendline.a.price;
  const slope = deltaPrice / deltaTime;

  // Extend by 20% of current length
  const extendTime = deltaTime * 0.2;
  const extendPrice = extendTime * slope;

  const newB = {
    time: trendline.b.time + extendTime,
    price: trendline.b.price + extendPrice
  };

  trendlineVisual.primitive.updateTrendline({
    b: newB
  });

  console.log('Extended trendline right:', selectedTrendlineId);
};
```

### 5. Add Popup Component to Render

**At the end of the JSX return statement** (after chartContainerRef div):
```tsx
{selectedTrendlineId && popupPosition && (
  <TrendlineConfigPopup
    trendline={trendlinesRef.current.get(selectedTrendlineId)?.primitive.getTrendline() || {}}
    position={popupPosition}
    onDelete={() => {
      deleteSelectedTrendline();
      setPopupPosition(null);
    }}
    onExtendLeft={extendTrendlineLeft}
    onExtendRight={extendTrendlineRight}
    onClose={() => {
      setSelectedTrendlineId(null);
      setPopupPosition(null);
    }}
  />
)}
```

### 6. Import the Popup Component

**At top of TradingChart.tsx**:
```typescript
import { TrendlineConfigPopup } from './TrendlineConfigPopup';
```

## Behavior Flow

1. **User clicks on trendline line** (not handles)
   - Hit test detects line click
   - `setSelectedTrendlineId(id)` called
   - Primitive updates to show golden highlight
   - Effect calculates popup position
   - Popup renders with controls

2. **User clicks "Extend Left"**
   - Calculates slope from existing points
   - Extends point A backward by 20% of line length
   - Updates primitive coordinates
   - Line extends into whitespace (even if no data)

3. **User clicks "Extend Right"**
   - Calculates slope from existing points
   - Extends point B forward by 20% of line length
   - Updates primitive coordinates
   - Line extends into whitespace (even if no data)

4. **User clicks "Delete"**
   - Calls existing `deleteSelectedTrendline()` function
   - Removes primitive from series
   - Clears selection state
   - Closes popup

5. **User clicks outside popup**
   - Popup closes
   - Selection cleared
   - Visual returns to normal

## Edge Cases Handled

- **No data at extended coordinates**: Extension still works because we're using time coordinates, not requiring actual OHLC data
- **Popup off-screen**: Adjustment logic keeps popup within viewport bounds
- **Multiple clicks**: Each click properly deselects previous and selects new
- **Drag vs Select**: Handle clicks trigger drag, line clicks trigger select

## Visual States

1. **Unselected**: Original trendline color (cyan, pink, etc.)
2. **Hovered**: Handles show golden highlight (existing behavior)
3. **Selected**: Entire line golden (#FFD700), thicker width, handles golden
4. **Selected + Hovered**: Handles show orange stroke (#FFA500)

## Files Modified

1. ✅ `frontend/src/components/TrendlineConfigPopup.tsx` (created)
2. ✅ `frontend/src/components/TrendlineConfigPopup.css` (created)
3. ⏳ `frontend/src/components/TradingChart.tsx` (needs modifications)

## Files Unchanged (already support selection)

1. ✅ `frontend/src/drawings/TrendlineHandlePrimitive.ts` (already has selection support)
2. ✅ `frontend/src/drawings/types.ts` (already has selected field)

## Testing Checklist

- [ ] Click on trendline line selects it (golden highlight)
- [ ] Click on handles starts drag (not selection)
- [ ] Popup appears at correct position
- [ ] Delete button removes trendline
- [ ] Extend Left adds ~20% to left side
- [ ] Extend Right adds ~20% to right side
- [ ] Extensions work even beyond data range
- [ ] Click outside popup closes it
- [ ] Multiple selections work correctly
- [ ] Works on all timeframes (1m, 5m, 15m, 30m, 1H, 2H, 4H, 1Y, 2Y, 3Y, YTD, MAX)
