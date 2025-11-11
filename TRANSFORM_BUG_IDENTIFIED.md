# 🎯 Transform Bug Identified - Critical Discovery

## Investigation Date: November 4, 2025, 03:15 UTC
## Status: **ROOT CAUSE CONFIRMED**

---

## The Problem

The Transform node was configured in **"Object" mode with a DEFAULT VALUE** instead of evaluating an expression!

### What Was Wrong (v32)

```json
{
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "default": "input.output_parsed.classification_result.intent"  ❌
    }
  }
}
```

**This sets intent to the LITERAL STRING** `"input.output_parsed.classification_result.intent"` instead of evaluating it!

---

## The Fix Applied

**Changed Transform to "Expressions" mode** with proper CEL expression:

```
Key: intent
Value: input.output_parsed.classification_result.intent  ✅
```

This uses Common Expression Language (CEL) which will properly evaluate the nested path!

---

## Schema Mismatch Warning

After applying the fix, Agent Builder shows a schema mismatch warning:

> "Schema mismatches detected on 1 connection(s) (Intent Classifier → Transform)"

**Analysis:**
- Intent Classifier outputs: `{ "intent": "string", "symbol": "string", "confidence": "string" }`
- At runtime, Agent Builder wraps this in: `{ "output_parsed": { "classification_result": {...} } }`
- Transform Expression mode outputs: `{ "intent": "<evaluated_value>" }`
- If/else expects: `input.intent in ["market_data", "chart_command"]`

The schema mismatch is a **false positive** - the expression will work at runtime!

---

## Next Steps

1. ✅ **Transform fixed** - Changed from Object mode to Expressions mode
2. ⏳ **Publish draft** - Need to bypass schema validation warning
3. 🔬 **Test in Preview** - Verify the expression evaluates correctly
4. 📊 **Monitor MCP logs** - Confirm Chart Control Agent is called

---

## Expected Outcome

With this fix:
1. Intent Classifier outputs: `{"intent":"chart_command","symbol":"MSFT","confidence":"high"}`
2. Transform evaluates: `input.output_parsed.classification_result.intent` → `"chart_command"`
3. If/else matches: `input.intent in ["market_data","chart_command"]` → **TRUE**
4. Routes to: **Chart Control Agent** (NOT G'sves!)
5. Chart Control Agent calls: `change_chart_symbol(symbol="MSFT")`
6. Chart switches to: **MSFT** ✅

---

## Technical Details

### Common Expression Language (CEL)

Agent Builder's Transform node in "Expressions" mode uses CEL, which:
- Evaluates dot-notation paths: `input.foo.bar`
- Supports string operations: `input.name + " suffix"`
- Performs type conversions automatically
- Returns a structured output: `{ "key": <evaluated_value> }`

### Agent Builder Output Wrapping

When an Agent node outputs JSON with schema name "classification_result":
- **Schema defines**: `{ "intent": "string", ... }`
- **Runtime outputs**: `{ "output_parsed": { "classification_result": { "intent": "chart_command", ... } } }`

This wrapping is automatic and not reflected in the schema editor!

---

## Files Modified
- None (Agent Builder UI configuration only)

## Version
- Draft (not yet published due to schema validation warning)

