# Chart Control Investigation Plan

**Date**: November 4, 2025  
**Status**: Agent detecting intent but not calling MCP tools  

---

## 🎯 **What We Know So Far**

### **From User's Test:**
```
Query: "show me meta"
Response: {"intent":"chart_command","symbol":"META","confidence":"high"}
          + Detailed analysis text

Query: "switch chart to nvda"  
Response: {"intent":"chart_command","symbol":"NVDA","confidence":"high"}
          + Detailed analysis text
```

### **Key Observations:**
1. ✅ Agent **understands** the queries correctly
2. ✅ Agent **detects** chart command intent
3. ✅ Agent **extracts** the correct symbols
4. ❌ Agent **doesn't call** the `change_chart_symbol` MCP tool
5. ❌ Chart **doesn't switch** (stays on current symbol)

---

## 🔍 **Investigation Steps**

### **Step 1: Check MCP Server Logs During Query**

**Goal**: Determine if the agent is calling tools at all

**Method**:
```bash
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp"
./test_chart_control.sh
```

**Then**:
1. Open https://gvses-market-insights.fly.dev/
2. Send: "show me meta"
3. Watch the logs

**Expected Results:**

**Scenario A: Tool IS being called** (Success!)
```
[CHART CONTROL] changeChartSymbol: {symbol: 'META'}
SSE connection established
[CHART CONTROL] changeChartSymbol response: {...}
```
→ **If you see this**: Tools are working! Issue is in frontend parsing.

**Scenario B: Tool is NOT being called** (Current issue)
```
SSE connection established
Handling POST message
[No CHART CONTROL logs]
```
→ **If you see this**: Agent Builder is not invoking the tools.

---

### **Step 2: Check Agent Builder Tool Configuration**

**Verify:**
1. ✅ `change_chart_symbol` is checked (enabled)
2. ✅ Approval is "Never require approval"
3. ⚠️ Reasoning effort is "low" (should be "high")
4. ❓ Are there ANY tool calls happening? (check for `get_stock_quote` calls)

**Questions to Answer:**
- Is the agent calling `get_stock_quote` to get the price data?
- If YES → Agent CAN call tools, just not choosing `change_chart_symbol`
- If NO → Agent isn't calling ANY tools (broader configuration issue)

---

### **Step 3: Test with Direct Tool Reference**

**Try these queries** to see if more explicit language helps:

```
Test 1: "call change_chart_symbol with symbol META"
Test 2: "use the change_chart_symbol tool for NVDA"  
Test 3: "execute change_chart_symbol({symbol: 'TSLA'})"
```

**Expected**:
- If these work → Agent needs explicit tool naming
- If these don't work → Agent isn't processing tool calls at all

---

### **Step 4: Check Reasoning Effort Impact**

**Current**: Reasoning effort = "low"  
**Test**: Change to "high" and retry

**Hypothesis**:
- Low reasoning = Agent takes shortcuts, skips tool evaluation
- High reasoning = Agent considers all options including tools

**Test**:
1. Change reasoning effort to "high"
2. Send: "show me meta"
3. Check logs for `[CHART CONTROL]`

---

## 🧪 **Diagnostic Test Suite**

### **Test 1: Basic Symbol Change**
```
Query: "show me meta"
Check: MCP logs for [CHART CONTROL]
Result: [ ] Tool called  [ ] Tool not called
```

### **Test 2: Explicit Command**
```
Query: "change chart to nvda"
Check: MCP logs for [CHART CONTROL]
Result: [ ] Tool called  [ ] Tool not called
```

### **Test 3: Imperative Language**
```
Query: "load TSLA on the chart"
Check: MCP logs for [CHART CONTROL]
Result: [ ] Tool called  [ ] Tool not called
```

### **Test 4: Direct Tool Reference**
```
Query: "call change_chart_symbol for AAPL"
Check: MCP logs for [CHART CONTROL]
Result: [ ] Tool called  [ ] Tool not called
```

### **Test 5: After Reasoning Increase**
```
Change: Reasoning effort → "high"
Query: "show me meta"
Check: MCP logs for [CHART CONTROL]
Result: [ ] Tool called  [ ] Tool not called
```

---

## 📊 **What Each Result Means**

### **If NO Tests Call Tools:**
**Problem**: Agent Builder configuration issue
**Solutions**:
1. Verify MCP server connection is active
2. Check if ANY tools are being called (look for `get_stock_quote`)
3. Try deleting and re-adding the MCP server connection
4. Check Agent Builder logs for errors

### **If SOME Tests Call Tools:**
**Problem**: Query phrasing triggers
**Solutions**:
1. Add minimal instruction: "Use MCP tools for chart requests"
2. Add example: "User: show me X → Call change_chart_symbol"
3. Increase reasoning effort to "high"

### **If Tests 4-5 Call Tools:**
**Problem**: Agent needs explicit guidance
**Solution**: Add instruction about when to use tools

---

## 🎯 **Most Likely Root Causes** (Ranked)

### **1. Reasoning Effort Too Low** (90% probability)
- **Symptom**: Agent generates good text but skips tools
- **Fix**: Change reasoning effort from "low" to "high"
- **Test**: Retry "show me meta" after change

### **2. Missing Tool Usage Instruction** (70% probability)
- **Symptom**: Agent understands intent but doesn't know to use tools
- **Fix**: Add one line: "Use MCP tools for chart operations"
- **Test**: Check if agent follows instruction

### **3. Tool Description Not Matching** (30% probability)
- **Symptom**: Agent doesn't recognize when to use `change_chart_symbol`
- **Fix**: Update tool description to include common phrases
- **Test**: Modify tool description in MCP server code

### **4. Agent Builder Bug** (10% probability)
- **Symptom**: Tools visible but never called despite configuration
- **Fix**: Try different agent model or recreate agent
- **Test**: Create a simple test agent with one tool

---

## ✅ **Quick Win: Increase Reasoning Effort**

**This is the highest probability fix:**

1. Open Agent Builder
2. Click "Chart Control Agent"
3. Find "Reasoning effort: low ▼"
4. Change to "Reasoning effort: high ▼"
5. Click "Update"
6. Test with: "show me meta"
7. Check MCP logs for `[CHART CONTROL]`

**Expected Result**: Agent takes more time to think, evaluates tools, and calls `change_chart_symbol`.

---

## 📝 **Testing Checklist**

Before adding any instructions, test these in order:

- [ ] Run `./test_chart_control.sh` to monitor logs
- [ ] Send "show me meta" and check if `[CHART CONTROL]` appears
- [ ] Change reasoning effort to "high"
- [ ] Retry "show me meta" with high reasoning
- [ ] If still no tool calls, check if `get_stock_quote` is being called
- [ ] Document results for each test

**Report Format**:
```
Test: "show me meta"
Reasoning: low
Tool Called: Yes/No
Log Output: [paste relevant logs]
```

---

## 🎯 **Next Steps Based on Results**

### **If Tools ARE Being Called:**
→ Issue is in frontend command parsing  
→ Check `RealtimeChatKit.tsx` message handling  
→ Verify `onChartCommand` callback is working  

### **If Tools Are NOT Being Called:**
→ Issue is in Agent Builder configuration  
→ First: Increase reasoning effort  
→ Second: Add minimal tool usage instruction  
→ Third: Test with different query phrasings  

---

## 🔧 **Emergency Fallback**

If nothing works after all tests:

**Add this ONE LINE to agent instructions:**
```
When users request chart changes (show me X, switch to X, load X), call the change_chart_symbol tool before responding.
```

This gives the agent explicit permission to use the tool without being overly prescriptive.

