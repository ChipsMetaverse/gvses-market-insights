# ChatKit Studio Widget Implementation Plan - ULTRATHINK Analysis

## Executive Summary

**Objective**: Implement visual ChatKit widgets for GVSES trading assistant using ChatKit Studio's production-ready Market News Feed widget.

**Key Finding**: ChatKit Studio provides a complete, professional widget that exactly matches GVSES requirements. No custom widget development needed - use the pre-built Market News Feed widget with proper Agent Builder configuration.

**Implementation Complexity**: Low - Primary work is Agent Builder configuration, not widget development.

**Timeline**: 2-4 hours for complete implementation and testing.

---

## Part 1: Widget Architecture Comparison

### ChatKit Studio Widget (Production-Ready) ✅

**File**: `/Volumes/WD My Passport 264F Media/claude-voice-mcp/.playwright-mcp/Market-News-Feed.widget`

**Format**: Version 1.0 .widget file with Jinja2 templating

**Data Schema** (JSON Schema validated):
```json
{
  "symbol": "string",
  "articles": [
    {
      "title": "string",
      "source": "string",
      "publishedAt": "string",
      "description": "string",
      "url": "string (uri)",
      "sourceType": "cnbc" | "yahoo"
    }
  ],
  "selectedSource": "all" | "cnbc" | "yahoo"
}
```

**Features**:
- ✅ Generic symbol support (works with any ticker)
- ✅ Dual-source filtering (CNBC + Yahoo Finance)
- ✅ Interactive chart integration (`chart.setSymbol` action)
- ✅ Refresh capability (`news.refresh` action)
- ✅ Clickable article links (`browser.openUrl` action)
- ✅ Color-coded source indicators (blue for CNBC, orange for Yahoo)
- ✅ Professional styling with proper spacing and typography
- ✅ Truncation for long text (maxLines: 2 for titles, 3 for descriptions)
- ✅ "Read More" buttons for each article
- ✅ Limit 10 articles displayed

### Our Initial Widget (Superseded) ⚠️

**File**: `/Volumes/WD My Passport 264F Media/claude-voice-mcp/chatkit-widgets/news-card-widget.json`

**Format**: Simple Card with ListView

**Limitations**:
- ❌ No source filtering
- ❌ No interactive actions
- ❌ No chart integration
- ❌ Basic styling only
- ❌ No color coding
- ❌ No "Read More" functionality

**Conclusion**: ChatKit Studio widget is superior in every way. Use it instead.

---

## Part 2: MCP Tool Response Mapping

### Current MCP Tool: `get_market_news`

**Server**: GVSES_Market_Data_Server (market-mcp-server)

**Expected Response Format** (inferred from backend):
```json
{
  "symbol": "TSLA",
  "news": [
    {
      "headline": "Trump buys at least $82 million in bonds backed by...",
      "source": "CNBC",
      "url": "https://www.cnbc.com/2025/11/16/...",
      "publishedAt": "2025-11-16T04:45:00Z",
      "summary": "Article summary text..."
    },
    {
      "headline": "Tesla stock surges on earnings beat",
      "source": "Yahoo Finance",
      "url": "https://finance.yahoo.com/...",
      "publishedAt": "2025-11-15T18:30:00Z",
      "summary": "Article summary..."
    }
  ]
}
```

### ChatKit Studio Widget Requirements

**Required Schema**:
```json
{
  "symbol": "TSLA",
  "articles": [
    {
      "title": "Trump buys at least $82 million in bonds backed by...",
      "source": "CNBC",
      "publishedAt": "2025-11-16T04:45:00Z",
      "description": "Article summary text...",
      "url": "https://www.cnbc.com/2025/11/16/...",
      "sourceType": "cnbc"
    }
  ],
  "selectedSource": "all"
}
```

### Data Transformation Logic

**Mapping Required**:
| MCP Field | Widget Field | Transformation |
|-----------|--------------|----------------|
| `symbol` | `symbol` | Direct mapping |
| `news[]` | `articles[]` | Array mapping |
| `news[].headline` | `articles[].title` | Rename field |
| `news[].source` | `articles[].source` | Direct mapping |
| `news[].publishedAt` | `articles[].publishedAt` | Direct mapping |
| `news[].summary` | `articles[].description` | Rename field |
| `news[].url` | `articles[].url` | Direct mapping |
| (derived) | `articles[].sourceType` | **NEW**: Derive from source name |
| N/A | `selectedSource` | **NEW**: Default to "all" |

### Critical New Field: `sourceType`

**Problem**: MCP tool returns `source: "CNBC"` (string), but widget needs `sourceType: "cnbc"` (enum: "cnbc" | "yahoo")

**Solution - Derivation Logic**:
```python
def derive_source_type(source_name: str) -> str:
    """Convert source name to ChatKit Studio enum value"""
    source_lower = source_name.lower()

    if "cnbc" in source_lower:
        return "cnbc"
    elif "yahoo" in source_lower:
        return "yahoo"
    else:
        # Default to yahoo for unknown sources
        return "yahoo"
```

**Agent Builder Implementation**:
```javascript
// In Agent Builder Code node:
articles.map(article => ({
  ...article,
  title: article.headline,
  description: article.summary,
  sourceType: article.source.toLowerCase().includes('cnbc') ? 'cnbc' : 'yahoo'
}))
```

---

## Part 3: Agent Builder Configuration Steps

### Step 1: Upload ChatKit Studio Widget

**Action**: Upload `.widget` file to Agent Builder

**Instructions**:
1. Navigate to [Agent Builder](https://platform.openai.com/agents)
2. Open G'sves workflow: `wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736`
3. Click "Widgets" tab in left sidebar
4. Click "Upload Widget" button
5. Select file: `/Volumes/WD My Passport 264F Media/claude-voice-mcp/.playwright-mcp/Market-News-Feed.widget`
6. Widget name: **"Market News Feed"** (matches ChatKit Studio name)
7. Click "Save"

**Verification**: Widget should appear in widgets list with version 1.0

---

### Step 2: Add Data Transformation Node

**Purpose**: Convert MCP tool response to widget-compatible format

**Node Type**: Code (JavaScript/Python)

**Input**: Raw MCP tool response from `get_market_news`

**Code** (JavaScript):
```javascript
// Input: mcpResponse = { symbol: "TSLA", news: [...] }

const transformedData = {
  symbol: mcpResponse.symbol,
  selectedSource: "all", // Default filter state
  articles: mcpResponse.news.map(article => {
    // Derive sourceType from source name
    const sourceType = article.source.toLowerCase().includes('cnbc')
      ? 'cnbc'
      : 'yahoo';

    return {
      title: article.headline,
      source: article.source,
      publishedAt: article.publishedAt,
      description: article.summary || article.headline, // Fallback if no summary
      url: article.url,
      sourceType: sourceType
    };
  })
};

// Limit to 10 articles (widget enforces this, but good to pre-filter)
transformedData.articles = transformedData.articles.slice(0, 10);

return transformedData;
```

**Output**: Widget-compatible data object

**Node Position**: Between MCP tool call and output node

---

### Step 3: Change Output Format to WIDGET

**Current State**: Output node set to TEXT (returns JSON as string)

**Required Change**: Output node set to WIDGET (returns structured widget object)

**Instructions**:
1. Locate the **Output Node** in Agent Builder workflow canvas
2. Click on the output node to open configuration panel
3. Find "Output Format" dropdown (currently set to "TEXT")
4. Change to **"WIDGET"**
5. New dropdown appears: "Select Widget"
6. Choose **"Market News Feed"** from dropdown
7. Click "Save"

**Critical**: This is the key change that fixes JSON text display issue

---

### Step 4: Map Data to Widget

**Purpose**: Connect transformation node output to widget data inputs

**Configuration**:
1. In Output Node configuration panel
2. Section: "Widget Data Mapping"
3. Map transformation node output to widget variables:

```json
{
  "symbol": "{{transformedData.symbol}}",
  "articles": "{{transformedData.articles}}",
  "selectedSource": "{{transformedData.selectedSource}}"
}
```

**Alternative** (if direct mapping supported):
- Select transformation node as data source
- Agent Builder auto-maps fields by name

---

### Step 5: Update Agent Prompt for Symbol Extraction

**Current Prompt Issue**: Agent may not extract ticker symbol consistently

**Enhanced Prompt Template**:
```markdown
You are GVSES, a professional market analysis assistant specializing in real-time market insights and news.

SYMBOL EXTRACTION:
When a user asks about a stock, extract the ticker symbol:
- "What's the latest news on Tesla?" → TSLA
- "Show me Apple updates" → AAPL
- "Microsoft news" → MSFT
- "GOOGL headlines" → GOOGL
- "Any news on Meta?" → META

If the user provides a company name, convert it to the ticker symbol.
If uncertain, ask for clarification.

MARKET NEWS WORKFLOW:
1. Extract the ticker symbol from the user's query
2. Call the `get_market_news` MCP tool with the symbol
3. Transform the response using the data transformation node
4. Return the result as a WIDGET (not TEXT)

IMPORTANT:
- Always return data in WIDGET format
- Never return JSON as text
- The Market News Feed widget will render automatically in ChatKit

SUPPORTED QUERIES:
- "What's the latest news on [SYMBOL/COMPANY]?"
- "Show me [SYMBOL] news"
- "Any updates on [COMPANY]?"
- "News about [SYMBOL]"

The widget is generic and works with any stock symbol.
```

---

### Step 6: Test in Agent Builder Preview

**Test Cases**:

#### Test 1: TSLA
- **Query**: "What's the latest news on Tesla?"
- **Expected Symbol**: TSLA
- **Expected Result**: Market News Feed widget with TSLA badge
- **Expected Articles**: 10 news articles about Tesla
- **Expected Sources**: Mix of CNBC and Yahoo Finance
- **Expected Filters**: All Sources (active), CNBC, Yahoo Finance buttons

#### Test 2: AAPL
- **Query**: "Show me Apple news"
- **Expected Symbol**: AAPL
- **Expected Result**: Market News Feed widget with AAPL badge
- **Expected Articles**: 10 news articles about Apple
- **Expected Colors**: Blue dots for CNBC, orange dots for Yahoo

#### Test 3: MSFT
- **Query**: "Any updates on Microsoft?"
- **Expected Symbol**: MSFT
- **Expected Result**: Market News Feed widget with MSFT badge

#### Test 4: GOOGL
- **Query**: "News about Google"
- **Expected Symbol**: GOOGL
- **Expected Result**: Market News Feed widget with GOOGL badge

#### Test 5: META
- **Query**: "Facebook news"
- **Expected Symbol**: META (agent should convert Facebook → META)
- **Expected Result**: Market News Feed widget with META badge

**Verification Checklist**:
- ✅ Widget renders visually (NOT as JSON text)
- ✅ Correct ticker symbol in badge
- ✅ News articles displayed in ListView
- ✅ Source names and timestamps visible
- ✅ Color-coded dots (blue for CNBC, orange for Yahoo)
- ✅ "All Sources" button active by default
- ✅ Article descriptions truncated properly (maxLines: 3)
- ✅ "Read More" buttons present
- ✅ Refresh button functional
- ✅ Chart button visible

---

### Step 7: Configure Interactive Actions

**Action 1: chart.setSymbol**
- **Trigger**: Click on chart button in widget header
- **Payload**: `{ symbol: "TSLA" }` (dynamic from widget data)
- **Result**: GVSES chart switches to display TSLA

**Implementation**:
1. In Agent Builder, add "Action Handler" node
2. Action type: `chart.setSymbol`
3. Handler logic: Call `/api/stock-history` with symbol
4. Update chart state in GVSES frontend

**Action 2: news.refresh**
- **Trigger**: Click on refresh button
- **Payload**: `{ symbol: "TSLA" }`
- **Result**: Re-fetch latest news for symbol

**Implementation**:
1. Add "Action Handler" node
2. Action type: `news.refresh`
3. Handler logic: Re-call `get_market_news` MCP tool
4. Update widget with new data

**Action 3: news.setSource**
- **Trigger**: Click on source filter buttons (All Sources, CNBC, Yahoo Finance)
- **Payload**: `{ source: "cnbc" | "yahoo" | "all" }`
- **Result**: Filter articles by source

**Implementation**:
1. Client-side filtering (widget handles this automatically)
2. OR server-side: Add MCP tool parameter `source_filter`

**Action 4: browser.openUrl**
- **Trigger**: Click on "Read More" button or article item
- **Payload**: `{ url: "https://www.cnbc.com/..." }`
- **Result**: Open article in new browser tab

**Implementation**:
1. ChatKit handles this natively
2. No additional Agent Builder configuration needed

---

### Step 8: Publish Workflow

**Pre-Flight Checklist**:
- ✅ Widget uploaded to Agent Builder
- ✅ Data transformation node created
- ✅ Output format changed to WIDGET
- ✅ Widget data mapping configured
- ✅ Agent prompt updated for symbol extraction
- ✅ Tested with 5+ different symbols
- ✅ All interactive actions configured

**Publish Steps**:
1. Click **"Publish"** button in Agent Builder
2. Version name: "Market News Widget v1.0"
3. Changelog: "Integrated ChatKit Studio Market News Feed widget with CNBC + Yahoo Finance sources"
4. Click "Confirm Publish"
5. Note the new workflow version number

**Deployment**:
- Frontend automatically uses latest published workflow
- No code changes required
- ChatKit session will use new widget rendering

---

## Part 4: Backend MCP Tool Verification

### Current Backend Endpoint: `/api/stock-news`

**File**: `backend/mcp_server.py`

**Current Implementation** (likely):
```python
@app.get("/api/stock-news")
async def get_stock_news(symbol: str):
    """Get market news for a symbol"""
    try:
        # Call MCP tool
        news_data = await market_service.get_news(symbol)
        return news_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Required Response Format

**Current Format** (needs verification):
```json
{
  "symbol": "TSLA",
  "news": [...]
}
```

**Widget-Compatible Format** (after transformation):
```json
{
  "symbol": "TSLA",
  "articles": [
    {
      "title": "...",
      "source": "CNBC",
      "publishedAt": "2025-11-16T04:45:00Z",
      "description": "...",
      "url": "https://...",
      "sourceType": "cnbc"
    }
  ],
  "selectedSource": "all"
}
```

### Verification Test

**Test Script**: `backend/test_stock_news_response.py`
```python
import requests

response = requests.get("http://localhost:8000/api/stock-news?symbol=TSLA")
data = response.json()

print("Response structure:")
print(f"Keys: {data.keys()}")
print(f"Symbol: {data.get('symbol')}")
print(f"News array length: {len(data.get('news', []))}")

if data.get('news'):
    first_article = data['news'][0]
    print("\nFirst article structure:")
    print(f"Keys: {first_article.keys()}")
    print(f"Headline: {first_article.get('headline')}")
    print(f"Source: {first_article.get('source')}")
    print(f"URL: {first_article.get('url')}")
```

**Expected Output**:
```
Response structure:
Keys: dict_keys(['symbol', 'news'])
Symbol: TSLA
News array length: 10

First article structure:
Keys: dict_keys(['headline', 'source', 'url', 'publishedAt', 'summary'])
Headline: Trump buys at least $82 million in bonds...
Source: CNBC
URL: https://www.cnbc.com/...
```

### Adjustment if Needed

If backend returns different format, update data transformation node in Agent Builder to match actual backend response.

---

## Part 5: Frontend Integration (Minimal Changes)

### Current ChatKit Integration

**File**: `frontend/src/components/RealtimeChatKit.tsx`

**Current State**:
- ChatKit component configured with session endpoint
- Supabase conversation persistence
- Widget parsing code added (may not be needed)

### Required Changes: NONE ✅

**Why**: ChatKit handles WIDGET format output natively when:
1. Agent Builder output format set to WIDGET
2. Widget uploaded to Agent Builder
3. Data properly mapped

**What Happens**:
- Agent Builder sends widget JSON to ChatKit
- ChatKit React component renders it visually
- No external widget parsing needed
- Widget appears inside ChatKit message stream

### Optional Cleanup (Phase 2)

**Files to Remove** (after confirming widgets work):
1. `frontend/src/utils/widgetParser.ts` - No longer needed
2. `frontend/src/components/ChatKitWidgetRenderer.tsx` - No longer needed
3. Widget parsing code in `RealtimeChatKit.tsx` - Simplify onMessage callback

**Reason**: External widget rendering was the wrong approach. ChatKit handles it internally when properly configured.

---

## Part 6: Testing Strategy

### Test Environment Setup

**Backend**:
```bash
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
cd frontend
npm run dev  # Port 5175
```

**MCP Servers**:
```bash
# Market MCP Server (Node.js 22 required)
cd market-mcp-server
npm start

# Alpaca MCP Server (if used)
cd alpaca-mcp-server
python server.py
```

### Manual Testing Checklist

#### Test 1: Visual Widget Rendering
- [ ] Open GVSES app: http://localhost:5175
- [ ] Start ChatKit session
- [ ] Send query: "What's the latest news on TSLA?"
- [ ] **Verify**: Widget renders visually (NOT as JSON text)
- [ ] **Verify**: Card layout with header, filters, and article list
- [ ] **Verify**: "Live News" status visible (if using our initial widget) or proper header (ChatKit Studio widget)

#### Test 2: Symbol Extraction
- [ ] Query: "Show me Apple news"
- [ ] **Verify**: Widget badge shows "AAPL" (not "Apple")
- [ ] **Verify**: Articles are about Apple Inc.

#### Test 3: Source Filtering
- [ ] Widget displays with "All Sources" button active
- [ ] Click "CNBC" filter button
- [ ] **Verify**: Only CNBC articles visible (blue dots)
- [ ] Click "Yahoo Finance" filter button
- [ ] **Verify**: Only Yahoo Finance articles visible (orange dots)
- [ ] Click "All Sources" button
- [ ] **Verify**: All articles visible again

#### Test 4: Article Interactions
- [ ] Click "Read More" button on any article
- [ ] **Verify**: Article URL opens in new browser tab
- [ ] **Verify**: URL is from CNBC or Yahoo Finance domain

#### Test 5: Chart Integration
- [ ] Click chart button in widget header
- [ ] **Verify**: GVSES trading chart switches to widget's symbol
- [ ] **Verify**: Chart displays correct ticker in header

#### Test 6: Refresh Functionality
- [ ] Click refresh button in widget header
- [ ] **Verify**: Widget shows loading state (if implemented)
- [ ] **Verify**: Widget updates with latest news articles
- [ ] **Verify**: Timestamps reflect current time

#### Test 7: Multiple Symbols
Test with various symbols to ensure generic support:
- [ ] TSLA (Tesla)
- [ ] AAPL (Apple)
- [ ] MSFT (Microsoft)
- [ ] GOOGL (Google)
- [ ] META (Meta/Facebook)
- [ ] NVDA (NVIDIA)
- [ ] AMZN (Amazon)
- [ ] SPY (S&P 500 ETF)

### Automated Testing with Playwright

**Test Script**: `backend/test_chatkit_widget_rendering.py`
```python
import asyncio
from playwright.async_api import async_playwright

async def test_widget_rendering():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Navigate to GVSES
        await page.goto("http://localhost:5175")

        # Wait for ChatKit to load
        await page.wait_for_selector("iframe[name='chatkit']", timeout=10000)

        # Send query via ChatKit input
        chatkit_input = await page.query_selector("textarea[placeholder*='message']")
        await chatkit_input.fill("What's the latest news on TSLA?")
        await chatkit_input.press("Enter")

        # Wait for response (up to 30 seconds)
        await page.wait_for_timeout(30000)

        # Take screenshot of result
        await page.screenshot(path="widget_rendering_test.png")

        # Verify widget rendered (not JSON text)
        chatkit_iframe = page.frame_locator("iframe[name='chatkit']")

        # Check for widget card element (not text containing '{')
        widget_card = await chatkit_iframe.locator("div[role='article']").count()
        json_text = await chatkit_iframe.locator("text='{\"widgets\":'").count()

        print(f"Widget cards found: {widget_card}")
        print(f"JSON text found: {json_text}")

        assert widget_card > 0, "Widget card should be present"
        assert json_text == 0, "JSON text should NOT be present"

        await browser.close()

asyncio.run(test_widget_rendering())
```

### Performance Benchmarks

**Target Metrics**:
- Widget render time: < 2 seconds from query send
- News fetch time: 3-5 seconds (CNBC + Yahoo hybrid via MCP)
- Interactive actions: < 500ms response time
- Chart integration: < 1 second to update chart

---

## Part 7: Troubleshooting Guide

### Issue 1: Widget Still Displays as JSON Text

**Symptoms**:
- ChatKit shows `{"widgets": [{"type": "Card"...}]}` as text
- No visual widget rendering

**Root Causes**:
1. Agent Builder output format still set to TEXT
2. Widget not uploaded to Agent Builder
3. Widget data mapping incorrect
4. Agent Builder workflow not published

**Fixes**:
1. Open Agent Builder → Verify output node format = WIDGET
2. Check "Widgets" tab → Ensure "Market News Feed" uploaded
3. Verify data mapping in output node configuration
4. Click "Publish" and wait for deployment

### Issue 2: Empty Widget or No Articles

**Symptoms**:
- Widget renders but shows 0 articles
- Widget shows error message

**Root Causes**:
1. MCP tool returning no data
2. Data transformation failing
3. Symbol extraction incorrect

**Debugging**:
```bash
# Test MCP tool directly
curl "http://localhost:8000/api/stock-news?symbol=TSLA"

# Check backend logs
# Look for MCP tool call errors
```

**Fixes**:
1. Verify MCP server running: `cd market-mcp-server && npm start`
2. Check MCP tool response format matches transformation logic
3. Add error handling in transformation node

### Issue 3: Wrong Symbol in Widget

**Symptoms**:
- Widget badge shows incorrect ticker
- Articles don't match expected company

**Root Cause**: Symbol extraction logic not working

**Fix**:
1. Update agent prompt with explicit symbol mapping:
```markdown
SYMBOL MAPPINGS:
- Tesla, Tesla Inc → TSLA
- Apple, Apple Inc → AAPL
- Microsoft, Microsoft Corp → MSFT
- Google, Alphabet → GOOGL
- Facebook, Meta → META
```

2. Add fallback: If symbol extraction fails, ask user for clarification

### Issue 4: Source Filter Not Working

**Symptoms**:
- Clicking CNBC/Yahoo buttons doesn't filter articles
- All articles always visible

**Root Cause**: `sourceType` field missing or incorrect

**Fix**:
1. Verify data transformation includes sourceType derivation:
```javascript
sourceType: article.source.toLowerCase().includes('cnbc') ? 'cnbc' : 'yahoo'
```

2. Check MCP tool response includes source field

### Issue 5: Interactive Actions Not Working

**Symptoms**:
- Clicking chart button does nothing
- Refresh button not working
- "Read More" links broken

**Root Causes**:
1. Action handlers not configured in Agent Builder
2. Frontend not listening for action events

**Fixes**:
1. Add action handler nodes in Agent Builder for:
   - `chart.setSymbol`
   - `news.refresh`
2. Verify `browser.openUrl` action payload includes valid URLs

### Issue 6: Widget Not Persisting in Conversation History

**Symptoms**:
- Refreshing page loses widget
- Only text visible in conversation history

**Root Cause**: Supabase message schema doesn't support widget JSON

**Fix** (Phase 3):
1. Update Supabase `messages` table schema:
```sql
ALTER TABLE messages ADD COLUMN widget_data JSONB;
```

2. Modify save logic in `RealtimeChatKit.tsx`:
```typescript
await supabase.from('messages').insert({
  conversation_id,
  role: 'assistant',
  content: textContent,
  widget_data: widgetJson  // NEW: Store widget separately
});
```

3. Modify load logic to reconstruct widget on page load

---

## Part 8: Deployment Checklist

### Pre-Deployment Verification

- [ ] Agent Builder workflow published (note version number)
- [ ] Market News Feed widget uploaded
- [ ] Output format set to WIDGET
- [ ] Data transformation node tested
- [ ] Symbol extraction working for 10+ symbols
- [ ] Source filtering functional
- [ ] Interactive actions configured
- [ ] Backend MCP tool returning correct data
- [ ] Frontend ChatKit component updated (if needed)
- [ ] All manual tests passing
- [ ] Playwright automated tests passing

### Deployment to Production

**Environment Variables** (`backend/.env`):
```bash
# Agent Builder
OPENAI_API_KEY=sk-...
AGENT_BUILDER_WORKFLOW_ID=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736

# MCP Servers
MCP_MARKET_SERVER_URL=http://localhost:3001
MCP_ALPACA_SERVER_URL=http://localhost:3003

# Supabase
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...

# ChatKit
CHATKIT_SESSION_ENDPOINT=https://api.openai.com/v1/agents/sessions
```

**Docker Deployment**:
```bash
# Build and deploy
docker-compose up --build -d

# Verify services
docker-compose ps

# Check logs
docker-compose logs -f backend
docker-compose logs -f market-mcp-server

# Test production widget
curl "https://gvses.fly.dev/api/stock-news?symbol=TSLA"
```

### Monitoring

**Key Metrics to Track**:
1. Widget render success rate (vs. JSON text display)
2. Average widget render time
3. MCP tool response times
4. Error rates per symbol
5. User engagement with interactive actions (chart, refresh, read more)

**Logging**:
```python
# Add to backend/mcp_server.py
import logging

logger.logging.getLogger(__name__)

@app.get("/api/stock-news")
async def get_stock_news(symbol: str):
    logger.info(f"Fetching news for symbol: {symbol}")

    try:
        news_data = await market_service.get_news(symbol)
        logger.info(f"Received {len(news_data['news'])} articles for {symbol}")
        return news_data
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Part 9: Phase 2 & 3 Roadmap

### Phase 2: Additional Widget Types

After Market News Feed is working, add:

**1. Technical Levels Widget**
- Source: ChatKit Studio "Technical Levels" widget
- Data: Support/Resistance levels, QE, ST, LTB
- MCP Tool: `get_technical_levels`
- Complexity: Medium

**2. Pattern Detection Widget**
- Source: ChatKit Studio "Pattern Detection" widget
- Data: Head & Shoulders, Triangles, Wedges
- MCP Tool: `detect_chart_patterns`
- Complexity: Medium

**3. Trading Chart Display Widget**
- Source: ChatKit Studio "Trading Chart Display" widget
- Data: OHLCV candlestick chart image
- Integration: TradingView Lightweight Charts snapshot
- Complexity: High (requires chart image generation)

**4. Economic Calendar Widget**
- Source: ChatKit Studio "Economic Calendar" widget
- Data: NFP, CPI, Fed meetings, GDP
- MCP Tool: `get_forex_calendar` (forex-mcp-server)
- Complexity: Low

### Phase 3: Advanced Features

**1. Widget Persistence in Supabase**
- Update message schema to store widget JSON
- Modify save/load logic
- Test conversation history with mixed content

**2. If/Else Routing in Agent Builder**
- News query → Market News Feed widget
- Technical query → Technical Levels widget
- Pattern query → Pattern Detection widget
- General query → Text response only

**3. Multi-Widget Responses**
- Single query returns multiple widgets
- Example: "Analyze TSLA" → News + Technical Levels + Pattern Detection
- Layout: Stacked widget cards

**4. Real-Time Widget Updates**
- WebSocket streaming for live news
- Auto-refresh on market hours
- Push notifications for breaking news

---

## Part 10: Success Metrics

### Definition of Success (Phase 1)

**Primary Goal**: Widget renders visually instead of JSON text

**Success Criteria**:
- ✅ 100% of queries return visual widgets (0% JSON text)
- ✅ Widget works with ANY stock symbol (tested with 20+ symbols)
- ✅ Source filtering functional (CNBC/Yahoo/All)
- ✅ Interactive actions working (chart, refresh, read more)
- ✅ Color-coded source indicators visible
- ✅ Article descriptions properly truncated
- ✅ Widget render time < 2 seconds
- ✅ MCP tool response time 3-5 seconds
- ✅ No console errors in browser
- ✅ No backend errors in logs

### User Experience Validation

**Before Fix** (JSON Text Display):
```
User: "What's the latest news on TSLA?"

Agent: {"response_text":"Here are the latest TSLA market news headlines:","query_intent":"news","symbol":"TSLA","widgets":[{"type":"Card","size":"lg",...}]}
```
**User Reaction**: 😞 Confused, can't read JSON, poor UX

**After Fix** (Visual Widget Display):
```
User: "What's the latest news on TSLA?"

Agent:
┌─────────────────────────────────────────────────┐
│ Market News Feed                    [TSLA] 🔄 📈 │
├─────────────────────────────────────────────────┤
│ [All Sources] [CNBC] [Yahoo Finance]            │
├─────────────────────────────────────────────────┤
│ 🔵 Trump buys at least $82 million in bonds... │
│    CNBC • 2 hours ago                           │
│    Tesla CEO Elon Musk announced...             │
│    [Read More]                                  │
│ ─────────────────────────────────────────────── │
│ 🟠 Tesla stock surges on earnings beat         │
│    Yahoo Finance • 5 hours ago                  │
│    Shares of Tesla jumped 8% after...          │
│    [Read More]                                  │
│ ─────────────────────────────────────────────── │
│ ... (8 more articles)                           │
└─────────────────────────────────────────────────┘
```
**User Reaction**: 😊 Clear, professional, easy to scan, interactive

---

## Conclusion

**Implementation Complexity**: Low (primarily configuration, not development)

**Timeline**:
- Widget upload: 10 minutes
- Agent Builder configuration: 1 hour
- Testing: 1 hour
- Deployment: 30 minutes
- **Total**: 2-4 hours

**Risk Level**: Low (using production-ready ChatKit Studio widget)

**Confidence Level**: Very High (based on Jeeves 2.0 working example)

**Next Action**: Upload Market News Feed widget to Agent Builder and change output format to WIDGET

---

**Document Version**: 1.0
**Created**: November 16, 2025
**Author**: Claude Code (ULTRATHINK Analysis)
**Status**: 🟢 Ready for Implementation
**Phase**: 1 (Market News Widget)
