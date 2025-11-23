# Agent Builder Widget Configuration Guide - Phase 1

## Overview

This guide walks through configuring the Agent Builder workflow to return **visual widgets** instead of JSON text. The widget is **generic** and dynamically adapts to any stock symbol requested by the user.

**Widget Capabilities**:
- Works with ANY stock ticker: TSLA, AAPL, MSFT, GOOGL, NVDA, META, etc.
- Displays latest market news in a professional card layout
- Auto-populates company name and news articles based on user query
- Renders visually inside ChatKit message stream (not as text)

---

## Phase 1: Widget Design & Agent Configuration

### Step 1: Widget Upload ✅

**File Created**: `chatkit-widgets/news-card-widget.json`

This widget template uses **dynamic placeholders** that work for any stock:
- `{{symbol}}` - Replaced with ticker symbol (TSLA, AAPL, etc.)
- `{{article_title}}` - News headline
- `{{article_source}}` - Source (CNBC, Yahoo Finance, etc.)
- `{{article_time}}` - Publication timestamp

**Widget Structure**:
```json
{
  "type": "Card",
  "size": "lg",
  "status": {"text": "Live News", "icon": "newspaper"},
  "children": [
    {"type": "Title", "value": "{{symbol}} Market News", "size": "lg"},
    {"type": "Divider", "spacing": 12},
    {"type": "ListView", "limit": 10, "children": [
      {
        "type": "ListViewItem",
        "children": [
          {"type": "Text", "value": "{{article_title}}", "weight": "semibold"},
          {"type": "Caption", "value": "{{article_source}} • {{article_time}}", "size": "sm"}
        ]
      }
    ]}
  ]
}
```

**To Upload**:
1. Navigate to [Agent Builder](https://platform.openai.com/agents)
2. Open your G'sves workflow (`wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736`)
3. Click "Widgets" tab in left sidebar
4. Click "Upload Widget"
5. Select `chatkit-widgets/news-card-widget.json`
6. Widget name: **"Market News Card"** (generic, not TSLA-specific)

---

### Step 2: Change Output Format from TEXT to WIDGET

**Current Issue**: Agent returns JSON as a **string** (TEXT format), causing ChatKit to display it as plain text.

**Solution**: Switch to WIDGET output format so ChatKit receives structured JSON objects.

#### Instructions:

1. **Open Agent Builder Workflow**:
   - Go to [Agent Builder](https://platform.openai.com/agents)
   - Select G'sves workflow

2. **Locate the Output Node** (currently set to TEXT):
   - This is the final node that returns the response
   - Currently configured to return `{"response_text": "...", "widgets": [...]}`as text

3. **Change Output Format**:
   - Click the output node
   - Change format from **TEXT** to **WIDGET**
   - Select the uploaded widget: **"Market News Card"**

4. **Configure Widget Data Mapping**:
   - Map agent variables to widget placeholders:
     - `{{symbol}}` ← Extract from user query or MCP tool response
     - `{{article_title}}` ← Loop through news articles array
     - `{{article_source}}` ← Article metadata
     - `{{article_time}}` ← Article timestamp

---

### Step 3: Prompt Engineering for Generic Symbol Support

The agent must dynamically identify the stock symbol from the user's query and populate the widget accordingly.

#### Updated Agent Prompt Template:

```markdown
You are a professional market analysis assistant. When users ask about stocks, you provide market news in a structured widget format.

IMPORTANT INSTRUCTIONS:
1. Extract the stock ticker symbol from the user's query
   - Examples: "TSLA" from "What's the latest news on Tesla?"
   - Examples: "AAPL" from "Show me Apple news"
   - Examples: "MSFT" from "Microsoft updates"
   - Examples: "GOOGL" from "Google stock news"

2. Use the `get_market_news` tool with the extracted symbol
   - Pass the ticker symbol as the `symbol` parameter
   - Retrieve up to 10 recent news articles

3. Return data in WIDGET format (not TEXT):
   - Populate {{symbol}} with the ticker (TSLA, AAPL, MSFT, etc.)
   - Loop through news articles to populate:
     - {{article_title}} - Headline
     - {{article_source}} - Source name
     - {{article_time}} - Formatted timestamp

4. The widget will automatically render visually in ChatKit

SUPPORTED QUERIES:
- "What's the latest news on [COMPANY/TICKER]?"
- "Show me [TICKER] news"
- "Any updates on [COMPANY]?"
- "News about [TICKER]"

The widget is generic and works with ANY stock symbol, not limited to specific companies.
```

---

### Step 4: Configure MCP Tool Integration

**Tool Required**: `get_market_news` from GVSES_Market_Data_Server

**Configuration**:
1. In Agent Builder workflow, add **Tool Call** node
2. Select MCP Server: **GVSES_Market_Data_Server**
3. Select Tool: **get_market_news**
4. Parameter mapping:
   ```json
   {
     "symbol": "{{extracted_symbol}}",
     "limit": 10
   }
   ```

**Tool Response Structure** (expected from backend):
```json
{
  "symbol": "AAPL",
  "articles": [
    {
      "title": "Apple announces new product line",
      "source": "CNBC",
      "publishedAt": "2025-11-16T04:45:00Z",
      "url": "https://..."
    },
    // ... more articles
  ]
}
```

---

### Step 5: Widget Data Transformation

The agent must transform MCP tool response into widget-compatible format:

#### Pseudocode Logic:
```javascript
// Extract symbol from user query
const symbol = extractSymbolFromQuery(userMessage);

// Fetch news via MCP tool
const newsData = await mcpClient.call("get_market_news", { symbol, limit: 10 });

// Transform for widget
const widgetData = {
  symbol: symbol,
  articles: newsData.articles.map(article => ({
    article_title: article.title,
    article_source: article.source,
    article_time: formatTimestamp(article.publishedAt)
  }))
};

// Return as WIDGET (not TEXT)
return {
  type: "widget",
  widget_id: "market-news-card",
  data: widgetData
};
```

#### Agent Builder Implementation:
1. Add **Code** node (if available) or use built-in transformation
2. Map `newsData.articles` array to widget's `ListView` children
3. Each article becomes a `ListViewItem` with title and caption

---

### Step 6: Test in Agent Builder Preview

**Test Queries** (to validate generic symbol support):

1. **TSLA Test**:
   - Query: "What's the latest news on Tesla?"
   - Expected: Widget displays with "TSLA Market News" title
   - Expected: 10 news articles about Tesla

2. **AAPL Test**:
   - Query: "Show me Apple news"
   - Expected: Widget displays with "AAPL Market News" title
   - Expected: 10 news articles about Apple

3. **MSFT Test**:
   - Query: "Any updates on Microsoft?"
   - Expected: Widget displays with "MSFT Market News" title
   - Expected: 10 news articles about Microsoft

4. **GOOGL Test**:
   - Query: "News about Google"
   - Expected: Widget displays with "GOOGL Market News" title
   - Expected: 10 news articles about Google

**What to Check**:
- ✅ Widget renders visually (NOT as JSON text)
- ✅ Correct ticker symbol in title
- ✅ News articles displayed in list format
- ✅ Sources and timestamps visible
- ✅ Card styling with "Live News" status badge

---

### Step 7: Common Issues & Troubleshooting

#### Issue 1: Widget Still Displays as JSON Text
**Cause**: Output format still set to TEXT instead of WIDGET
**Fix**:
- Open workflow in Agent Builder
- Verify output node format is **WIDGET** (not TEXT)
- Ensure widget is selected from dropdown

#### Issue 2: Empty Widget or Missing Data
**Cause**: MCP tool not returning data or mapping is incorrect
**Fix**:
- Test MCP tool independently: `curl http://localhost:8000/api/stock-news?symbol=TSLA`
- Verify tool response structure matches expected format
- Check data mapping in Agent Builder transformation node

#### Issue 3: Widget Shows Wrong Symbol
**Cause**: Symbol extraction logic not working
**Fix**:
- Add explicit symbol extraction in prompt
- Test with variations: "Tesla", "TSLA", "Tesla stock", etc.
- Use fallback: if symbol not detected, ask user to clarify

#### Issue 4: Template Variables Not Replaced
**Cause**: Widget data not properly mapped to template placeholders
**Fix**:
- Verify widget data structure matches template expectations
- Check that `{{symbol}}`, `{{article_title}}`, etc. are in agent response
- Review Agent Builder data transformation logic

---

### Step 8: Publish Workflow

Once testing is successful:

1. Click **"Publish"** in Agent Builder
2. Note the new workflow version number
3. Frontend will automatically use updated workflow (no code changes needed)
4. Test in production:
   - Navigate to `http://localhost:5175` (or production URL)
   - Start ChatKit session
   - Send query: "What's the latest news on AAPL?"
   - Verify widget renders visually

---

## Expected User Experience

### Before Fix (JSON Text Display):
```
User: "What's the latest news on TSLA?"

Agent: {"response_text":"Here are the latest TSLA market news headlines:","query_intent":"news","symbol":"TSLA","widgets":[{"type":"Card","size":"lg","status":{"text":"Live News","icon":"newspaper"},"children":[{"type":"Title","value":"TSLA Market News","size":"lg"},{"type":"Divider","spacing":12},{"type":"ListView","limit":10,"children":[{"type":"ListViewItem","children":[{"type":"Text","value":"Trump buys at least $82 million in bonds...","weight":"semibold"},{"type":"Caption","value":"CNBC • 2025-11-16 04:45 UTC","size":"sm"}]}]}]}]}
```
**(Displays as ugly JSON text - BAD UX)**

### After Fix (Visual Widget Display):
```
User: "What's the latest news on TSLA?"

Agent:
┌─────────────────────────────────────────┐
│ 🟢 Live News                            │
├─────────────────────────────────────────┤
│ TSLA Market News                        │
├─────────────────────────────────────────┤
│ • Trump buys at least $82 million       │
│   in bonds...                           │
│   CNBC • 2025-11-16 04:45 UTC          │
│                                         │
│ • Tesla stock surges on earnings beat  │
│   Yahoo Finance • 2025-11-15 18:30 UTC │
│                                         │
│ ... (8 more articles)                  │
└─────────────────────────────────────────┘
```
**(Displays as professional card widget - GOOD UX)**

---

## Widget Versatility - Works with ANY Symbol

The same widget configuration handles multiple use cases:

### Tech Stocks:
- "What's happening with AAPL?" → Apple news widget
- "Show me NVDA updates" → NVIDIA news widget
- "MSFT news" → Microsoft news widget
- "Any GOOGL headlines?" → Google news widget

### Automotive:
- "Tesla news" → TSLA news widget
- "Ford updates" → F news widget
- "GM stock news" → GM news widget

### Finance:
- "JPMorgan news" → JPM news widget
- "Goldman Sachs updates" → GS news widget
- "Bank of America" → BAC news widget

### Market Indices:
- "SPY news" → S&P 500 ETF news widget
- "QQQ updates" → NASDAQ ETF news widget
- "DIA news" → Dow Jones ETF news widget

**One widget, infinite symbols!**

---

## Next Steps (After Phase 1 Success)

### Phase 2: Frontend Cleanup
- Remove external widget parsing code (`widgetParser.ts`, `ChatKitWidgetRenderer.tsx`)
- Simplify `RealtimeChatKit.tsx` onMessage callback
- Trust ChatKit to handle widget rendering internally

### Phase 3: Persistence Updates
- Modify Supabase message schema to store widget JSON
- Update save/load logic to handle both text and widget messages
- Test conversation history with mixed content

### Phase 4: Additional Widget Types
- Create widgets for:
  - Technical levels (support/resistance)
  - Chart patterns (head & shoulders, triangles)
  - Economic calendar events
  - Stock charts (candlestick images)
- Use If/Else routing to multiple agents (one per widget type)

---

## Success Criteria

Phase 1 is complete when:
- ✅ Widget renders visually in ChatKit (not as JSON text)
- ✅ Works with ANY stock symbol (not just TSLA)
- ✅ News articles populate correctly
- ✅ Card styling matches design (dark theme, green status badge)
- ✅ ListView displays up to 10 articles with titles and captions
- ✅ Testing confirms behavior across 5+ different symbols

---

**Implementation By**: Claude Code
**Date**: November 15, 2025
**Status**: 🟡 Ready for Agent Builder Upload
**Next Action**: Upload `news-card-widget.json` to Agent Builder and switch output format to WIDGET
