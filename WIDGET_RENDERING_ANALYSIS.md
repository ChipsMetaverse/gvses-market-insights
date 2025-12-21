# Widget Rendering Analysis

## Current State: ❌ Raw JSON Display

### What We're Seeing:
- Agent outputs complete JSON object
- Displayed as plain text in chat
- No visual widget card rendering
- Same behavior in Agent Builder Preview mode

### Expected Behavior:
- Beautiful stock card with:
  - Company name & price
  - Interactive TradingView chart
  - Stats grid (Volume, Market Cap, etc.)
  - Technical indicators
  - News feed
  - Events timeline

---

## Root Causes Analysis

### Possibility 1: Agent Builder Preview Limitations
**Hypothesis:** Preview mode doesn't render widgets, only production does

**Evidence:**
- Preview mode is for testing workflow logic
- Widget rendering might only work in deployed ChatKit environment
- No widget metadata visible in Agent output

**Test:** Publish workflow and test in production ChatKit environment

---

### Possibility 2: Missing Widget Configuration
**Hypothesis:** Widget not properly linked to Agent Builder output

**Required Components:**
1. Widget defined in ChatKit Studio (✅ EXISTS: `wig_5cjvy39s`)
2. Widget schema matches agent output format (❓ UNKNOWN)
3. Agent response includes widget metadata (❌ MISSING)

**What's Missing:**
```json
{
  "widget": {
    "type": "gvses-stock-card",
    "id": "wig_5cjvy39s"
  },
  "data": { /* ... stock data ... */ }
}
```

---

### Possibility 3: Output Format Mismatch
**Hypothesis:** Agent output structure doesn't match widget schema

**Current Agent Output:**
```json
{
  "company": "Apple, Inc.",
  "symbol": "AAPL",
  "chartData": [ /* 82 entries */ ],
  ...
}
```

**Widget Might Expect:**
```json
{
  "type": "widget",
  "widget_id": "wig_5cjvy39s",
  "props": {
    "company": "Apple, Inc.",
    ...
  }
}
```

---

## Solutions (Priority Order)

### Solution 1: Modify Agent Instructions ⭐ RECOMMENDED
**Add to G'sves Agent System Prompt:**
```
IMPORTANT: When responding with stock data, you MUST:
1. Return JSON wrapped in widget metadata:
{
  "widget": {"id": "wig_5cjvy39s", "type": "stock-card"},
  "data": { /* your stock data here */ }
}

2. Ensure chartData contains MAXIMUM 50 entries
3. Use only the MOST RECENT data points
```

**Pros:**
- ✅ Fixes both truncation AND widget rendering
- ✅ Single change, two problems solved
- ✅ No code changes required

**Cons:**
- ❌ Requires re-testing agent
- ❌ Depends on agent following instructions

---

### Solution 2: Add Transform Node for Widget Wrapping
**Create new Transform node:**
```javascript
// Input: stock_data from G'sves
// Output: widget-wrapped data

{
  "widget": {
    "id": "wig_5cjvy39s",
    "type": "stock-card"
  },
  "data": input.stock_data
}
```

**Pros:**
- ✅ Guaranteed widget metadata
- ✅ Separates concerns (data vs presentation)

**Cons:**
- ❌ Doesn't solve chartData truncation
- ❌ Still need separate truncation solution

---

### Solution 3: Frontend Truncation (Defensive Programming)
**Modify Widget Parser:**
```typescript
// In widget parser/renderer
function parseStockData(data: any) {
  return {
    ...data,
    chartData: data.chartData.slice(-50) // Last 50 points only
  };
}
```

**Pros:**
- ✅ Bulletproof - works regardless of agent behavior
- ✅ Fast to implement
- ✅ Defensive programming best practice

**Cons:**
- ❌ Wastes bandwidth with excess data
- ❌ Doesn't fix root cause

---

### Solution 4: Publish & Test in Production
**Hypothesis Test:** Widget rendering only works in production

**Steps:**
1. Publish Agent Builder workflow (version 22)
2. Test in production ChatKit environment
3. Check if widget renders correctly

**If YES:**
- Preview mode limitations confirmed
- Widget rendering is working
- Only need to fix chartData truncation

**If NO:**
- Widget configuration issue
- Need Solution 1 or 2

---

## Immediate Action Plan

### Step 1: Publish Workflow & Test Production
```bash
# In Agent Builder:
1. Click "Publish" button
2. Navigate to production ChatKit URL
3. Test with "show me AAPL"
4. Check if widget renders
```

### Step 2: If Widget Still Doesn't Render
Modify G'sves agent system prompt to add:
```
OUTPUT FORMAT:
You must wrap your response in widget metadata:
{
  "widget_id": "wig_5cjvy39s",
  "widget_type": "stock-card",
  "data": { /* your stock data */ }
}

CRITICAL: chartData array MUST contain maximum 50 entries.
Use only the most recent data points.
```

### Step 3: Frontend Defensive Truncation
Add to widget parser:
```typescript
if (data.chartData?.length > 50) {
  data.chartData = data.chartData.slice(-50);
  console.warn(`Truncated chartData from ${data.chartData.length} to 50 points`);
}
```

---

## ChartData Truncation Solutions

### Since Option 1 Failed (MCP Modification)
**Why It Failed:**
- Agent Builder uses cloud-hosted MCP server
- Our local modifications don't affect Agent Builder
- Need different approach

### Alternative Solutions:

#### Option A: Agent Instruction (SIMPLEST) ⭐
**Add to system prompt:**
```
CRITICAL RULE: chartData array MUST contain EXACTLY 50 entries or fewer.
If you receive more than 50 data points, keep only the LAST 50 (most recent).
```

#### Option B: Transform Node (COMPLEX)
- Already attempted (ChartDataTruncator)
- Has CEL array slicing errors
- Not connected to workflow
- Would need While loop workaround

#### Option C: Frontend Truncation (DEFENSIVE)
```typescript
chartData: response.chartData.slice(-50)
```

---

## Recommended Implementation Strategy

### Phase 1: Quick Win (5 minutes)
1. ✅ Add frontend truncation (defensive)
2. ✅ Test widget rendering in production
3. ✅ Document results

### Phase 2: Proper Fix (15 minutes)
1. ✅ Modify G'sves agent instructions:
   - Add widget wrapping requirement
   - Add 50-point chartData limit
   - Add recent-data-only constraint
2. ✅ Test in Agent Builder Preview
3. ✅ Publish to production
4. ✅ Validate widget renders + data truncated

### Phase 3: Cleanup (5 minutes)
1. ✅ Delete unused ChartDataTruncator node
2. ✅ Update documentation
3. ✅ Mark tasks complete

---

## Success Criteria

### Widget Rendering ✅
- [ ] Visual stock card displays (not raw JSON)
- [ ] Chart renders with candlesticks
- [ ] Stats grid populated
- [ ] News feed shows articles
- [ ] Technical indicators visible

### ChartData Truncation ✅
- [ ] chartData.length ≤ 50
- [ ] Most recent data points retained
- [ ] No performance lag
- [ ] Widget renders smoothly

---

## Files Requiring Changes

1. **Agent Builder - G'sves Agent System Prompt**
   - Location: Agent Builder > G'sves node > Instructions
   - Changes: Add widget wrapping + 50-point limit

2. **Frontend Widget Parser (Optional Defensive)**
   - Location: `frontend/src/components/widget/parser.ts` (or similar)
   - Changes: Add truncation safety check

3. **Cleanup**
   - Location: Agent Builder workflow
   - Changes: Delete ChartDataTruncator Transform node
