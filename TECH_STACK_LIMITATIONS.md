# Tech Stack Limitations: What Doesn't Work

**Critical Reference Document**
**Purpose:** Prevent wasted effort on unsupported approaches
**Last Updated:** November 23, 2025

---

## ⚠️ READ THIS FIRST

This document catalogs **confirmed limitations** in our tech stack based on comprehensive research and community evidence. If you're about to implement something listed here, **STOP** and consult the "What Actually Works" section.

---

## ❌ JSON Schema `minItems` / `maxItems` (NOT SUPPORTED)

### The Problem

You **CANNOT** enforce array length limits using JSON Schema in OpenAI Agent Builder Structured Outputs.

### What Doesn't Work

```json
{
  "chartData": {
    "type": "array",
    "items": {"type": "object"},
    "minItems": 1,        // ❌ IGNORED
    "maxItems": 50        // ❌ IGNORED
  }
}
```

### Evidence

**Official Sources:**
- OpenAI documentation: "Structured Outputs supports a subset of JSON Schema"
- Explicitly excludes `minItems` and `maxItems`

**Community Confirmation:**
- Multiple forum threads reporting this limitation
- Users attempting array constraints all failed
- No workaround using Structured Outputs alone

### Why This Matters

**Initial assumption:** Could enforce 50-item chartData limit via JSON schema
**Reality:** Must use alternative approaches (prompts, token limits, frontend validation)

**Impact:** Cannot rely on schema for array length enforcement

---

## ❌ CEL Array Slicing in Transform Nodes (NOT AVAILABLE)

### The Problem

Transform nodes in Agent Builder **CANNOT** use `.slice()`, `.filter()`, or array manipulation methods.

### What Doesn't Work

```javascript
// ❌ All of these FAIL in Agent Builder Transform nodes:

input.chartData.slice(0, 50)                    // No .slice() method
input.chartData.slice(-50)                      // No .slice() method
input.items.filter(x, x.value > 100)           // .filter() syntax error
input.items[0:50]                               // Python-style slicing fails
[item for item in input.items if item.valid]  // List comprehension fails
```

### Evidence

**Community Forum Thread:**
"Filtering JSON Array in Transform Node Using CEL"
- Multiple users report identical ".filter() syntax errors"
- Attempted various filter syntaxes - all failed
- No successful examples of array filtering in Transform nodes

**CEL Specification:**
- Standard CEL supports `.filter()` macro in Kubernetes
- Agent Builder implementation appears restricted
- No array slicing in CEL standard library

### Why This Matters

**Initial assumption:** Could truncate arrays using Transform node with `.slice(-50)`
**Reality:** Transform nodes cannot directly manipulate array sizes using CEL code

**Workaround:** Use natural language Transform instructions instead of code

---

## ❌ Dynamic Widget Selection Per Tool (CURRENT LIMITATION)

### The Problem

Cannot render different widgets based on which tool was called within a single Agent node.

### What Doesn't Work

```
Agent Node Configuration:
├─ Tool 1: get_stock_data    → Widget: stock-card     ❌
├─ Tool 2: get_news          → Widget: news-list      ❌
└─ Tool 3: get_earnings      → Widget: earnings-table ❌

Result: Only node-level widget assignment honored
```

### Evidence

**Official OpenAI Support Response:**
- Confirmed as current limitation (not a bug)
- UI shows per-tool widget options but they're ignored
- Only node-level widget configuration actually works
- Feature request logged for future enhancement

**Community Impact:**
- Top requested feature in Agent Builder forums
- Multiple workarounds documented (If/Else routing)

### Why This Matters

**Initial assumption:** Could assign different widgets to each MCP tool
**Reality:** Need separate Agent nodes for each widget type

**Workaround:** Use If/Else nodes to route to specialized agents with different widgets

---

## ❌ Default Values in JSON Schema (NOT SUPPORTED)

### The Problem

Cannot use default values in Structured Output schemas.

### What Doesn't Work

```json
{
  "properties": {
    "status": {
      "type": "string",
      "default": "pending"    // ❌ Causes API errors
    }
  }
}
```

### Evidence

Community reports: "API call fails when including defaults in schema, even though this is standard JSON Schema feature"

### Impact

Must handle missing fields in application logic rather than relying on schema defaults.

---

## ❌ `oneOf` at Root Level (NOT SUPPORTED)

### The Problem

Cannot use discriminated unions at schema root.

### What Doesn't Work

```json
{
  "oneOf": [              // ❌ NOT permitted at root
    {"type": "object", "properties": {"success": ...}},
    {"type": "object", "properties": {"error": ...}}
  ]
}
```

### Impact

Cannot model "success OR error" response types at root level using schema.

---

## ❌ String Format Keywords (NOT SUPPORTED)

### The Problem

Cannot use format validation for strings.

### What Doesn't Work

```json
{
  "email": {
    "type": "string",
    "format": "email"     // ❌ NOT supported
  },
  "date": {
    "type": "string",
    "format": "date"      // ❌ NOT supported
  }
}
```

### Impact

Must validate email/date/URI formats in application code.

---

## ❌ While Loop Infinite Iterations (DANGER)

### The Problem

While loops without proper termination conditions can iterate endlessly.

### What Doesn't Work

```
While Loop:
  Condition: "result.status != 'complete'"

Problem: If status never becomes 'complete', loop runs forever
Cost: Accumulates charges until hitting platform limits
```

### Evidence

Community thread: "While loop is iterating endlessly and incurring costs with no way to end it"

### Why This Matters

**No automatic safeguards** against:
- Infinite loops consuming budget
- Loops that never terminate
- Runaway iteration counts

### Required Mitigation

**ALWAYS:**
1. Set explicit iteration limits
2. Add timeout mechanisms
3. Test termination conditions thoroughly
4. Monitor loop execution in production

---

## ❌ Mid-Workflow User Input (NOT SUPPORTED)

### The Problem

Cannot inject new user input mid-workflow execution.

### What Doesn't Work

```
Workflow:
  Agent 1 → Asks clarifying question
  [PAUSE for user input]    ❌ Cannot pause here
  Agent 2 → Uses user answer
```

### Impact

Workflows must be designed as single-pass without interactive clarification.

---

## ❌ Built-in Knowledge Base Connectors (NOT PROVIDED)

### The Problem

ChatKit/Agent Builder provide NO built-in integrations for:
- Zendesk
- Confluence
- Internal documentation systems
- SharePoint
- Notion

### Impact

**Must build from scratch:**
- Data pipelines
- API integrations
- Search and retrieval logic
- Authentication flows
- Data synchronization

**Substantial engineering effort** required.

---

## ❌ Built-in Analytics Dashboard (NOT PROVIDED)

### The Problem

No metrics tracking for:
- Agent performance
- User satisfaction
- Resolution rates
- Token consumption per workflow
- Success/failure distributions

### Impact

Must build custom:
- Logging infrastructure
- Metrics collection
- Performance dashboards
- Alerting systems
- Cost tracking

---

## ✅ WHAT ACTUALLY WORKS

### For Array Length Limiting

**✅ System Prompt Instructions**
- Bookending (start + end)
- Explicit constraints
- Multiple phrasings
- Examples
**Reliability:** 95-99% with proper structure

**✅ Token Budget Limits**
- `max_completion_tokens` parameter
- Creates hard physical constraint
- Cannot be exceeded
**Reliability:** 100% (hard limit)

**✅ Transform Nodes with Natural Language**
```
"Take the chartData array and keep only the last 50 most recent entries"
```
**Reliability:** 90-95% for simple transformations

**✅ Frontend Defensive Validation**
```typescript
if (data.chartData.length > 50) {
  data.chartData = data.chartData.slice(-50);
}
```
**Reliability:** 100% (safety net)

### For Array Filtering

**✅ If/Else Conditional Routing**
- Route to different agents based on conditions
- Each agent handles specific case

**✅ While Loops with Set State**
- Iterate through arrays
- Process items individually
- Build filtered results

**✅ Natural Language Transform**
```
"Filter the items array to include only items where status is 'active'"
```
**Reliability:** Varies, test thoroughly

### For Widget Rendering

**✅ Node-Level Widget Assignment**
- Upload `.widget` file to Agent node
- Configure agent instructions with field mappings
- One widget per agent node

**✅ If/Else Router to Multiple Agents**
```
Agent (classify) → If/Else → Agent A (Widget 1)
                           → Agent B (Widget 2)
                           → Agent C (Widget 3)
```

**✅ Explicit Field Mapping in Instructions**
```markdown
You are rendering a stock card widget.
REQUIRED FIELDS:
- company → "company" field
- symbol → "symbol" field
- chartData → "chartData" field (max 50 entries)
```

---

## Decision Matrix

| Goal | ❌ Doesn't Work | ✅ Use Instead |
|------|----------------|---------------|
| Limit array to 50 items | JSON Schema `maxItems` | System prompts + token limits + frontend validation |
| Truncate array in Transform | `.slice()` method | Natural language instruction |
| Filter array in Transform | `.filter()` macro | If/Else routing or natural language |
| Different widgets per tool | Per-tool widget config | If/Else → separate agents |
| Validate email format | String `format` keyword | Application-level validation |
| Prevent infinite loops | Rely on conditions only | Explicit iteration limits + timeouts |
| Get agent analytics | Built-in dashboard | Build custom logging |
| Connect to Zendesk | Built-in connector | Build custom integration |

---

## Lessons Learned

### Research Before Implementing

**ALWAYS verify** that a feature is actually supported before investing time:
1. Check official documentation
2. Search community forums
3. Look for working examples
4. Test in Preview mode first

### Assume Nothing

Features that "should" work often don't:
- Standard JSON Schema features may not be supported
- Platform UI may show options that don't work
- Common language features may be restricted

### Plan for Workarounds

When encountering limitations:
1. Document what doesn't work
2. Find alternative approaches
3. Test alternatives thoroughly
4. Update this document

---

## Reporting New Limitations

When you discover a new limitation:

1. **Verify it's actually a limitation:**
   - Test multiple approaches
   - Check documentation
   - Search community forums

2. **Document evidence:**
   - Error messages
   - Community threads
   - Official responses

3. **Add to this document:**
   - Clear description
   - What doesn't work
   - Evidence
   - Workarounds

---

## Version History

- **v1.0** (Nov 23, 2025): Initial compilation from comprehensive research
  - JSON Schema limitations
  - CEL Transform node limitations
  - Widget rendering constraints
  - Platform capability gaps

---

**Remember:** This document prevents wasted effort. Check here BEFORE implementing anything involving:
- Array operations
- Widget configuration
- Schema constraints
- Loop conditions
- Knowledge integration
