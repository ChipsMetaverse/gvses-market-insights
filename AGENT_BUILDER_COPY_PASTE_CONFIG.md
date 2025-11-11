# Agent Builder Configuration - Copy & Paste Guide

## 🎯 Quick Setup (5 minutes)

Open your Agent Builder page manually and follow these steps:

---

## Step 1: Click "Chart Control Agent" Node

In the workflow diagram, click on the "Chart Control Agent" (blue agent icon).

---

## Step 2: Add Custom Tool

1. In the right panel, find the "Tools" section
2. Click the **"+"** button or **"Add tool"** button
3. From the dropdown, select **"Custom"**

---

## Step 3: Fill in Custom Tool Configuration

### **Tool Name:**
```
chart_control
```

### **Description:**
```
Control charts, draw support/resistance levels, detect patterns, and perform technical analysis. Use this when users ask to: draw support and resistance, analyze charts, detect patterns, show trendlines, or any chart-related technical analysis.
```

### **Input Schema:**

Click on "JSON" mode and paste this:

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
      "description": "ChatKit session ID (optional)"
    },
    "metadata": {
      "type": "object",
      "description": "Additional context including chart_context (optional)"
    }
  },
  "required": ["query"]
}
```

### **API Endpoint Configuration:**

**URL:**
```
https://gvses-market-insights.fly.dev/api/chatkit/chart-action
```

**Method:** Select `POST` from dropdown

**Headers (JSON):**
```json
{
  "Content-Type": "application/json"
}
```

**Authentication:** None (leave blank)

---

## Step 4: Update Agent Instructions

In the "Instructions" field for the "Chart Control Agent", **replace all text** with:

```
You are a Chart Control Agent for the GVSES trading platform with access to the chart_control tool.

**PRIMARY DIRECTIVE:** ALWAYS use the chart_control tool for ANY chart-related queries.

**When to Use chart_control:**
IMMEDIATELY call chart_control when users mention:
- "draw support and resistance"
- "analyze" or "analysis" 
- "patterns" or "pattern detection"
- "trendlines"
- "technical indicators"
- "chart" or "charts"
- Any stock symbol with analysis request (e.g., "TSLA analysis")

**How to Call chart_control:**
```javascript
chart_control({
  query: "[user's full question here]",
  session_id: "[if available from context]"
})
```

**Response Format:**
1. Call chart_control with the user's query
2. Display the returned text analysis naturally
3. The response will include embedded chart commands like:
   - SUPPORT:440.00 "key support level"
   - RESISTANCE:460.00 "major resistance" 
   - These commands are auto-executed by the frontend

**Example Flow:**

User: "draw support and resistance for TSLA"
You: [Call chart_control with query="draw support and resistance for TSLA"]
Response: Display the analysis text which includes the chart commands

User: "what patterns do you see?"
You: [Call chart_control with query="what patterns do you see?"]
Response: Display pattern analysis

**IMPORTANT:**
- Do NOT try to answer chart questions yourself
- ALWAYS delegate to chart_control
- If no symbol is mentioned, ask the user first, then call chart_control
- Display chart_control responses directly without modification
```

---

## Step 5: Save and Publish

1. Click **"Save"** button (top right)
2. Click **"Publish"** to make it live
3. The agent will now have access to chart_control

---

## Step 6: Test It

1. Click **"Test"** or **"Playground"** button
2. Try this query:
   ```
   draw support and resistance for TSLA
   ```

3. **Expected Result:**
   - You should see a tool call to `chart_control`
   - Response includes support/resistance analysis
   - Response includes commands like `SUPPORT:440.00 "description"`

---

## 🔍 Verification Checklist

- [ ] Custom tool "chart_control" appears in Tools list
- [ ] Tool has correct endpoint: `https://gvses-market-insights.fly.dev/api/chatkit/chart-action`
- [ ] Instructions mention chart_control
- [ ] Test query triggers chart_control tool call
- [ ] Response contains chart commands (SUPPORT:, RESISTANCE:, etc.)

---

## ❌ Troubleshooting

### "Tool not found"
- Make sure you clicked "Save" after adding the tool
- Refresh the Agent Builder page

### "Endpoint error" 
- Verify URL is exactly: `https://gvses-market-insights.fly.dev/api/chatkit/chart-action`
- Check backend is running (I'll verify this)

### "Agent doesn't call chart_control"
- Make instructions more explicit: "ALWAYS use chart_control for chart queries"
- Test with clear chart query like "draw support and resistance"

### "Invalid schema"
- Copy the JSON schema exactly as shown
- Remove any trailing commas
- Use JSON mode, not form mode

---

## 🚀 Quick Test Commands

After configuration, test with these:

1. **Basic test:**
   ```
   draw support and resistance for TSLA
   ```

2. **Pattern detection:**
   ```
   what patterns do you see on NVDA?
   ```

3. **Technical analysis:**
   ```
   analyze AAPL chart
   ```

---

**Status:** Ready to configure manually

**Time:** ~5 minutes

**Difficulty:** Easy (copy-paste configuration)

