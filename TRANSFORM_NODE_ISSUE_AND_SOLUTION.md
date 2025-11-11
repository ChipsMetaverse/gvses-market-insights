# Transform Node Configuration Issue & Solution

## Problem Summary

The Transform node in "Object" mode treats the "Value" fields as **literal strings**, not CEL expressions. This causes the output to be:
```json
{
  "output_text": "input.text",  // literal string!
  "chart_commands": "input.chart_commands"  // literal string!
}
```

Instead of evaluating to the actual values from the input.

---

## Root Cause

In Agent Builder's Transform node:
- **"Expressions" mode**: Values should be CEL expressions WITHOUT quotes
- **"Object" mode**: "Simple" editor treats Value field as static defaults for the AGENT to fill
- **"Object" mode**: "Advanced" editor with `"default"` field also generates static values

The Transform node is designed for AGENTS to generate structured JSON output matching a schema, NOT for passthrough/extraction of existing values from the workflow.

---

## CORRECT Solution: Remove Transform, Simplify Workflow

### Current Problematic Flow:
```
Chart Control Agent ──┐
                      ├──→ Transform (broken) ──→ End Node
G'sves ─────────────┘
```

### CORRECT Simple Flow:
```
Chart Control Agent ──→ End Node
G'sves ──────────────→ End Node
```

**BUT**: End node receiving TWO inputs causes ambiguity (outputs "undefined").

### ACTUAL BEST Solution:
```
If/else
  ├─→ Chart Control Agent ──→ End Node
  └─→ G'sves ──────────────→ End Node
```

**With Chart Control Agent output schema changed to match End node exactly:**

**Chart Control Agent current output schema:**
```json
{
  "text": "string",
  "chart_commands": ["array"]
}
```

**End node expects:**
```json
{
  "output_text": "string",
  "chart_commands": ["array"]
}
```

**SOLUTION**: Update Chart Control Agent output schema to use `output_text` instead of `text`:

```json
{
  "output_text": {
    "type": "string",
    "description": "Response text for user"
  },
  "chart_commands": {
    "type": "array",
    "items": { "type": "string" },
    "description": "Chart commands like ['LOAD:SYMBOL']"
  }
}
```

---

## Step-by-Step Fix

### 1. Delete Transform Node
- Click on the Transform node (between agents and End)
- Delete it

### 2. Update Chart Control Agent Output Schema
- Click on Chart Control Agent
- Click on the output schema
- Change field name from `text` to `output_text`
- Keep `chart_commands` as-is

### 3. Reconnect Edges
- Chart Control Agent → End Node (direct connection)
- G'sves → End Node (direct connection)

### 4. Update Chart Control Agent Instructions
Add to instructions:
```
CRITICAL: Your output MUST match this exact schema:
{
  "output_text": "Your response text here",
  "chart_commands": ["LOAD:SYMBOL"]
}

Note: Use "output_text" NOT "text" as the field name!
```

---

## Alternative: Keep Transform Node, Use Passthrough

If you want to keep the Transform node for clarity, configure it as a **passthrough** that simply forwards the entire input:

**Transform Configuration:**
- Mode: "Object"
- Delete all properties
- In Advanced JSON schema, use:

```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": true
}
```

This allows all fields to pass through unchanged.

---

## Why This is Complex

Agent Builder's Transform node has multiple modes:
1. **Expressions mode**: For extracting/calculating values using CEL
2. **Object mode (Simple)**: For AGENTS to generate structured outputs
3. **Object mode (Advanced)**: Same as Simple, but with JSON schema

None of these modes are designed for simple "map field A to field B" operations. They're designed for:
- Agents generating structured responses
- Extracting specific fields from complex nested objects  
- Calculating derived values

For simple field renaming (`text` → `output_text`), it's easier to just **update the Agent's output schema** to match the End node's expected schema.

---

## Recommended Immediate Action

1. **Delete the Transform node**
2. **Update Chart Control Agent** output schema: `text` → `output_text`
3. **Publish** as v35
4. **Test** in live app

This is the cleanest, simplest solution.

---

**Created**: 2025-11-04  
**Status**: Solution Identified  
**Action**: Delete Transform, Update Agent Schema, Republish

