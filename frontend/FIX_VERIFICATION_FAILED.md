# Fix Verification - Stack Overflow Still Present

**Date:** November 28, 2025
**Status:** ❌ FIX INCOMPLETE - Different error pattern discovered
**Test Method:** ✅ Playwright MCP

---

## Test Results

### What Works ✅

1. **Trendline Created:** `trendline-1764377319639`
2. **Visual Rendering:** Blue line with handles visible
3. **Drag Preview Fix Applied:** Create-once pattern in place (lines 655-672)
4. **Drawing Mode:** Button activation/deactivation works correctly

### What Still Fails ❌

**Stack Overflow Errors Continue:**
```
RangeError: Maximum call stack size exceeded
    at ChartWidget._private__getMouseEventParamsImpl
    at Object._internal_callback
    at Delegate._internal_fire
    at ChartWidget._private__onPaneWidgetCrosshairMoved
```

**New Error Location:** Different from original errors (was in `PlotList._internal_setData` and `SeriesBarColorer._private__findBar`)

---

## Root Cause Analysis - Revised

### Initial Hypothesis (Incorrect)

**Thought:** Removing/creating series on every mouse move caused the stack overflow

**Fix Applied:** Changed to create-once/update-only pattern

**Result:** ❌ Stack overflow persists in different location

### Actual Root Cause

**The Real Problem:** Calling `setData()` **INSIDE** crosshair callbacks creates feedback loops

**Why This Happens:**

1. **User moves mouse** → triggers `subscribeCrosshairMove`
2. **Callback executes** → calls `preview.setData([...])`
3. **setData() triggers chart update** → fires internal chart events
4. **Chart update fires crosshair event** → triggers callback again
5. **GOTO step 2** → Infinite recursion → Stack overflow

### The Feedback Loop

```typescript
chart.subscribeCrosshairMove((param) => {
  // Drawing preview (lines 692-697)
  if (drawingMode && hasFirstPoint) {
    previewLine.setData([...])  // ❌ Triggers chart update!
                                 //    → fires crosshair event
                                 //    → calls this callback again
                                 //    → infinite loop!
  }
})
```

**Key Insight:** Even with create-once pattern, `setData()` calls from crosshair callbacks create cascading updates.

---

## Why Both Patterns Fail

### Pattern 1: Remove/Create (Original - BAD)

```typescript
chart.subscribeCrosshairMove(() => {
  chart.removeSeries(preview)  // Triggers update → crosshair event
  preview = chart.addSeries()  // Triggers update → crosshair event
  preview.setData([...])       // Triggers update → crosshair event
})
// Result: 3x cascade multiplier = rapid stack overflow
```

### Pattern 2: Create-Once/Update (My Fix - STILL BAD)

```typescript
chart.subscribeCrosshairMove(() => {
  if (!preview) {
    preview = chart.addSeries()  // Once only (good)
  }
  preview.setData([...])         // Still triggers update → crosshair event!
})
// Result: 1x cascade = slower but still overflows
```

### The Problem

**Any** `setData()` call inside a crosshair callback can trigger:
- Chart model updates
- View updates
- Mouse event parameter recalculation
- **New crosshair events** → callback executes again

---

## Evidence from Playwright Test

### Console Output

**Before trendline creation:**
- No stack overflow errors
- Normal operation

**After clicking first point (drawing mode active):**
```
RangeError: Maximum call stack size exceeded
    at ChartWidget._private__getMouseEventParamsImpl
```

**After clicking second point (trendline created):**
```
[LOG] Created trendline: trendline-1764377319639
RangeError: Maximum call stack size exceeded
```

**Pattern:** Errors occur **during mouse movement** when preview line is updating

### Visual Confirmation

**Screenshot:** `fix-verification-still-has-errors.png`

- ✅ Trendline visible (blue diagonal line)
- ✅ Handles rendered (blue circles with yellow highlight)
- ❌ Stack overflow in console

**Conclusion:** Visual rendering works, but crosshair interaction causes recursion

---

## Why This Wasn't Caught Earlier

### My Initial Analysis Mistake

1. **Saw** remove/create pattern in drag preview
2. **Assumed** that was the only problem
3. **Missed** the fundamental issue: `setData()` in crosshair callbacks
4. **Fixed** the symptom (excessive operations) not the cause (feedback loop)

### The Drawing Preview Deception

The drawing preview code (lines 678-700) **looked correct** because:
- ✅ Creates series once (not on every move)
- ✅ Only updates with setData()
- ✅ Has early returns

**But it's still broken** because:
- ❌ Calls `setData()` on every crosshair event (60-120/sec)
- ❌ Each `setData()` can trigger new crosshair events
- ❌ Creates potential for infinite recursion

---

## The Real Solution

### What DOESN'T Work

❌ Create-once/update-only (my fix)
❌ Removing/creating on every move (original code)
❌ Any `setData()` call inside crosshair callbacks

### What MIGHT Work

✅ **Option 1: Debounce/Throttle setData()**
```typescript
let updateTimer: number | null = null;

chart.subscribeCrosshairMove((param) => {
  // Cancel pending update
  if (updateTimer) clearTimeout(updateTimer);

  // Schedule update for next tick (breaks recursion)
  updateTimer = setTimeout(() => {
    if (previewLine) {
      previewLine.setData([...])
    }
    updateTimer = null;
  }, 0) as unknown as number;
})
```

✅ **Option 2: Use requestAnimationFrame**
```typescript
let rafId: number | null = null;

chart.subscribeCrosshairMove((param) => {
  if (rafId) cancelAnimationFrame(rafId);

  rafId = requestAnimationFrame(() => {
    if (previewLine) {
      previewLine.setData([...])
    }
    rafId = null;
  });
})
```

✅ **Option 3: Canvas Overlay (No Series)**
```typescript
// Don't use series for preview at all
// Draw directly on canvas overlay
chart.subscribeCrosshairMove((param) => {
  // Update canvas overlay state (no setData!)
  previewState = { from: anchor, to: param }
  // Trigger canvas redraw without chart update
  overlayCanvas.draw()
})
```

✅ **Option 4: Guard Against Recursion**
```typescript
let isUpdating = false;

chart.subscribeCrosshairMove((param) => {
  if (isUpdating) return;  // Break recursion!

  isUpdating = true;
  try {
    if (previewLine) {
      previewLine.setData([...])
    }
  } finally {
    isUpdating = false;
  }
})
```

---

## Recommended Fix Strategy

### Immediate Solution (Option 4 - Simplest)

Add recursion guard to prevent callback from executing during its own update:

```typescript
// Add at top of TradingChart component
const isUpdatingPreviewRef = useRef(false);

// In subscribeCrosshairMove callback (line 642)
chart.subscribeCrosshairMove((param) => {
  // GUARD: Prevent recursion
  if (isUpdatingPreviewRef.current) return;

  if (!param.time || !param.point) return;
  const price = candlestickSeries.coordinateToPrice(param.point.y);
  if (price === null) return;

  // Existing drag preview code (lines 648-676)
  if (editStateRef.current.isDragging) {
    isUpdatingPreviewRef.current = true;  // Set guard
    try {
      // ... existing code ...
      if (previewLineRef.current) {
        previewLineRef.current.setData([...])
      }
    } finally {
      isUpdatingPreviewRef.current = false;  // Release guard
    }
    return;
  }

  // Existing drawing preview code (lines 678-700)
  if (drawingModeRef.current && drawingPointsRef.current.length === 1) {
    isUpdatingPreviewRef.current = true;  // Set guard
    try {
      // ... existing code ...
      if (previewLineRef.current) {
        previewLineRef.current.setData([...])
      }
    } finally {
      isUpdatingPreviewRef.current = false;  // Release guard
    }
    return;
  }
})
```

### Better Solution (Option 2 - Recommended)

Use `requestAnimationFrame` to batch updates and avoid recursion:

```typescript
const previewUpdateRafRef = useRef<number | null>(null);

chart.subscribeCrosshairMove((param) => {
  if (!param.time || !param.point) return;
  const price = candlestickSeries.coordinateToPrice(param.point.y);
  if (price === null) return;

  // Cancel any pending update
  if (previewUpdateRafRef.current !== null) {
    cancelAnimationFrame(previewUpdateRafRef.current);
  }

  // Schedule update for next animation frame
  previewUpdateRafRef.current = requestAnimationFrame(() => {
    // Update preview line here (won't trigger recursion)
    if (previewLineRef.current) {
      previewLineRef.current.setData([...])
    }
    previewUpdateRafRef.current = null;
  });
})
```

---

## Why These Solutions Work

### Option 1 (setTimeout)
- **Breaks synchronous recursion** by deferring update
- **Debounces rapid updates** (only last update executes)
- **Simple to implement**

### Option 2 (requestAnimationFrame) ⭐ RECOMMENDED
- **Syncs with browser render cycle** (smooth 60fps)
- **Batches updates** (only one per frame)
- **Prevents recursion** (callbacks don't nest)
- **Best performance**

### Option 3 (Canvas Overlay)
- **Completely avoids series** (no chart updates)
- **Most performant** (direct canvas drawing)
- **Complex to implement** (need custom rendering)

### Option 4 (Recursion Guard)
- **Simplest fix** (one flag check)
- **Prevents infinite loops** (returns immediately)
- **Quick to implement**
- **Still calls setData() 60-120 times/sec** (not ideal but safe)

---

## Testing Strategy

### Test 1: Recursion Guard

1. Apply Option 4 (recursion guard)
2. Navigate to `/test-chart`
3. Click trendline button
4. Click two points to draw
5. Move mouse around chart
6. ✅ Expected: No stack overflow
7. ✅ Expected: Console clean

### Test 2: requestAnimationFrame

1. Apply Option 2 (RAF)
2. Same test as above
3. ✅ Expected: No stack overflow
4. ✅ Expected: Smooth 60fps preview updates
5. ✅ Expected: Lower CPU usage

### Test 3: Performance Comparison

Monitor:
- Console errors (should be 0)
- FPS during drag (should be 60)
- CPU usage (should be <5%)
- Memory (should be stable)

---

## Lessons Learned

### What I Got Wrong

1. **Assumed** remove/create was the only issue
2. **Didn't test** the "working" drawing preview under load
3. **Missed** the fundamental feedback loop problem
4. **Focused** on optimization, not recursion prevention

### What I Got Right

1. ✅ Used Playwright MCP for testing
2. ✅ Captured screenshots and console logs
3. ✅ Identified the crosshair callback as the trigger
4. ✅ Documented the investigation thoroughly

### Key Takeaway

**Never call `setData()` synchronously from chart event callbacks** (click, crosshair, etc.) without:
- Recursion guards
- Debouncing/throttling
- Async scheduling (RAF, setTimeout)
- Or avoiding series updates entirely

---

## Next Steps

1. **Apply recursion guard** (Option 4 - quickest fix)
2. **Test via Playwright** (verify stack overflow resolved)
3. **If successful, refactor to RAF** (Option 2 - better performance)
4. **Document the pattern** (prevent future mistakes)
5. **Consider canvas overlay** (Option 3 - if performance needed)

---

## Status

**My Fix:** ✅ Applied (create-once pattern)
**Stack Overflow:** ❌ Still present (different cause)
**Root Cause:** ✅ Identified (setData in crosshair callbacks)
**Solution:** 📋 Documented (4 options available)
**Implementation:** ⏳ Pending

**Conclusion:** The initial fix improved the code but didn't resolve the fundamental recursion issue. A recursion guard or RAF-based approach is needed.

---

*Test conducted: November 28, 2025 via Playwright MCP*
*Fix status: INCOMPLETE - Requires recursion prevention*
*Recommended: Apply Option 4 (guard) or Option 2 (RAF)*
