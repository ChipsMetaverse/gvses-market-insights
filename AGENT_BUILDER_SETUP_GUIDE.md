# Agent Builder Custom Action Setup Guide

## 🎯 Goal
Add the `chart_control` custom action to the "Gvses" agent in Agent Builder.

---

## ⚠️ **Issue with MCP SSE Server**

The MCP SSE server (`https://gvses-mcp-sse-server.fly.dev/sse`) is **NOT compatible** with Agent Builder's tool loading system.

**Why:**
- Agent Builder expects tool schemas via MCP protocol messages
- Our SSE server is a transport layer, not a tool definition provider
- The error "Unable to load tools" means no tool schemas found

**Solution:**
Use a **direct HTTP action** instead, which calls our backend API directly.

---

## 📋 **Step-by-Step Setup**

### **Step 1: Open Agent Builder**

Go to: https://platform.openai.com/agent-builder/edit?version=draft&workflow=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736

### **Step 2: Click on "Gvses" Agent Node**

In the workflow diagram, click on the "Gvses" agent node (the blue agent icon in the middle-right).

### **Step 3: Add Custom Action**

**Option A: If there's an "Add Action" or "Add Tool" button:**
1. Click "Add Action" or "Add Tool"
2. Choose "Custom HTTP Action" or "External API"

**Option B: If you need to add in the Instructions:**
1. Scroll to the "Instructions" field
2. Add the tool definition in JSON format (see below)

### **Step 4: Configure the Action**

**Action Name:** `chart_control`

**Description:**
```
Control charts, draw support/resistance, detect patterns, and perform technical analysis. 
Use this when user asks about: 'draw support and resistance', 'what patterns do you see?', 
'analyze this chart', 'show trendlines', 'detect patterns', or any chart-related technical analysis.
```

**Endpoint URL:**
```
https://gvses-market-insights.fly.dev/api/chatkit/chart-action
```

**Method:** `POST`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Parameters Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "The user's chart-related query"
    },
    "session_id": {
      "type": "string",
      "description": "Current ChatKit session ID (if available)"
    },
    "metadata": {
      "type": "object",
      "description": "Additional context including chart_context"
    }
  },
  "required": ["query"]
}
```

**Full JSON Config** (use this if adding via JSON):
```json
{
  "name": "chart_control",
  "description": "Control charts, draw support/resistance, detect patterns, and perform technical analysis. Use this when user asks about: 'draw support and resistance', 'what patterns do you see?', 'analyze this chart', 'show trendlines', 'detect patterns', or any chart-related technical analysis.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The user's chart-related query"
      },
      "session_id": {
        "type": "string",
        "description": "Current ChatKit session ID (if available)"
      },
      "metadata": {
        "type": "object",
        "description": "Additional context"
      }
    },
    "required": ["query"]
  },
  "endpoint": {
    "url": "https://gvses-market-insights.fly.dev/api/chatkit/chart-action",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

### **Step 5: Update Agent Instructions**

In the "Gvses" agent's **Instructions** field, add this at the top:

```
You are a trading assistant with chart control capabilities.

IMPORTANT: When users ask about charts, patterns, support/resistance, or technical analysis, 
you MUST call the chart_control action.

Always use chart_control for:
- "draw support and resistance"
- "what patterns do you see?"
- "analyze this chart"
- "show me trendlines"
- "detect patterns"
- Any chart-related technical analysis

When calling chart_control:
1. Pass the user's full query
2. Include session_id if available
3. The action will return text analysis + chart commands
4. Display the response text naturally to the user
5. The chart commands (SUPPORT:, RESISTANCE:, TRENDLINE:) will be auto-executed

If you don't know which chart is loaded, ask the user for the ticker symbol first.
```

### **Step 6: Save and Publish**

1. Click **"Save"** button
2. Click **"Publish"** to deploy the changes
3. Test in the Agent Builder playground

---

## 🧪 **Testing in Agent Builder Playground**

### **Test 1: Simple Chart Query**

**Input:**
```
draw support and resistance for TSLA
```

**Expected:**
- Agent calls `chart_control` action
- Returns analysis with support/resistance levels
- Response includes commands like:
  ```
  SUPPORT:440.00 "key support level"
  RESISTANCE:460.00 "major resistance"
  ```

### **Test 2: Pattern Detection**

**Input:**
```
what patterns do you see on NVDA?
```

**Expected:**
- Agent calls `chart_control` action
- Returns pattern analysis
- May include pattern overlay commands

### **Test 3: Chart Awareness**

**Input:**
```
analyze this chart
```

**Expected:**
- Agent might ask "which chart?" OR
- If session has chart context, analyzes directly

---

## ❌ **Common Issues & Fixes**

### **Issue 1: "Unable to load tools"**

**Cause:** Trying to use MCP SSE server as a tool provider

**Fix:** Use direct HTTP action configuration (as shown above)

### **Issue 2: Agent doesn't call chart_control**

**Cause:** Instructions not clear enough

**Fix:** Make instructions more explicit:
```
ALWAYS call chart_control for chart queries. Do NOT try to answer chart 
questions yourself. ALWAYS use the tool.
```

### **Issue 3: Authentication errors**

**Cause:** Missing or invalid API key

**Fix:** 
- Ensure `OPENAI_API_KEY` is set in backend `.env`
- Check backend logs for authentication errors

### **Issue 4: Timeout errors**

**Cause:** Backend processing takes too long

**Fix:**
- Increase Agent Builder timeout (if configurable)
- Optimize backend agent_orchestrator performance

---

## 📊 **Verify Setup**

### **Backend Verification**

Test the endpoint directly:

```bash
curl -X POST https://gvses-market-insights.fly.dev/api/chatkit/chart-action \
  -H "Content-Type: application/json" \
  -d '{
    "query": "draw support and resistance for TSLA",
    "session_id": "test_session",
    "metadata": {
      "chart_context": {
        "symbol": "TSLA",
        "timeframe": "1D"
      }
    }
  }' | jq
```

**Expected Response:**
```json
{
  "success": true,
  "text": "I'll analyze TSLA and draw support/resistance levels...\n\nSUPPORT:440.00 \"key level\"...",
  "chart_commands": [
    "SUPPORT:440.00 \"key support level\"",
    "RESISTANCE:460.00 \"major resistance\""
  ],
  "data": {
    "tools_used": ["detect_chart_patterns"],
    "chart_context": {"symbol": "TSLA", "timeframe": "1D"}
  }
}
```

### **Agent Builder Verification**

1. Open Agent Builder playground
2. Type a chart query
3. Check the "Tool Calls" panel
4. Verify `chart_control` was called
5. Check response contains chart commands

---

## 🚀 **Alternative: If Custom Actions Don't Work**

If Agent Builder doesn't support custom HTTP actions, use **Function Calling** instead:

1. Define function in Agent Builder as:
   ```json
   {
     "name": "chart_control",
     "description": "...",
     "parameters": {...}
   }
   ```

2. Agent Builder will return function call requests

3. Our frontend intercepts these and calls the backend

4. Frontend sends results back to Agent Builder

(This requires more complex frontend integration)

---

## 📞 **Need Help?**

If you encounter issues:

1. Check backend logs: `fly logs -a gvses-market-insights`
2. Check Agent Builder execution logs
3. Test endpoint directly with curl
4. Verify Agent Builder has latest published version

---

**Status:** Ready to configure

**Estimated Time:** 15 minutes

**Difficulty:** Easy (if custom actions supported) or Medium (if function calling needed)

