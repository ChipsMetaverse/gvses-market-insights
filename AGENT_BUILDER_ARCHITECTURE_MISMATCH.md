# Agent Builder Architecture Mismatch - Critical Findings

**Date:** November 17, 2025
**Status:** 🚨 **ARCHITECTURAL CONFLICT DETECTED**
**Discovery Method:** Playwright automation + Agent Builder inspection

---

## Executive Summary

The OpenAI Agent Builder workflow has **TWO CONFLICTING widget architectures** configured simultaneously:

1. **Template Widget System** (Output format: Widget with uploaded file)
2. **Inline Widget Orchestration** (Agent instructions with ChatKit components)

**This architectural mismatch makes the Transform node approach invalid.**

---

## Discovery Process

### 1. Initial Assumption (From WIDGET_TRANSFORM_REQUIREMENTS.md)
- Assumed Transform node could execute JavaScript to reshape data
- Proposed Transform node with functions like `formatRelativeTime()`
- Expected to insert between GVSES_Market_Data_Server and widget rendering

### 2. Agent Builder Investigation (via Playwright)
**Workflow Structure Discovered:**
```
Start → Intent Classifier → Transform → G'sves → End
```

**Transform Node Position:**
- Located BEFORE G'sves agent (not after)
- Transforms Intent Classifier output, not stock data

**Transform Node Capabilities:**
- ❌ **Does NOT support JavaScript**
- ✅ Common Expression Language (CEL) for simple expressions
- ✅ JSON schema definitions for structured output
- ❌ No support for functions like `formatRelativeTime()`

### 3. G'sves Agent Configuration Analysis

**Output Format:**
```
Output format: Widget
Widget file: "GVSES stock card (fixed)"
```

**Agent Instructions (Excerpt):**
```markdown
## Widget Response Format

ALWAYS return your response in this JSON structure:

{
  "response_text": "Your natural language explanation",
  "query_intent": "news|economic_events|patterns|technical_levels|chart|comprehensive",
  "symbol": "EXTRACTED_TICKER_SYMBOL",
  "widgets": [
    {
      "type": "Card",
      "size": "lg",
      "children": [...]
    }
  ]
}
```

**Widget Selection Rules:**
- News Intent → Market News Feed Widget (Card, ListView, Badge components)
- Economic Events → Economic Calendar Widget
- Patterns → Pattern Detection + Chart
- Technical Levels → Levels + Chart
- Chart → Chart Only
- Comprehensive → ALL Widgets

---

## The Architectural Conflict

### Conflicting System #1: Template Widget (Uploaded File)

**How it works:**
1. Widget file uploaded: "GVSES stock card (fixed)"
2. Agent returns **DATA** to fill the template
3. Widget template has Jinja2 variables expecting specific data structure
4. Data validation test found 4 mismatches between tool output and template expectations

**Expected Data Structure:**
```json
{
  "company": "Apple Inc",
  "symbol": "AAPL",
  "price": {
    "current": 272.41,
    "change": 1.23
  },
  "news": [
    {
      "title": "Article headline",
      "time": "2h",  // Relative time string
      "url": "https://..."  // Field named "url"
    }
  ],
  "patterns": [  // Direct array
    {
      "type": "doji",
      "confidence": 75
    }
  ]
}
```

### Conflicting System #2: Inline Widget Orchestration (Agent Instructions)

**How it works:**
1. NO uploaded widget template used
2. Agent returns **COMPLETE WIDGET JSON** with ChatKit components
3. Widget structure defined inline in agent's response
4. No data transformation needed - agent builds widgets directly

**Expected Response Structure:**
```json
{
  "response_text": "Here are the latest news for TSLA:",
  "query_intent": "news",
  "symbol": "TSLA",
  "widgets": [
    {
      "type": "Card",
      "size": "lg",
      "status": {"text": "Live News", "icon": "newspaper"},
      "children": [
        {"type": "Title", "value": "TSLA Market News", "size": "lg"},
        {"type": "Divider", "spacing": 12},
        {"type": "ListView", "limit": 10, "children": [...]}
      ]
    }
  ]
}
```

---

## Why Transform Node Won't Work

### 1. Wrong Position in Workflow
```
Intent Classifier → [Transform] → G'sves → End
                      ^^^^^^^^^
                      Transforms intent, NOT stock data
```

The Transform node processes Intent Classifier output (user's query intent), not GVSES_Market_Data_Server output (stock data).

### 2. Wrong Technology
- Transform node uses **Common Expression Language (CEL)**
- Does NOT support JavaScript functions
- Cannot execute code like:
  ```javascript
  function formatRelativeTime(unixTimestamp) { ... }
  ```

### 3. Wrong Data Flow
For template widgets, data transformation must happen:
- **In the backend tool** (GVSES_Market_Data_Server returns widget-formatted data)
- **OR in the agent's final output** (agent reformats tool data before returning)
- **NOT in a Transform node** (wrong position, wrong capabilities)

---

## Root Cause Analysis

**The configuration represents TWO DIFFERENT WIDGET APPROACHES:**

### Approach A: Template Widget (What the upload suggests)
- Use uploaded widget file "GVSES stock card (fixed)"
- Agent returns data to fill template variables
- Requires backend tool to match widget's expected data structure
- 4 data mismatches currently blocking this

### Approach B: Inline Orchestration (What the instructions describe)
- No uploaded widget template
- Agent dynamically generates ChatKit component JSON
- Flexible - agent can build any widget structure
- Instructions already fully implement this

**Current state:** Both approaches configured, causing confusion

---

## Validation Test Results Recap

**Test File:** `backend/test_widget_data_shape.py`

**Issues Found:**
1. ❌ Missing `company` field (tool returns `price_data.company_name`)
2. ❌ News missing `time` field (tool returns Unix `published` timestamp)
3. ❌ News `url` vs `link` mismatch
4. ❌ Patterns wrong type (object with `detected` array instead of direct array)

**Formatting Status:**
✅ All formatting correct ($ symbols, M/B/T units already applied)

---

## Recommended Solutions

### Option 1: Use Inline Widget Orchestration (RECOMMENDED)

**Why:** Agent instructions already implement this fully

**Changes Required:**
1. **Remove uploaded widget file** from Output format
2. **Keep agent instructions** (already complete)
3. **Set Output format to "Text"** or default (not Widget)
4. Agent will return inline widget JSON as per instructions

**Pros:**
- ✅ Already fully implemented in instructions
- ✅ More flexible (agent can build any widget type)
- ✅ No backend changes needed
- ✅ No data transformation needed
- ✅ Works with current GVSES_Market_Data_Server output

**Cons:**
- ❌ Invalidates the uploaded "GVSES stock card (fixed)" widget file
- ❌ Agent must build widget JSON for every response

### Option 2: Fix Template Widget Data Mismatches

**Why:** Make the uploaded widget actually work

**Changes Required:**
1. **Update backend** `GVSES_Market_Data_Server` tool:
   ```python
   # Add company field
   data["company"] = data["price_data"]["company_name"]

   # Transform news timestamps
   for article in data["news"]:
       article["time"] = format_relative_time(article["published"])
       article["url"] = article.pop("link")

   # Extract patterns array
   data["patterns"] = data["patterns"]["detected"]
   ```

2. **Remove widget orchestration instructions** (conflicting approach)

3. **Simplify agent instructions** to just return the stock data

**Pros:**
- ✅ Uses the fixed widget file that's already uploaded
- ✅ Agent just returns data (simpler)
- ✅ Widget template handles rendering

**Cons:**
- ❌ Requires backend code changes
- ❌ Less flexible (locked into single widget structure)
- ❌ Current instructions become invalid

### Option 3: Hybrid Approach

**Why:** Use both systems for different intents

**Changes Required:**
1. Keep inline widgets for: news, economic_events, patterns, technical_levels
2. Use template widget ONLY for comprehensive queries
3. Update backend for comprehensive data format
4. Agent decides which system to use based on intent

**Pros:**
- ✅ Leverages both systems
- ✅ Flexibility for most queries
- ✅ Rich comprehensive view with template

**Cons:**
- ❌ Most complex to implement
- ❌ Two parallel widget systems to maintain
- ❌ Confusing architecture

---

## Decision Matrix

| Criteria | Option 1: Inline Only | Option 2: Template Only | Option 3: Hybrid |
|----------|----------------------|------------------------|------------------|
| **Implementation Effort** | Low (already done) | Medium (backend changes) | High (both systems) |
| **Flexibility** | High | Low | High |
| **Maintenance** | Low | Medium | High |
| **Performance** | Medium (agent builds JSON) | High (template renders) | Medium |
| **Current State Alignment** | Instructions ✅ | Widget file ✅ | Both ✅ |

---

## Immediate Next Steps

### If choosing Option 1 (Inline Orchestration):
1. Click "GVSES stock card (fixed)" button to remove widget
2. Change Output format from "Widget" to "Text"
3. Publish workflow
4. Test: Ask "What's the latest on AAPL?" - should return inline widgets

### If choosing Option 2 (Template Widget):
1. Update `backend/market_data_service.py` or `comprehensive_stock_data` endpoint
2. Implement 4 data transformations (company, news time, news url, patterns)
3. Remove widget orchestration from agent instructions
4. Publish workflow
5. Test: Ask "What's the latest on AAPL?" - should render template widget

### If choosing Option 3 (Hybrid):
1. Implement Option 2 backend changes
2. Update agent instructions to route by intent
3. Add logic: if comprehensive → return data, else → return inline widgets
4. Publish workflow
5. Test multiple intents

---

## Technical Documentation References

- **Agent Instructions:** Scroll through G'sves agent configuration panel
- **Widget File:** `.playwright-mcp/GVSES-stock-card-fixed-.widget`
- **Data Validation:** `backend/test_widget_data_shape.py`
- **Transform Requirements:** `WIDGET_TRANSFORM_REQUIREMENTS.md` (now obsolete)
- **Jinja2 Fix:** `AGENT_BUILDER_JINJA_FIX.md` (still relevant if using template)

---

## Conclusion

The Transform node approach **will not work** because:
1. Agent Builder Transform nodes don't support JavaScript
2. Transform node is in wrong position (before G'sves, not after)
3. Two conflicting widget systems configured simultaneously

**Recommended Path:** Option 1 (Inline Widget Orchestration)
- Fastest to deploy (already implemented)
- Most flexible architecture
- No backend changes required
- Aligns with agent instructions

**Alternative Path:** Option 2 (Template Widget)
- Use the fixed widget file that was created
- Requires backend data transformation
- Simpler agent logic
- Less flexible for different query types

**Decision required from user before proceeding.**

---

*Investigation completed: November 17, 2025*
*Method: Playwright automation + Agent Builder analysis*
*Status: Awaiting user decision on architectural path*
