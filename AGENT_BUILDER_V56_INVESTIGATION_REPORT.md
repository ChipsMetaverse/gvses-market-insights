# Agent Builder v56 Workflow Investigation Report

**Date**: November 16, 2025
**Status**: 🔴 CRITICAL CONFLICTS IDENTIFIED
**Version**: v56 (intended production base)

## Executive Summary

Investigation of v56 workflow revealed **multiple critical conflicts** between the widget template approach and ChatKit components approach. The workflow is misconfigured with:
1. Widget template attached but incompatible instructions
2. Transform node dropping critical data fields
3. Two conflicting output methodologies mixed together

## Workflow Structure (v56)

```
Start → Intent Classifier → Transform → G'sves → End
```

## Node-by-Node Analysis

### 1. Intent Classifier Agent

**Configuration:**
- **Model**: gpt-4.1
- **Output format**: JSON
- **Output schema**: `classification_result`
- **Include chat history**: ✓ Enabled

**Output Schema:**
```json
{
  "intent": "market_data|chart_command|educational|technical|news|company-info|general_chat",
  "symbol": "string (ticker) or null",
  "confidence": "high|medium|low"
}
```

**Status**: ✅ CORRECT - Properly configured

---

### 2. Transform Node

**Configuration:**
- **Transform output type**: Expressions
- **Current mappings**:
  - `intent` ← `input.output_parsed.intent`

**CRITICAL ISSUE**: ❌ **MISSING FIELDS**
- Missing: `symbol` ← `input.output_parsed.symbol`
- Missing: `confidence` ← `input.output_parsed.confidence`

**Impact**: The G'sves agent never receives the stock symbol or confidence level from the Intent Classifier!

**Status**: 🔴 BROKEN - Only passing 1 of 3 fields

---

### 3. G'sves Agent

**Configuration:**
- **Model**: gpt-5-nano
- **Reasoning effort**: medium
- **Output format**: Widget (Widget ChatKit)
- **Widget template**: "GVSES stock card (fixed)" ✅ ATTACHED
- **Tools**: GVSES_Market_Data_Server, GVSES Trading Knowledge Base
- **Include chat history**: ✓ Enabled

**CRITICAL CONFLICT**: The agent has TWO INCOMPATIBLE configurations:

#### Configuration A: Widget Template (OLD Approach)
**Template**: "GVSES stock card (fixed)"
**Required Schema**:
```json
{
  "company": "Acme Corp",
  "symbol": "ACME",
  "timestamp": "Updated Nov 16, 2025 2:45 PM ET",
  "price": {
    "current": "$123.45",
    "changeLabel": "+1.23 (1.01%)",
    "changeColor": "success",
    "afterHours": {...}
  },
  "timeframes": ["1D", "5D", "1M", ...],
  "selectedTimeframe": "1D",
  "chartData": [...],
  "stats": {
    "open": "$121.00",
    "volume": "12.3M",
    "marketCap": "$55.4B",
    ...
  },
  "technical": {
    "position": "Bullish",
    "color": "success",
    "levels": {...}
  },
  "patterns": [...],
  "newsFilters": [...],
  "selectedSource": "all",
  "news": [...],
  "events": [...]
}
```

**Template Code**: Uses JSX syntax with `${company}`, `${symbol}`, etc.

#### Configuration B: ChatKit Components (NEW Approach)
**Agent Instructions**: Tell the agent to return ChatKit components:
```json
{
  "response_text": "Your natural language explanation",
  "query_intent": "news|economic_events|patterns|technical_levels|chart|comprehensive",
  "symbol": "EXTRACTED_TICKER_SYMBOL",
  "widgets": [
    {
      "type": "Card",
      "size": "lg",
      "status": {"text": "Live News", "icon": "newspaper"},
      "children": [
        {"type": "Title", "value": "[SYMBOL] Market News", "size": "lg"},
        {"type": "Divider", "spacing": 12},
        {"type": "ListView", "limit": 10, "children": [...]}
      ]
    }
  ]
}
```

**Component Types**: Card, Title, Divider, ListView, ListViewItem, Text, Caption, Badge, Row, Col, Box, Spacer, Button, Image

**Status**: 🔴 CRITICAL CONFLICT - Two incompatible approaches mixed

---

## Root Cause Analysis

### Problem 1: Widget Template vs ChatKit Components

**What's happening:**
- The widget template expects a fixed data schema (company, symbol, price, stats, etc.)
- The agent instructions tell it to construct ChatKit components (Card, Title, ListView, etc.)
- **These are mutually exclusive approaches!**

**Why it's a problem:**
- Widget templates require complete data objects matching specific schema
- ChatKit components are constructed by the agent using primitives
- The agent can't do both simultaneously

---

### Problem 2: Transform Node Data Loss

**What's happening:**
- Intent Classifier outputs: `intent`, `symbol`, `confidence`
- Transform node only maps: `intent`
- G'sves agent receives: ONLY `intent` field

**Why it's a problem:**
- The agent doesn't know which stock symbol the user asked about
- The agent can't determine confidence level
- The widget template needs the `symbol` field to display data

---

### Problem 3: Instruction Mismatch

**What's happening:**
- Agent instructions contain extensive ChatKit component examples
- These examples conflict with the widget template schema
- The agent gets confused about which format to use

**Why it's a problem:**
- Inconsistent output format
- Agent may try to follow instructions instead of template
- Unpredictable behavior

---

## Comparison: Widget Template vs ChatKit Components

| Aspect | Widget Template | ChatKit Components |
|--------|----------------|-------------------|
| **Data Format** | Fixed schema (company, symbol, price, stats) | Dynamic JSON (Card, Title, ListView) |
| **Agent Role** | Populate data fields | Construct UI components |
| **Flexibility** | Low - fixed template | High - agent decides structure |
| **Output Format** | Single data object | Array of widget objects |
| **Syntax** | JSX template with `${variables}` | JSON component tree |
| **Complexity** | Agent provides data | Agent designs UI |

**These approaches cannot coexist in the same agent configuration!**

---

## Recommended Fix Strategy

Based on user instruction: **"work from v56, to keep the widget file"**

### Step 1: Fix Transform Node ✅
Add missing field mappings:
```
Key: symbol      Value: input.output_parsed.symbol
Key: confidence  Value: input.output_parsed.confidence
```

### Step 2: Remove ChatKit Instructions from G'sves Agent ✅
**Remove all sections** containing:
- ChatKit component examples (Card, Title, ListView, etc.)
- Widget orchestration guidelines
- ChatKit component types list

**Keep**:
- Personality section
- Core capabilities
- Available tools
- Guardrails

### Step 3: Update G'sves Agent Instructions ✅
**Add new instructions** to generate widget template data:
```markdown
# Widget Template Output

You MUST return a JSON object matching this exact schema for the "GVSES stock card (fixed)" widget:

{
  "company": "Company name (e.g., 'Tesla, Inc.')",
  "symbol": "Stock ticker (e.g., 'TSLA')",
  "timestamp": "Updated [current date and time]",
  "price": {
    "current": "$XXX.XX",
    "changeLabel": "+X.XX (X.XX%)" or "-X.XX (X.XX%)",
    "changeColor": "success" or "danger",
    "afterHours": {...} // optional
  },
  "timeframes": ["1D", "5D", "1M", "3M", "6M", "1Y", "YTD", "MAX"],
  "selectedTimeframe": "1D",
  "chartData": [...],
  "stats": {...},
  "technical": {...},
  "patterns": [...],
  "news": [...],
  "events": [...]
}

Use the {{intent}} variable from the workflow to determine which sections to populate.
Use the {{symbol}} variable from the workflow to fetch stock data.
```

### Step 4: Verify Widget Template Compatibility ✅
Ensure the agent's output schema matches the widget template's required schema exactly.

### Step 5: Test in Preview Mode ✅
1. Switch to Preview mode
2. Test query: "What's TSLA trading at?"
3. Verify:
   - Transform node passes `intent`, `symbol`, `confidence`
   - G'sves agent receives all three fields
   - Agent generates widget template data (not ChatKit components)
   - Widget renders correctly

### Step 6: Publish as New Version ✅
1. Save changes as draft
2. Publish to production
3. Mark as production version

---

## Expected Data Flow (After Fix)

```
User: "What's TSLA trading at?"
  ↓
[Intent Classifier]
  Output: {"intent": "market_data", "symbol": "TSLA", "confidence": "high"}
  ↓
[Transform]
  Output: {"intent": "market_data", "symbol": "TSLA", "confidence": "high"}
  ↓
[G'sves Agent]
  Input: intent="market_data", symbol="TSLA", confidence="high"
  Uses tools: get_stock_quote("TSLA"), get_stock_history("TSLA")
  Output: Widget template data object with company, symbol, price, stats, etc.
  ↓
[Widget Template: GVSES stock card (fixed)]
  Renders: Beautiful stock card with price, charts, technical levels, news
```

---

## Technical Details

### Widget Template Schema (GVSES stock card (fixed))

**Full Schema Requirements**:
```typescript
{
  company: string,
  symbol: string,
  timestamp: string,
  price: {
    current: string,
    changeLabel: string,
    changeColor: "success" | "danger",
    afterHours?: {
      price: string,
      changeLabel: string,
      changeColor: "success" | "danger"
    }
  },
  timeframes: string[],
  selectedTimeframe: string,
  chartData: Array<{date: string, Close: number}>,
  stats: {
    open: string,
    volume: string,
    marketCap: string,
    dayLow: string,
    yearLow: string,
    eps: string,
    dayHigh: string,
    yearHigh: string,
    peRatio: string
  },
  technical: {
    position: string,
    color: string,
    levels: {
      sh: string,
      bl: string,
      now: string,
      btd: string
    }
  },
  patterns: Array<{
    id: string,
    name: string,
    confidence: string,
    direction: string,
    color: string
  }>,
  newsFilters: Array<{value: string, label: string}>,
  selectedSource: string,
  news: Array<{
    id: string,
    headline: string,
    source: string,
    timeAgo: string,
    color: string,
    url: string
  }>,
  events: Array<{
    id: string,
    name: string,
    date: string,
    countdown: string,
    color: string
  }>
}
```

### Transform Node CEL Expressions

**Required mappings**:
```
intent      → input.output_parsed.intent
symbol      → input.output_parsed.symbol
confidence  → input.output_parsed.confidence
```

**CEL Documentation**: Common Expression Language allows accessing nested fields with dot notation.

---

## Version Comparison

| Version | Widget Template | Instructions Match | Transform Fields | Status |
|---------|----------------|-------------------|------------------|--------|
| v56 | ✅ Attached | ❌ Mismatch | ❌ 1/3 fields | BROKEN |
| v60 | ❌ None | ❌ ChatKit only | Unknown | BROKEN (JSON output) |
| v61 | ❌ Detached | ✅ ChatKit | ✅ Pass-through | WRONG APPROACH |

**Correct Target**: v56 FIXED with widget template + matching instructions + complete Transform

---

## Questions for Investigation

1. **Why was ChatKit component approach added to widget template config?**
   - Was this intentional?
   - Is there a reason for mixing approaches?

2. **Why does Transform node only pass intent field?**
   - Was `symbol` and `confidence` intentionally dropped?
   - Or is this an incomplete configuration?

3. **What is the intended production approach?**
   - Widget templates (fixed schema)?
   - ChatKit components (dynamic construction)?
   - Need to choose ONE approach

---

## Next Steps

### Immediate Actions
1. ✅ Fix Transform node to pass all three fields
2. ✅ Remove ChatKit instructions from G'sves agent
3. ✅ Add widget template data generation instructions
4. ✅ Test in Preview mode
5. ✅ Publish corrected version

### Documentation
1. ✅ Create this investigation report
2. Document the correct widget template schema
3. Create testing checklist
4. Document the fixed workflow

### Validation
1. Test with various intents (market_data, news, technical, etc.)
2. Verify symbol extraction works correctly
3. Confirm widget renders with real data
4. Check all widget template fields populate correctly

---

## Related Documentation

- Widget Template: https://widgets.chatkit.studio/editor/33797fb9-0471-42cc-9aaf-8cf50139b909
- Agent Builder v60 Output Format Fix: AGENT_BUILDER_OUTPUT_FORMAT_FIX.md
- Agent Builder v60 Investigation: AGENT_BUILDER_V60_OUTPUT_FORMAT_INVESTIGATION.md
- ChatKit Widgets Complete: CHATKIT_WIDGETS_COMPLETE.md

---

## Conclusion

**Critical Issues Identified**:
1. 🔴 Widget template + ChatKit instructions conflict
2. 🔴 Transform node dropping `symbol` and `confidence` fields
3. 🔴 Agent confused about which output format to use

**Recommended Approach**:
- **Use widget template** (as user requested)
- **Remove conflicting ChatKit instructions**
- **Fix Transform node** to pass all data
- **Update agent instructions** to generate widget template data

**Severity**: HIGH - Workflow fundamentally broken
**Priority**: URGENT - Must fix before production deployment
**Effort**: MEDIUM - Requires careful configuration changes

**Outcome**: A working v56 workflow that uses the widget template correctly with proper data flow from Intent Classifier → Transform → G'sves → Widget Template rendering.
