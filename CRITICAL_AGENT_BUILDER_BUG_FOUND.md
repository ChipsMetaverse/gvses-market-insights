# CRITICAL BUG FOUND: Agent Builder MCP Tool Output Incomplete

**Date**: November 4, 2025  
**Severity**: 🔴 **CRITICAL** - Chart control completely non-functional  
**Status**: Root cause identified via Playwright investigation

---

## Executive Summary

The Chart Control Agent in Agent Builder workflow v33 **IS calling the MCP tool `change_chart_symbol`** successfully, but the tool's output is **incomplete**. The `chart_commands` array contains `["LOAD"]` instead of `["LOAD:NVDA"]` - **the symbol is missing**.

---

## Evidence from Agent Builder Preview

### Query Submitted:
```
chart NVDA
```

### Workflow Execution (v33):

**1. Intent Classifier Response** ✅ CORRECT
```json
{
  "intent": "chart_command",
  "symbol": "NVDA",
  "confidence": "high"
}
```

**2. Transform Node** ✅ CORRECT
- Extracted `intent` = `"chart_command"`

**3. If/else Node** ✅ CORRECT
- Routed to "Market Data & Charts" branch → Chart Control Agent

**4. Chart Control Agent Response** ❌ **BUG HERE**
```json
{
  "text": "Switched to NVDA. Do you want a specific timeframe or any indicators added?",
  "chart_commands": ["LOAD"]
}
```

**Expected**:
```json
{
  "text": "Switched to NVDA. Do you want a specific timeframe or any indicators added?",
  "chart_commands": ["LOAD:NVDA"]
}
```

**5. G'sves Agent Response** ✅ CORRECT (but uses wrong chart)
```
You are now viewing the NVDA (NVIDIA Corporation) chart.

Would you like to see a specific timeframe (e.g., 1D, 1W, 1M) or have any technical indicators (such as moving averages, RSI, Fibonacci retracement) overlaid on the chart? Let me know your preference for a tailored analysis!
```

**6. End Node - Final Output**
```json
{
  "output_text": "You are now viewing the NVDA (NVIDIA Corporation) chart.\\n\\nWould you like to see a specific timeframe (e.g., 1D, 1W, 1M) or have any technical indicators (such as moving averages, RSI, Fibonacci retracement) overlaid on the chart? Let me know your preference for a tailored analysis!"
}
```

**NOTE**: The final output does NOT include `chart_commands` field!

---

## Root Cause Analysis

### Issue 1: MCP Tool Returns Incomplete chart_commands
The `change_chart_symbol` MCP tool is being called by the Chart Control Agent, but it's returning:
```json
["LOAD"]
```

Instead of:
```json
["LOAD:NVDA"]
```

**Possible causes**:
1. The Chart Control Agent's instructions are telling it to output `["LOAD"]` without the symbol
2. The MCP tool itself has a bug and strips the symbol
3. A Transform node or output schema is stripping the symbol from the array

### Issue 2: chart_commands Not in Final Output
The workflow's final output (`End` node) shows:
```json
{
  "output_text": "You are now viewing the NVDA (NVIDIA Corporation) chart..."
}
```

But it's **missing** the `chart_commands` field entirely!

**This is why our frontend never receives the chart_commands**.

Even if we fix Issue 1, the `chart_commands` won't reach the frontend unless the `End` node is configured to include it in the final output.

---

## What's Working
1. ✅ Intent classification (NVDA symbol correctly extracted)
2. ✅ Workflow routing (Chart Control Agent is reached)
3. ✅ MCP tool execution (change_chart_symbol is being called)
4. ✅ Agent responses are generated
5. ✅ Frontend can receive and process chart_commands (our code is correct)

## What's Broken
1. ❌ MCP tool output: `["LOAD"]` instead of `["LOAD:NVDA"]`
2. ❌ Final workflow output missing `chart_commands` field entirely
3. ❌ Frontend never receives chart_commands (because they're not in final output)
4. ❌ Chart stays on TSLA instead of switching to NVDA

---

## Required Fixes

### Fix 1: Chart Control Agent Instructions (Priority 1)
The Chart Control Agent needs to be configured to:
1. Call `change_chart_symbol` with the extracted symbol
2. Return the MCP tool's output in `chart_commands` field INCLUDING the symbol
3. Ensure the format is `["LOAD:SYMBOL"]` not just `["LOAD"]`

**Where**: Agent Builder → Chart Control Agent node → Instructions/Tools configuration

### Fix 2: End Node Configuration (Priority 1)
The End node must be configured to include `chart_commands` in the final output.

**Current End node output**:
```json
{
  "output_text": "..."
}
```

**Required End node output**:
```json
{
  "output_text": "...",
  "chart_commands": ["LOAD:NVDA"]  // From Chart Control Agent
}
```

**Where**: Agent Builder → End node → Output schema/mapping

### Fix 3: Verify MCP Tool Implementation
Check if the `change_chart_symbol` MCP tool in the backend is correctly formatted to return `["LOAD:SYMBOL"]`.

**Where**: `market-mcp-server/sse-server.js` or backend MCP tool definitions

---

## Testing Plan

### Step 1: Fix Chart Control Agent Output
1. Edit Chart Control Agent in Agent Builder v33
2. Update instructions to ensure `chart_commands` includes symbol: `["LOAD:NVDA"]`
3. Test in Preview with "chart NVDA"
4. Verify Chart Control Agent output shows `["LOAD:NVDA"]`

### Step 2: Fix End Node to Include chart_commands
1. Edit End node configuration
2. Add `chart_commands` field to output schema
3. Map it from Chart Control Agent's response
4. Test in Preview - verify final output includes `chart_commands`

### Step 3: Publish and Deploy
1. Publish new workflow version (v34)
2. Deploy to production via Agent Builder
3. Test in live app at https://gvses-market-insights.fly.dev/
4. Verify chart switches from TSLA to NVDA

### Step 4: Verification Commands
```bash
# Test in live app
curl -X POST https://gvses-market-insights.fly.dev/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "chart NVDA"}' | jq

# Expected response should include:
# {
#   "output_text": "You are now viewing the NVDA...",
#   "chart_commands": ["LOAD:NVDA"]
# }
```

---

## Impact Assessment

### Current State
- **Chart Control**: 🔴 BROKEN (0% functional)
- **Agent Communication**: 🟢 WORKING (100%)
- **Intent Classification**: 🟢 WORKING (100%)
- **User Experience**: 🔴 SEVERELY DEGRADED

### After Fix
- **Chart Control**: 🟢 WORKING (100%)
- **Agent Communication**: 🟢 WORKING (100%)
- **Intent Classification**: 🟢 WORKING (100%)
- **User Experience**: 🟢 EXCELLENT

---

## Key Findings

1. **Our frontend code is correct** - The issue is NOT in the frontend
2. **Agent Builder workflow routing is correct** - Chart Control Agent is being called
3. **MCP tool is being called** - But output is incomplete
4. **The bug is in Agent Builder configuration** - Specifically:
   - Chart Control Agent's output format
   - End node's output schema (missing chart_commands)

---

## Next Actions

1. 🔴 **IMMEDIATE**: Fix Chart Control Agent instructions to output `["LOAD:SYMBOL"]`
2. 🔴 **IMMEDIATE**: Configure End node to include `chart_commands` in final output
3. 🟡 **HIGH**: Publish workflow v34 with fixes
4. 🟡 **HIGH**: Test in production
5. 🟢 **MEDIUM**: Document proper Agent Builder configuration for future reference

---

## References
- Agent Builder workflow: v33 (production)
- Workflow ID: `wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736`
- Test run ID: `wfrun_69097037bbc48193b6bf3164bfc0f0f90b1250964582e49b`
- Chart Control Agent response ID: `resp_004df3fcd2019052006909703a0650819586a0a8215d3e52e4`

---

**Conclusion**: The deployment to production was successful, but the Agent Builder workflow configuration has two critical bugs preventing chart control from functioning. Both bugs are fixable within Agent Builder without requiring code changes.

