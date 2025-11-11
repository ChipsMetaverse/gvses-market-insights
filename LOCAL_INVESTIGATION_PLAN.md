# 🔬 LOCAL INVESTIGATION PLAN

**Goal**: Debug why chart_commands aren't working without relying on production console.log

---

## 🎯 Core Issues to Investigate

### Issue 1: chart_commands Format
**Symptom**: Agent Builder returns `["LOAD"]` instead of `["LOAD:NVDA"]`
**Location**: Agent Builder End node output

### Issue 2: Debug Logging Not Working
**Symptom**: console.log statements stripped in production
**Root Cause**: Minification removes console.log

### Issue 3: Chart Not Switching
**Symptom**: Chart stays on TSLA instead of switching to NVDA
**Possible Causes**:
1. chart_commands truncated at source (Agent Builder)
2. chart_commands lost in transit (frontend parsing)
3. chart_commands not being executed (enhancedChartControl)

---

## 🔍 Investigation Strategy

### Step 1: Verify Agent Builder Output Format
Instead of debugging via console.log, let's check the **actual Agent Builder workflow configuration** directly.

**Questions to Answer**:
1. What is the Chart Control Agent's MCP tool returning?
2. What is the End node's field mapping configuration?
3. Is the End node correctly extracting `chart_commands` from the Chart Control Agent?

### Step 2: Add Alternative Logging Mechanism
Since console.log is being stripped, use:
1. **Network tab inspection** - Check the actual HTTP response from Agent Builder
2. **DOM manipulation** - Add visible debug output to the page
3. **Alert statements** - Temporary visual debugging
4. **LocalStorage logging** - Persist debug data

### Step 3: Test Locally
Run the frontend locally with dev server (no minification) to see the full debug output.

---

## 🛠️ Proposed Fix Strategy

### Fix 1: Add Visual Debug Output (Production-Safe)
Add a debug panel to the UI that shows:
- Last received chart_commands
- Last agent message data
- Current chart symbol

This will work even with minification.

### Fix 2: Check Agent Builder Configuration
Use Playwright MCP to inspect the End node's actual configuration and verify the field mappings are correct.

### Fix 3: Test Local Dev Build
Run `npm run dev` locally and test the chat interaction to see full debug output.

---

## 📋 Action Items

1. ✅ Read the End node configuration from Agent Builder
2. ✅ Check the Chart Control Agent's output format
3. ✅ Add visual debug panel to frontend (production-safe)
4. ✅ Deploy and test with visual debugging
5. ✅ Fix root cause based on findings

---

## 🎬 Let's Start!

