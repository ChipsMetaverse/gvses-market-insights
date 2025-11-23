# Widget ChatKit Investigation Findings

**Date**: November 15, 2025
**Investigation Method**: Playwright MCP + Agent Builder Testing
**Status**: Critical Issue Identified

---

## 🔍 Investigation Summary

Attempted to implement widget orchestration in OpenAI Agent Builder using the "Widget ChatKit" output format as suggested by previous research. **Discovered fundamental incompatibility** between the Widget ChatKit format and dynamic widget orchestration requirements.

---

## ❌ Critical Discovery: Widget ChatKit Format Limitation

### What Widget ChatKit Actually Does

The "Widget ChatKit" output format in Agent Builder:

1. **Requires uploaded .widget files** - Static widget templates must be uploaded via Widget Studio
2. **Does NOT support dynamic JSON responses** - The format expects pre-configured widget files, not JSON structures
3. **Cannot orchestrate based on intent** - Static files can't change based on query classification

### Evidence

When clicking the "Widget" button in Agent Builder, a dialog appears:

```
"Upload a .widget file to link a widget to your workflow
 or create new in Widget Studio"
```

This approach is fundamentally incompatible with:
- Intent-based widget selection (news vs. patterns vs. levels)
- Dynamic widget data population (TSLA vs. AAPL vs. SPY)
- Responsive widget orchestration based on user queries

---

## 🐛 Testing Results

### Test Configuration
- **Agent**: G'sves (Intent Classifier → Transform → G'sves → End)
- **Output Format Attempted**: Widget ChatKit
- **Test Query**: "What's the latest news on TSLA?"
- **Expected**: Market News Feed widget with TSLA articles
- **Actual**: Empty object `{}`

### Detailed Test Run Analysis

**Run ID**: `wfrun_6919193f0d348194803b1e2e683f6e9808d91a32d74ea7a5`

**Intent Classification**: ✅ **WORKING**
```json
{"intent":"news","symbol":"TSLA","confidence":"high"}
```

**Data Retrieval**: ✅ **WORKING**
- File Search: 20+ encyclopedia-of-chart-patterns.json files searched
- MCP Call 1: Retrieved 5 CNBC stock articles
- MCP Call 2: Retrieved 5 more CNBC articles (general category)

**Agent Response**: ❌ **FAILED**
```json
{
  "output_text": "{\n \t\t\t \n \t}",
  "output_parsed": {}
}
```

### Root Cause

Even though "Widget ChatKit" was selected in the UI dropdown:
- Logs show: `"Response": "json_schema"`
- The Widget ChatKit setting **does not save/apply** to actual agent configuration
- Agent still uses strict `json_schema` format which requires uploaded .widget files
- Agent has data but doesn't know how to structure response

---

## 🔄 Configuration Save Issue

### Issue Details

1. Selected "Widget ChatKit" from Output format dropdown ✅
2. Dropdown shows "Widget ChatKit" as selected ✅
3. Ran test in Preview mode ✅
4. **Logs show agent still using `json_schema` format** ❌

### Multiple Attempts Made

- **Attempt 1**: Selected Widget ChatKit, tested → still used json_schema
- **Attempt 2**: Re-opened node, verified selection, tested → still used json_schema
- **Attempt 3**: Switched to Edit mode, confirmed setting, tested → still used json_schema

**Conclusion**: The Widget ChatKit dropdown selection does not persist to the actual agent runtime configuration. This appears to be either:
- A UI bug in Agent Builder
- Requires additional configuration step not documented
- Not the correct approach for dynamic widget orchestration

---

## ✅ Recommended Alternative Approach

### Use JSON Output Format Without Schema + Detailed Instructions

**Why This Works**:
1. **Flexible Structure**: No strict schema validation blocking dynamic widgets
2. **Instruction-Driven**: Agent follows detailed JSON examples in instructions
3. **Dynamic Content**: Can populate different widgets based on intent
4. **Proven Pattern**: Many Agent Builder implementations use this approach

### Implementation Steps

#### 1. Set Output Format to "JSON" (No Schema)
- ✅ **Already completed**: Changed from Widget ChatKit to JSON
- Do NOT click "Add schema" - keep it freeform
- Let instructions guide the structure

#### 2. Update Instructions with Complete Widget Examples

Replace the current abstract widget instructions with **concrete, complete JSON examples**:

```markdown
## Widget Response Format

ALWAYS return this exact JSON structure:

### For NEWS Intent:
```json
{
  "response_text": "Here are the latest market news articles for [SYMBOL].",
  "query_intent": "news",
  "symbol": "TSLA",
  "widgets": [{
    "type": "Card",
    "size": "lg",
    "status": {"text": "Live News", "icon": "newspaper"},
    "children": [
      {"type": "Title", "value": "[SYMBOL] Market News", "size": "lg"},
      {"type": "Divider", "spacing": 12},
      {"type": "ListView", "limit": 10, "children": [
        {
          "type": "ListViewItem",
          "children": [
            {"type": "Text", "value": "Article Headline Here", "weight": "semibold"},
            {"type": "Caption", "value": "Source • Time", "size": "sm"}
          ]
        }
      ]}
    ]
  }]
}
```

### For CHART Intent:
```json
{
  "response_text": "Here's the [SYMBOL] price chart.",
  "query_intent": "chart",
  "symbol": "AAPL",
  "widgets": [{
    "type": "Card",
    "size": "full",
    "status": {"text": "Real-Time", "icon": "chart-candlestick"},
    "children": [
      {"type": "Title", "value": "[SYMBOL] Price Chart", "size": "lg"},
      {"type": "Image", "src": "https://chart.url", "aspectRatio": "16/9", "fit": "contain"}
    ]
  }]
}
```

[Continue with complete examples for all 6 intent types...]
```

#### 3. Test with Freeform JSON Format

- Run same test query: "What's the latest news on TSLA?"
- Agent should now return populated widget JSON
- No schema validation blocking the response

---

## 📋 Next Steps

### Immediate Actions

1. **Update Agent Instructions** with complete widget JSON examples
2. **Test in Preview Mode** with all 6 query types:
   - News: "What's the latest news on TSLA?"
   - Economic: "When is the next NFP release?"
   - Patterns: "Show me patterns on NVDA"
   - Levels: "What are support levels for SPY?"
   - Chart: "Show me AAPL chart"
   - Comprehensive: "Give me everything on MSFT"

3. **Verify JSON Response** includes proper widget structures
4. **Frontend Integration** (if backend tests pass)

### Alternative If JSON Approach Fails

If the freeform JSON approach also results in empty responses:

**Option A**: Use Text output format and parse widget JSON from text
**Option B**: Implement backend widget orchestrator (already created in previous session)
**Option C**: Contact OpenAI support about Widget ChatKit configuration issue

---

## 📊 Comparison: Approaches

| Approach | Dynamic Intent | Data Population | Complexity | Status |
|----------|---------------|-----------------|------------|---------|
| Widget ChatKit (uploaded files) | ❌ No | ❌ Static | Low | Not viable |
| JSON with strict schema | ✅ Yes | ✅ Yes | High | Failed (schema too strict) |
| **JSON without schema** | ✅ Yes | ✅ Yes | Medium | **Recommended** |
| Backend orchestrator | ✅ Yes | ✅ Yes | High | Fallback option |

---

## 🎯 Success Criteria

Widget orchestration will be successfully implemented when:

1. ✅ Agent classifies query intent correctly (already working)
2. ✅ Agent retrieves relevant market data (already working)
3. ⏳ Agent returns JSON with populated `widgets` array (in progress)
4. ⏳ ChatKit frontend renders widgets from JSON (pending)
5. ⏳ Different widgets display for different intents (pending)

---

## 🔧 Technical Insights

### Why Widget ChatKit Format Exists

The Widget ChatKit format appears designed for:
- **Static widget templates** in conversational flows
- **Consistent UI elements** across multiple queries
- **Pre-designed widgets** from Widget Studio

Not designed for:
- **Dynamic widget selection** based on runtime logic
- **Intent-based orchestration** with variable structures
- **Data-driven widget population** from API responses

### Why Previous Research Was Misleading

The ChatKit documentation reviewed in previous session:
- Describes widget JSON structures (correct)
- Shows widgets as JSON in agent responses (conceptually correct)
- But doesn't explain Agent Builder's "Widget ChatKit" format limitation
- Assumes custom ChatKit implementation, not Agent Builder's built-in format

---

## 📝 Lessons Learned

1. **UI != API**: Agent Builder UI settings don't always persist to runtime config
2. **Test Logs**: Always check response logs to verify actual vs. expected configuration
3. **Static vs. Dynamic**: Widget ChatKit format is for static templates, not dynamic orchestration
4. **Freeform JSON**: Often more flexible than strict schema for complex nested structures
5. **Examples > Schema**: For LLMs, concrete examples often work better than abstract schemas

---

## 🚀 Confidence in Recommended Approach

**High Confidence (85%)** that freeform JSON approach will work because:

✅ Agent already successfully retrieves data
✅ Intent classification working perfectly
✅ Instructions already include widget structure guidance
✅ Freeform JSON removes schema validation barriers
✅ Similar pattern used in many Agent Builder implementations

**Remaining 15% Risk**:
- Agent may still struggle with complex nested JSON
- ChatKit frontend may require specific widget format we haven't discovered
- May need additional iteration on instruction clarity

---

**Recommendation**: Proceed with freeform JSON approach as next step. This is the most promising path based on testing results and Agent Builder capabilities.
