# Widget Implementation Guide - Backend Integration

**Date**: November 13, 2025, 3:00 AM
**Status**: 📋 **IMPLEMENTATION READY** - Step-by-step guide to add widget support

---

## Understanding ChatKit Widgets

### Key Insight
**Widgets are NOT configured in Agent Builder UI**. Instead:
- Widgets are **returned by your backend** as part of agent responses
- Your backend generates widget JSON when appropriate
- ChatKit client renders the widget in the chat
- User clicks trigger actions back to your backend

---

## Architecture Overview

```
User: "Show me chart controls"
    ↓
Agent Builder → Your Backend API
    ↓
Backend: Detects request for controls
    ↓
Backend: Returns widget JSON in response
    ↓
ChatKit: Renders interactive widget
    ↓
User: Clicks "TSLA" button
    ↓
ChatKit: Sends action to backend
    ↓
Backend: Processes action (change_chart_symbol)
    ↓
Chart: Updates to TSLA
```

---

## Implementation Steps

### Step 1: Add Widget JSON File

Create a file to store the widget definition:

```bash
# backend/widgets/chart_controls.json
```

```json
{
  "type": "Card",
  "size": "md",
  "children": [
    {
      "type": "Col",
      "gap": 3,
      "children": [
        {
          "type": "Title",
          "value": "Trading Chart Controls",
          "size": "md"
        }
      ]
    },
    {
      "type": "Divider"
    },
    {
      "type": "Col",
      "gap": 2,
      "children": [
        {
          "type": "Caption",
          "value": "Symbol"
        },
        {
          "type": "Row",
          "wrap": "wrap",
          "gap": 2,
          "children": [
            {
              "type": "Button",
              "label": "AAPL",
              "variant": "solid",
              "onClickAction": {
                "type": "chart.setSymbol",
                "payload": { "symbol": "AAPL" }
              }
            },
            {
              "type": "Button",
              "label": "TSLA",
              "variant": "outline",
              "onClickAction": {
                "type": "chart.setSymbol",
                "payload": { "symbol": "TSLA" }
              }
            },
            {
              "type": "Button",
              "label": "NVDA",
              "variant": "outline",
              "onClickAction": {
                "type": "chart.setSymbol",
                "payload": { "symbol": "NVDA" }
              }
            },
            {
              "type": "Button",
              "label": "MSFT",
              "variant": "outline",
              "onClickAction": {
                "type": "chart.setSymbol",
                "payload": { "symbol": "MSFT" }
              }
            }
          ]
        }
      ]
    },
    {
      "type": "Divider"
    },
    {
      "type": "Col",
      "gap": 2,
      "children": [
        {
          "type": "Caption",
          "value": "Timeframe"
        },
        {
          "type": "Row",
          "wrap": "wrap",
          "gap": 2,
          "children": [
            {
              "type": "Button",
              "label": "1m",
              "variant": "solid",
              "onClickAction": {
                "type": "chart.setTimeframe",
                "payload": { "timeframe": "1m" }
              }
            },
            {
              "type": "Button",
              "label": "5m",
              "variant": "outline",
              "onClickAction": {
                "type": "chart.setTimeframe",
                "payload": { "timeframe": "5m" }
              }
            },
            {
              "type": "Button",
              "label": "15m",
              "variant": "outline",
              "onClickAction": {
                "type": "chart.setTimeframe",
                "payload": { "timeframe": "15m" }
              }
            },
            {
              "type": "Button",
              "label": "1h",
              "variant": "outline",
              "onClickAction": {
                "type": "chart.setTimeframe",
                "payload": { "timeframe": "1h" }
              }
            },
            {
              "type": "Button",
              "label": "1d",
              "variant": "outline",
              "onClickAction": {
                "type": "chart.setTimeframe",
                "payload": { "timeframe": "1d" }
              }
            }
          ]
        }
      ]
    },
    {
      "type": "Divider"
    },
    {
      "type": "Col",
      "gap": 2,
      "children": [
        {
          "type": "Caption",
          "value": "Indicators"
        },
        {
          "type": "Row",
          "wrap": "wrap",
          "gap": 2,
          "children": [
            {
              "type": "Button",
              "label": "SMA",
              "variant": "outline",
              "color": "info",
              "onClickAction": {
                "type": "chart.toggleIndicator",
                "payload": { "key": "sma" }
              }
            },
            {
              "type": "Button",
              "label": "EMA",
              "variant": "outline",
              "color": "info",
              "onClickAction": {
                "type": "chart.toggleIndicator",
                "payload": { "key": "ema" }
              }
            },
            {
              "type": "Button",
              "label": "Bollinger Bands",
              "variant": "outline",
              "color": "info",
              "onClickAction": {
                "type": "chart.toggleIndicator",
                "payload": { "key": "bb" }
              }
            },
            {
              "type": "Button",
              "label": "RSI",
              "variant": "outline",
              "color": "info",
              "onClickAction": {
                "type": "chart.toggleIndicator",
                "payload": { "key": "rsi" }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Step 2: Add Widget Action Handler

Create endpoint to handle widget button clicks:

```python
# backend/mcp_server.py

import json
from pathlib import Path

# Load widget definition
CHART_CONTROLS_WIDGET = json.loads(
    Path("widgets/chart_controls.json").read_text()
)

@app.post("/api/widget-action")
async def handle_widget_action(request: Request):
    """
    Handle widget button click actions

    Called when user clicks buttons in the chart controls widget
    """
    try:
        body = await request.json()
        action = body.get("action", {})
        item_id = body.get("itemId")

        action_type = action.get("type")
        payload = action.get("payload", {})

        logger.info(f"Widget action: {action_type} with payload: {payload}")

        if action_type == "chart.setSymbol":
            symbol = payload.get("symbol")
            # Store chart command for frontend polling
            await store_chart_command({
                "action": "change_symbol",
                "symbol": symbol
            })
            return JSONResponse({
                "success": True,
                "message": f"Chart updated to {symbol}"
            })

        elif action_type == "chart.setTimeframe":
            timeframe = payload.get("timeframe")
            await store_chart_command({
                "action": "set_timeframe",
                "timeframe": timeframe
            })
            return JSONResponse({
                "success": True,
                "message": f"Timeframe changed to {timeframe}"
            })

        elif action_type == "chart.toggleIndicator":
            indicator_key = payload.get("key")
            await store_chart_command({
                "action": "toggle_indicator",
                "indicator": indicator_key,
                "enabled": True
            })
            return JSONResponse({
                "success": True,
                "message": f"Toggled {indicator_key} indicator"
            })

        else:
            return JSONResponse({
                "success": False,
                "message": f"Unknown action type: {action_type}"
            }, status_code=400)

    except Exception as e:
        logger.error(f"Widget action error: {e}")
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=500)


async def store_chart_command(command: dict):
    """
    Store chart command for frontend polling

    This integrates with your existing chart command system
    """
    # Use your existing chart command storage mechanism
    # This is likely already implemented in your chartControlService
    pass
```

### Step 3: Add Widget Response Endpoint

Create endpoint that returns widget when requested:

```python
@app.post("/api/chat-widget")
async def get_chart_controls_widget(request: Request):
    """
    Return chart controls widget

    Called by agent when user asks for chart controls
    """
    try:
        body = await request.json()
        query = body.get("query", "")

        # Check if user is asking for chart controls
        control_keywords = ["chart control", "show controls", "chart options", "trading controls"]

        if any(keyword in query.lower() for keyword in control_keywords):
            return JSONResponse({
                "widget": CHART_CONTROLS_WIDGET,
                "message": "Here are your trading chart controls. Click any button to update the chart."
            })

        return JSONResponse({
            "message": "What would you like to do?"
        })

    except Exception as e:
        logger.error(f"Widget response error: {e}")
        return JSONResponse({
            "error": str(e)
        }, status_code=500)
```

### Step 4: Update Agent Instructions

Modify the Chart Control Agent instructions to return widgets:

```markdown
# Chart Control Agent - Widget Mode

## Role
You are the Chart Control Agent for the GVSES trading platform. You provide interactive chart controls via widgets.

## When to Show Widget

When user asks for:
- "show me chart controls"
- "I want to control the chart"
- "give me trading controls"
- "show chart options"

**Return the chart controls widget** by calling the backend widget endpoint.

## Response Format

When showing widget:
```
Here are your trading chart controls. Click any button to update the chart:

[Widget will render here]

You can:
• Change symbols: Click AAPL, TSLA, NVDA, or MSFT
• Adjust timeframe: Select 1m, 5m, 15m, 1h, or 1d
• Toggle indicators: Enable SMA, EMA, Bollinger Bands, or RSI
```

## Important Notes

- Widgets provide better UX than voice commands
- No authentication issues (unlike MCP servers)
- Users get visual feedback on selections
- Actions are explicit and reliable
```

---

## Alternative: Direct Response Integration

If you want the agent to return widgets directly in responses:

### Option A: Python SDK Integration

```python
from chatkit import ChatKit, Card, Button, Row, Col, Title, Caption, Divider

def create_chart_controls_widget(selected_symbol="AAPL", selected_timeframe="1m"):
    """Generate chart controls widget dynamically"""

    symbols = ["AAPL", "TSLA", "NVDA", "MSFT"]
    timeframes = ["1m", "5m", "15m", "1h", "1d"]
    indicators = [
        {"key": "sma", "label": "SMA"},
        {"key": "ema", "label": "EMA"},
        {"key": "bb", "label": "Bollinger Bands"},
        {"key": "rsi", "label": "RSI"}
    ]

    return Card(
        size="md",
        children=[
            Col(gap=3, children=[
                Title(value="Trading Chart Controls", size="md")
            ]),
            Divider(),
            Col(gap=2, children=[
                Caption(value="Symbol"),
                Row(
                    wrap="wrap",
                    gap=2,
                    children=[
                        Button(
                            label=sym,
                            variant="solid" if sym == selected_symbol else "outline",
                            onClickAction={
                                "type": "chart.setSymbol",
                                "payload": {"symbol": sym}
                            }
                        )
                        for sym in symbols
                    ]
                )
            ]),
            Divider(),
            Col(gap=2, children=[
                Caption(value="Timeframe"),
                Row(
                    wrap="wrap",
                    gap=2,
                    children=[
                        Button(
                            label=tf,
                            variant="solid" if tf == selected_timeframe else "outline",
                            onClickAction={
                                "type": "chart.setTimeframe",
                                "payload": {"timeframe": tf}
                            }
                        )
                        for tf in timeframes
                    ]
                )
            ]),
            Divider(),
            Col(gap=2, children=[
                Caption(value="Indicators"),
                Row(
                    wrap="wrap",
                    gap=2,
                    children=[
                        Button(
                            label=ind["label"],
                            variant="outline",
                            color="info",
                            onClickAction={
                                "type": "chart.toggleIndicator",
                                "payload": {"key": ind["key"]}
                            }
                        )
                        for ind in indicators
                    ]
                )
            ])
        ]
    )
```

### Option B: Direct JSON Response

```python
@app.post("/api/agent-response")
async def agent_response(request: Request):
    """
    Agent response that includes widgets
    """
    body = await request.json()
    query = body.get("query", "")

    if "chart controls" in query.lower():
        return JSONResponse({
            "type": "message",
            "content": "Here are your trading chart controls:",
            "widgets": [CHART_CONTROLS_WIDGET]
        })

    # Regular response for other queries
    return JSONResponse({
        "type": "message",
        "content": "How can I help you?"
    })
```

---

## Testing the Widget

### Test Widget Rendering

```bash
# 1. Start backend
cd backend && uvicorn mcp_server:app --reload

# 2. Test widget endpoint
curl -X POST http://localhost:8000/api/chat-widget \
  -H "Content-Type: application/json" \
  -d '{"query": "show me chart controls"}'

# Expected response:
# {
#   "widget": { ... chart controls widget JSON ... },
#   "message": "Here are your trading chart controls..."
# }
```

### Test Widget Actions

```bash
# Test button click action
curl -X POST http://localhost:8000/api/widget-action \
  -H "Content-Type: application/json" \
  -d '{
    "action": {
      "type": "chart.setSymbol",
      "payload": { "symbol": "TSLA" }
    },
    "itemId": "test-123"
  }'

# Expected response:
# {
#   "success": true,
#   "message": "Chart updated to TSLA"
# }
```

---

## Frontend Integration (if needed)

If you want to handle widgets in your React frontend:

```typescript
// frontend/src/services/widgetService.ts

export async function fetchChartControlsWidget() {
  const response = await fetch('/api/chat-widget', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: 'show me chart controls' })
  });

  const data = await response.json();
  return data.widget;
}

export async function handleWidgetAction(action: any, itemId: string) {
  const response = await fetch('/api/widget-action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, itemId })
  });

  return response.json();
}
```

---

## Deployment Checklist

- [ ] Create `backend/widgets/chart_controls.json` with widget definition
- [ ] Add `/api/widget-action` endpoint to handle button clicks
- [ ] Add `/api/chat-widget` endpoint to return widget
- [ ] Update agent instructions to trigger widget responses
- [ ] Test widget rendering in Agent Builder Preview
- [ ] Test button click actions
- [ ] Verify chart updates when buttons clicked
- [ ] Deploy to production
- [ ] Test end-to-end flow

---

## Advantages Recap

✅ **No MCP Authentication**: Bypasses Chart_Control_Backend issues
✅ **Visual Feedback**: Users see current selections
✅ **Better UX**: Click instead of voice/text
✅ **Reliable**: Direct action payloads, no parsing
✅ **Professional**: Clean, organized interface

---

## Next Steps

1. **Create widget file**: `backend/widgets/chart_controls.json`
2. **Implement handlers**: Add `/api/widget-action` endpoint
3. **Test locally**: Verify widget rendering and actions
4. **Deploy**: Push to production and test
5. **Optional**: Add more widgets for alerts, watchlist, etc.

The widget is designed and ready - now it just needs backend integration! 🚀
