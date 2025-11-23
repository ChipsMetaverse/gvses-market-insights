# Agent Builder Code Generation Bugs - CRITICAL

## Investigation Date: November 11, 2025

---

## Executive Summary

**ROOT CAUSE:** Agent Builder is generating **INCORRECT TypeScript code** with two critical bugs that cause 100% failure on chart commands. The visual workflow configuration is correct, but the code generation has serious flaws.

**Impact:** All chart commands fail because:
1. Transform node generates string literal instead of accessing variable
2. Routing logic executes both agents sequentially instead of conditional branching

---

## Bug #1: Transform Node String Literal Error (CRITICAL)

### Location
**File:** Agents SDK TypeScript code (Line 1722-1724)

### Incorrect Generated Code
```typescript
const transformResult = {
  intent: "input.output_parsed.intent"  // ❌ STRING LITERAL, NOT VARIABLE ACCESS!
};
```

### What Should Be Generated
```typescript
const transformResult = {
  intent: intentClassifierResult.output_parsed.intent  // ✅ CORRECT
};
```

### Root Cause
The Transform node in Agent Builder is configured to access `input.output_parsed.intent`, but the code generator is treating this as a **string literal** instead of a **variable reference**.

### Impact
The `transformResult.intent` contains the literal string `"input.output_parsed.intent"` instead of the actual intent value like `"chart_command"`.

**Result:**
- `transformResult.intent == "educational"` → **Always FALSE**
- `transformResult.intent in ["market_data", "chart_command"]` → **Always FALSE**
- All conditions fail, workflow always falls through to "Else" branch → G'sves

### Example Execution
```typescript
// What happens:
intentClassifierResult = {
  output_parsed: { intent: "chart_command", symbol: "TSLA", confidence: "high" }
}

transformResult = {
  intent: "input.output_parsed.intent"  // ❌ Literal string, not "chart_command"
}

// If/else evaluation:
if (transformResult.intent == "educational")  // "input.output_parsed.intent" == "educational" → FALSE
else if (transformResult.intent in ["market_data", "chart_command"])  // FALSE
else  // ✅ ALWAYS EXECUTES THIS BRANCH
```

---

## Bug #2: Sequential Execution Instead of Conditional Routing (CRITICAL)

### Location
**File:** Agents SDK TypeScript code (Lines 1725-1754)

### Incorrect Generated Code
```typescript
} else if (transformResult.intent in ["market_data", "chart_command"]) {
  // Run Chart Control Agent
  const chartControlAgentResultTemp = await runner.run(
    chartControlAgent,
    [...conversationHistory]
  );
  conversationHistory.push(...chartControlAgentResultTemp.newItems.map((item) => item.rawItem));

  const chartControlAgentResult = {
    output_text: chartControlAgentResultTemp.finalOutput ?? ""
  };

  // ❌ THEN ALSO RUN G'SVES (NOT A ROUTING BRANCH!)
  const gSvesResultTemp = await runner.run(
    gSves,
    [...conversationHistory]
  );
  conversationHistory.push(...gSvesResultTemp.newItems.map((item) => item.rawItem));

  const gSvesResult = {
    output_text: gSvesResultTemp.finalOutput ?? ""
  };

  return gSvesResult;  // ❌ RETURNS G'SVES RESULT, NOT CHART CONTROL AGENT!
```

### What Should Be Generated
```typescript
} else if (transformResult.intent in ["market_data", "chart_command"]) {
  // Run Chart Control Agent
  const chartControlAgentResultTemp = await runner.run(
    chartControlAgent,
    [...conversationHistory]
  );
  conversationHistory.push(...chartControlAgentResultTemp.newItems.map((item) => item.rawItem));

  const chartControlAgentResult = {
    output_text: chartControlAgentResultTemp.finalOutput ?? ""
  };

  return chartControlAgentResult;  // ✅ RETURN CHART CONTROL RESULT
```

### Root Cause
The code generator is treating the workflow as a **sequential pipeline** where both Chart Control Agent and G'sves run one after another, instead of a **conditional branch** where only ONE agent runs based on the intent.

### Impact
Even if Bug #1 was fixed and chart commands matched the condition:
1. Chart Control Agent runs and generates chart analysis
2. **G'sves also runs** and overrides the chart analysis
3. **G'sves result is returned** instead of Chart Control Agent result
4. User receives generic market data instead of chart display

### Visual Workflow vs Generated Code Mismatch

**Visual Workflow (Correct):**
```
If/else
  ├─ "Market Data & Charts" → Chart Control Agent → End
  └─ "Else" → G'sves → End
```

**Generated Code (Incorrect):**
```
If/else
  └─ "Market Data & Charts":
       1. Run Chart Control Agent
       2. Run G'sves  // ❌ SHOULDN'T HAPPEN
       3. Return G'sves result  // ❌ WRONG RESULT
```

---

## Intent Classifier Configuration (CORRECT)

The Intent Classifier agent is properly configured:

```typescript
const intentClassifier = new Agent({
  name: "Intent Classifier",
  instructions: `You are an intent classifier for the GVSES Market Analysis Assistant.
    Analyze the user message and classify it into one of these categories:

    1. "market_data" - Stock prices, earnings, financial data
    2. "chart_command" - Show/display chart requests
    3. "educational" - Trading education and how-to questions
    4. "technical" - Technical analysis and indicators
    5. "news" - Market news and headlines
    6. "company-info" - Company details and business information
    7. "general_chat" - Greetings and general conversation

    Extract any stock symbol mentioned (TSLA, AAPL, etc.) or set to null if none found.
    Set confidence level based on how clear the intent is: "high", "medium", or "low".

    The JSON schema will enforce the proper response format.
    Input: {{user_message}}
    Output: classification_result`,
  model: "gpt-4.1",
  outputType: IntentClassifierSchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 2048,
    store: true
  }
});
```

**Schema:**
```typescript
const IntentClassifierSchema = z.object({
  intent: z.string(),
  symbol: z.string(),
  confidence: z.string()
});
```

This is **working correctly** - the Intent Classifier will return `intent: "chart_command"` for "show me Tesla".

---

## Complete Execution Flow Analysis

### User Input: "show me Tesla"

**Step 1: Intent Classifier (✅ Works)**
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

**Step 2: Transform (❌ Bug #1)**
```typescript
transformResult = {
  intent: "input.output_parsed.intent"  // ❌ Literal string!
};
// Should be: { intent: "chart_command" }
```

**Step 3: If/Else (❌ Both bugs combine)**
```typescript
if (transformResult.intent == "educational")
  // "input.output_parsed.intent" == "educational" → FALSE

else if (transformResult.intent in ["market_data", "chart_command"])
  // "input.output_parsed.intent" in ["market_data", "chart_command"] → FALSE

else  // ✅ THIS BRANCH EXECUTES
  // Runs G'sves agent
  // Returns generic market data response
```

**Result:** Chart command fails, user gets generic G'sves response instead of chart display.

---

## Why This Happens

### Transform Node Configuration Issue
Looking at the Transform node in Agent Builder, it likely has:
- **Input field:** `input.output_parsed.intent`
- **Code generator interpretation:** Treats as string literal instead of variable reference

**Agent Builder should:**
- Recognize `input` as the previous node's output reference
- Generate code that accesses `intentClassifierResult.output_parsed.intent`

**Agent Builder actually does:**
- Treats the entire expression as a string literal
- Generates `intent: "input.output_parsed.intent"`

### If/Else Routing Logic Issue
Looking at the If/else configuration:
- **Visual UI:** Shows three separate output branches (Educational, Market/Chart, Else)
- **Expected behavior:** Only ONE branch executes based on condition

**Agent Builder should:**
- Generate if/else if/else with return statements in each branch
- Only execute ONE agent based on matching condition

**Agent Builder actually does:**
- Generates sequential execution within if branch
- Runs Chart Control Agent, THEN G'sves, returns G'sves result

---

## Verification Using Agents SDK Code

### Intent Classifier Output Format
```typescript
const intentClassifierResult = {
  output_text: JSON.stringify(intentClassifierResultTemp.finalOutput),
  output_parsed: intentClassifierResultTemp.finalOutput
};
```

**This is correct!** Intent Classifier returns structured output with `output_parsed.intent`.

### Transform Reference Bug
```typescript
const transformResult = {
  intent: "input.output_parsed.intent"  // ❌ Should be: intentClassifierResult.output_parsed.intent
};
```

**This is the smoking gun!** The string literal prevents any condition from matching.

### Routing Logic Bug
```typescript
} else if (transformResult.intent in ["market_data", "chart_command"]) {
  const chartControlAgentResult = await runner.run(chartControlAgent, [...]);
  const gSvesResult = await runner.run(gSves, [...]);  // ❌ Shouldn't run here
  return gSvesResult;  // ❌ Wrong return value
```

**This is the second smoking gun!** Both agents run, wrong result returned.

---

## Workarounds (Until Agent Builder Fixes)

### Option 1: Fix Transform Node
In Agent Builder UI, try changing Transform node from:
```
input.output_parsed.intent
```
To a different syntax that might generate correct code (if possible).

### Option 2: Use Direct Responses API
Instead of Agent Builder workflows, use the Direct Responses API with custom routing logic in `backend/services/agent_orchestrator.py`.

### Option 3: Simplify Workflow
Remove Transform node entirely:
1. Intent Classifier → outputs `intent`
2. If/else directly checks `intentClassifierResult.intent` (not sure if Agent Builder supports this)

### Option 4: Report to OpenAI
These are critical bugs in Agent Builder code generation that should be reported to OpenAI.

---

## Recommended Fixes (For OpenAI)

### Fix #1: Transform Node Code Generation
**Current:**
```typescript
const transformResult = {
  intent: "input.output_parsed.intent"  // ❌ String literal
};
```

**Should be:**
```typescript
const transformResult = {
  intent: intentClassifierResult.output_parsed.intent  // ✅ Variable access
};
```

**Solution:** Agent Builder should:
1. Parse `input.output_parsed.intent` as variable reference
2. Replace `input` with the actual previous node variable name
3. Generate code that accesses the structured output

### Fix #2: If/Else Routing Code Generation
**Current:**
```typescript
} else if (transformResult.intent in ["market_data", "chart_command"]) {
  const chartControlAgentResult = await runner.run(chartControlAgent, [...]);
  const gSvesResult = await runner.run(gSves, [...]);
  return gSvesResult;
```

**Should be:**
```typescript
} else if (transformResult.intent in ["market_data", "chart_command"]) {
  const chartControlAgentResult = await runner.run(chartControlAgent, [...]);
  return chartControlAgentResult;  // ✅ Return correct result
} else {
  const gSvesResult = await runner.run(gSves, [...]);
  return gSvesResult;
}
```

**Solution:** Agent Builder should:
1. Generate separate if/else branches for each condition
2. Only execute ONE agent per branch
3. Return the result from the executed agent
4. Not chain multiple agents sequentially in routing branches

---

## Impact Assessment

### Severity
**CRITICAL** - 100% failure rate on primary feature (chart display)

### Affected Users
All users attempting to use chart commands via Agent Builder workflow

### Affected Workflows
Any Agent Builder workflow using:
1. Transform nodes with variable references
2. If/else nodes with multiple agent routing

### Workaround Availability
**Limited** - Direct Responses API can be used but loses visual workflow benefits

---

## Testing After Fix

### Test Cases

**Test 1: Chart Command**
- Input: "show me Tesla"
- Expected: Chart Control Agent executes, returns chart analysis
- Current: G'sves executes, returns generic data

**Test 2: Educational Query**
- Input: "How do stop losses work?"
- Expected: Educational branch (routing TBD)
- Current: G'sves executes (correct by coincidence due to "else" fallthrough)

**Test 3: General Query**
- Input: "Good morning"
- Expected: G'sves executes, returns market brief
- Current: G'sves executes (correct by coincidence)

### Validation Steps
1. Fix Transform node variable reference generation
2. Fix If/else conditional branching generation
3. Regenerate Agents SDK code
4. Test all three routing paths
5. Verify only ONE agent executes per request
6. Verify correct agent result is returned

---

## References

### Generated Code Location
- Agent Builder → Code button → Agents SDK tab → TypeScript
- Lines 1722-1724: Transform bug
- Lines 1726-1753: Routing bug

### Related Documentation
- `IF_ELSE_ROUTING_ROOT_CAUSE_CONFIRMED.md` - Initial routing investigation
- `PRODUCTION_BUG_INVESTIGATION.md` - Original bug report
- OpenAI Agent Builder Docs: https://platform.openai.com/docs/guides/agent-builder

---

## Conclusion

The visual Agent Builder workflow is **correctly configured**, but the code generation has **two critical bugs**:

1. **Transform node generates string literals** instead of variable references
2. **If/else routing executes agents sequentially** instead of conditionally

These bugs cause 100% failure on chart commands because:
- Conditions never match due to string literal comparison
- Even if they matched, wrong agent result would be returned

**Action Required:** Report bugs to OpenAI Agent Builder team for code generation fixes.

**Temporary Workaround:** Use Direct Responses API with custom routing logic until Agent Builder code generation is fixed.

---

**Investigation Completed:** November 11, 2025
**Investigator:** Claude Code
**Method:** Playwright MCP + Agents SDK code analysis
**Status:** Root cause confirmed - Agent Builder code generation bugs identified
