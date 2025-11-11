# V32 Investigation Findings - Critical Issue Persists

## Investigation Date: November 4, 2025, 02:36 UTC
## Method: Playwright MCP Testing + MCP Server Log Analysis
## Status: 🚨 **CHART CONTROL AGENT STILL BYPASSED IN v32**

---

## Executive Summary

Despite publishing v32 with supposedly fixed edge routing, **Chart Control Agent is STILL being bypassed** in actual workflow execution. The visual diagram looks correct, but the runtime behavior does not match.

---

## 🔍 Test Results - v32

### Test Query: `"show me microsoft"`

**Actual Execution Path (from Preview)**:
```
Start 
  ↓
Intent Classifier (✅ outputs: {"intent":"chart_command","symbol":"MSFT","confidence":"high"})
  ↓
Transform (✅ extracts intent correctly)
  ↓
If/else (✅ matches "Market Data & Charts" condition)
  ↓
❌ G'sves (WRONG! Chart Control Agent is missing!)
  ↓
End
```

**Expected Path**:
```
Start → Intent Classifier → Transform → If/else → Chart Control Agent → G'sves → End
```

---

## 📊 Evidence

### 1. Preview Execution Log
- **Agents that ran**: Start, Intent Classifier, Transform, If/else, G'sves, End
- **Agents that did NOT run**: Chart Control Agent ❌

### 2. MCP Server Logs
```
[2025-11-04T02:12:01Z] SSE connection established
[2025-11-04T02:12:01Z] Handling POST message (3 times)
[2025-11-04T02:12:01Z] SSE connection closed
```

**NO TOOL CALLS!** No `CHART CONTROL`, `changeChartSymbol`, or any chart-related tool invocations appeared in the logs.

### 3. Workflow Diagram (v32)
The visual diagram LOOKS correct:
- ✅ 8 edges (up from 7 in v31)
- ✅ Chart Control Agent node is visible and appears to be connected
- ✅ "Market Data & Charts" label visible on If/else node

### 4. Final Output
```json
{
  "output_text": "Microsoft (MSFT) — Real-Time Snapshot ... [analysis]"
}
```

**NO `chart_commands` FIELD!** The output is only text, no structured chart commands.

---

## 🐛 Root Cause Analysis

### Hypothesis 1: Edge Routing is STILL Wrong (Despite Visual Appearance)
**Likelihood**: 🔴 **HIGH**

The workflow diagram may show edges that don't match the actual runtime routing configuration. Agent Builder's visual representation might be out of sync with the underlying workflow definition.

**Evidence**:
- Diagram shows Chart Control Agent connected
- Runtime execution skips Chart Control Agent entirely
- This discrepancy suggests the visual editor and runtime config are not in sync

### Hypothesis 2: "Else" Branch is Matching Instead
**Likelihood**: 🟡 **MEDIUM**

The If/else condition `input.intent in ["market_data", "chart_command"]` might be evaluating to FALSE, causing the workflow to take the "Else" path directly to G'sves.

**Counter-Evidence**:
- Intent Classifier correctly outputs `{"intent":"chart_command"}`
- Transform should extract `intent = "chart_command"`
- Condition should match `"chart_command" in ["market_data", "chart_command"]` → TRUE

### Hypothesis 3: Multiple Edges to G'sves are Conflicting
**Likelihood**: 🟡 **MEDIUM**

Looking at the edges list:
```
- node_yjmoc7ht to node_51nc0a72 (If/else → Educational? or Chart Control?)
- node_yjmoc7ht to node_e28i3ocm (If/else → G'sves - DIRECT!)
- node_51nc0a72 to node_e28i3ocm (Chart Control → G'sves)
- node_yjmoc7ht to node_e28i3ocm (If/else → G'sves - DUPLICATE!)
```

**THERE ARE TWO EDGES FROM IF/ELSE TO G'SVES!** This is the smoking gun!

---

## 🎯 THE ACTUAL PROBLEM

Looking at the edge list carefully:

**Current Edges (8 total)**:
1. `node_qtlnozgv → node_7ecbcsob` (Start → Intent Classifier) ✅
2. `node_7ecbcsob → node_7w6nj2y9` (Intent Classifier → Transform) ✅
3. `node_7w6nj2y9 → node_yjmoc7ht` (Transform → If/else) ✅
4. `node_yjmoc7ht → node_51nc0a72` (If/else [Educational?] → Chart Control Agent?) ❓
5. **`node_yjmoc7ht → node_e28i3ocm`** (If/else → G'sves) ❌ **DUPLICATE/WRONG BRANCH**
6. `node_51nc0a72 → node_e28i3ocm` (Chart Control Agent → G'sves) ✅
7. **`node_yjmoc7ht → node_e28i3ocm`** (If/else → G'sves) ❌ **DUPLICATE!**
8. `node_e28i3ocm → node_fd4zvx4o` (G'sves → End) ✅

**THERE ARE 3 BRANCHES FROM IF/ELSE (`yjmoc7ht`)**:
- Educational → Chart Control Agent? (edge #4)
- Market Data & Charts → G'sves (edge #5) ❌ **WRONG!**
- Else → G'sves (edge #7) ✅

**THE "MARKET DATA & CHARTS" BRANCH IS STILL GOING DIRECTLY TO G'SVES!**

---

## 🔧 What Went Wrong with v32

When you manually reconnected the edges, it appears that:

1. ✅ You successfully connected Chart Control Agent → G'sves (edge #6)
2. ❌ You did NOT remove the old If/else "Market Data & Charts" → G'sves edge (edge #5)
3. ❌ You did NOT connect If/else "Market Data & Charts" → Chart Control Agent

**Result**: Chart Control Agent is connected to G'sves, but there's NO INCOMING EDGE from If/else to Chart Control Agent!

---

## ✅ Correct Edge Configuration

**Should Be (8 edges)**:
1. Start → Intent Classifier ✅
2. Intent Classifier → Transform ✅
3. Transform → If/else ✅
4. **If/else [Educational] → G'sves** ✅
5. **If/else [Market Data & Charts] → Chart Control Agent** ❌ MISSING!
6. **Chart Control Agent → G'sves** ✅ (Already exists)
7. **If/else [Else] → G'sves** ✅
8. G'sves → End ✅

---

## 🚀 Fix Required for v33

### Step 1: Delete Wrong Edge
**Edge to Delete**: If/else "Market Data & Charts" → G'sves (currently edge #5)

### Step 2: Create Correct Edge
**Edge to Add**: If/else "Market Data & Charts" → Chart Control Agent

### Visual Guide:
```
        ┌─────────┐
        │ If/else │
        └───┬─┬─┬─┘
            │ │ │
  Edu  ─────┘ │ └───── Else
              │
       Market Data & Charts
              │
              ↓
    ┌─────────────────┐
    │Chart Control Ag │  ← THIS CONNECTION IS MISSING!
    └────────┬─────────┘
             ↓
          G'sves
```

---

## 🧪 Verification Steps for v33

1. **Delete**: Click on edge from If/else "Market Data & Charts" output to G'sves, press Delete
2. **Add**: Drag from If/else "Market Data & Charts" output handle to Chart Control Agent input handle
3. **Publish** as v33
4. **Test in Preview**: Send "show me microsoft"
5. **Expected**: Chart Control Agent appears between If/else and G'sves in execution log
6. **Check MCP logs**: Should see `changeChartSymbol("MSFT")` tool call
7. **Verify output**: Should include `chart_commands: ["LOAD:MSFT"]`

---

## 📸 Evidence Files

- `workflow_v32_fixed_edges.png` - Shows v32 diagram (looks correct but isn't)
- `if_else_config_v32.png` - Shows If/else node configuration
- Preview test results - Confirms Chart Control Agent is bypassed
- MCP server logs - Confirms no tool calls were made

---

## 🎯 Success Criteria

When v33 is correctly configured, the test "show me microsoft" should produce:

✅ Execution path includes Chart Control Agent  
✅ MCP server logs show `changeChartSymbol("MSFT")` tool call  
✅ Final output includes `chart_commands: ["LOAD:MSFT"]`  
✅ Chart on trading app switches to MSFT symbol  

---

## 💡 Key Learning

**Agent Builder's visual diagram can be misleading!** The edges that appear in the diagram may not match the actual runtime routing. Always verify with Preview execution to see which agents actually run.

The edge list from the accessibility tree is more reliable than the visual appearance.

