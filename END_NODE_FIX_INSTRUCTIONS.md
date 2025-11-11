# End Node Fix - Manual Instructions

## 🎯 Quick Summary
**All automated fixes are complete and deployed.** The remaining issue is that the End node in Agent Builder needs field mappings configured to extract values from the Chart Control Agent.

---

## 🚨 The Problem

**Current End Node Output**:
```json
{
  "output_text": "undefined",
  "chart_commands": ["undefined"]
}
```

**Expected End Node Output**:
```json
{
  "output_text": "Loaded NVDA. Choose a timeframe...",
  "chart_commands": ["LOAD:NVDA"]
}
```

---

## ✅ Step-by-Step Fix

### 1. Open Agent Builder
Navigate to: https://platform.openai.com/agent-builder/edit?workflow=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736&version=34

### 2. Select the End Node
Click on the **End** node in the workflow canvas (it's the final node that outputs `workflow_response`)

### 3. Look for Field Mappings
In the right panel, **scroll down** below the schema definition. You should find a section for:
- "Fields"
- "Mapping"
- "Output Configuration"
- Or similar

### 4. Configure Field Mappings

You need to map the End node's output fields to the input from previous nodes:

#### For `output_text`:
- **Field Name**: `output_text`
- **Type**: Expression
- **Value/Expression**: `input.text`
- **Description**: Extract response text from the previous agent

#### For `chart_commands`:
- **Field Name**: `chart_commands`
- **Type**: Expression
- **Value/Expression**: `input.chart_commands`
- **Description**: Extract chart commands from Chart Control Agent

### 5. Handle Multiple Input Sources (Optional)

Since the End node receives input from both Chart Control Agent and G'sves, you may need fallback logic:

```
output_text: input.text || input.output_text || ""
chart_commands: input.chart_commands || []
```

---

## 🧪 Test Before Publishing

### 1. Use Preview Function
- Click the **Preview** button
- Type: "Show me NVDA chart"
- Wait for execution to complete

### 2. Check End Node Output
- Click on the End node during execution
- Verify the output shows:
  ```json
  {
    "output_text": "Loaded NVDA...",
    "chart_commands": ["LOAD:NVDA"]
  }
  ```

### 3. Check Agent Builder Logs
- Click on the response log link
- Verify in the detailed logs that `chart_commands` contains `["LOAD:NVDA"]`

---

## 📤 Publish When Ready

1. Click **Deploy** button (top right)
2. Confirm deployment as v35
3. Wait for workflow to go into production

---

## 🔍 Verify in Live App

### 1. Navigate to Live App
https://gvses-market-insights.fly.dev

### 2. Connect Voice
Click "Connect voice" button

### 3. Test Chart Command
Type in chat or say: "Show me NVDA chart"

### 4. Verify Chart Switches
- Chart should switch from TSLA to NVDA
- Chart title should update to "NVDA"
- Console should show: `[ChatKit] Processing chart_commands: {raw: ["LOAD:NVDA"], normalized: "LOAD:NVDA"}`

---

## 🐛 Troubleshooting

### If End Node Still Shows "undefined"

**Option A: Check Input Variable Names**
The End node might be receiving data under different property names. Use the Preview's detailed logs to see the exact structure of the input to the End node.

**Option B: Try Different Expression Paths**
- `input.output_parsed.text`
- `input.output.text`
- `input[0].text` (if it's an array)

**Option C: Use Code View**
1. Click **Code** button (top right)
2. Scroll to the End node section
3. Manually inspect the output mapping code
4. Make sure it's extracting from the correct input path

---

## 📊 Current Status

### ✅ Completed
- [x] MCP tool returns correct format: `["LOAD:NVDA"]`
- [x] Chart Control Agent outputs correct data
- [x] Frontend handles array-to-string conversion
- [x] All code changes committed and deployed

### ⚠️ Pending (This Manual Fix)
- [ ] End node field mappings configured
- [ ] End-to-end test passes
- [ ] Chart switches correctly in live app

---

## 🎯 Why This Matters

Without the End node field mappings:
- The workflow executes correctly internally
- The Chart Control Agent generates the right data
- But the final output to the client is incomplete
- Frontend never receives the `chart_commands`
- Chart never switches

**Once this is fixed, the entire chart control flow will work end-to-end!**

---

## 💡 Quick Reference

**Agent Builder Workflow**:
- URL: https://platform.openai.com/agent-builder/edit?workflow=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736&version=34
- Version: v34 (production)
- Next Version: v35 (after this fix)

**Expected Field Mappings**:
```typescript
{
  output_text: input.text,
  chart_commands: input.chart_commands
}
```

**Test Query**:
"Show me NVDA chart"

**Expected Result**:
Chart switches from TSLA to NVDA ✅

---

**Created**: 2025-11-04  
**Status**: Awaiting Manual Configuration  
**Estimated Time**: 5-10 minutes

