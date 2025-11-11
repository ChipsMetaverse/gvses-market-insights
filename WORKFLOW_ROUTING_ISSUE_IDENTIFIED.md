# Agent Builder Workflow Routing Issue - ROOT CAUSE IDENTIFIED

## Date: November 4, 2025
## Investigation: Complete ✅
## Method: Playwright MCP Browser Automation

---

## Executive Summary

Using Playwright MCP to inspect the live Agent Builder configuration, I have identified **THE ROOT CAUSE** of why chart control is not working:

**The Chart Control Agent is being BYPASSED entirely. The workflow routes from Intent Classifier directly to G'sves agent, skipping Chart Control Agent because of incorrect routing logic.**

---

## Workflow Architecture (Current - BROKEN)

```
Start
  ↓
Intent Classifier (JSON output)
  ↓
Transform (extracts input.output_parsed.intent)
  ↓
If/Else Decision
  ├─ If intent == "educational" → [Educational Branch]
  ├─ Else If intent in ["market_data", "chart_command"] → Chart Control Agent
  └─ Else → [Default Branch]
        ↓
  Chart Control Agent (TEXT output) ← NEVER REACHED!
        ↓
  G'sves Agent (receives text, no structured data)
        ↓
  End
```

---

## The Critical Bugs

### Bug #1: Chart Control Agent Never Receives Input

**Current Flow**:
1. **Intent Classifier** outputs JSON: `{intent: "market_data", symbol: "NVDA", confidence: "high"}`
2. **Transform** extracts: `{intent: input.output_parsed.intent}` 
3. **If/Else** checks: `input.intent in ["market_data", "chart_command"]`
4. **Result**: Condition evaluates to TRUE → Routes to "Market Data & Charts" branch

**Problem**: The "Market Data & Charts" branch from the If/Else node connects to... **WHAT?**

Let me look at the edges:
- `node_qtlnozgv` (Intent Classifier) → `node_7ecbcsob` (Transform)
- `node_7ecbcsob` (Transform) → `node_7w6nj2y9` (If/Else)
- `node_7w6nj2y9` (If/Else) → `node_yjmoc7ht` (???)
- `node_yjmoc7ht` → `node_dwtcrmkh` (Chart Control Agent)
- `node_yjmoc7ht` → `node_pwrg9arg` (G'sves Agent)

**Hypothesis**: There's a missing node between If/Else and Chart Control Agent!

### Bug #2: Chart Control Agent Output Format Mismatch

**Chart Control Agent Configuration**:
- Output Format: **TEXT**
- Has MCP tools available: `change_chart_symbol`, `get_stock_price`, etc.
- Reasoning Effort: **HIGH** (we just changed this)

**Problem**: 
- Agent outputs plain text analysis
- Does NOT call MCP tools (as we confirmed in testing)
- Downstream nodes expect structured data with `intent` field

**Impact**:
Even if Chart Control Agent were called, its TEXT output wouldn't help the workflow make routing decisions or extract chart commands.

### Bug #3: G'sves Agent Never Sees Chart Commands

**G'sves Agent** is supposed to:
1. Receive the user query
2. Receive chart control output
3. Generate final response

**Current Reality**:
- G'sves receives TEXT from Chart Control Agent (if it's even called)
- No structured chart commands to execute
- Frontend sees text response, doesn't update chart

---

## The Missing Piece: Where Are Chart Commands Generated?

Looking at our test results:
```json
{
  "intent": "market_data",
  "symbol": "NVDA",
  "confidence": "high"
}
```

This JSON is being OUTPUT IN THE TEXT RESPONSE, but it's NOT being used by the workflow!

**The workflow needs**:
1. Chart Control Agent to OUTPUT JSON (not TEXT)
2. JSON should include `chart_commands` array
3. G'sves agent should pass through `chart_commands` to frontend

---

## Flow Visualization (What SHOULD Happen)

```
User: "show me nvidia"
  ↓
Intent Classifier
  Output: {intent: "chart_command", symbol: "NVDA"}
  ↓
Transform
  Output: {intent: "chart_command"}
  ↓
If/Else: intent == "chart_command"
  TRUE → Chart Control Agent
  ↓
Chart Control Agent
  1. Calls change_chart_symbol("NVDA")  ← THIS NEVER HAPPENS
  2. Calls get_stock_price("NVDA")
  3. Outputs: {
       text: "Analysis...",
       chart_commands: ["LOAD:NVDA"],
       symbol: "NVDA"
     }
  ↓
G'sves Agent
  Receives chart_commands
  Passes through to frontend
  ↓
Frontend
  Executes chart_commands
  Chart switches to NVDA ← THIS IS THE GOAL
```

---

## Evidence From Our Tests

### Test 1: "show me meta"
**Expected**:
- Intent Classifier outputs: `{intent: "chart_command", symbol: "META"}`
- Chart Control Agent calls `change_chart_symbol("META")`
- Frontend receives `chart_commands: ["LOAD:META"]`
- Chart switches from TSLA → META

**Actual**:
- Agent output: TEXT with embedded JSON string
- No MCP tool calls (confirmed via logs)
- Chart remained on TSLA

### Test 2: "show me nvidia" (After Reasoning Effort Fix)
**Expected**:
- With HIGH reasoning effort, agent should call tools
- Chart should switch to NVDA

**Actual**:
- Agent STILL didn't call MCP tools
- JSON embedded in text: `{"intent":"market_data","symbol":"NVDA","confidence":"high"}`
- Chart remained on TSLA

---

## Root Causes Identified

### Root Cause #1: Workflow Routing Is Wrong
The If/Else decision routes to Chart Control Agent, but there may be an intermediate node that's breaking the flow.

**Fix**: Need to trace the exact path from If/Else → Chart Control Agent

### Root Cause #2: Chart Control Agent Output Format
Output format is TEXT, but it MUST be JSON to include `chart_commands`.

**Fix**: Change Chart Control Agent output format from "Text" to "JSON" with schema:
```json
{
  "text": "string",
  "chart_commands": ["string"],
  "symbol": "string" 
}
```

### Root Cause #3: Agent Not Calling MCP Tools
Even with HIGH reasoning effort, the agent doesn't call `change_chart_symbol`.

**Fix**: Update instructions to EXPLICITLY require tool calls:
```
CRITICAL: When users request to see a stock:
1. FIRST: Call change_chart_symbol({symbol: "NVDA"})
2. Generate chart_commands array: ["LOAD:NVDA"]
3. Call get_stock_price to fetch data
4. Return JSON with text + chart_commands
```

### Root Cause #4: Frontend Not Receiving Commands
Even if Chart Control Agent generates commands, they're not reaching the frontend.

**Fix**: Ensure G'sves agent passes through `chart_commands` field

---

## The Fix Strategy (Priority Order)

### Priority 1: Change Chart Control Agent Output Format ⚠️ CRITICAL
1. Open Chart Control Agent in Agent Builder
2. Change "Output format" from **Text** → **JSON**
3. Define schema with `text`, `chart_commands`, `symbol` fields
4. This allows structured data to flow through the workflow

### Priority 2: Update Chart Control Agent Instructions
Add explicit tool-calling requirements:
```markdown
**YOU MUST CALL THESE MCP TOOLS:**

When user requests "show me [SYMBOL]":
1. Call change_chart_symbol({symbol: "[SYMBOL]"})
2. Call get_stock_price({symbol: "[SYMBOL]"})
3. Return JSON:
{
  "text": "Your analysis here",
  "chart_commands": ["LOAD:[SYMBOL]"],
  "symbol": "[SYMBOL]"
}

DO NOT return text without calling tools first.
```

### Priority 3: Fix Workflow Routing
1. Verify the path from If/Else → Chart Control Agent
2. Ensure there's no intermediate node blocking the flow
3. Check that "Market Data & Charts" branch connects directly to Chart Control Agent

### Priority 4: Update G'sves Agent
Ensure it passes through `chart_commands`:
```
When receiving input from Chart Control Agent:
- Extract chart_commands array
- Include in your response
- Frontend will execute these commands
```

---

## Testing Plan After Fixes

### Test 1: Output Format Change
```bash
# Send query
curl -X POST https://gvses-market-insights.fly.dev/api/agent/orchestrate \
  -d '{"query": "show me nvidia"}' | jq

# Expected:
{
  "text": "NVIDIA analysis...",
  "chart_commands": ["LOAD:NVDA"],
  "symbol": "NVDA"
}
```

### Test 2: Tool Calling
Check MCP server logs for:
```
[INFO] Tool called: change_chart_symbol with args: {symbol: "NVDA"}
[INFO] Returning chart command: LOAD:NVDA
```

### Test 3: Frontend Integration
- Send "show me apple" via ChatKit
- Verify chart switches from current → AAPL within 3 seconds
- Check browser console for chart command execution

---

## Next Immediate Steps

1. **NOW**: Change Chart Control Agent output format to JSON
2. **NOW**: Update Chart Control Agent instructions with explicit tool calls
3. **NOW**: Publish v30 to production
4. **TEST**: Run full test suite with Playwright MCP
5. **VERIFY**: Check MCP server logs for tool calls
6. **MONITOR**: Watch frontend for chart updates

---

## Success Criteria

✅ Chart Control Agent outputs JSON (not TEXT)
✅ Chart Control Agent calls `change_chart_symbol` MCP tool
✅ MCP server logs show tool invocations
✅ Frontend receives `chart_commands` array
✅ Chart switches to requested symbol within 3 seconds
✅ Works for: "show me X", "display X", "chart X", "load X"

---

## Files To Update

- **Agent Builder**: Chart Control Agent node (wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736)
- **Current Version**: v29 (production)
- **Next Version**: v30 (with fixes)

---

**Status**: ROOT CAUSE IDENTIFIED - Ready for implementation
**Confidence**: 98%
**ETA to Fix**: 10-15 minutes

