# Phase 0 Findings: Widget Configuration Verification

**Date:** November 23, 2025
**Purpose:** Document actual widget configuration discovered in Agent Builder

---

## Critical Discoveries

### 1. Widget Metadata Wrapper NOT NEEDED ✅

**Finding:** The agent does NOT need to output widget metadata wrapper.

**Evidence:**
- Agent Builder "Output format" is set to "Widget"
- Widget selected: "GVSES stock card (fixed)"
- Agent instructions explicitly state: "Return ONLY the data JSON object - no additional wrapper"
- Agent instructions state: "Let the widget template handle visual rendering"

**Implication:** Agent Builder automatically wraps the agent's JSON output in widget metadata when Output format is set to "Widget". The agent only needs to return the pure data object.

**What This Means:**
- ❌ Agent does NOT output: `{"widget_id": "...", "widget_type": "...", "data": {...}}`
- ✅ Agent outputs: `{"company": "...", "symbol": "...", "chartData": [...]}`
- ✅ Agent Builder wraps it automatically

---

### 2. Widget ID Correction

**Previous assumption:** Widget ID is `wig_5cjvy39s`
**Actual widget:** "GVSES stock card (fixed)"
**Widget ID:** Unknown (not exposed in Agent Builder UI, handled internally)

**Why this matters:** We were looking for the wrong widget in ChatKit Studio. The actual widget being used is "GVSES stock card (fixed)".

---

### 3. Conflicting Instruction Found (LINE 835)

**Current instruction (WRONG):**
```markdown
chartData array (100+ historical data points from getStockHistory with OHLCV format...)
```

**Problem:** Says "100+ historical data points" which directly conflicts with 50-point limit requirement.

**Location:** Agent instructions, paragraph ref e835 (approximately line 835 in the instructions)

**Must be changed to:**
```markdown
chartData array (MAXIMUM 50 historical data points from getStockHistory with OHLCV format...)
```

---

## Impact on Implementation Strategy

### Original Plan (Based on Research)
1. Verify widget metadata format (Format A vs Format B)
2. Add widget wrapper to agent output
3. Add 50-point truncation enforcement
4. Frontend defensive validation

### Simplified Plan (Based on Actual Configuration)
1. ✅ **No widget wrapper needed** - Agent Builder handles this automatically
2. ✅ **Fix conflicting "100+" instruction** to "MAXIMUM 50"
3. ✅ **Add bookending enforcement** at start and end of instructions
4. ✅ **Frontend defensive validation** as safety net

**Time savings:** Eliminates need to figure out widget metadata format and modify agent to output wrapper.

---

## Updated Solution Implementation

### Phase 1: Modify Agent Instructions

**Step 1.1: Fix Conflicting Instruction (Line 835)**

**Find:**
```markdown
chartData array (100+ historical data points from getStockHistory...
```

**Replace with:**
```markdown
chartData array (**MAXIMUM 50 historical data points** - if getStockHistory returns more than 50 points, you MUST keep only the last 50 most recent data points...
```

**Step 1.2: Add Bookending Enforcement**

**At START of instructions (after "# 🎯 TOOL USAGE INSTRUCTIONS"):**
```markdown
# 🚨 CRITICAL REQUIREMENTS (ABSOLUTE)

**RULE 1: chartData MUST NEVER EXCEED 50 ENTRIES**

When processing getStockHistory responses:
1. Check array length: if chartData.length > 50
2. Keep ONLY the last 50 entries (most recent data)
3. Conceptually apply: chartData = chartData.slice(-50)
4. NEVER return more than 50 entries in chartData array

This is MANDATORY and NON-NEGOTIABLE.
```

**At END of instructions (after "CRITICAL FINAL REMINDERS"):**
```markdown
# 🚨 FINAL VERIFICATION CHECKPOINT

**BEFORE RETURNING YOUR JSON OUTPUT:**

## ✓ Verify chartData Length
1. Count chartData array length
2. If > 50: STOP and truncate to last 50 entries
3. NEVER proceed with chartData.length > 50

This is your FINAL check. Verify compliance NOW before output.
```

---

## Next Steps

1. Click "Edit" button on G'sves agent instructions
2. Apply Step 1.1: Fix line 835 conflict
3. Apply Step 1.2: Add bookending enforcement
4. Save changes
5. Test in Preview mode
6. Verify chartData.length ≤ 50

---

**Status:** Phase 0 Complete ✅
**Next Phase:** Phase 1 - Modify Agent Instructions
