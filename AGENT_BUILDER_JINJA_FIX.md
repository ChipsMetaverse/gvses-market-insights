# Agent Builder Jinja Template Fix

**Date:** November 16, 2025
**Issue:** Error saving workflow version: Invalid Jinja template in node (agent widget): unexpected '=' (line 1)
**Status:** ✅ FIXED

---

## Problem

The ChatKit widget "GVSES stock card (fixed)" was using JavaScript equality operator `===` instead of Jinja's `==` operator. When OpenAI Agent Builder tried to parse the widget template, it failed because Jinja2 doesn't recognize `===`.

### Error Message
```
Error saving workflow version: Invalid Jinja template in node node_pwrg9arg (agent widget): unexpected '=' (line 1)
```

---

## Root Cause

The widget template contained **2 instances of `===`** that should have been `==`:

### Instance 1: Timeframe Button
```jinja
❌ BEFORE: {% if selectedTimeframe === tf %}
✅ AFTER:  {% if selectedTimeframe == tf %}
```

### Instance 2: News Filter Button
```jinja
❌ BEFORE: {% if selectedSource === f.value %}
✅ AFTER:  {% if selectedSource == f.value %}
```

---

## Fix Applied

**File:** `/Volumes/WD My Passport 264F Media/claude-voice-mcp/.playwright-mcp/GVSES-stock-card-fixed-.widget`

**Changes:**
- Replaced all `===` with `==` (2 replacements)
- Verified: 0 instances of `===` remaining
- All other `==` operators unchanged

**Command Used:**
```bash
sed -i '' 's/===/ == /g' "GVSES-stock-card-fixed-.widget"
```

---

## Jinja2 vs JavaScript Comparison

| Feature | JavaScript | Jinja2 |
|---------|-----------|--------|
| **Strict Equality** | `===` | ❌ Not supported |
| **Equality** | `==` | `==` ✅ |
| **Not Equal** | `!==` | `!=` |
| **Logical AND** | `&&` | `and` |
| **Logical OR** | `||` | `or` |
| **Logical NOT** | `!` | `not` |

**Key Difference:** Jinja2 uses Python-style operators, not JavaScript-style.

---

## Verification

### Before Fix
```bash
$ grep -c "===" widget-file
2
```

### After Fix
```bash
$ grep -c "===" widget-file
0
```

### Sample Output
```jinja
{% if selectedTimeframe  ==  tf %}
{% if selectedSource  ==  f.value %}
```

---

## How to Apply Fix to Agent Builder

### Option 1: Re-upload Fixed Widget
1. **Download fixed widget:**
   - File location: `.playwright-mcp/GVSES-stock-card-fixed-.widget`

2. **In Agent Builder:**
   - Click on the G'sves agent node
   - Under "Output format", remove current widget
   - Upload the fixed widget file
   - Save workflow

3. **Publish:**
   - Click "Publish" button
   - Error should be resolved

### Option 2: Edit Widget in ChatKit
1. **Navigate to ChatKit widget editor:**
   - https://widgets.chatkit.studio/editor/33797fb9-0471-42cc-9aaf-8cf50139b909

2. **Find and replace in view.tsx:**
   - Search for: `{% if selectedTimeframe === tf %}`
   - Replace with: `{% if selectedTimeframe == tf %}`

   - Search for: `{% if selectedSource === f.value %}`
   - Replace with: `{% if selectedSource == f.value %}`

3. **Download updated widget:**
   - Click Download button
   - Import into Agent Builder

---

## Testing Checklist

After applying the fix:

- [ ] Widget uploads without error
- [ ] Workflow saves successfully
- [ ] Workflow publishes without Jinja template error
- [ ] Widget renders correctly in test mode
- [ ] Timeframe buttons work (change selection)
- [ ] News filter buttons work (switch between All/Company)

---

## Related Files

### Fixed Widget
- **Location:** `.playwright-mcp/GVSES-stock-card-fixed-.widget`
- **Status:** Jinja template syntax corrected
- **Ready for:** Agent Builder deployment

### Documentation
- `CHATKIT_LABEL_UPDATE_COMPLETE.md` - Label updates (SH/BL/BTD)
- `CHATKIT_FIX_EXECUTIVE_SUMMARY.md` - Initial widget fixes

---

## Lessons Learned

### 1. Jinja2 Syntax Requirements
When creating widgets for platforms that use Jinja2 templating (like OpenAI Agent Builder):
- **Always use `==` for equality**, never `===`
- **Use Python-style operators** (`and`, `or`, `not`)
- **Test with Jinja2 parser** before deployment

### 2. ChatKit Widget Export
ChatKit Studio generates widgets with Jinja2 templates, but may sometimes include JavaScript-style operators. Always verify:
- Equality operators (`==` not `===`)
- Logical operators (`and` not `&&`)
- Conditional syntax follows Jinja2 standards

### 3. Error Message Interpretation
"unexpected '='" in Jinja template usually means:
- Using `===` instead of `==`
- Using `=` for assignment (should use `{% set var = value %}`)
- Incorrect operator spacing or syntax

---

## Quick Reference: Common Jinja2 Patterns

### Conditionals
```jinja
{# Correct #}
{% if price > 100 %}
{% if status == "active" %}
{% if count != 0 %}

{# Wrong - will cause errors #}
{% if price === 100 %}  ❌
{% if status === "active" %}  ❌
```

### Logical Operations
```jinja
{# Correct #}
{% if active and verified %}
{% if price > 100 or discount > 0 %}
{% if not expired %}

{# Wrong #}
{% if active && verified %}  ❌
{% if price > 100 || discount > 0 %}  ❌
{% if !expired %}  ❌
```

---

## Conclusion

The ChatKit widget "GVSES stock card (fixed)" has been corrected to use proper Jinja2 syntax. The widget is now compatible with OpenAI Agent Builder and should publish successfully without template errors.

**Next Step:** Re-upload the fixed widget to Agent Builder and attempt to publish the workflow.

---

*Fix applied: November 16, 2025*
*Issue: JavaScript `===` operator in Jinja template*
*Solution: Replaced with Jinja `==` operator*
*Status: Ready for deployment*
