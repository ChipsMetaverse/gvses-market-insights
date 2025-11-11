# Transform Node Configuration Guide

## Current Status

✅ Transform node added between agents and End node  
✅ Transform mode set to "Expressions"  
✅ First field "output_text" key entered  
⚠️ Need to configure field values

---

## Required Configuration

### Field 1: `output_text`

**Key**: `output_text` ✅ (already entered)  
**Value**: `input.text`  
**Purpose**: Extract the text response from either Chart Control Agent or G'sves

#### How to Configure:
1. Click on the Value paragraph (currently shows `input.foo + 1`)
2. Select all text (Cmd+A or triple-click)
3. Type: `input.text`
4. Press Enter or click outside to save

---

### Field 2: `chart_commands`

**Key**: `chart_commands`  
**Value**: `input.chart_commands`  
**Purpose**: Extract the chart commands array from Chart Control Agent

#### How to Configure:
1. Click the "Add" button (➕ Add)
2. In the new field, enter Key: `chart_commands`
3. Click on the Value area
4. Type: `input.chart_commands`
5. Press Enter or click outside to save

---

## Expected Result

After configuration, the Transform node should output:

```json
{
  "output_text": "<text from agent>",
  "chart_commands": ["LOAD:NVDA"]
}
```

This will then flow to the End node, which will use these values for its final output.

---

## Testing After Configuration

### Step 1: Preview Test
1. Click "Preview" button
2. Type: "Show me NVDA chart"
3. Wait for execution to complete

### Step 2: Verify Transform Output
Look for the Transform node's output in the execution trace:
- Should show `output_text`: "Loaded NVDA chart..."
- Should show `chart_commands`: ["LOAD:NVDA"]

### Step 3: Verify End Node Output
Look for the final workflow output:
- Should NO LONGER show "undefined"
- Should show actual text and chart commands

### Step 4: Publish
1. Click "Publish" button
2. Confirm to publish as v35

### Step 5: Test Live App
1. Navigate to: https://gvses-market-insights.fly.dev
2. Connect voice
3. Type: "Show me NVDA chart"
4. Verify chart switches from TSLA to NVDA

---

## Troubleshooting

### If Transform shows schema errors:
- Make sure the keys are exact: `output_text` and `chart_commands`
- Make sure the values reference `input.text` and `input.chart_commands`

### If End node still shows undefined:
- Verify the edge connections:
  - Chart Control Agent → Transform
  - G'sves → Transform
  - Transform → End
- Check that End node schema matches Transform output

### If chart doesn't switch in live app:
- Check browser console for `[ChatKit] Processing chart_commands` log
- Verify the chart_commands array is being passed correctly
- May need to wait for CDN cache to clear (2-5 minutes)

---

## Current Workflow Structure

```
Intent Classifier
  ↓
Transform (intent extraction)
  ↓
If/else
  ├─→ Chart Control Agent ──┐
  └─→ G'sves              ──┤
                            ↓
                      [NEW TRANSFORM] ← Configure this!
                            ↓
                          End Node
```

---

**Status**: Awaiting manual configuration  
**Next Step**: Configure Transform node values as described above  
**Estimated Time**: 2-3 minutes

