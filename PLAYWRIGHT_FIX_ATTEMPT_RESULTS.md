# Playwright Fix Attempt Results

**Date**: November 4, 2025  
**Method**: Direct Agent Builder modification via Playwright MCP  
**Status**: ⚠️ **PARTIAL SUCCESS** - Instructions updated, but bug persists

---

## Changes Made Via Playwright

### 1. Chart Control Agent Instructions - UPDATED ✅

**What was changed:**
- Added explicit formatting rules for `chart_commands`
- Added examples of correct vs incorrect formats
- Emphasized that `["LOAD"]` alone is WRONG

**New instructions added:**
```markdown
📊 CRITICAL: chart_commands FORMAT

Your chart_commands array MUST include the symbol in EVERY command:
✅ CORRECT: ["LOAD:NVDA"]
✅ CORRECT: ["LOAD:AAPL", "TIMEFRAME:1D"]  
❌ WRONG: ["LOAD"] (MISSING SYMBOL!)

**Format Rules:**
- LOAD command: ALWAYS "LOAD:SYMBOL" (e.g., "LOAD:NVDA", "LOAD:TSLA")
- Support/Resistance: "SUPPORT:123.45" or "RESISTANCE:456.78"  
- Timeframe: "TIMEFRAME:1D" (valid: 1D, 5D, 1M, 6M, 1Y, YTD, MAX)

**NEVER output ["LOAD"] alone - it MUST be ["LOAD:SYMBOL"]**
```

### 2. End Node Output Schema - ADDED ✅

**What was added:**
```json
{
  "type": "object",
  "properties": {
    "output_text": {
      "type": "string",
      "description": "Final response text to display to user"
    },
    "chart_commands": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Chart commands from Chart Control Agent"
    }
  },
  "additionalProperties": false,
  "required": ["output_text"],
  "title": "workflow_response"
}
```

---

## Test Results

### Test Query: "chart NVDA"

**Workflow Execution (Draft version):**

1. ✅ Intent Classifier: `{"intent":"chart_command","symbol":"NVDA","confidence":"high"}`
2. ✅ Transform: Extracted intent correctly
3. ✅ If/else: Routed to Chart Control Agent
4. ❌ **Chart Control Agent**: `{"text":"Loaded NVDA...","chart_commands":["LOAD"]}`
5. ✅ G'sves: Generated response about NVDA

**PROBLEM: Chart Control Agent STILL outputs `["LOAD"]` instead of `["LOAD:NVDA"]`**

---

## Root Cause Analysis

### Why The Instructions Didn't Fix It

The updated instructions explicitly tell the agent to use `["LOAD:NVDA"]` format, but it's STILL outputting `["LOAD"]`. This suggests:

**Hypothesis 1: MCP Tool Bug**
The `change_chart_symbol` MCP tool might be returning `["LOAD"]` without the symbol, and the agent is just passing through the tool's output.

**Evidence:**
- The agent text says "Loaded NVDA" (knows the symbol)
- But `chart_commands` only has `["LOAD"]` (missing symbol)
- This suggests the tool was called with "NVDA" but returned incomplete data

**Hypothesis 2: Agent Ignoring Instructions**
The AI model (gpt-5) might be ignoring the explicit format instructions in favor of what it learned from previous examples or tool responses.

**Hypothesis 3: Response Schema Override**
The Chart Control Agent's response schema might be overriding the instructions and forcing a specific format.

---

## Critical Finding

**Location of Bug: `change_chart_symbol` MCP Tool**

The Chart Control Agent's response schema (from earlier investigation) shows:
```json
{
  "chart_commands": {
    "type": "array",
    "items": {"type": "string"},
    "description": "Array of chart commands like LOAD:SYMBOL, SUPPORT:123.45, etc"
  }
}
```

The description says "LOAD:SYMBOL" but the agent outputs "LOAD".

**This means the MCP tool `change_chart_symbol` itself is returning the wrong format!**

---

## Next Steps Required

### 1. Check MCP Tool Implementation ⚠️ CRITICAL

**File to inspect**: `market-mcp-server/sse-server.js` or MCP tool definitions

**What to look for:**
```javascript
// WRONG - returns just ["LOAD"]
change_chart_symbol(symbol) {
  return {chart_commands: ["LOAD"]};
}

// CORRECT - should return ["LOAD:SYMBOL"]
change_chart_symbol(symbol) {
  return {chart_commands: [`LOAD:${symbol}`]};
}
```

### 2. Fix MCP Tool Output Format

The `change_chart_symbol` tool needs to:
1. Accept symbol parameter (e.g., "NVDA")
2. Return `{chart_commands: ["LOAD:NVDA"]}` not `{chart_commands: ["LOAD"]}`

### 3. Alternative: Post-Process in Agent

If MCP tool can't be fixed, add this to Chart Control Agent instructions:
```
AFTER calling change_chart_symbol tool:
1. Extract the symbol from user query
2. REPLACE ["LOAD"] with ["LOAD:{SYMBOL}"]
3. Return the corrected chart_commands array
```

---

## Workflow Status

**Draft Version:**
- ✅ Chart Control Agent instructions updated
- ✅ End node output schema added
- ❌ Chart commands still incorrect: `["LOAD"]` vs `["LOAD:NVDA"]`
- ⏳ NOT PUBLISHED (still in draft)

**Next Action:**
1. Investigate MCP tool implementation
2. Fix tool to return `["LOAD:SYMBOL"]` format
3. Test again
4. Publish if working

---

## Files That Need Investigation

1. `market-mcp-server/sse-server.js` - MCP server implementation
2. Backend MCP tool definitions - wherever `change_chart_symbol` is defined
3. Chart Control Agent configuration - tool call parameters

---

## Conclusion

The Playwright modifications successfully updated the Agent Builder configuration, but **the root cause is in the MCP tool implementation**, not the agent configuration. The tool is returning incomplete data (`["LOAD"]` without symbol).

**Action Required**: Fix the `change_chart_symbol` MCP tool to include the symbol in its output format.

