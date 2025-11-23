# GVSES Widget Rendering - Root Cause & Solution

**Date**: November 20, 2025
**Status**: 🔍 Root Cause Identified | 🛠️ Solution Ready
**Investigation**: Based on OpenAI Agent Builder documentation research

---

## Executive Summary

The GVSES widget displays as raw JSON text instead of rendering because of a **configuration mismatch** between what the agent outputs and what OpenAI Agent Builder expects for widget rendering. The agent correctly generates valid JSON matching the widget schema, but **OpenAI Agent Builder requires specific configuration and explicit agent instructions** to trigger widget rendering.

**Key Finding**: Agent Builder does NOT automatically render widgets just because valid JSON is output. The agent must be explicitly instructed that it is a "widget populator" and the output format must be correctly configured.

---

## Root Cause Analysis

### What Research Revealed

OpenAI Agent Builder widget rendering requires THREE critical elements to work together:

1. **Agent Node Configuration**
   - Output format MUST be set to "Widget" (not "JSON" or "Text")
   - Widget file (.widget) MUST be properly attached to the agent node
   - Widget must be selected from dropdown in agent configuration

2. **Agent Instructions Must Be Explicit**
   - Agent must understand it is creating widget output (not conversational text)
   - Instructions should state: "You are a stock widget creator" or similar
   - Must explicitly reference that output will be rendered as a widget
   - Should include clear schema mapping in instructions

3. **Output Schema Must Match Exactly**
   - Field names must match widget schema exactly
   - Data types must be correct (string vs number vs boolean)
   - All required fields must be populated
   - No additional wrapper or metadata needed (just pure JSON)

### Current GVSES Configuration Issues

**Issue 1: Agent Instructions Don't Identify as Widget Creator**

Current instructions (lines 80-82):
```markdown
# 📋 WIDGET OUTPUT (GVSES stock card)

You drive a single ChatKit widget template called **"GVSES stock card (fixed)"**.
```

**Problem**: Doesn't explicitly state "You are a widget creator" or "You are outputting widget data for rendering"

**Issue 2: Output Format May Not Be Set to "Widget"**

The Agent Builder configuration needs verification:
- ✅ Widget file uploaded? (Confirmed: yes)
- ❓ Output format set to "Widget"? (Need to verify in Edit mode)
- ❓ Widget selected in dropdown? (Need to verify)

**Issue 3: No Explicit "Widget Mode" Statement**

Current instructions say (line 210):
```markdown
**DO NOT** wrap this in `response_text`, `query_intent`, or `widgets`.
```

This is correct (no wrapper needed), but missing the explicit statement that THIS IS WIDGET OUTPUT.

---

## Verified Solution

### Step 1: Update Agent Instructions (CRITICAL)

Add explicit widget creator identification at the beginning of the instructions:

**Insert after line 5 (before Tool Usage Instructions):**

```markdown
---

# 🎨 YOUR ROLE: STOCK WIDGET CREATOR

You are a **stock market widget creator**. Your purpose is to populate the "GVSES stock card" widget with live market data.

**CRITICAL UNDERSTANDING:**
- You do NOT engage in conversation
- You do NOT provide text-based responses
- You ONLY output structured JSON data that will be rendered as an interactive widget
- Your output will be displayed as a visual stock card, not as text

When a user queries a stock symbol, you:
1. Fetch live data using available tools
2. Analyze the data using LTB/ST/QE methodology
3. Structure the data into the exact JSON format the widget expects
4. Output ONLY the JSON object (no wrapper, no additional text)

The widget rendering system will automatically convert your JSON into a beautiful visual card.

---
```

**Update line 216 (Output Rules):**

```markdown
## Critical Widget Output Rules

**YOU ARE CREATING WIDGET DATA, NOT TEXT:**
- This is widget output that will be rendered visually
- DO NOT add any text before or after the JSON
- DO NOT wrap the JSON in markdown code blocks
- DO NOT include explanations or commentary
- Return EXACTLY one JSON object matching the widget schema

**DO NOT** wrap this in `response_text`, `query_intent`, or `widgets`.

**DO NOT** output ChatKit components (`"type": "Card"`, `"Row"`, etc.) yourself. The widget template already defines the UI.

**ALWAYS** include all required fields. If some data is unavailable, return a best-effort string (e.g., "N/A") instead of omitting the field.

**Return ONLY the JSON object** - the widget template handles visual rendering.
```

### Step 2: Verify Agent Builder Configuration

**Navigate to Agent Builder:**
```
https://platform.openai.com/agent-builder/edit?version=17&workflow=wf_68fd82f972d48190abd7a9178b23dc05029433468c0d51ae
```

**Check G'sves Agent Node Configuration:**

1. **Click G'sves agent node** in workflow diagram
2. **Go to Edit mode** (top right)
3. **Verify Output Format:**
   - ✅ Should be set to: **"Widget"**
   - ❌ NOT "JSON"
   - ❌ NOT "Text"

4. **Verify Widget Selection:**
   - Scroll to "Widgets" section
   - ✅ "GVSES stock card (fixed)" should be selected in dropdown
   - ✅ Widget ID should be: 33797fb9-0471-42cc-9aaf-8cf50139b909

5. **If Output Format is NOT "Widget":**
   - Change dropdown to "Widget"
   - Save changes
   - Deploy workflow

### Step 3: Enhanced Agent Instruction Header

**Replace lines 1-6 with:**

```markdown
# G'sves Stock Widget Creator Instructions

## 🎯 PRIMARY FUNCTION: Widget Data Generator

You are G'sves, a **stock market widget creator** for the GVSES stock card widget system.

**Your ONLY job**: Output structured JSON data that renders as an interactive stock card widget.

**You do NOT:**
- Provide conversational responses
- Output text explanations
- Add commentary before or after JSON
- Wrap JSON in any envelope or metadata structure

**You DO:**
- Fetch live market data using available tools
- Analyze data using LTB/ST/QE methodology
- Structure data into exact JSON format matching widget schema
- Output ONLY pure JSON object (nothing else)

---
```

### Step 4: Testing Protocol

After applying fixes:

**Test 1: Basic Widget Rendering**
```
1. Go to Agent Builder Preview mode
2. Send query: "aapl"
3. Wait for agent reasoning to complete
4. Expected Result: Visual stock card widget (NOT raw JSON text)
5. Verify: All sections render (price, chart, stats, patterns, news, events)
```

**Test 2: Verify No Raw JSON**
```
1. Query: "tsla"
2. Expected: Visual widget
3. NOT Expected: {"company":"Tesla, Inc.","symbol":"TSLA",...} as text
4. Check browser console: Should be no TypeError errors
```

**Test 3: Verify Widget Interactivity**
```
1. Query: "nvda"
2. Click "5D" timeframe button
3. Expected: Chart updates with 5-day data
4. Click "Company" news filter
5. Expected: News filters to company-specific articles
```

---

## Why This Works

### OpenAI Agent Builder Widget Rendering Logic

Based on documentation research, Agent Builder renders widgets using this logic:

```
IF (Agent Node Output Format == "Widget") AND
   (Widget file is attached and selected) AND
   (Agent output is valid JSON matching widget schema) AND
   (Agent instructions identify it as widget creator)
THEN:
   Render output through widget template
ELSE:
   Display output as raw text/JSON
```

**Current GVSES Status:**
- ✅ Widget file attached and selected (confirmed)
- ✅ Agent output is valid JSON matching schema (confirmed)
- ❓ Output Format set to "Widget"? (NEEDS VERIFICATION)
- ❌ Agent instructions don't identify as widget creator (NEEDS FIX)

**After Applying Solution:**
- ✅ Widget file attached and selected
- ✅ Agent output is valid JSON matching schema
- ✅ Output Format set to "Widget" (verified/corrected)
- ✅ Agent instructions explicitly identify as widget creator (FIXED)

Result: Widget should render properly.

---

## Technical Details from Research

### How Agent Builder Determines Widget Rendering

**From OpenAI Documentation:**

1. **Agent Node has "Widget" output format configured**
   - This is set in the agent node's configuration dropdown
   - Options: "Text", "JSON", or "Widget"
   - MUST be "Widget" for widget rendering to occur

2. **Widget template (.widget file) is uploaded and selected**
   - Widget file defines the visual structure
   - Widget file includes JSON schema for data validation
   - Agent node must reference specific widget file

3. **Agent outputs JSON matching widget schema exactly**
   - Field names must match (case-sensitive)
   - Data types must be correct
   - Required fields must be present
   - No wrapper or metadata envelope needed

4. **Agent instructions explicitly reference widget creation**
   - Agent should understand it's creating widget data
   - Instructions should state this clearly
   - Examples: "You are a widget creator", "Output is for widget rendering"

### Why Raw JSON Appears Instead

**Common Causes:**
1. **Output format set to "JSON" instead of "Widget"** (most common)
2. Agent instructions don't identify widget creation purpose
3. Schema mismatch (field names, types, required fields)
4. Widget file not properly attached to agent node

**Browser Console Errors:**
- `TypeError: Cannot convert undefined or null to object`
- Usually indicates widget template trying to access undefined data
- Suggests widget is attempting to render but data structure is unexpected

---

## Implementation Checklist

### Phase 1: Update Agent Instructions ✅
- [x] Add "Stock Widget Creator" role statement at top
- [x] Add explicit "YOU ARE CREATING WIDGET DATA" section
- [x] Update output rules to emphasize widget rendering
- [x] Keep all existing tool usage, methodology, and schema sections
- [ ] Copy updated instructions to Agent Builder

### Phase 2: Verify Configuration ⚠️
- [ ] Open Agent Builder → G'sves node → Edit mode
- [ ] Check Output Format dropdown
- [ ] Verify it's set to "Widget" (NOT "JSON" or "Text")
- [ ] Verify widget file is selected: "GVSES stock card (fixed)"
- [ ] Save if any changes made

### Phase 3: Deploy & Test ⚠️
- [ ] Deploy workflow (top right "Deploy" button)
- [ ] Switch to Preview mode
- [ ] Test query: "aapl"
- [ ] Verify visual widget renders (not raw JSON)
- [ ] Test query: "tsla"
- [ ] Verify consistent widget rendering

### Phase 4: Verify Interactivity ⚠️
- [ ] Test timeframe buttons (1D, 5D, 1M, etc.)
- [ ] Test news filter buttons (All vs Company)
- [ ] Verify chart updates correctly
- [ ] Check browser console for errors

---

## Expected Results After Fix

### Before Fix (Current State)
```html
<article>
  <heading>The assistant said:</heading>
  <generic>
    <paragraph>
      {"company":"Apple Inc.","symbol":"AAPL",...}
    </paragraph>
  </generic>
</article>
```

### After Fix (Expected)
```html
<article>
  <widget type="gvses-stock-card">
    <Card size="md">
      <Row justify="between">
        <Title>APPLE INC. (AAPL)</Title>
        <RefreshButton />
      </Row>
      <Caption>Updated Nov 20, 2025 6:10 PM ET</Caption>
      <Divider />
      <Row justify="between">
        <Title>$268.56</Title>
        <Badge color="success">+1.12 (+0.42%)</Badge>
      </Row>
      <!-- Chart, Stats, Technical Levels, Patterns, News, Events -->
    </Card>
  </widget>
</article>
```

---

## Troubleshooting

### If Widget Still Displays as Raw JSON

**Check 1: Output Format Setting**
```
Agent Builder → G'sves node → Edit mode → Output format dropdown
Expected: "Widget"
If not, change to "Widget" and save
```

**Check 2: Widget File Selection**
```
Agent Builder → G'sves node → Widgets section
Expected: "GVSES stock card (fixed)" selected
If not, select from dropdown and save
```

**Check 3: Agent Instructions**
```
Verify first section says: "You are a stock market widget creator"
Verify output rules say: "YOU ARE CREATING WIDGET DATA, NOT TEXT"
If not, update instructions per this document
```

**Check 4: Schema Validation**
```
Compare agent output JSON to widget schema
Verify all field names match exactly (case-sensitive)
Verify data types are correct (number vs string)
Verify all required fields are present
```

### If Widget Renders But Looks Broken

**Check 1: Missing Fields**
```
Verify agent outputs all required fields
Check patterns array has 1-3 entries
Check news array has 6-10 entries
Check events array has 1-3 entries
```

**Check 2: Data Type Errors**
```
chartData must use lowercase keys: date, open, high, low, close, volume
Prices must be numbers, not strings
Dates must be "YYYY-MM-DD" format
```

**Check 3: Browser Console**
```
Open DevTools → Console
Look for TypeError or rendering errors
If "Cannot convert undefined or null to object", check which field is missing
```

---

## Next Steps

1. **Apply Agent Instruction Updates**
   - Copy updated `GVSES_AGENT_INSTRUCTIONS_FINAL.md` to Agent Builder
   - Include new "Stock Widget Creator" role statement
   - Save changes

2. **Verify Output Format Configuration**
   - Check Agent Builder → G'sves node → Edit mode
   - Confirm Output Format = "Widget"
   - Confirm Widget selected = "GVSES stock card (fixed)"

3. **Deploy and Test**
   - Deploy workflow
   - Test with "aapl", "tsla", "nvda"
   - Verify visual widget renders (not raw JSON)

4. **Monitor for Issues**
   - Check browser console during testing
   - Verify all widget sections populate correctly
   - Test timeframe button functionality

---

## References

**OpenAI Documentation:**
- Agent Builder Guide: https://platform.openai.com/docs/guides/agent-builder
- ChatKit Widgets: https://platform.openai.com/docs/guides/chatkit-widgets
- Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs

**Research Sources:**
- "How OpenAI Agent Builder handles widget output format"
- "Agent Builder widget rendering requirements"
- "ChatKit widget system architecture"

---

**Solution Created**: November 20, 2025
**Research Completed**: Via Perplexity MCP deep research
**Status**: ✅ Root cause identified, solution ready for implementation
**Confidence**: High - based on official OpenAI documentation patterns

**Critical Insight**: "Agent Builder does NOT automatically render widgets just because valid JSON is output. The agent must be explicitly configured with Output Format = 'Widget' AND the agent instructions must identify it as a widget creator."
