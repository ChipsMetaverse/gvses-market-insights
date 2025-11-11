# Workflow Routing Fix - Implementation Plan

## Date: 2025-11-06 19:45 PST

## Confirmed Root Cause

**If/else "Market Data & Charts" output routes to G'sves instead of Chart Control Agent.**

### Evidence from Preview Test

```
Query: "Show me NVDA chart"

Execution Path:
1. ✅ Start
2. ✅ Intent Classifier
   → Output: {"intent":"chart_command","symbol":"NVDA","confidence":"high"}
3. ✅ Transform
4. ✅ If/else
   → Condition: input.intent in ["market_data", "chart_command"]
   → Evaluation: TRUE (matched "chart_command")
   → Output: "Market Data & Charts"
5. ❌ G'sves Agent (WRONG!)
   → Provides detailed price analysis
   → Does NOT call change_chart_symbol()
6. ✅ End

Chart Control Agent: ❌ NEVER EXECUTED
```

## Node IDs (from JavaScript inspection)

```javascript
{
  "node_yjmoc7ht": "If/else",
  "node_dwtcrmkh": "Chart Control Agent",
  "node_pwrg9arg": "G'sves"
}
```

## Current Edges from If/else

```javascript
{
  "node_yjmoc7ht-case-1": "node_dwtcrmkh",  // Chart Control Agent
  "node_yjmoc7ht-fallback": "node_pwrg9arg" // G'sves
}
```

## The Fix Strategy

Since Agent Builder's UI doesn't provide obvious controls to modify edge connections, I'll need to either:

### Option 1: Use JavaScript DOM manipulation
- Find the workflow data structure in the page
- Modify the edge connections programmatically
- Trigger a save/update

### Option 2: Delete and recreate nodes
- Delete the If/else node
- Recreate it with correct connections
- Republish

### Option 3: Export/Import workflow JSON
- Export the current workflow
- Edit the JSON to fix routing
- Import the corrected workflow

## Recommended Approach

**Create a new "Else if" case for "Market Data & Charts" that connects to Chart Control Agent**, ensuring the routing logic is correct.

The issue is likely that:
- case-0 (Educational Queries) → ???
- case-1 (currently labeled "Market Data & Charts") → Chart Control Agent BUT this is actually being bypassed
- fallback (Else) → G'sves (this is catching everything including chart_command!)

I need to verify which case is actually matching and reconnect accordingly.

## Status

- Root cause: ✅ CONFIRMED
- Fix strategy: ✅ IDENTIFIED
- Implementation: ⏳ IN PROGRESS
- Testing: ⏸️ PENDING
- Deployment: ⏸️ PENDING

## Next Steps

1. Switch to Code view
2. Inspect the If/else node configuration more closely
3. Determine exact routing issue
4. Implement fix (likely need to swap edge targets or recreate connections)
5. Publish v40
6. Test via Preview
7. Verify chart control works end-to-end
