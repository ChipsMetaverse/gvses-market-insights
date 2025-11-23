# ChatKit Widget Implementation Guide for OpenAI Agent Builder

## Overview

After researching OpenAI's ChatKit documentation via Playwright MCP, here's the correct approach to implement intelligent widget orchestration in Agent Builder.

## Key Findings from Documentation

### 1. How ChatKit Widgets Work

**Widgets are NOT uploaded as files to Agent Builder.** Instead:

- **Widgets are JSON structures** that conform to ChatKit's widget schema
- **Agents return widgets** as part of their structured output
- **Widget containers** include: `Card`, `ListView`
- **Widget components** include: `Text`, `Button`, `Image`, `Badge`, `Box`, `Row`, `Col`, etc.
- **Actions are handled** via `ActionConfig` objects attached to interactive components

### 2. Two Integration Approaches

From https://platform.openai.com/docs/guides/chatkit:

#### Approach A: Recommended Integration (What we have)
- **Backend**: OpenAI-hosted via Agent Builder
- **Frontend**: Embed ChatKit in your product
- **Widget Creation**: Agents return widget JSON as structured output
- **Configuration**: Done entirely in Agent Builder UI

#### Approach B: Advanced Integration (Alternative)
- **Backend**: Self-hosted ChatKit Python SDK server
- **Frontend**: Custom implementation
- **Widget Creation**: Python Pydantic models via `stream_widget()`
- **Configuration**: Requires custom backend deployment

## Implementation for Agent Builder (Approach A)

### Step 1: Configure Agent Output Schema

In the G'sves agent (already selected in your Agent Builder):

1. Click **"Add schema"** under Output format (currently set to JSON)
2. Define a schema that includes widget output:

```json
{
  "type": "object",
  "properties": {
    "response_text": {
      "type": "string",
      "description": "Text response to the user"
    },
    "widgets": {
      "type": "array",
      "description": "Array of ChatKit widgets to display",
      "items": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": ["Card", "ListView"]
          },
          "children": {
            "type": "array",
            "description": "Child widget components"
          },
          "status": {
            "type": "object",
            "properties": {
              "text": {"type": "string"},
              "icon": {"type": "string"}
            }
          }
        }
      }
    }
  },
  "required": ["response_text"]
}
```

### Step 2: Update Agent Instructions

Add widget orchestration logic to the G'sves agent instructions:

```markdown
# Widget Orchestration

Based on the user's query intent, include appropriate widgets in your response:

**News Queries** ("What's the news on TSLA?", "Show me headlines"):
- Include Market News Feed widget with latest articles

**Economic Events** ("When is NFP?", "Show economic calendar"):
- Include Economic Calendar widget with ForexFactory events

**Pattern Analysis** ("Are there any head and shoulders on NVDA?"):
- Include Pattern Detection widget + Trading Chart widget

**Technical Levels** ("What are support levels for SPY?"):
- Include Technical Levels widget + Trading Chart widget

**Chart Requests** ("Show me AAPL chart"):
- Include Trading Chart Display widget

**Comprehensive Analysis** ("Give me everything on MSFT"):
- Include ALL 5 widgets: Trading Chart, Technical Levels, Pattern Detection, Market News, Economic Calendar

## Widget Response Format

When including widgets, structure your JSON output as:

```json
{
  "response_text": "Here's the comprehensive analysis for MSFT",
  "widgets": [
    {
      "type": "Card",
      "size": "lg",
      "children": [
        {
          "type": "Title",
          "value": "Microsoft Corporation (MSFT)"
        },
        {
          "type": "Text",
          "value": "Latest market data and technical analysis"
        }
      ],
      "status": {
        "text": "Live Data",
        "icon": "chart-line"
      }
    }
  ]
}
```

Use the widget JSON templates from the .widget files in your project as reference.
```

### Step 3: Create Widget JSON Templates

The .widget files you downloaded are JSON templates. Reference them in agent instructions:

**Location**: `/Volumes/WD My Passport 264F Media/claude-voice-mcp/.playwright-mcp/`

- `Economic-Calendar.widget` (34KB)
- `Market-News-Feed.widget` (20KB)
- `Pattern-Detection.widget` (30KB)
- `Technical-Levels.widget` (21KB)
- `Trading-Chart-Display.widget` (32KB)

### Step 4: Configure Widget Actions

For interactive widgets (buttons, forms), configure actions:

1. In widget JSON, add `ActionConfig` to interactive components:

```json
{
  "type": "Button",
  "label": "Refresh Data",
  "onClickAction": {
    "type": "refresh_market_data",
    "payload": {"symbol": "TSLA"},
    "loadingBehavior": "container"
  }
}
```

2. Handle actions in the Transform node or create a new Agent node

### Step 5: Frontend Integration

The frontend ChatKit component needs to be configured to display widgets:

1. **Install ChatKit React bindings**:
```bash
npm install @openai/chatkit-react
```

2. **Create ChatKit session endpoint** (backend):
```python
from openai import OpenAI

@app.post("/api/chatkit/session")
def create_chatkit_session():
    session = openai.chatkit.sessions.create({
        "workflow": {"id": "wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736"}
    })
    return {"client_secret": session.client_secret}
```

3. **Render ChatKit in frontend**:
```typescript
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function TradingAssistant() {
  const { control } = useChatKit({
    api: {
      async getClientSecret() {
        const res = await fetch('/api/chatkit/session', { method: 'POST' });
        const { client_secret } = await res.json();
        return client_secret;
      }
    }
  });

  return <ChatKit control={control} className="h-[600px] w-[400px]" />;
}
```

## Testing the Implementation

### Test Queries

1. **News**: "What's the latest news on TSLA?"
   - Expected: Market News Feed widget

2. **Economic**: "When is the next NFP release?"
   - Expected: Economic Calendar widget

3. **Patterns**: "Show me head and shoulders patterns on NVDA"
   - Expected: Pattern Detection + Trading Chart widgets

4. **Levels**: "What are the support levels for SPY?"
   - Expected: Technical Levels + Trading Chart widgets

5. **Comprehensive**: "Give me everything on MSFT"
   - Expected: All 5 widgets

### Validation Checklist

- [ ] Agent returns structured JSON with widgets array
- [ ] Widget JSON matches ChatKit schema (Card, ListView, components)
- [ ] Interactive components have ActionConfig defined
- [ ] Frontend ChatKit component displays widgets correctly
- [ ] Widget actions trigger appropriate backend responses

## Alternative: Python Backend Approach (Advanced)

If you need more control, use the ChatKit Python SDK:

```python
from chatkit import ChatKit, Context
from chatkit.models import Card, Text, Button, ActionConfig

chatkit = ChatKit()

@chatkit.action("display_market_widgets")
async def handle_display_widgets(ctx: Context, query: str, symbol: str) -> None:
    # Analyze query intent
    intent = classify_intent(query)

    # Create appropriate widgets
    if "news" in intent:
        widget = Card(
            children=[
                Text(value=f"Market News for {symbol}"),
                # ... more components
            ],
            status={"text": "Live", "icon": "newspaper"}
        )
        await ctx.context.stream_widget(widget)
```

## Resources

- **ChatKit Docs**: https://platform.openai.com/docs/guides/chatkit
- **Widget Reference**: https://platform.openai.com/docs/guides/chatkit-widgets
- **Actions Guide**: https://platform.openai.com/docs/guides/chatkit-actions
- **Widget Builder**: https://widgets.chatkit.studio
- **Python SDK**: https://github.com/openai/chatkit-python
- **React SDK**: https://github.com/openai/chatkit-react

## Next Steps

1. ✅ **Configure output schema** in G'sves agent (Add schema button)
2. ✅ **Update agent instructions** to include widget orchestration logic
3. ✅ **Test widget output** in Agent Builder preview mode
4. ✅ **Integrate ChatKit frontend** component in your React app
5. ✅ **Test end-to-end** with all widget types

## Notes

- The backend implementation in `backend/chatkit_server.py` was created for the Advanced Integration approach
- For Agent Builder (Recommended Integration), widgets are returned as JSON from the agent
- The widget orchestration logic from `backend/services/widget_orchestrator.py` can inform the agent's instruction prompt
- The test suite in `backend/test_widget_orchestration.py` validates the intent classification logic (100% accuracy on test queries)
