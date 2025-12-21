# Trendline Selection & Config Feature - Implementation Status

## ✅ Completed Components

### 1. TrendlineConfigPopup Component
**File**: `frontend/src/components/TrendlineConfigPopup.tsx`

**Features**:
- Golden-themed popup UI matching trendline selection highlight
- Delete trendline button
- Extend Left button
- Extend Right button
- Auto-positioning with viewport bounds checking
- Click-outside-to-close behavior
- Informational text about line extension behavior

### 2. TrendlineConfigPopup Styles
**File**: `frontend/src/components/TrendlineConfigPopup.css`

**Features**:
- Golden border and highlights (#FFD700)
- Dark semi-transparent background with blur
- Smooth animations
- Hover effects on all buttons
- Red delete button styling
- Responsive button layout

### 3. TrendlineHandlePrimitive Selection Support
**File**: `frontend/src/drawings/TrendlineHandlePrimitive.ts`

**Already Existing Features** ✅:
- `selected` property in trendline data structure
- Visual highlighting when selected (golden color #FFD700, thicker line)
- Hit testing for line clicks (`hitTest` method lines 109-186)
- Hover state for handles and line

### 4. Type Definitions
**File**: `frontend/src/drawings/types.ts`

**Already Existing** ✅:
- `selected?: boolean` field in BaseDrawing interface
- `name?: string` field for trendline labels

### 5. TradingChart Integration - Partial
**File**: `frontend/src/components/TradingChart.tsx`

**Completed**:
- ✅ Import TrendlineConfigPopup component (line 29)
- ✅ `selectedTrendlineId` state exists (line 104)
- ✅ `popupPosition` state added (line 105)
- ✅ `deleteSelectedTrendline()` function exists (line 272)
- ✅ Click handler exists (line 764)

## ⏳ Remaining Implementation Tasks

### Task 1: Add Extension Functions
**Location**: After `deleteSelectedTrendline()` function (~line 293)

**Code to add**:
```typescript
const extendTrendlineLeft = () => {
  if (!selectedTrendlineId) return

  const trendlineVisual = trendlinesRef.current.get(selectedTrendlineId)
  if (!trendlineVisual || !chartRef.current) return

  const trendline = trendlineVisual.primitive.getTrendline()

  // Calculate slope
  const deltaTime = (trendline.b.time as number) - (trendline.a.time as number)
  const deltaPrice = trendline.b.price - trendline.a.price
  const slope = deltaPrice / deltaTime

  // Extend by 20% of current length
  const extendTime = deltaTime * 0.2
  const extendPrice = extendTime * slope

  const newA = {
    time: (trendline.a.time as number) - extendTime,
    price: trendline.a.price - extendPrice
  }

  trendlineVisual.primitive.updateTrendline({
    a: newA
  })

  console.log('Extended trendline left:', selectedTrendlineId)
}

const extendTrendlineRight = () => {
  if (!selectedTrendlineId) return

  const trendlineVisual = trendlinesRef.current.get(selectedTrendlineId)
  if (!trendlineVisual || !chartRef.current) return

  const trendline = trendlineVisual.primitive.getTrendline()

  // Calculate slope
  const deltaTime = (trendline.b.time as number) - (trendline.a.time as number)
  const deltaPrice = trendline.b.price - trendline.a.price
  const slope = deltaPrice / deltaTime

  // Extend by 20% of current length
  const extendTime = deltaTime * 0.2
  const extendPrice = extendTime * slope

  const newB = {
    time: (trendline.b.time as number) + extendTime,
    price: trendline.b.price + extendPrice
  }

  trendlineVisual.primitive.updateTrendline({
    b: newB
  })

  console.log('Extended trendline right:', selectedTrendlineId)
}

const updateTrendlineSelection = (id: string, isSelected: boolean) => {
  const trendlineVisual = trendlinesRef.current.get(id)
  if (!trendlineVisual) return

  const primitive = trendlineVisual.primitive
  const currentData = primitive.getTrendline()

  primitive.updateTrendline({
    ...currentData,
    selected: isSelected
  })
}
```

### Task 2: Add Popup Position Tracking Effect
**Location**: After the lazy loading effect (~line 750)

**Code to add**:
```typescript
// Track selected trendline and calculate popup position
useEffect(() => {
  if (!selectedTrendlineId || !chartRef.current || !candlestickSeriesRef.current) {
    setPopupPosition(null)
    return
  }

  const trendlineVisual = trendlinesRef.current.get(selectedTrendlineId)
  if (!trendlineVisual) return

  const trendline = trendlineVisual.primitive.getTrendline()

  // Position popup near the midpoint of the trendline
  const midTime = ((trendline.a.time as number) + (trendline.b.time as number)) / 2
  const midPrice = (trendline.a.price + trendline.b.price) / 2

  const x = chartRef.current.timeScale().timeToCoordinate(midTime as Time)
  const y = candlestickSeriesRef.current.priceToCoordinate(midPrice)

  if (x !== null && y !== null) {
    // Offset popup slightly from the line
    setPopupPosition({ x: x + 20, y: y - 60 })
  }
}, [selectedTrendlineId])
```

### Task 3: Add Selection Logic to Click Handler
**Location**: Inside `chart.subscribeClick` handler (~line 850)

**Code to add** (after the handle drag detection logic):
```typescript
// After checking handles for dragging, check if clicking on trendline line for selection
if (!editStateRef.current.isDragging) {
  for (const [id, trendlineVisual] of trendlinesRef.current.entries()) {
    const primitive = trendlineVisual.primitive
    const hitResult = primitive.hitTest(param.point.x, param.point.y)

    if (hitResult && hitResult.externalId.includes('-line')) {
      // Clicked on line (not handle) - select it
      if (selectedTrendlineId !== id) {
        // Deselect previous
        if (selectedTrendlineId) {
          updateTrendlineSelection(selectedTrendlineId, false)
        }
        // Select new
        setSelectedTrendlineId(id)
        updateTrendlineSelection(id, true)
        console.log('Selected trendline:', id)
      }
      return
    }
  }

  // If clicked on empty space, deselect
  if (selectedTrendlineId) {
    updateTrendlineSelection(selectedTrendlineId, false)
    setSelectedTrendlineId(null)
  }
}
```

### Task 4: Add Popup Component to JSX
**Location**: At the end of the return statement

**Code to add** (before the closing div of the chart container):
```tsx
{selectedTrendlineId && popupPosition && (
  <TrendlineConfigPopup
    trendline={trendlinesRef.current.get(selectedTrendlineId)?.primitive.getTrendline() || {} as any}
    position={popupPosition}
    onDelete={() => {
      deleteSelectedTrendline()
      setPopupPosition(null)
    }}
    onExtendLeft={extendTrendlineLeft}
    onExtendRight={extendlineRight}
    onClose={() => {
      if (selectedTrendlineId) {
        updateTrendlineSelection(selectedTrendlineId, false)
      }
      setSelectedTrendlineId(null)
      setPopupPosition(null)
    }}
  />
)}
```

## Testing Needed After Implementation

1. **Selection**:
   - [ ] Click on trendline line highlights it in gold
   - [ ] Click on handles triggers drag (not selection)
   - [ ] Click on empty space deselects
   - [ ] Only one trendline can be selected at a time

2. **Popup**:
   - [ ] Popup appears near selected trendline
   - [ ] Popup stays within viewport bounds
   - [ ] Click outside popup closes it
   - [ ] Popup shows correct trendline name/label

3. **Delete**:
   - [ ] Delete button removes trendline from chart
   - [ ] Popup closes after deletion
   - [ ] Selection state cleared

4. **Extension**:
   - [ ] Extend Left adds ~20% to left side
   - [ ] Extend Right adds ~20% to right side
   - [ ] Extensions maintain slope correctly
   - [ ] Extensions work even beyond data range
   - [ ] Lines extend into whitespace grid area

5. **Cross-Timeframe**:
   - [ ] Works on all timeframes (1m, 5m, 15m, 30m, 1H, 2H, 4H, 1Y, 2Y, 3Y, YTD, MAX)
   - [ ] Auto-trendlines from backend can be selected
   - [ ] User-drawn trendlines can be selected

## Files Summary

### Created Files ✅
1. `/frontend/src/components/TrendlineConfigPopup.tsx` (116 lines)
2. `/frontend/src/components/TrendlineConfigPopup.css` (127 lines)
3. `/TRENDLINE_SELECTION_IMPLEMENTATION.md` (implementation plan)
4. `/TRENDLINE_FEATURE_STATUS.md` (this file)

### Modified Files ✅
1. `/frontend/src/components/TradingChart.tsx`:
   - Added TrendlineConfigPopup import
   - Added popupPosition state

### Files Needing Modification ⏳
1. `/frontend/src/components/TradingChart.tsx`:
   - Add extension functions
   - Add popup position effect
   - Add selection logic to click handler
   - Add popup component to JSX

### Files Ready (No Changes Needed) ✅
1. `/frontend/src/drawings/TrendlineHandlePrimitive.ts` - Already supports selection
2. `/frontend/src/drawings/types.ts` - Already has selected field
3. `/backend/trendline_builder.py` - Fixed extension issue (no future dates)

## Next Steps

1. Add the 4 remaining code sections to `TradingChart.tsx`
2. Test selection on user-drawn trendlines
3. Test selection on auto-trendlines from backend
4. Test extension functionality
5. Test on all 12 timeframes
6. Verify popup positioning on different screen sizes

## Key Design Decisions

1. **Extension Amount**: 20% of current line length (configurable)
2. **Popup Position**: Midpoint of trendline + offset
3. **Selection Color**: Golden (#FFD700) to match handle highlights
4. **Delete Confirmation**: No confirmation dialog (can undo by closing and not saving)
5. **Extension Direction**: Maintains slope, extends in same direction as line
