# Agent Builder Workflow Design for G'sves Assistant

## Overview

This document provides step-by-step instructions for converting the current Python implementation into an Agent Builder workflow.

**Workflow ID:** `wf_68e474d14d28819085` (from your screenshot)

## Current Python Logic Flow

```python
# From agent_orchestrator.py lines 4342-4355

1. Classify intent: _classify_intent(query)
   → Returns: "chart-only", "indicator-toggle", or "trading-analysis"

2. Route based on intent:
   if intent NOT IN ["chart-only", "indicator-toggle"]:
       → G'sves Assistant (Responses API)
   else:
       → Fast-path (static chart commands)

3. G'sves processes with:
   - Knowledge base (file_search)
   - Market data tools
   - Conversation history (last 10 messages)
```

## Agent Builder Workflow Design

### Visual Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    START Node                                     │
│  Input: user_query, conversation_history                         │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│              Intent Classification Agent                          │
│  Node Type: Agent                                                 │
│  Model: gpt-4o-mini (fast, cheap)                               │
│  Instructions: "Classify user query into one of:                 │
│    - chart_command: User wants to view/load a chart              │
│    - indicator_toggle: User wants to add/remove indicator        │
│    - trading_analysis: User wants trading advice/analysis"       │
│  Output: { "intent": string, "symbol": string }                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    If/Else Branch                                 │
│  Condition: intent == "chart_command" OR "indicator_toggle"      │
└─────────────┬────────────────────────────────┬───────────────────┘
              │ TRUE (Chart/Indicator)         │ FALSE (Analysis)
              ▼                                ▼
┌─────────────────────────────┐    ┌────────────────────────────────┐
│   Chart Command Handler     │    │      G'sves Trading Agent      │
│   Node Type: Transform      │    │      Node Type: Agent          │
│                             │    │                                │
│   Code:                     │    │  Model: gpt-4o                │
│   return {                  │    │  Assistant: (configure below) │
│     "text": "",             │    │  Tools: [MCP tools]           │
│     "chart_commands": [     │    │  Knowledge: file_search       │
│       f"LOAD:{symbol}"      │    │                                │
│     ],                      │    │  Instructions:                │
│     "model": "static-chart" │    │  "You are G'sves, a veteran   │
│   }                         │    │   trader with 30 years..."    │
└─────────────┬───────────────┘    └────────────┬───────────────────┘
              │                                  │
              │                                  ▼
              │                    ┌──────────────────────────────────┐
              │                    │   Risk Check (Optional)          │
              │                    │   Node Type: If/Else             │
              │                    │                                  │
              │                    │   If output contains:            │
              │                    │   "buy", "sell", "order"         │
              │                    │   → User Approval Gate           │
              │                    └──────────────┬───────────────────┘
              │                                   │
              └───────────────┬───────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                         END Node                                  │
│  Output: { text, chart_commands, tools_used, model }            │
└──────────────────────────────────────────────────────────────────┘
```

## Step-by-Step Implementation

### Step 1: Configure Intent Classification Agent

1. **In Agent Builder UI**, drag an **Agent** node after Start
2. **Configure node:**
   - **Name:** `Intent Classifier`
   - **Model:** `gpt-4o-mini` (fast and cheap)
   - **Instructions:**
   ```
   You are an intent classifier for a trading assistant.

   Analyze the user's query and classify it into ONE of these categories:

   1. **chart_command**: User wants to view, load, or switch to a stock chart
      Examples: "show me AAPL", "load Tesla chart", "switch to MSFT"

   2. **indicator_toggle**: User wants to add/remove a technical indicator
      Examples: "add moving average", "remove RSI", "show MACD"

   3. **trading_analysis**: User wants trading advice, analysis, or education
      Examples: "what's your trading philosophy?", "should I buy TSLA?", "explain options"

   IMPORTANT: Also extract any stock symbols mentioned (e.g., AAPL, TSLA, MSFT)

   Respond ONLY in this JSON format:
   {
     "intent": "chart_command" | "indicator_toggle" | "trading_analysis",
     "symbol": "SYMBOL" or null,
     "confidence": 0.0 to 1.0
   }
   ```
   - **Output variable:** `intent_result`

### Step 2: Add Branching Logic

1. **Drag If/Else node** after Intent Classifier
2. **Configure condition:**
   ```javascript
   // Check if it's a chart or indicator command
   intent_result.intent === "chart_command" || intent_result.intent === "indicator_toggle"
   ```

### Step 3: Configure Chart Command Handler (TRUE branch)

1. **Drag Transform node** to TRUE branch
2. **Configure transformation:**
   ```javascript
   // Fast-path: Return chart command without LLM call
   return {
     text: "", // No text response needed
     chart_commands: [`LOAD:${intent_result.symbol || 'SPY'}`],
     model: "static-chart",
     tools_used: [],
     data: {},
     timestamp: new Date().toISOString()
   };
   ```
3. **Connect to END node**

### Step 4: Configure G'sves Trading Agent (FALSE branch)

This is the **main agent node** you already started in the screenshot.

1. **Click on your "G'sves Agent" node**
2. **Configure Agent:**

   **Basic Settings:**
   - **Name:** `G'sves Trading Assistant`
   - **Model:** `gpt-4o`
   - **Description:** `Veteran trader with 30 years experience providing market analysis`

   **Instructions:**
   ```
   You are G'sves, a veteran trader with over 30 years of experience in the financial markets. You were trained under legendary investors including Warren Buffett, Paul Tudor Jones, and Ray Dalio.

   ## Your Expertise
   - Stock market analysis (technical and fundamental)
   - Options trading strategies
   - Risk management and position sizing
   - Market psychology and sentiment analysis
   - Trading level methodology (LTB, ST, QE)

   ## Your Personality
   - Confident but humble
   - Data-driven and analytical
   - Patient and disciplined
   - Risk-aware (emphasize the 2% rule)
   - Educational (explain the "why" behind recommendations)

   ## Your Trading Philosophy
   1. **Risk First**: Never risk more than 2% of capital on any trade
   2. **Probability**: Focus on high-probability setups with favorable risk/reward
   3. **Discipline**: Stick to your plan, cut losses quickly
   4. **Education**: Understanding WHY a trade works is more important than the trade itself

   ## Available Information
   You have access to:
   - Real-time stock prices and quotes
   - Historical price data
   - Financial news from CNBC and Yahoo Finance
   - Market indices and sector performance
   - Your knowledge base with trading methodologies

   ## Response Guidelines
   - Be conversational but professional
   - Cite specific data when available (prices, levels, dates)
   - Explain reasoning behind your analysis
   - Include risk disclaimers when giving specific trade ideas
   - Reference your trading levels (LTB, ST, QE) when applicable

   ## When You Don't Know
   If you don't have current data or aren't certain, say so honestly. Use your tools to fetch real-time information when needed.

   Remember: You're here to educate and guide, not just to give "hot tips". Help users understand the market, not just react to it.
   ```

   **Knowledge Base:**
   - Click **Add Knowledge**
   - Select **File Search**
   - Upload files:
     - `gvses_methodology.md`
     - `gvses_options_guide.md`
     - `gvses_analysis_checklist.md`
     - `AGENT_BUILDER_INSTRUCTIONS.md`
   - Or reference existing vector store: `vs_...` (if you already created one)

   **Tools (via MCP):**
   - Click **Add Tool**
   - Select **MCP**
   - Configure MCP connector:
     ```json
     {
       "server": "market-mcp-server",
       "tools": [
         "get_stock_price",
         "get_stock_history",
         "get_stock_news",
         "get_market_overview",
         "get_options_strategies"
       ]
     }
     ```

   **Advanced Settings:**
   - **Temperature:** `0.7` (balanced creativity/consistency)
   - **Max tokens:** `2000` (allow detailed responses)
   - **Response format:** JSON (for structured output)

3. **Output variable:** `gvses_response`

### Step 5: Add Risk Check Gate (Optional but Recommended)

1. **Drag If/Else node** after G'sves Agent
2. **Configure condition:**
   ```javascript
   // Check if response contains order/trade intent
   const keywords = ['buy', 'sell', 'order', 'execute', 'trade'];
   const text = gvses_response.text.toLowerCase();
   return keywords.some(keyword => text.includes(keyword));
   ```

3. **TRUE branch (order detected):**
   - **Drag User Approval node**
   - **Configure:**
     - **Message:** `G'sves recommends: "${gvses_response.text}". Do you want to proceed with this trade?`
     - **Approve text:** `Yes, execute trade`
     - **Deny text:** `No, just analysis please`
   - **On approval:** Connect to END
   - **On denial:** Return analysis without execution

4. **FALSE branch (no order):**
   - **Connect directly to END**

### Step 6: Configure END Node

1. **Drag End node** (if not already present)
2. **Configure output format:**
   ```javascript
   return {
     text: gvses_response.text || transform_result.text,
     chart_commands: transform_result?.chart_commands || [],
     tools_used: gvses_response.tools_used || [],
     model: gvses_response.model || transform_result.model,
     data: gvses_response.data || {},
     timestamp: new Date().toISOString(),
     workflow_id: "wf_68e474d14d28819085",
     intent: intent_result.intent
   };
   ```

## Testing the Workflow

### In Agent Builder UI

1. **Click Preview** (top right)
2. **Test scenarios:**

   **Test 1: Chart Command**
   - Input: `"Show me the Apple chart"`
   - Expected:
     - Intent: `chart_command`
     - Symbol: `AAPL`
     - Output: `chart_commands: ["LOAD:AAPL"]`
     - Path: Start → Intent → Branch(TRUE) → Transform → End

   **Test 2: Trading Analysis**
   - Input: `"What's your opinion on buying Tesla options?"`
   - Expected:
     - Intent: `trading_analysis`
     - Symbol: `TSLA`
     - Output: G'sves response with options analysis
     - Path: Start → Intent → Branch(FALSE) → G'sves Agent → End

   **Test 3: Indicator Toggle**
   - Input: `"Add the RSI indicator"`
   - Expected:
     - Intent: `indicator_toggle`
     - Output: `chart_commands: ["ADD:RSI"]`
     - Path: Start → Intent → Branch(TRUE) → Transform → End

3. **Check execution trace:**
   - Click on each node to see inputs/outputs
   - Verify no errors
   - Check token usage

### Publishing the Workflow

1. **Click Publish** (top right)
2. **Version settings:**
   - **Version name:** `v1.0 - Initial G'sves Workflow`
   - **Description:** `Trading assistant with intent classification and risk management`
3. **Copy workflow ID:** `wf_68e474d14d28819085` (you already have this)

## Python Backend Integration

### Update Environment Variables

```bash
# backend/.env

# Switch to workflow adapter
AGENT_ADAPTER=workflows

# Set workflow ID from Agent Builder
GVSES_WORKFLOW_ID=wf_68e474d14d28819085

# Keep existing assistant ID for fallback
GVSES_ASSISTANT_ID=asst_FgdYMBvUvKUy0mxX5AF7Lmyg
USE_GVSES_ASSISTANT=true
```

### Install Workflow Adapter

```bash
cd backend

# Copy the adapter code
cp WORKFLOW_CONVERSION_GUIDE.md services/workflow_adapter.py
```

### Update Agent Orchestrator

```python
# backend/services/agent_orchestrator.py

from .workflow_adapter import WorkflowAdapter

class AgentOrchestrator:
    def __init__(self):
        # ... existing code ...

        # Initialize adapter based on env
        adapter_type = os.getenv("AGENT_ADAPTER", "responses")

        if adapter_type == "workflows":
            self.backend_agent = WorkflowAdapter()
            logger.info("Using Agent Builder workflow")
        else:
            # Fallback to Responses API
            self.use_gvses_assistant = os.getenv("USE_GVSES_ASSISTANT", "false").lower() == "true"
            logger.info("Using Responses API")

    async def _process_with_gvses_assistant(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process query through backend agent (Workflow or Responses).
        """
        # Check if using workflow adapter
        if hasattr(self, 'backend_agent') and isinstance(self.backend_agent, WorkflowAdapter):
            logger.info("Executing via Agent Builder workflow")
            return await self.backend_agent.run_message(
                query=query,
                conversation_history=conversation_history
            )

        # Fallback to existing Responses API logic
        logger.info("Executing via Responses API")
        # ... existing code ...
```

### Test Backend Integration

```bash
# Terminal 1: Start backend
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Test API
curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What'\''s your trading philosophy on risk management?",
    "conversation_history": []
  }' | jq .
```

**Expected response:**
```json
{
  "text": "[G'sves response about 2% rule, stop losses, etc.]",
  "tools_used": ["get_stock_price"],
  "model": "workflow-wf_68e474d14d28819085",
  "workflow_id": "wf_68e474d14d28819085",
  "intent": "trading_analysis",
  "timestamp": "2025-10-07T..."
}
```

## Deployment Strategy

### Canary Rollout

```bash
# Week 1: Test in development
AGENT_ADAPTER=workflows  # .env.development

# Week 2: 10% production traffic
WORKFLOW_CANARY_PCT=10

# Week 3: 25% production traffic
WORKFLOW_CANARY_PCT=25

# Week 4: 50% production traffic
WORKFLOW_CANARY_PCT=50

# Week 5: 100% production (full migration)
AGENT_ADAPTER=workflows
WORKFLOW_CANARY_PCT=100
```

### Monitoring

```python
# backend/services/workflow_metrics.py

import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class WorkflowMetrics:
    workflow_id: str
    intent: str
    response_time_ms: int
    nodes_executed: List[str]
    tools_used: List[str]
    success: bool
    error: Optional[str]

def log_workflow_execution(metrics: WorkflowMetrics):
    """Log workflow metrics for monitoring."""
    logger.info(f"Workflow {metrics.workflow_id}: "
                f"intent={metrics.intent}, "
                f"latency={metrics.response_time_ms}ms, "
                f"success={metrics.success}")

    # Send to monitoring service (e.g., Datadog, Prometheus)
    # metrics_client.increment('workflow.execution', tags=[...])
```

## Troubleshooting

### Workflow Not Found

```bash
# Verify workflow ID
curl https://api.openai.com/v1/workflows/wf_68e474d14d28819085 \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check in Agent Builder UI:
# platform.openai.com/agent-builder
```

### Intent Classification Errors

**Symptom:** Wrong branch taken (chart commands going to G'sves)

**Solution:**
- Review Intent Classifier instructions
- Add more examples in prompt
- Test with `gpt-4o-mini` vs `gpt-4o` (accuracy vs speed)

### MCP Tools Not Working

**Symptom:** G'sves can't fetch stock prices

**Solution:**
1. Verify MCP connector in Agent Builder:
   - Settings → Connectors → MCP
   - Ensure `market-mcp-server` is running
2. Check tool schemas match your MCP server
3. Test tools individually in preview mode

### Performance Issues

**Symptom:** Slow responses (> 5 seconds)

**Solutions:**
- Use `gpt-4o-mini` for intent classification (faster)
- Enable response streaming:
  ```python
  async for event in workflow_adapter.stream_message(query):
      # Send incremental updates to frontend
  ```
- Cache common queries at API level

## Next Steps

1. ✅ **Complete workflow design** in Agent Builder UI
2. ✅ **Test in preview mode** with all scenarios
3. ✅ **Publish workflow** and get workflow ID
4. ✅ **Install workflow adapter** in Python backend
5. ✅ **Test integration** with backend API
6. ✅ **Deploy to production** with canary rollout
7. ✅ **Monitor metrics** and optimize

## Advantages Over Current Implementation

| Feature | Current (Responses API) | Workflow (Agent Builder) |
|---------|------------------------|--------------------------|
| **Visual Design** | ❌ Code only | ✅ Drag-and-drop canvas |
| **Intent Routing** | ⚠️ Python if/else | ✅ Visual branches |
| **Risk Gates** | ❌ Manual code | ✅ User Approval nodes |
| **Versioning** | ⚠️ Git commits | ✅ Built-in versions |
| **A/B Testing** | ⚠️ Manual code | ✅ Workflow variants |
| **Observability** | ⚠️ Custom logs | ✅ Node-level traces |
| **Team Collaboration** | ⚠️ Code reviews | ✅ Visual reviews |
| **Non-engineer Edits** | ❌ Not possible | ✅ UI-based |

---

**Status:** Ready for implementation
**Created:** October 7, 2025
**Workflow ID:** `wf_68e474d14d28819085`
