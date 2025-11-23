# Remaining Work Investigation - Agent Builder ChatKit Fix

## Investigation Date: Nov 17, 2025

## Current State Analysis

### ✅ **What's Already Correct**

1. **Widget Template Attached**: "GVSES stock card (fixed)" template is properly attached to G'sves agent (ref=e643)
2. **Output Format**: Set to "Widget" (ref=e636) - correct for template-based rendering
3. **Tools Configured**: Both GVSES_Market_Data_Server and GVSES Trading Knowledge Base are connected (ref=e610)
4. **Transform Node**: FIXED (previous session) - Now passes all three fields:
   - `intent` ← `input.output_parsed.intent` ✅
   - `symbol` ← `input.output_parsed.symbol` ✅
   - `confidence` ← `input.output_parsed.confidence` ✅

### ❌ **What Needs to Be Fixed**

#### 1. Agent Instructions (CRITICAL - In Progress)

**Current Instructions Problem**:
- Contains massive "# WIDGET ORCHESTRATION" section (ref=e343 onwards)
- Tells agent to output **component JSON**: `{"widgets": [{"type": "Card", "children": [...]}]}`
- Includes extensive ChatKit component examples (Card, ListView, Badge, Title, Image, Box, Row)
- This conflicts with the attached widget template which expects **data JSON**

**Correct Instructions** (in `CORRECT_GVSES_INSTRUCTIONS.md`):
- Contains "# WIDGET TEMPLATE OUTPUT" section
- Tells agent to output **data JSON**: `{"company": "...", "symbol": "...", "price": {...}, "stats": {...}}`
- Documents the complete data schema matching the widget template
- Explains how to use workflow variables: `{{intent}}`, `{{symbol}}`, `{{confidence}}`
- Provides intent-based population guidelines (market_data, news, technical, chart, comprehensive)

**Key Differences**:
```diff
- ## Widget Response Format
- ALWAYS return your response in this JSON structure:
- {
-   "response_text": "Your natural language explanation",
-   "query_intent": "news|economic_events|...",
-   "symbol": "EXTRACTED_TICKER_SYMBOL",
-   "widgets": [{"type": "Card", "size": "lg", "children": [...]}]
- }

+ ## Required Output Schema
+ {
+   "company": "Full company name",
+   "symbol": "Stock ticker from {{symbol}} workflow variable",
+   "timestamp": "Updated [current date and time]",
+   "price": {"current": "$XXX.XX", "changeLabel": "...", "changeColor": "..."},
+   "stats": {...},
+   "technical": {...},
+   "patterns": [...],
+   "news": [...],
+   "events": [...]
+ }
```

---

## Remaining Work Breakdown

### 🔴 **Task 1: Replace Agent Instructions** (CRITICAL - Currently Working)

**Status**: In Progress
**Complexity**: Simple (copy/paste operation)
**Impact**: HIGH - This is the root cause of the widget not rendering

**Steps**:
1. ✅ Navigate to Agent Builder v56 draft
2. ✅ Click on G'sves agent node
3. ✅ Located instructions editor (contenteditable TipTap field at ref=e289)
4. ⏳ Select all current instructions
5. ⏳ Replace with content from `CORRECT_GVSES_INSTRUCTIONS.md`
6. ⏳ Save changes

**Technical Details**:
- Instructions field is a TipTap/ProseMirror rich text editor
- Located at: `div[contenteditable="true"].tiptap.ProseMirror`
- Can be edited via Playwright browser_run_code with focus + keyboard commands

---

### 🟡 **Task 2: Test in Agent Builder Preview Mode** (Next)

**Status**: Pending
**Complexity**: Simple (5-10 minutes)
**Impact**: HIGH - Validates the fix works

**Steps**:
1. Switch to Preview mode (ref=e35)
2. Test query: "What's TSLA trading at?"
3. Verify agent outputs **data JSON** (not component JSON)
4. Check all required fields are present:
   - ✅ company, symbol, timestamp
   - ✅ price object with current, changeLabel, changeColor
   - ✅ stats object with open, volume, marketCap, etc.
   - ✅ technical object with position, color, levels
   - ✅ patterns array
   - ✅ news array
   - ✅ events array

**Success Criteria**:
- Agent returns JSON matching the data schema
- No `{"widgets": [...]}` structure in response
- All workflow variables ({{intent}}, {{symbol}}, {{confidence}}) are used correctly

---

### 🟢 **Task 3: Frontend Cleanup** (Optional but Recommended)

**Status**: Pending
**Complexity**: Medium (30-60 minutes)
**Impact**: LOW - Frontend already has ChatKit component, manual rendering not needed

**Files to Update**:

#### A. `frontend/src/components/RealtimeChatKit.tsx` (557 lines)
**Remove** (Lines 168-177):
```typescript
const parsedResponse = parseAgentResponse(message.content);
if (parsedResponse.hasWidgets && parsedResponse.parsedResponse?.widgets) {
  console.log('[ChatKit] ✅ Detected ChatKit widgets:', parsedResponse.parsedResponse.widgets);
  setChatKitWidgets(parsedResponse.parsedResponse.widgets);
  if (parsedResponse.displayText) {
    displayContent = parsedResponse.displayText;
  }
}
```

**Replace with**:
```typescript
// Trust ChatKit component to display template-rendered widgets
// No manual widget parsing needed when using Agent Builder templates
```

#### B. `frontend/src/utils/widgetParser.ts` (158 lines)
**Action**: DELETE FILE (or keep for reference but don't use)
**Reason**: Expects component JSON structure, not needed for template-based widgets

#### C. `frontend/src/components/ChatKitWidgetRenderer.tsx` (508 lines)
**Action**: DELETE FILE (or keep for reference but don't use)
**Reason**: 500+ lines of manual widget rendering logic, not needed when ChatKit handles rendering

**Why This is Optional**:
- Frontend has `@openai/chatkit-react` SDK installed (package.json line 18)
- The `<ChatKit>` component should automatically display template-rendered widgets
- Manual parsing/rendering is redundant when using templates
- Leaving these files won't break anything, just adds unnecessary code

---

### 🟢 **Task 4: End-to-End Testing** (Final Step)

**Status**: Pending
**Complexity**: Simple (10-15 minutes)
**Impact**: HIGH - Confirms everything works in production

**Test Scenarios**:

1. **Market Data Intent**:
   - Query: "What's TSLA trading at?"
   - Expected: Stock card with price, stats, technical levels

2. **News Intent**:
   - Query: "Show me Tesla news"
   - Expected: Stock card with news section populated

3. **Technical Intent**:
   - Query: "Give me NVDA technical levels"
   - Expected: Stock card with technical section emphasized

4. **Chart Intent**:
   - Query: "Show me Apple chart"
   - Expected: Stock card with chartData populated

5. **Comprehensive Intent**:
   - Query: "Give me complete MSFT analysis"
   - Expected: Stock card with ALL sections fully populated

**Success Criteria**:
- Widget renders in ChatKit component
- All sections display correctly based on intent
- Real market data is shown (not placeholder text)
- No console errors in browser DevTools

---

## Technical Root Cause Summary

**The Problem**:
```
Agent Builder Template (Approach A)    ←  MISMATCH  →    Frontend Expectations (Approach B)
↓                                                                      ↓
Expects: Data JSON                                        Expects: Component JSON
{                                                         {
  "company": "Tesla, Inc.",                                 "widgets": [{
  "symbol": "TSLA",                                           "type": "Card",
  "price": {...}                                              "children": [...]
}                                                           }]
                                                          }
```

**The Solution**:
1. Update agent instructions → Tell it to output data JSON (not component JSON)
2. Trust the template → Template applies data to JSX automatically
3. Trust ChatKit SDK → `<ChatKit>` component displays rendered widgets
4. Remove manual logic → No need for widgetParser or ChatKitWidgetRenderer

---

## Next Immediate Action

**Focus on Task 1**: Replace the G'sves agent instructions in Agent Builder.

**File Ready**: `/Volumes/WD My Passport 264F Media/claude-voice-mcp/CORRECT_GVSES_INSTRUCTIONS.md`

**Technical Approach**:
1. Use Playwright to focus on contenteditable instructions field
2. Select all text (Cmd+A)
3. Delete (Backspace or Delete key)
4. Paste new instructions from file
5. Click outside field to auto-save

**Estimated Time**: 5 minutes
