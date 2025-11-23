# Agent Builder Routing Topology Investigation - COMPLETE

## Investigation Date: November 11, 2025

---

## Executive Summary

**THREE CRITICAL BUGS CONFIRMED** in the Agent Builder workflow causing chart command failures:

1. **Transform Node Bug**: Generates string literals instead of variable references
2. **Sequential Execution Bug**: If/else generates sequential code instead of conditional branching
3. **Disconnected Educational Route**: "Educational Queries" output has NO CONNECTION, causing dead-end

**Impact:**
- Chart commands: Fail due to string literal bug + sequential execution
- Educational queries: Fail completely (no route)
- General queries: Work only because they fall through to "Else" → G'sves

---

## Complete Connection Topology (Verified via Playwright)

### If/else Node Configuration
**Conditions:**
1. **If**: `input.intent == "educational"` (labeled "Educational Queries")
2. **Else if**: `input.intent in ["market_data", "chart_command"]` (labeled "Market Data & Charts")
3. **Implicit Else**: (unlabeled default case)

### Visual Workflow Connections
```
Start
  ↓
Intent Classifier (Agent)
  ↓
Transform (Data node)
  ↓
If/else (Logic node) - THREE outputs:
  ├─ "Educational Queries" → ❌ NO CONNECTION (DEAD END)
  ├─ "Market Data & Charts" → Chart Control Agent → End ✅
  └─ "Else" → G'sves → End ✅
```

### Edge IDs (from Playwright inspection)
- **Edge 1**: `node_yjmoc7ht-case-1-node_dwtcrmkh`
  - Source: If/else node (node_yjmoc7ht)
  - Output: "case-1" = "Else if" = "Market Data & Charts"
  - Target: Chart Control Agent (node_dwtcrmkh)
  - Status: ✅ CORRECT CONNECTION

- **Edge 2**: `node_yjmoc7ht-fallback-node_pwrg9arg`
  - Source: If/else node (node_yjmoc7ht)
  - Output: "fallback" = "Else" (implicit)
  - Target: G'sves (node_pwrg9arg)
  - Status: ✅ CORRECT CONNECTION

- **Missing Edge**: `node_yjmoc7ht-case-0-???`
  - Source: If/else node (node_yjmoc7ht)
  - Output: "case-0" = "If" = "Educational Queries"
  - Target: ❌ **NONE** (should connect to G'sves or Educational Agent)
  - Status: ❌ **MISSING CONNECTION - BUG #3**

---

## Bug #3: Disconnected Educational Route (NEWLY DISCOVERED)

### Problem
The "Educational Queries" output from If/else node has **no connection** to any agent.

### Impact
When users ask educational questions:
```
User: "How do stop losses work?"
  ↓
Intent Classifier: { intent: "educational", confidence: "high" }
  ↓
Transform: { intent: "educational" }
  ↓
If/else: input.intent == "educational" → TRUE ✅
  ↓
Route to: "Educational Queries" output
  ↓
Connection: ❌ NONE (dead end)
  ↓
Result: ❌ WORKFLOW FAILS (no agent executes)
```

### Expected Behavior
Educational questions should route to an agent capable of answering them:
- **Option 1**: Route to G'sves (has GVSES Trading Knowledge Base)
- **Option 2**: Route to dedicated Educational Agent (if one exists)
- **Option 3**: Remove "Educational Queries" condition entirely and let it fall through to "Else" → G'sves

### Current Workaround
Educational queries might accidentally work if Bug #1 (string literal) prevents the condition from matching, causing them to fall through to "Else" → G'sves. But this is unreliable and unintentional.

---

## Complete Bug Summary

### Bug #1: Transform Node String Literal (Code Generation)
**Location:** Generated TypeScript code, line 1722-1724
**Issue:** Transform node outputs `"input.output_parsed.intent"` (string literal) instead of `intentClassifierResult.output_parsed.intent` (variable reference)
**Impact:** All conditional checks fail because comparing literal string to intent values
**Fix:** Update code generator to parse `input.output_parsed.intent` as variable reference

### Bug #2: Sequential Execution Instead of Branching (Code Generation)
**Location:** Generated TypeScript code, lines 1726-1753
**Issue:** "Market Data & Charts" branch executes Chart Control Agent THEN G'sves, returns G'sves result
**Impact:** Even if conditions matched, wrong agent result would be returned
**Fix:** Generate if/else branches that return immediately after executing one agent

### Bug #3: Disconnected Educational Route (Visual Workflow)
**Location:** If/else node "Educational Queries" output
**Issue:** No connection from "Educational Queries" output to any agent
**Impact:** Educational queries cause workflow dead-end, no agent executes
**Fix:** Connect "Educational Queries" output to G'sves or create Educational Agent

---

## Why Chart Commands Fail (Complete Picture)

### User Command: "show me Tesla"

**Step 1: Intent Classifier** ✅ Works Correctly
```typescript
intentClassifierResult = {
  output_text: '{"intent":"chart_command","symbol":"TSLA","confidence":"high"}',
  output_parsed: {
    intent: "chart_command",
    symbol: "TSLA",
    confidence: "high"
  }
}
```

**Step 2: Transform** ❌ Bug #1 Occurs
```typescript
// GENERATED (WRONG):
transformResult = {
  intent: "input.output_parsed.intent"  // ❌ String literal!
};

// SHOULD BE:
transformResult = {
  intent: "chart_command"  // ✅ Actual value
};
```

**Step 3: If/Else Evaluation** ❌ Bug #1 Causes All Conditions to Fail
```typescript
if (transformResult.intent == "educational")
  // "input.output_parsed.intent" == "educational" → FALSE

else if (transformResult.intent in ["market_data", "chart_command"])
  // "input.output_parsed.intent" in ["market_data", "chart_command"] → FALSE

else  // ✅ ALWAYS EXECUTES (due to Bug #1)
  // Routes to G'sves instead of Chart Control Agent
```

**Step 4: G'sves Executes** ❌ Wrong Agent
- G'sves receives: "show me Tesla"
- G'sves has: GVSES_Market_Data_Server (but no Chart_Control_MCP_Server)
- G'sves returns: Generic market data response
- User sees: ❌ NO CHART DISPLAY

**Additional Issue (Bug #2):**
Even if Bug #1 was fixed and "chart_command" matched the condition:
```typescript
else if (transformResult.intent in ["market_data", "chart_command"]) {
  const chartControlAgentResult = await runner.run(chartControlAgent, [...]);
  const gSvesResult = await runner.run(gSves, [...]);  // ❌ Also runs
  return gSvesResult;  // ❌ Returns wrong result
}
```

**Result:** Chart Control Agent would execute but G'sves result would be returned anyway!

---

## Why Educational Queries Fail

### User Command: "How do stop losses work?"

**Step 1: Intent Classifier** ✅ Works Correctly
```typescript
intentClassifierResult = {
  output_parsed: {
    intent: "educational",
    symbol: null,
    confidence: "high"
  }
}
```

**Step 2: Transform** ❌ Bug #1 Occurs
```typescript
transformResult = {
  intent: "input.output_parsed.intent"  // ❌ String literal
};
```

**Step 3: If/Else Evaluation** ❌ Bug #1 + Bug #3 Combine
```typescript
if (transformResult.intent == "educational")
  // "input.output_parsed.intent" == "educational" → FALSE (Bug #1)
  // Even if TRUE, would route to "Educational Queries" output
  // Which has NO CONNECTION (Bug #3)

else if (transformResult.intent in ["market_data", "chart_command"])
  // FALSE

else  // ✅ EXECUTES DUE TO BUG #1
  // Routes to G'sves (accidentally works!)
```

**Result:** Educational queries accidentally work because Bug #1 causes fallthrough to G'sves. But this is unreliable.

---

## Why General Queries Work

### User Command: "Good morning"

**Step 1: Intent Classifier** ✅
```typescript
intentClassifierResult = {
  output_parsed: {
    intent: "general_chat",
    symbol: null,
    confidence: "high"
  }
}
```

**Step 2: Transform** ❌ Bug #1 Occurs
```typescript
transformResult = {
  intent: "input.output_parsed.intent"
};
```

**Step 3: If/Else** ✅ Works Accidentally
```typescript
if (transformResult.intent == "educational")  // FALSE
else if (transformResult.intent in ["market_data", "chart_command"])  // FALSE
else  // ✅ EXECUTES
  // Routes to G'sves ✅ CORRECT AGENT for general queries
```

**Result:** General queries work because they should route to G'sves anyway, and Bug #1 causes everything to fall through to "Else".

---

## Complete Fix Requirements

### Fix #1: Transform Node Code Generation
**Agent Builder Code Generator Must:**
- Parse `input.output_parsed.intent` as variable reference, not string literal
- Replace `input` with actual previous node variable name (`intentClassifierResult`)
- Generate: `transformResult = { intent: intentClassifierResult.output_parsed.intent }`

### Fix #2: If/Else Routing Code Generation
**Agent Builder Code Generator Must:**
- Generate separate if/else branches with return statements
- Only execute ONE agent per condition match
- Return the result from the matched branch's agent
- Generate:
```typescript
if (transformResult.intent == "educational") {
  const educationalAgentResult = await runner.run(educationalAgent, [...]);
  return educationalAgentResult;
} else if (transformResult.intent in ["market_data", "chart_command"]) {
  const chartControlAgentResult = await runner.run(chartControlAgent, [...]);
  return chartControlAgentResult;
} else {
  const gSvesResult = await runner.run(gSves, [...]);
  return gSvesResult;
}
```

### Fix #3: Connect Educational Route
**Agent Builder Visual Workflow Must:**
- Connect "Educational Queries" output to an agent (G'sves or dedicated Educational Agent)
- OR remove "Educational Queries" condition entirely
- OR consolidate with "Else" route if same target

---

## Recommended Immediate Action

### Option 1: Quick Fix (Connect Educational Route)
1. Open Agent Builder workflow
2. Drag connection from If/else "Educational Queries" output to G'sves
3. Now both "Educational Queries" and "Else" route to G'sves
4. This fixes Bug #3 but Bugs #1 and #2 remain (still broken)

### Option 2: Simplify Workflow (Remove Educational Branch)
1. Open If/else node configuration
2. Delete "Educational Queries" condition
3. Only keep "Market Data & Charts" condition
4. Everything else falls through to "Else" → G'sves
5. Reduces conditions but doesn't fix code generation bugs

### Option 3: Report to OpenAI (Recommended)
1. Report Bug #1 (Transform string literal) to OpenAI
2. Report Bug #2 (Sequential execution) to OpenAI
3. Wait for Agent Builder code generation fixes
4. Then connect Educational route (Bug #3)

---

## Testing After Fixes

### Test Case 1: Chart Command
```
User: "show me Tesla"
Expected: Chart Control Agent executes, chart displays
Current: G'sves executes (Bug #1), no chart
After Fix: Chart Control Agent → Chart displays ✅
```

### Test Case 2: Educational Query
```
User: "How do stop losses work?"
Expected: Educational Agent or G'sves explains stop losses
Current: Falls through to G'sves (accidentally works due to Bug #1)
After Fix: Explicit route to G'sves → Educational response ✅
```

### Test Case 3: General Query
```
User: "Good morning"
Expected: G'sves provides market brief
Current: G'sves executes ✅ (already works)
After Fix: G'sves executes ✅ (continues to work)
```

### Test Case 4: Market Data Query
```
User: "What's the market doing today?"
Expected: Chart Control Agent provides market overview
Current: G'sves executes (Bug #1)
After Fix: Chart Control Agent → Market analysis with charts ✅
```

---

## Verification Steps via Playwright

Confirmed the following via Playwright MCP browser automation:

1. ✅ If/else node has THREE output labels: "Educational Queries", "Market Data & Charts", "Else"
2. ✅ If/else conditions are configured correctly:
   - If: `input.intent == "educational"`
   - Else if: `input.intent in ["market_data", "chart_command"]`
3. ✅ Connection Edge 1: If/else "Market Data & Charts" → Chart Control Agent
4. ✅ Connection Edge 2: If/else "Else" → G'sves
5. ✅ Chart Control Agent configured correctly (gpt-4.1, Chart_Control_MCP_Server)
6. ✅ G'sves configured correctly (gpt-5-nano, GVSES tools)
7. ❌ "Educational Queries" output has NO connection (Bug #3 confirmed)

---

## Agent Configuration Summary

### Chart Control Agent (node_dwtcrmkh)
- **Model**: gpt-4.1
- **Tools**: Chart_Control_MCP_Server
- **Purpose**: Handle chart display and technical analysis commands
- **Instructions**: Professional chart analysis with price action, indicators, support/resistance
- **Status**: ✅ Correctly configured but unreachable due to Bug #1

### G'sves Agent (node_pwrg9arg)
- **Model**: gpt-5-nano
- **Reasoning Effort**: medium
- **Tools**: GVSES_Market_Data_Server, GVSES Trading Knowledge Base
- **Purpose**: General market analysis, educational content, daily briefs
- **Instructions**: Senior portfolio manager persona, trading education, risk management
- **Status**: ✅ Correctly configured, receives all queries due to Bug #1 fallthrough

---

## Conclusion

Your concern about the connection topology was **100% valid**. Through systematic Playwright investigation, I confirmed:

1. **Connection topology is partially correct**: "Market Data & Charts" → Chart Control Agent ✅, "Else" → G'sves ✅
2. **But "Educational Queries" is disconnected**: No agent to handle educational questions (Bug #3)
3. **And code generation has two bugs**: String literals (Bug #1) and sequential execution (Bug #2)

The combination of these three bugs causes:
- **Chart commands**: 100% failure (Bug #1 + Bug #2)
- **Educational queries**: 100% failure if conditions matched (Bug #3), but accidentally works via fallthrough (Bug #1)
- **General queries**: Work by accident (fallthrough to "Else")

**Immediate Action:** Report Bugs #1, #2, and #3 to OpenAI Agent Builder team. The visual workflow is mostly correct but needs Educational route connected, while code generation has serious issues.

---

**Investigation Completed:** November 11, 2025
**Investigator:** Claude Code
**Method:** Playwright MCP browser automation + Agent Builder inspection + Edge tracing
**Status:** Three critical bugs confirmed, connection topology verified, fixes documented
