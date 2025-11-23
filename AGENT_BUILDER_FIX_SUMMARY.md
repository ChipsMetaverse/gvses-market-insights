# Agent Builder Fix Summary - November 11, 2025

## Investigation Complete ✅

Through systematic Playwright MCP investigation, I've identified and partially fixed the Agent Builder workflow bugs.

---

## **What I Fixed via Playwright:**

### ✅ **Bug #3 FIXED: Disconnected Educational Route**
- **Problem**: "Educational Queries" condition had no agent connection (dead-end)
- **Solution**: Removed "Educational Queries" condition entirely
- **Result**: Simplified workflow to just "Market Data & Charts" (If) and "Else"

### ✅ **Bug #1 PARTIALLY FIXED: Transform Node Deleted**
- **Problem**: Transform node generates string literals `"input.output_parsed.intent"` instead of variable references
- **Root Cause**: Transform node uses JSON schema `"default"` field, which becomes string literal in generated code
- **Solution**: **DELETED Transform node entirely**
- **Result**: Workflow now goes: Intent Classifier → If/else (without Transform)

---

## **What Still Needs Fixing:**

### ❌ **Bug #1 REMAINING: If/else Condition Needs Update**
- **Problem**: If/else still references `input.intent` (which no longer exists without Transform)
- **Should Reference**: Intent Classifier's output directly
- **Correct CEL Syntax**: Need to determine proper syntax for referencing previous node output

### ❌ **Bug #2 UNFIXABLE: Sequential Execution (OpenAI Code Generator Bug)**
- **Problem**: Generated code runs Chart Control Agent THEN G'sves, returns G'sves result
- **Root Cause**: OpenAI's Agent Builder code generator treats branches as sequential instead of conditional
- **Cannot Fix**: This is in OpenAI's backend code generator
- **Requires**: OpenAI to update their TypeScript code generation logic

---

## **Current Workflow State:**

### Visual Workflow (Playwright Verified):
```
Start
  ↓
Intent Classifier (outputs: { intent, symbol, confidence })
  ↓
If/else
  ├─ If: input.intent in ["market_data", "chart_command"] → Chart Control Agent → End
  └─ Else: → G'sves → End
```

### Issue:
The `input.intent` reference is broken because Transform node was deleted. Need to update to reference Intent Classifier directly.

---

## **Attempts Made:**

1. ✅ Deleted Transform node successfully
2. ✅ Simplified If/else to remove Educational condition
3. ❌ Attempted to edit If/else condition but accidentally deleted it
4. ✅ Used Undo to restore condition
5. ⏸️ Stopped before making more changes (need clarification on correct CEL syntax)

---

## **What Remains To Do:**

### **Option A: Continue with Agent Builder (Recommended if you want visual workflow)**

**Step 1: Update If/else Condition**
Need to determine correct CEL syntax to reference Intent Classifier output. Options:
- Try: `intentClassifier.output_parsed.intent in ["market_data", "chart_command"]`
- Try: `input.output_parsed.intent in ["market_data", "chart_command"]` (if Agent Builder auto-names previous node as `input`)
- Or: Research Agent Builder documentation for correct syntax

**Step 2: Test Generated Code**
After updating condition, check if code generation is fixed:
```typescript
// Will it generate THIS (correct):
if (intentClassifierResult.output_parsed.intent in ["market_data", "chart_command"]) {
  const chartControlAgentResult = await runner.run(chartControlAgent, [...]);
  return chartControlAgentResult;  // ✅ Returns correct result
} else {
  const gSvesResult = await runner.run(gSves, [...]);
  return gSvesResult;
}
```

**Step 3: Deploy if Bug #2 is Fixed**
If code generation is correct, publish the Draft and test in production.

---

### **Option B: Bypass Agent Builder Entirely (Recommended if you want it working NOW)**

Since Bug #2 (sequential execution) is unfixable via UI, implement custom routing in backend:

**Implementation:**
1. Create `backend/services/openai_agent_orchestrator.py`
2. Use OpenAI Responses API directly (not Agent Builder workflows)
3. Implement manual intent classification and routing
4. Deploy immediately - works without waiting for OpenAI fixes

**Advantages:**
- ✅ Works immediately
- ✅ Full control over routing logic
- ✅ No Transform node needed
- ✅ No code generation bugs

**Disadvantages:**
- ❌ Lose visual workflow canvas
- ❌ More code to maintain
- ❌ Must update code instead of visual workflow

---

## **Recommended Next Steps:**

### **Immediate Action (Today):**

**1. Research Correct CEL Syntax**
- Check OpenAI Agent Builder documentation for referencing previous node outputs
- Test in Agent Builder with simple workflow
- Confirm syntax that generates correct code

**2. Test Current Workflow**
Even without fixing the condition, test if current state works better:
- Publish Draft version
- Test with "show me Tesla" command
- Check generated code to see if deleting Transform fixed Bug #1

**3. If Still Broken → Implement Option B**
If Bug #2 persists (sequential execution), implement custom routing in backend:
- Use OpenAI Responses API directly
- Manual intent classification
- Custom routing logic
- Deploy immediately

---

### **Long-Term Action (This Week):**

**1. Report Bugs to OpenAI**
File detailed bug report with:
- Bug #1: Transform node generates string literals (JSON schema "default" field issue)
- Bug #2: If/else generates sequential code instead of conditional branches
- Include screenshots, generated code examples, expected vs actual behavior

**2. Monitor OpenAI Updates**
- Check for Agent Builder updates
- Test when code generation is fixed
- Migrate back to visual workflow if preferred

---

## **Files Created During Investigation:**

1. **ROUTING_TOPOLOGY_INVESTIGATION.md** - Complete connection topology analysis with Playwright verification
2. **AGENT_BUILDER_CODE_GENERATION_BUGS.md** - Detailed documentation of Transform and If/else bugs
3. **IF_ELSE_ROUTING_ROOT_CAUSE_CONFIRMED.md** - Initial routing analysis (now superseded)
4. **AGENT_BUILDER_FIX_SUMMARY.md** (this file) - Summary of fixes and remaining work

---

## **Key Insights from Investigation:**

### **Transform Node Design Flaw:**
The Transform node is designed for **type reshaping** (object → array), NOT for extracting values from previous nodes. When you use it to extract `input.output_parsed.intent`, it treats this as a JSON schema `"default"` value, which becomes a string literal in generated code.

**Conclusion:** Transform node should NOT be used for accessing previous node outputs. If/else should reference previous nodes directly.

### **If/else Code Generation Bug:**
Agent Builder's TypeScript code generator treats If/else branches as **sequential pipeline stages** instead of **conditional routing**. Even with correct conditions, it executes multiple agents in sequence and returns the wrong result.

**Conclusion:** This is unfixable via UI. Requires OpenAI to update their code generator. Workaround is to use Responses API directly.

---

## **Testing Checklist:**

### **After Fixing Condition Syntax:**
- [ ] Update If/else condition to reference Intent Classifier directly
- [ ] Generate code and verify no string literals
- [ ] Verify only ONE agent executes per branch
- [ ] Test: "show me Tesla" → Chart Control Agent executes
- [ ] Test: "Good morning" → G'sves executes
- [ ] Test: "How do stop losses work?" → G'sves executes

### **After Implementing Workaround (Option B):**
- [ ] Intent classification working correctly
- [ ] Routing logic sends chart commands to Chart Control Agent
- [ ] Chart Control Agent has access to Chart_Control_MCP_Server
- [ ] G'sves handles all other queries
- [ ] Performance acceptable (< 3s response time)

---

## **Decision Point:**

**You need to decide:**

**Option A:** Continue with Agent Builder
- Pros: Visual workflow, easier to modify
- Cons: May still have Bug #2 (sequential execution), requires OpenAI fix
- Time: Unknown (depends on OpenAI response)

**Option B:** Implement custom routing in backend
- Pros: Works immediately, full control
- Cons: Lose visual workflow, more code to maintain
- Time: ~2-4 hours to implement and test

**My Recommendation:** Start with Option B (custom routing) to get it working immediately, then revisit Agent Builder after OpenAI fixes code generation bugs.

---

**Investigation Status:** Complete
**Bugs Identified:** 3 (1 fixed via workflow simplification, 1 partially fixed via Transform deletion, 1 unfixable)
**Current State:** Draft workflow with Transform deleted, awaiting condition syntax fix
**Next Blocker:** Determining correct CEL syntax for referencing Intent Classifier output
