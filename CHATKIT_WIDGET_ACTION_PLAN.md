# ChatKit Widget Implementation - Immediate Action Plan

## Status: Ready for Agent Builder Configuration

**Current State**: ChatKit Studio Market News Feed widget analyzed and ready for integration

**Root Cause Identified**: Agent Builder output format set to TEXT (returns JSON as string)

**Solution**: Change output format to WIDGET and configure data transformation

---

## Immediate Actions Required (User)

### Action 1: Upload Widget to Agent Builder ⏱️ 10 minutes

1. **Navigate**: https://platform.openai.com/agents
2. **Open Workflow**: G'sves (`wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736`)
3. **Upload Widget**:
   - Click "Widgets" tab
   - Click "Upload Widget"
   - Select: `/Volumes/WD My Passport 264F Media/claude-voice-mcp/.playwright-mcp/Market-News-Feed.widget`
   - Name: "Market News Feed"
   - Click Save

**Verification**: Widget appears in widgets list

---

### Action 2: Add Data Transformation Node ⏱️ 30 minutes

**Purpose**: Convert MCP tool response to widget-compatible format

**Node Type**: Code (JavaScript)

**Position**: Between MCP tool call and output node

**Code**:
```javascript
// Input: mcpResponse from get_market_news tool
// Output: Widget-compatible data

const transformedData = {
  symbol: mcpResponse.symbol,
  selectedSource: "all", // Default filter
  articles: mcpResponse.news.map(article => {
    // CRITICAL: Derive sourceType from source name
    const sourceType = article.source.toLowerCase().includes('cnbc')
      ? 'cnbc'
      : 'yahoo';

    return {
      title: article.headline,           // Rename: headline → title
      source: article.source,
      publishedAt: article.publishedAt,
      description: article.summary || article.headline, // Fallback
      url: article.url,
      sourceType: sourceType             // NEW: Required by widget
    };
  })
};

// Limit to 10 articles
transformedData.articles = transformedData.articles.slice(0, 10);

return transformedData;
```

**Verification**: Test node with sample MCP response

---

### Action 3: Change Output Format to WIDGET ⏱️ 5 minutes

**Current**: Output node format = TEXT (❌ returns JSON as string)

**Required**: Output node format = WIDGET (✅ renders visual widget)

**Steps**:
1. Click on Output Node in workflow canvas
2. Find "Output Format" dropdown
3. Change from "TEXT" to "WIDGET"
4. New dropdown appears: "Select Widget"
5. Choose "Market News Feed"
6. Click Save

**This is the critical fix for JSON text display issue**

---

### Action 4: Map Data to Widget ⏱️ 15 minutes

**In Output Node Configuration**:

**Section**: "Widget Data Mapping"

**Mapping**:
```json
{
  "symbol": "{{transformedData.symbol}}",
  "articles": "{{transformedData.articles}}",
  "selectedSource": "{{transformedData.selectedSource}}"
}
```

**Alternative**: Select transformation node as data source for auto-mapping

---

### Action 5: Update Agent Prompt ⏱️ 20 minutes

**Add to Agent System Prompt**:

```markdown
SYMBOL EXTRACTION RULES:
When user asks about a stock, extract the ticker symbol:
- "Tesla" / "Tesla Inc" → TSLA
- "Apple" / "Apple Inc" → AAPL
- "Microsoft" / "Microsoft Corp" → MSFT
- "Google" / "Alphabet" → GOOGL
- "Facebook" / "Meta" → META
- "NVIDIA" → NVDA
- "Amazon" → AMZN

If uncertain, ask user for clarification.

MARKET NEWS WORKFLOW:
1. Extract ticker from user query
2. Call get_market_news MCP tool
3. Transform response (data transformation node handles this)
4. Return as WIDGET (not TEXT)

IMPORTANT: Always return WIDGET format, never JSON text.
```

---

### Action 6: Test in Agent Builder Preview ⏱️ 30 minutes

**Test Queries**:

1. **TSLA**: "What's the latest news on Tesla?"
   - ✅ Widget displays with TSLA badge
   - ✅ 10 news articles visible
   - ✅ Blue dots for CNBC, orange for Yahoo

2. **AAPL**: "Show me Apple news"
   - ✅ Widget displays with AAPL badge
   - ✅ Source filtering works

3. **MSFT**: "Any updates on Microsoft?"
   - ✅ Correct symbol extraction
   - ✅ Article descriptions truncated properly

4. **GOOGL**: "News about Google"
   - ✅ Facebook → META conversion working

5. **META**: "Facebook updates"
   - ✅ Company name → ticker conversion

**What to Verify**:
- ✅ Widget renders visually (NOT JSON text)
- ✅ Correct ticker in badge
- ✅ News articles in ListView
- ✅ Color-coded source dots
- ✅ Filter buttons present
- ✅ "Read More" buttons visible
- ✅ Refresh and chart buttons functional

---

### Action 7: Publish Workflow ⏱️ 10 minutes

**Pre-Publish Checklist**:
- ✅ Widget uploaded
- ✅ Transformation node created
- ✅ Output format = WIDGET
- ✅ Data mapping configured
- ✅ Prompt updated
- ✅ Tested with 5+ symbols

**Publish Steps**:
1. Click "Publish" button
2. Version name: "Market News Widget v1.0"
3. Changelog: "ChatKit Studio Market News Feed widget integration"
4. Click Confirm

**Post-Publish**: Test in production at http://localhost:5175

---

## Expected Results

### Before Fix (Current State):
```
User: "What's the latest news on TSLA?"

Agent: {"response_text":"...","widgets":[{"type":"Card"...}]}
```
**Problem**: JSON text displayed, unusable

### After Fix (Expected):
```
User: "What's the latest news on TSLA?"

Agent:
┌─────────────────────────────────────────┐
│ Market News Feed         [TSLA] 🔄 📈  │
├─────────────────────────────────────────┤
│ [All Sources] [CNBC] [Yahoo Finance]   │
├─────────────────────────────────────────┤
│ 🔵 Trump buys bonds backed by...       │
│    CNBC • 2 hours ago                  │
│    Tesla CEO announced...              │
│    [Read More]                         │
│ ─────────────────────────────────────── │
│ 🟠 Tesla stock surges on earnings      │
│    Yahoo Finance • 5 hours ago         │
│    [Read More]                         │
│ ─────────────────────────────────────── │
│ ... (8 more articles)                  │
└─────────────────────────────────────────┘
```
**Result**: Professional visual widget, fully interactive

---

## Troubleshooting Quick Reference

### Issue: Widget still shows JSON text
**Fix**: Verify output format = WIDGET (not TEXT)

### Issue: No articles displayed
**Fix**: Check MCP server running, test `/api/stock-news?symbol=TSLA`

### Issue: Wrong symbol in badge
**Fix**: Update prompt with explicit symbol mappings

### Issue: Source filter not working
**Fix**: Verify sourceType derivation in transformation node

---

## Success Criteria

**Phase 1 Complete When**:
- ✅ Widget renders visually (0% JSON text)
- ✅ Works with ANY stock symbol
- ✅ Source filtering functional
- ✅ Interactive actions working
- ✅ Render time < 2 seconds
- ✅ No console errors

---

## Timeline

**Total Time**: 2-4 hours

**Breakdown**:
- Upload widget: 10 min
- Add transformation: 30 min
- Change output format: 5 min
- Configure mapping: 15 min
- Update prompt: 20 min
- Testing: 30 min
- Publish: 10 min
- Buffer: 1-2 hours

---

## Next Steps After Phase 1

Once Market News Feed widget is working:

**Phase 2**: Add additional widgets
- Technical Levels widget
- Pattern Detection widget
- Economic Calendar widget

**Phase 3**: Advanced features
- Widget persistence in Supabase
- If/Else routing to multiple widgets
- Real-time widget updates

---

**Document Version**: 1.0
**Created**: November 16, 2025
**Status**: 🟢 Ready for Implementation
**Confidence**: Very High (based on Jeeves 2.0 working example)
