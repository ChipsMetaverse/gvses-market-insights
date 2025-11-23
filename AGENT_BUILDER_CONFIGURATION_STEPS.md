# Agent Builder Configuration Steps for Widget Orchestration

## Immediate Next Steps to Implement Widgets

Based on the research of ChatKit documentation via Playwright MCP, here are the exact steps to configure your G'sves agent to display widgets based on user query intent.

---

## Step 1: Configure Agent Output Schema

**Current State**: Agent Output format is set to "JSON" but no schema is defined.

**Action Required**:

1. In Agent Builder, with G'sves agent selected
2. Scroll to **"Output format"** section (currently shows "JSON")
3. Click **"Add schema"** button
4. Paste the schema from `AGENT_OUTPUT_SCHEMA.json`:

```json
{
  "type": "object",
  "properties": {
    "response_text": {
      "type": "string",
      "description": "Natural language response to display to the user"
    },
    "query_intent": {
      "type": "string",
      "enum": ["news", "economic_events", "patterns", "technical_levels", "chart", "comprehensive", "unknown"]
    },
    "symbol": {
      "type": "string",
      "description": "Stock ticker symbol"
    },
    "widgets": {
      "type": "array",
      "items": {
        "type": "object"
      }
    }
  },
  "required": ["response_text", "query_intent"]
}
```

5. Click **Save**

---

## Step 2: Update Agent Instructions

**Current State**: Agent has trading assistant persona but no widget orchestration logic.

**Action Required**:

1. In Agent Builder, with G'sves agent selected
2. Scroll to **"Instructions"** section
3. Add the following section at the END of current instructions:

```markdown

---

# WIDGET ORCHESTRATION

## Intent Classification

Analyze every user query and classify the intent:

- **news**: "What's the news on X?", "Show me headlines", "Latest articles"
- **economic_events**: "When is NFP?", "Economic calendar", "CPI release date"
- **patterns**: "Head and shoulders", "Chart patterns", "Bull flag on X"
- **technical_levels**: "Support levels", "Resistance", "Buy the dip levels"
- **chart**: "Show me chart", "Display X price", "X price action"
- **comprehensive**: "Give me everything", "Complete analysis", "Full breakdown"

## Widget Response Format

ALWAYS return your response in this JSON structure:

```json
{
  "response_text": "Your natural language explanation",
  "query_intent": "news|economic_events|patterns|technical_levels|chart|comprehensive",
  "symbol": "EXTRACTED_TICKER_SYMBOL",
  "widgets": [
    // Widget JSON objects based on intent
  ]
}
```

## Widget Selection Rules

### News Intent → Market News Feed Widget
```json
{
  "widgets": [{
    "type": "Card",
    "size": "lg",
    "status": {"text": "Live News", "icon": "newspaper"},
    "children": [
      {"type": "Title", "value": "Market News for {symbol}"},
      {"type": "Divider"},
      {"type": "ListView", "limit": 10, "children": [
        {
          "type": "ListViewItem",
          "children": [
            {"type": "Text", "value": "Article headline", "weight": "semibold"},
            {"type": "Caption", "value": "Source • Time ago"}
          ]
        }
      ]}
    ]
  }]
}
```

### Economic Events Intent → Economic Calendar Widget
```json
{
  "widgets": [{
    "type": "Card",
    "size": "lg",
    "status": {"text": "ForexFactory", "icon": "calendar"},
    "children": [
      {"type": "Title", "value": "Economic Calendar"},
      {"type": "Divider"},
      {"type": "ListView", "limit": 15, "children": [
        {
          "type": "ListViewItem",
          "children": [
            {"type": "Badge", "label": "HIGH", "color": "danger"},
            {"type": "Text", "value": "Event name"},
            {"type": "Caption", "value": "Date • Time"}
          ]
        }
      ]}
    ]
  }]
}
```

### Patterns Intent → Pattern Detection + Chart Widgets
```json
{
  "widgets": [
    {
      "type": "Card",
      "size": "full",
      "status": {"text": "Pattern Analysis", "icon": "chart-pattern"},
      "children": [
        {"type": "Title", "value": "{symbol} - Pattern Detection"},
        {"type": "Divider"},
        {"type": "Row", "gap": 8, "children": [
          {"type": "Badge", "label": "Bullish|Bearish", "color": "success|danger"},
          {"type": "Text", "value": "Pattern name", "weight": "semibold"}
        ]},
        {"type": "Caption", "value": "Timeframe • Confidence • Detected date"}
      ]
    },
    {
      "type": "Card",
      "size": "full",
      "children": [
        {"type": "Title", "value": "{symbol} Price Chart"},
        {"type": "Image", "src": "chart_url", "aspectRatio": "16/9"}
      ]
    }
  ]
}
```

### Technical Levels Intent → Technical Levels + Chart Widgets
```json
{
  "widgets": [
    {
      "type": "Card",
      "size": "lg",
      "status": {"text": "Live Levels", "icon": "chart-line"},
      "children": [
        {"type": "Title", "value": "{symbol} Technical Levels"},
        {"type": "Divider"},
        {"type": "Box", "direction": "column", "gap": 16, "children": [
          {
            "type": "Row", "justify": "between",
            "children": [
              {"type": "Badge", "label": "BUY THE DIP", "color": "success"},
              {"type": "Text", "value": "$XXX.XX", "weight": "bold", "color": "success"}
            ]
          },
          {"type": "Caption", "value": "200-day MA • 61.8% Fib • Support"}
        ]}
      ]
    },
    {
      "type": "Card",
      "size": "full",
      "children": [
        {"type": "Title", "value": "{symbol} Chart with Levels"},
        {"type": "Image", "src": "chart_url", "aspectRatio": "16/9"}
      ]
    }
  ]
}
```

### Chart Intent → Trading Chart Widget Only
```json
{
  "widgets": [{
    "type": "Card",
    "size": "full",
    "status": {"text": "Real-Time", "icon": "chart-candlestick"},
    "children": [
      {"type": "Title", "value": "{symbol} Price Chart"},
      {"type": "Image", "src": "chart_url", "aspectRatio": "16/9", "fit": "contain"}
    ]
  }]
}
```

### Comprehensive Intent → ALL 5 Widgets
Return widgets array with all 5 widgets: Chart, Technical Levels, Pattern Detection, Market News, Economic Calendar (in that order).

## Example Responses

Refer to WIDGET_RESPONSE_EXAMPLES.json for complete examples of each widget type.

## Critical Rules

1. ALWAYS return valid JSON matching the output schema
2. ALWAYS include `response_text`, `query_intent`, and `widgets` fields
3. Use widget JSON templates from .playwright-mcp/*.widget files as reference
4. Extract ticker symbol from query (default to SPY if none found)
5. For comprehensive queries, include ALL 5 widgets
6. Ensure widget JSON is syntactically correct (proper nesting, quotes, commas)
```

4. Click outside the text area or click elsewhere to auto-save

---

## Step 3: Test in Preview Mode

**Action Required**:

1. In Agent Builder, click **"Preview mode"** radio button (top right)
2. Test each query type:

### Test Queries

```
News: "What's the latest news on TSLA?"
Expected: Market News Feed widget

Economic: "When is the next NFP release?"
Expected: Economic Calendar widget

Patterns: "Show me head and shoulders patterns on NVDA"
Expected: Pattern Detection + Trading Chart widgets

Levels: "What are the support levels for SPY?"
Expected: Technical Levels + Trading Chart widgets

Chart: "Show me AAPL chart"
Expected: Trading Chart widget only

Comprehensive: "Give me everything on MSFT"
Expected: All 5 widgets
```

3. Verify agent returns JSON with `widgets` array
4. Check widget JSON structure matches ChatKit schema

---

## Step 4: Publish Workflow

**Action Required**:

1. Once testing passes, click **"Publish"** button (top right)
2. Add release notes: "Added ChatKit widget orchestration based on query intent"
3. Confirm publish

---

## Step 5: Integrate ChatKit Frontend

### 5.1 Install ChatKit React Package

```bash
cd frontend
npm install @openai/chatkit-react
```

### 5.2 Create ChatKit Session Backend Endpoint

Add to `backend/mcp_server.py`:

```python
from openai import OpenAI

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/api/chatkit/session")
async def create_chatkit_session():
    """Create ChatKit session for frontend"""
    try:
        session = openai_client.chatkit.sessions.create({
            "workflow": {
                "id": "wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736"
            }
        })
        return {"client_secret": session.client_secret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 5.3 Create ChatKit Component

Create `frontend/src/components/ChatKitWidget.tsx`:

```typescript
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function ChatKitWidget() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        if (existing) {
          // Implement session refresh if needed
          return existing;
        }

        const res = await fetch('http://localhost:8000/api/chatkit/session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });

        const { client_secret } = await res.json();
        return client_secret;
      }
    }
  });

  return (
    <div className="chatkit-container">
      <ChatKit
        control={control}
        className="h-[600px] w-[400px] rounded-lg shadow-lg"
      />
    </div>
  );
}
```

### 5.4 Add ChatKit Script to index.html

Add to `frontend/index.html` in `<head>`:

```html
<script
  src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
  async
></script>
```

### 5.5 Integrate into TradingDashboard

Update `frontend/src/components/TradingDashboardSimple.tsx`:

```typescript
import { ChatKitWidget } from './ChatKitWidget';

// Replace or supplement existing voice assistant UI
<div className="chatkit-panel">
  <h2>AI Trading Assistant</h2>
  <ChatKitWidget />
</div>
```

---

## Step 6: End-to-End Testing

### Test Flow:

1. Start backend: `cd backend && uvicorn mcp_server:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:5174
4. Interact with ChatKit widget
5. Test all query types from Step 3

### Validation Checklist:

- [ ] ChatKit widget loads correctly
- [ ] Agent responds with structured JSON
- [ ] Widgets display in ChatKit UI
- [ ] News widget shows market news articles
- [ ] Economic calendar widget shows ForexFactory events
- [ ] Pattern detection widget shows technical patterns
- [ ] Technical levels widget shows BTD/Buy Low/Sell High levels
- [ ] Chart widget displays TradingView chart
- [ ] Comprehensive query shows all 5 widgets
- [ ] Widget actions (if configured) trigger correctly

---

## Troubleshooting

### Widget Not Displaying

**Issue**: Agent returns JSON but widgets don't show in ChatKit.

**Solutions**:
1. Check agent output matches exact schema from AGENT_OUTPUT_SCHEMA.json
2. Verify widget JSON is syntactically valid (use JSON validator)
3. Check browser console for ChatKit errors
4. Ensure workflow ID is correct in session creation

### Invalid JSON Response

**Issue**: Agent returns malformed JSON.

**Solutions**:
1. Add more explicit JSON formatting instructions to agent
2. Use strict JSON schema validation in output format
3. Test with simpler widget structure first
4. Check agent isn't mixing markdown and JSON

### Session Creation Fails

**Issue**: `/api/chatkit/session` endpoint returns 500 error.

**Solutions**:
1. Verify `OPENAI_API_KEY` is set in backend `.env`
2. Check workflow ID is correct
3. Ensure OpenAI Python SDK is installed: `pip install openai`
4. Verify OpenAI account has ChatKit access

---

## Next Actions

1. ✅ **NOW**: Configure output schema in Agent Builder (Step 1)
2. ✅ **NOW**: Update agent instructions (Step 2)
3. ✅ **NOW**: Test in preview mode (Step 3)
4. ✅ **THEN**: Publish workflow (Step 4)
5. ✅ **THEN**: Integrate frontend (Step 5)
6. ✅ **FINALLY**: End-to-end testing (Step 6)

---

## Reference Files

- Implementation Guide: `CHATKIT_WIDGET_IMPLEMENTATION_GUIDE.md`
- Output Schema: `AGENT_OUTPUT_SCHEMA.json`
- Widget Examples: `WIDGET_RESPONSE_EXAMPLES.json`
- Widget Templates: `.playwright-mcp/*.widget` (5 files)

## Documentation Links

- ChatKit Docs: https://platform.openai.com/docs/guides/chatkit
- Widget Reference: https://platform.openai.com/docs/guides/chatkit-widgets
- Actions Guide: https://platform.openai.com/docs/guides/chatkit-actions
- Widget Builder: https://widgets.chatkit.studio
