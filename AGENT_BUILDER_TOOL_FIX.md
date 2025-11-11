# Agent Builder Tool Configuration Fix

## 🎯 **Problem Identified**

The MCP server **IS** exposing chart control tools correctly:
- ✅ `change_chart_symbol` - Changes the chart symbol
- ✅ `set_chart_timeframe` - Changes timeframe
- ✅ `toggle_chart_indicator` - Toggles indicators
- ✅ `capture_chart_snapshot` - Takes screenshots

**BUT** Agent Builder is configured with a single custom function tool named `chart_control` that doesn't map to these actual MCP tools.

---

## 🔍 **Root Cause**

### **Current Configuration:**
```
Agent Builder → Custom Tool "chart_control" → ??? → MCP Server Tools
```

The custom `chart_control` tool is a wrapper/abstraction, but Agent Builder doesn't know:
1. **When** to call it (lacks specific trigger patterns)
2. **What** MCP tools it maps to internally
3. **How** to structure the arguments

### **What Should Happen:**
```
Agent Builder → MCP Server → change_chart_symbol({symbol: "NVDA"})
```

Agent Builder should directly see and call the MCP tools, not a custom wrapper.

---

## ✅ **Solution: Remove Custom Tool, Use MCP Tools Directly**

### **Step 1: Remove the `chart_control` Custom Tool**

In Agent Builder:
1. Click on "Chart Control Agent" node
2. In the Tools section, find `chart_control`
3. Click the "X" or "Remove tool" button
4. Save changes

### **Step 2: Verify MCP Server Tools Are Visible**

After removing the custom tool, Agent Builder should automatically see the **actual MCP tools** from the server:

Expected tools visible in Agent Builder:
- ✅ `get_stock_quote`
- ✅ `get_stock_history`
- ✅ `get_market_overview`
- ✅ `get_market_news`
- ✅ **`change_chart_symbol`** ← Key tool for "Show me NVDA"
- ✅ **`set_chart_timeframe`** ← For changing timeframes
- ✅ **`toggle_chart_indicator`** ← For indicators
- ✅ **`capture_chart_snapshot`** ← For screenshots

### **Step 3: Update Agent Instructions**

Replace current instructions with:

```markdown
You are a professional trading chart assistant for the GVSES platform.

**YOUR TOOLS:**

You have direct access to these MCP tools:

1. **change_chart_symbol** - ALWAYS use this when users say:
   - "Show me [SYMBOL]"
   - "Display [SYMBOL]"
   - "Chart [SYMBOL]"
   - "Switch to [SYMBOL]"
   - "Load [SYMBOL]"

2. **set_chart_timeframe** - Use when users request different timeframes:
   - "Show 1 hour chart"
   - "Switch to daily"
   - "Use 5 minute candles"

3. **toggle_chart_indicator** - Use for technical indicators:
   - "Add RSI"
   - "Show MACD"
   - "Turn on Bollinger Bands"

4. **get_stock_quote** - Use for price queries:
   - "What's the price of AAPL?"
   - "How much is Tesla trading at?"

5. **get_market_news** - Use for news requests:
   - "Latest news for NVDA"
   - "What's happening with Tesla?"

**CRITICAL RULES:**

1. **Always call the tool, never just describe what you would do**
   
   ❌ Bad: "I would switch the chart to NVDA for you."
   ✅ Good: [Calls change_chart_symbol(symbol="NVDA")] "I've switched the chart to NVDA."

2. **Call tools IMMEDIATELY when the user requests an action**
   
   User: "Show me NVDA"
   You: [Call change_chart_symbol immediately]
   Then: Respond with "Loaded NVDA chart. Here's the analysis..."

3. **Combine multiple tools when needed**
   
   User: "Show me TSLA on 1 hour timeframe with RSI"
   You: 
   - Call change_chart_symbol(symbol="TSLA")
   - Call set_chart_timeframe(timeframe="1h")
   - Call toggle_chart_indicator(indicator="rsi", enabled=true)
   - Then provide analysis

**EXAMPLES:**

User: "Show me NVDA"
Assistant: [Calls change_chart_symbol({symbol: "NVDA"})]
Assistant: "Loaded NVDA on your chart. Currently trading at $202.49..."

User: "Switch to 5 minute chart"
Assistant: [Calls set_chart_timeframe({timeframe: "5m"})]
Assistant: "Switched to 5-minute candles. The recent price action shows..."

User: "Add RSI indicator"
Assistant: [Calls toggle_chart_indicator({indicator: "rsi", enabled: true})]
Assistant: "RSI indicator added to your chart. Current RSI is..."

**Remember**: Your job is to CONTROL the chart, not just talk about it!
```

### **Step 4: Increase Reasoning Effort**

Change "Reasoning effort" from "low" to **"medium"** or **"high"**.

This gives the agent more time to:
- Evaluate which tools to use
- Consider tool calling before generating text
- Better understand user intent

### **Step 5: Test Again**

1. Navigate to: https://gvses-market-insights.fly.dev/
2. Send message: "Show me NVDA"
3. **Expected behavior**:
   - Agent calls `change_chart_symbol({symbol: "NVDA"})`
   - MCP server logs: `[CHART CONTROL] changeChartSymbol response: {symbol: 'NVDA', ...}`
   - Frontend receives: `LOAD:NVDA` command
   - Chart switches from TSLA to NVDA
   - Agent says: "I've loaded NVDA on your chart..."

---

## 🎯 **Why This Will Work**

### **Before (Current State):**
```
User: "Show me NVDA"
  ↓
Agent Builder sees custom "chart_control" tool
  ↓
Agent doesn't know when to use it (no explicit triggers)
  ↓
Agent generates text response without calling tool
  ↓
❌ Chart stays on TSLA
```

### **After (Fixed State):**
```
User: "Show me NVDA"
  ↓
Agent Builder sees actual "change_chart_symbol" tool
  ↓
Tool description: "Change the symbol displayed on the trading chart"
  ↓
Agent instructions: "ALWAYS use change_chart_symbol when users say 'Show me [SYMBOL]'"
  ↓
Agent calls: change_chart_symbol({symbol: "NVDA"})
  ↓
MCP server executes tool
  ↓
✅ Chart switches to NVDA
```

---

## 📋 **Verification Checklist**

After making these changes, verify:

### **In Agent Builder:**
- [ ] `chart_control` custom tool removed
- [ ] `change_chart_symbol` visible in tools list
- [ ] `set_chart_timeframe` visible in tools list
- [ ] `toggle_chart_indicator` visible in tools list
- [ ] Agent instructions updated with explicit "ALWAYS use..." rules
- [ ] Reasoning effort set to "medium" or "high"
- [ ] Approval set to "Never require approval"

### **In MCP Server Logs:**
- [ ] Agent Builder connecting successfully
- [ ] `tools/list` request returning all tools
- [ ] When tool is called: `[CHART CONTROL] changeChartSymbol` logs appear

### **In Frontend:**
- [ ] Chart receives `LOAD:NVDA` command
- [ ] Chart switches from TSLA to NVDA
- [ ] Agent message includes: "I've loaded NVDA..." or similar

---

## 🚀 **Alternative: Keep Custom Tool BUT Fix It**

If you prefer to keep the custom `chart_control` tool (for abstraction), you need to:

1. **Update the tool description** to be MUCH more explicit:
```json
{
  "name": "chart_control",
  "description": "REQUIRED: Call this tool whenever users request chart changes. Use for: 'show me [SYMBOL]', 'switch to [SYMBOL]', 'display [SYMBOL]', 'load [SYMBOL]', 'chart [SYMBOL]'. Internally calls change_chart_symbol, set_chart_timeframe, toggle_chart_indicator, etc. ALWAYS call this tool for ANY chart-related request.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {"type": "string", "enum": ["change_symbol", "set_timeframe", "toggle_indicator"], "description": "What action to perform"},
      "symbol": {"type": "string", "description": "Stock symbol (for change_symbol action)"},
      "timeframe": {"type": "string", "description": "Timeframe (for set_timeframe action)"},
      "indicator": {"type": "string", "description": "Indicator name (for toggle_indicator action)"},
      "enabled": {"type": "boolean", "description": "Enable/disable (for toggle_indicator action)"}
    },
    "required": ["action"]
  }
}
```

2. **Add explicit examples in agent instructions**:
```markdown
User: "Show me NVDA"
Assistant: [Calls chart_control({action: "change_symbol", symbol: "NVDA"})]
```

**However**, using the MCP tools directly (recommended approach) is simpler and more reliable because each tool has a clear, specific purpose.

---

## 📊 **Expected Timeline**

- **Step 1-2** (Remove custom tool): 2 minutes
- **Step 3** (Update instructions): 5 minutes
- **Step 4** (Increase reasoning): 1 minute
- **Step 5** (Test): 5 minutes

**Total**: ~15 minutes to complete fix

---

## ✅ **Success Criteria**

**Test Query**: "Show me NVDA"

**Must See:**
1. ✅ MCP server logs: `[CHART CONTROL] changeChartSymbol response: {symbol: 'NVDA'}`
2. ✅ Frontend console: Received `LOAD:NVDA` command
3. ✅ Chart visually switches from TSLA to NVDA
4. ✅ Agent response includes acknowledgment: "I've loaded NVDA..." or "Switched to NVDA..."

**If All 4 Happen**: 🎉 **CHART CONTROL IS WORKING!**

