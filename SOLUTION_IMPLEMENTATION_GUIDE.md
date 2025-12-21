# Solution Implementation Guide: Fixing G'sves Agent Widget Rendering

**Purpose:** Step-by-step guide for implementing chartData truncation and widget metadata wrapping
**Based on:** Comprehensive tech stack research (Nov 23, 2025)
**Approach:** Multi-layered defense using proven techniques

---

## Executive Summary

### The Problem

1. **chartData Exceeding Limit**: Agent returns 104 entries (target: max 50)
2. **Widget Not Rendering**: Missing metadata wrapper structure
3. **Conflicting Instructions**: Line 683 says "30-50 points", contradicting enforcement

### The Solution

**Multi-layered approach** using proven techniques:

| Layer | Mechanism | Reliability |
|-------|-----------|-------------|
| 1 | System prompt bookending | 95-99% |
| 2 | Conflict resolution (line 683) | Essential |
| 3 | Natural language Transform | 90-95% |
| 4 | Token budget limit (optional) | 100% (hard limit) |
| 5 | Frontend defensive validation | 100% (safety net) |

---

## Prerequisites

### Required Access

- [ ] OpenAI Agent Builder (to modify G'sves agent)
- [ ] Playwright MCP (to automate Agent Builder modifications)
- [ ] ChatKit Studio (to inspect widget configuration)
- [ ] Frontend codebase (for defensive validation)

### Required Information

**Before proceeding, we need:**
1. ✅ G'sves agent workflow ID
2. ⚠️ Actual widget metadata format (need to verify in ChatKit Studio)
3. ✅ Current agent instructions (have access)

---

## Phase 0: Verify Widget Configuration

### Why This First?

We have **conflicting information** about widget metadata format:

**Format A:**
```json
{
  "widget_id": "wig_5cjvy39s",
  "widget_type": "stock-card",
  "data": {...}
}
```

**Format B:**
```json
{
  "widget": {
    "id": "wig_5cjvy39s",
    "type": "stock-card"
  },
  "data": {...}
}
```

### Action: Inspect Widget in ChatKit Studio

**Step 1: Navigate to Widget**
```bash
# Use Playwright to navigate to ChatKit Studio
# URL: widgets.chatkit.studio or platform.openai.com/chatkit-studio
```

**Step 2: Find Widget `wig_5cjvy39s`**
- Search by ID or name
- Open configuration
- View schema/structure definition

**Step 3: Document Exact Format**
- Record required metadata structure
- Note all required data fields
- Capture example output if available

**Decision Point:**
- [ ] Format A confirmed → Proceed with Format A
- [ ] Format B confirmed → Proceed with Format B
- [ ] Different format → Document and adapt

**⏸️ PAUSE HERE until widget format verified**

---

## Phase 1: Modify G'sves Agent Instructions

### Estimated Time: 15 minutes

### Step 1.1: Remove Conflicting Instructions (CRITICAL)

**Location:** Line 683 (approximately)

**Current (CONFLICTING):**
```markdown
- `chartData` array (30-50 historical data points from getStockHistory...
```

**Replace with:**
```markdown
- `chartData` array (**STRICTLY LIMITED to MAXIMUM 50 entries** - if you receive more than 50 data points from getStockHistory, you MUST keep only the last 50 most recent data points using conceptual array truncation...
```

**Why:** Eliminates conflict between "30-50" range and "MAXIMUM 50" requirement

**Implementation:**
```python
# Use Playwright MCP to navigate to Agent Builder
# Open G'sves agent instructions
# Find line 683
# Use Edit tool to replace text
```

---

### Step 1.2: Add Enforcement at START of Instructions

**Location:** After initial role definition (around line 342)

**Add:**
```markdown
# 🚨 ABSOLUTE REQUIREMENTS (NON-NEGOTIABLE)

**RULE 1: chartData ARRAY LENGTH**
You MUST limit chartData to MAXIMUM 50 entries. This is MANDATORY.

When processing data from getStockHistory:
1. Check if chartData.length > 50
2. If yes: Keep ONLY the LAST 50 points (most recent data)
3. NEVER return more than 50 entries in your final output
4. Conceptually apply: chartData = chartData.slice(-50)

**RULE 2: Widget Metadata Wrapper**
Your ENTIRE response MUST be wrapped in widget metadata format:

[INSERT VERIFIED FORMAT FROM PHASE 0 HERE]

Example:
{
  "widget_id": "wig_5cjvy39s",
  "widget_type": "stock-card",
  "data": {
    "company": "Apple Inc.",
    "symbol": "AAPL",
    "chartData": [...],  // MAX 50 entries
    ...
  }
}

These requirements are NON-NEGOTIABLE and apply to EVERY response.
```

---

### Step 1.3: Add Enforcement at END of Instructions

**Location:** Create or find "CRITICAL FINAL REMINDERS" section at end

**Add:**
```markdown
# 🚨 FINAL ENFORCEMENT CHECKPOINT

**BEFORE RETURNING YOUR RESPONSE**, verify:

## ✓ chartData Length Check
1. Count the chartData array length
2. If chartData.length > 50:
   - STOP and truncate to last 50 entries
   - Keep ONLY the most recent data points
   - Use conceptual logic: chartData.slice(-50)
3. NEVER return responses with chartData.length > 50

## ✓ Widget Metadata Wrapper Check
1. Verify your response structure starts with:
   ```json
   {
     "widget_id": "wig_5cjvy39s",
     "widget_type": "stock-card",
     "data": { ... }
   }
   ```
2. NEVER return unwrapped JSON like:
   ```json
   {
     "company": "...",
     "symbol": "..."
   }
   ```

**These are your FINAL checks before output.**
Re-verify compliance now.
```

**Why Bookending Works:**
- Models give higher attention to START (primacy bias)
- Models give higher attention to END (recency bias)
- Double reinforcement dramatically improves compliance

---

### Step 1.4: Update ALL Example Outputs

**Find:** Every JSON example in instructions showing output format

**Current (WRONG):**
```json
{
  "company": "Apple Inc.",
  "symbol": "AAPL",
  ...
}
```

**Replace with (CORRECT):**
```json
{
  "widget_id": "wig_5cjvy39s",
  "widget_type": "stock-card",
  "data": {
    "company": "Apple Inc.",
    "symbol": "AAPL",
    "chartData": [
      // Show exactly 3-5 example entries here
      // Add comment: "... (maximum 50 entries total)"
    ],
    ...
  }
}
```

**Why:** Models learn from examples more effectively than prose descriptions

---

### Step 1.5: Add Explicit Truncation Logic

**Location:** In tool usage instructions for getStockHistory

**Add:**
```markdown
### Using getStockHistory Tool

**MANDATORY POST-PROCESSING:**
After receiving data from getStockHistory, you MUST apply this logic:

```
// Conceptual code - apply this logic:
let chartData = getStockHistory_response;

if (chartData.length > 50) {
    // Keep only the last 50 (most recent) entries
    chartData = chartData.slice(-50);
}

// Verify: chartData.length should now be ≤ 50
```

This truncation is REQUIRED before including data in your response.

**CRITICAL:** Always use the MOST RECENT data (last 50 points), not the first 50.
```

---

### Step 1.6: Save and Test in Preview Mode

**Save Changes:**
```python
# In Agent Builder
# Click "Save" button
# Verify changes persisted
```

**Test in Preview:**
```python
# Switch to Preview mode
# Submit query: "show me AAPL"
# Wait for completion
# Examine output structure
```

**Validate:**
- [ ] Widget metadata wrapper present?
- [ ] chartData.length ≤ 50?
- [ ] All required fields populated?

**If test fails:**
- Review error messages
- Check instruction modifications
- Verify no syntax errors in instructions
- Re-test

---

## Phase 2: Add Transform Node (Optional Enhancement)

### When to Use This

If system prompt approach alone doesn't achieve >95% compliance

### Implementation

**Step 2.1: Add Transform Node**

**Location:** Between G'sves agent and output

**Configuration:**
```
Input: stock_data from G'sves agent
Output: truncated_stock_data

Instruction:
"Take the input stock data object. Check if chartData array has more
than 50 entries. If it does, keep only the last 50 most recent entries.
Return the modified stock data object with truncated chartData array."
```

**Step 2.2: Connect to Workflow**

```
G'sves Agent → Transform Node → End Node
```

**Why:** Adds additional defense layer if prompt compliance isn't 100%

---

## Phase 3: Frontend Defensive Validation

### Estimated Time: 5 minutes

### Implementation

**File:** `frontend/src/components/widget/parser.ts` (or equivalent)

**Add:**
```typescript
/**
 * Parse and validate stock widget data
 * Defensive validation ensures chartData never exceeds limits
 */
function parseStockWidgetData(response: any) {
  // Defensive chartData truncation
  if (response.data && response.data.chartData) {
    const originalLength = response.data.chartData.length;

    if (originalLength > 50) {
      console.warn(
        `[Widget Parser] Truncating chartData from ${originalLength} to 50 points. ` +
        `Agent instructions may need updating.`
      );

      // Keep last 50 (most recent) entries
      response.data.chartData = response.data.chartData.slice(-50);
    }
  }

  // Validate widget metadata (for monitoring)
  if (!response.widget_id && !response.widget) {
    console.error(
      '[Widget Parser] Widget metadata wrapper missing. ' +
      'Agent instructions may need updating.'
    );
  }

  return response;
}

// Use in widget rendering pipeline
export function renderStockWidget(rawResponse: any) {
  const validatedData = parseStockWidgetData(rawResponse);
  // ... continue with rendering
}
```

**Why:**
- **Safety net** catches any cases that slip through agent
- **Monitoring** logs when truncation occurs
- **Production resilience** prevents widget rendering failures

---

## Phase 4: Set Token Budget (Optional)

### When to Use This

For absolute guarantee that output cannot exceed physical limits

### Calculation

```
Each chartData entry ≈ 200 tokens (estimated)
50 entries = 10,000 tokens
Widget metadata wrapper ≈ 1,000 tokens
Other fields (stats, news, etc.) ≈ 3,000 tokens
Safety margin ≈ 2,000 tokens

Total: 16,000 tokens
```

### Implementation

**In Agent Node Configuration:**
```
max_completion_tokens = 16000
```

**Trade-off:**
- ✅ Hard guarantee against excessive output
- ⚠️ May truncate legitimate content if budget too tight
- ⚠️ Requires careful calibration

**Recommendation:** Start without token limits, add only if needed

---

## Testing and Validation

### Test Cases

**Test 1: Normal Query**
```
Query: "show me AAPL"
Expected:
- chartData.length ≤ 50 ✓
- Widget metadata present ✓
- Widget renders correctly ✓
```

**Test 2: Edge Case**
```
Query: "show me TSLA with maximum detail"
Expected:
- Agent still respects 50-point limit ✓
- No attempt to bypass constraints ✓
```

**Test 3: Multiple Symbols**
```
Query: "show me AAPL, GOOGL, MSFT"
Expected:
- Each response has ≤50 chartData points ✓
```

### Validation Checklist

**Agent Output:**
- [ ] Widget metadata wrapper present
- [ ] widget_id = "wig_5cjvy39s"
- [ ] widget_type = "stock-card"
- [ ] chartData exists and is array
- [ ] chartData.length ≤ 50
- [ ] All required fields populated

**Widget Rendering:**
- [ ] Visual stock card displays (not raw JSON)
- [ ] Chart renders with candlesticks
- [ ] Stats grid populated
- [ ] No console errors

**Performance:**
- [ ] Response time acceptable
- [ ] Token consumption reasonable
- [ ] No degradation in quality

---

## Monitoring and Optimization

### Metrics to Track

**Compliance Metrics:**
```javascript
// Log chartData lengths
console.log('chartData length:', response.data.chartData.length);

// Track truncation occurrences
if (originalLength > 50) {
  metrics.increment('widget.chartData.truncated');
}

// Track metadata wrapper presence
if (!response.widget_id) {
  metrics.increment('widget.metadata.missing');
}
```

**Quality Metrics:**
- Widget rendering success rate
- User engagement with widgets
- Error rates

### Optimization Opportunities

**If compliance < 95%:**
1. Review agent instructions for clarity
2. Add more examples
3. Strengthen enforcement language
4. Consider Transform node addition

**If quality declining:**
1. Check if 50-point limit too aggressive
2. Review which data points being kept
3. Adjust to keep most relevant data

**If performance issues:**
1. Review token consumption
2. Consider smaller data payloads
3. Optimize widget rendering

---

## Rollback Plan

### If Changes Cause Issues

**Step 1: Revert to Previous Version**
```
In Agent Builder:
- View version history
- Select previous working version
- Publish that version
```

**Step 2: Frontend Rollback**
```git
git revert <commit-hash>
git push
```

**Step 3: Document Issues**
- What went wrong?
- Which approach failed?
- What error messages occurred?

**Step 4: Revise Strategy**
- Consult TECH_STACK_LIMITATIONS.md
- Try alternative approaches
- Test more thoroughly before deployment

---

## Success Criteria

### Phase 1 Success (Minimum Viable)

- [ ] chartData length ≤ 50 in 95%+ of responses
- [ ] Widget metadata wrapper present in 95%+ of responses
- [ ] No conflicting instructions in agent prompt
- [ ] Widget renders correctly in production

### Phase 2 Success (Optimal)

- [ ] chartData length ≤ 50 in 99%+ of responses
- [ ] Widget metadata wrapper present in 99%+ of responses
- [ ] Transform node providing additional safety
- [ ] Frontend validation as final safety net
- [ ] Monitoring and metrics in place

---

## Next Steps After Implementation

1. **Monitor production for 1 week**
   - Track compliance metrics
   - Collect user feedback
   - Identify edge cases

2. **Optimize based on data**
   - Adjust constraints if needed
   - Refine instructions
   - Update documentation

3. **Document learnings**
   - Update this guide with findings
   - Share insights with team
   - Improve process for future agents

---

## Appendix A: Quick Reference

### Agent Instruction Modifications

| Location | Change | Purpose |
|----------|--------|---------|
| Line 683 | Remove "30-50" conflict | Eliminate contradiction |
| Line ~342 | Add ABSOLUTE REQUIREMENTS | Primacy enforcement |
| End of file | Add FINAL CHECKPOINT | Recency enforcement |
| Tool instructions | Add truncation logic | Explicit guidance |
| All examples | Add widget wrapper | Learning from examples |

### Validation Commands

```bash
# Test Agent Builder in Preview
# Navigate to Preview mode
# Submit: "show me AAPL"
# Check output structure

# Test frontend locally
npm run dev
# Open browser
# Test widget rendering
```

---

**Remember:** This is a multi-layered approach. No single mechanism provides 100% reliability. The combination creates robust protection.

**Last Updated:** November 23, 2025
