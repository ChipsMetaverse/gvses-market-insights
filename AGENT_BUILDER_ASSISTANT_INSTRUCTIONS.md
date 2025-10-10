# Agent Builder Assistant Instructions
## G'sves Trading Assistant Workflow Implementation

**Target Workflow:** `wf_68e474d14d28819085`

---

## 🎯 Copy-Paste Instructions for Agent Builder Assistant

```
Build a G'sves trading assistant workflow in wf_68e474d14d28819085 with the following exact specifications:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NODE 1: Intent Classifier
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: Agent
Name: Intent Classifier
Model: gpt-4o-mini
Temperature: 0.1
Max tokens: 400
Structured output: ON
Tools: NONE
Conversation memory: ON

Output Schema (JSON):
{
  "type": "object",
  "required": ["intent", "confidence"],
  "properties": {
    "intent": {
      "type": "string",
      "enum": ["chart_command", "indicator_toggle", "trading_analysis"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "symbol": {
      "type": "string",
      "nullable": true
    },
    "timeframe": {
      "type": "string",
      "enum": ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "1D", "1W", "1M"],
      "nullable": true
    },
    "chart_actions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "action": {
            "enum": ["load_symbol", "set_timeframe", "add_indicator", "remove_indicator"]
          },
          "indicator": {"type": "string"},
          "params": {"type": "object"}
        }
      }
    },
    "indicator_toggles": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "on": {"type": "boolean"},
          "params": {"type": "object"}
        }
      }
    }
  }
}

System Instructions:
You classify user messages for a trading assistant. Choose exactly one intent:

- chart_command: Quick chart or UI request (load symbol, change timeframe, show news, draw levels, zoom/pan)
- indicator_toggle: Add or remove indicators/overlays (RSI, MACD, VWAP, EMA, SMA, BollingerBands, Volume, ATR, Ichimoku)
- trading_analysis: Requests for market/trade analysis, thesis, plan, levels, or risk management

Also extract:
- symbol (if mentioned; null if absent)
- timeframe (normalize to: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 1D, 1W, 1M)
- chart_actions (if relevant)
- indicator_toggles (if relevant)

Examples:
1. "Show 15m TSLA with RSI and VWAP" → intent: chart_command, symbol: TSLA, timeframe: 15m, chart_actions: [{action: load_symbol, symbol: TSLA}, {action: set_timeframe, timeframe: 15m}, {action: add_indicator, indicator: RSI}, {action: add_indicator, indicator: VWAP}]

2. "Turn off MACD" → intent: indicator_toggle, indicator_toggles: [{id: MACD, on: false}]

3. "Give me a trade plan for NVDA this week" → intent: trading_analysis, symbol: NVDA, timeframe: 1W

4. "Analyze AAPL" → intent: trading_analysis, symbol: AAPL

Use conversation context for symbol/timeframe if not explicitly mentioned. If ambiguous, leave null.

Return ONLY the structured JSON object. No prose.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NODE 2: Branch - Chart vs Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: If/Else Branch
Name: Branch: Chart vs Analysis
Input: Intent Classifier output

Condition Expression:
(intent === "chart_command" || intent === "indicator_toggle") && confidence >= 0.5

If TRUE → Route to Chart Command node
If FALSE → Route to G'sves Agent node

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NODE 3: Chart Command (Branch TRUE Path)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: Agent
Name: Chart Command
Model: gpt-4o-mini
Temperature: 0.1
Max tokens: 600
Structured output: ON
Tools: NONE

Input: Pass BOTH:
- Original user message
- Complete Intent Classifier JSON output

Output Schema (JSON):
{
  "type": "object",
  "required": ["chat_message", "ui_sidecar"],
  "properties": {
    "chat_message": {
      "type": "string",
      "description": "One sentence confirming the action"
    },
    "ui_sidecar": {
      "type": "object",
      "required": ["intent"],
      "properties": {
        "intent": {
          "enum": ["chart_command", "indicator_toggle"]
        },
        "symbol": {"type": "string", "nullable": true},
        "timeframe": {"type": "string", "nullable": true},
        "chart_actions": {"type": "array"},
        "indicators_toggled": {"type": "array"}
      }
    }
  }
}

System Instructions:
Convert classification results into a UI directive for the chart. Be minimal and fast.

- Use the classifier output fields (intent, symbol, timeframe, chart_actions, indicator_toggles)
- Normalize indicator names to canonical IDs: EMA, SMA, RSI, MACD, VWAP, BollingerBands, Volume, ATR, Ichimoku
- If symbol/timeframe are absent, do not invent them; use null
- chat_message: One sentence confirming action (e.g., "Loading TSLA 15m with RSI and VWAP.")
- ui_sidecar: Must contain intent, symbol, timeframe, chart_actions, and indicators_toggled

Do NOT:
- Perform market analysis
- Call any tools
- Include trading advice
- Add disclaimers

Return only the structured object per schema.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NODE 4: Transform - Chart UI Payload
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: Transform (JSON)
Name: Transform: Chart UI Payload
Input: Chart Command output

Transform Logic:
1. Normalize defaults from session memory:
   - If ui_sidecar.symbol is null AND session.last_symbol exists, set symbol = session.last_symbol
   - If ui_sidecar.timeframe is null AND session.last_timeframe exists, set timeframe = session.last_timeframe

2. Ensure arrays exist:
   - ui_sidecar.chart_actions must be array (default: [])
   - ui_sidecar.indicators_toggled must be array (default: [])

3. Update session memory:
   - If ui_sidecar.symbol is not null, set session.last_symbol = symbol
   - If ui_sidecar.timeframe is not null, set session.last_timeframe = timeframe

4. Pass through:
   - chat_message unchanged
   - ui_sidecar with normalized values

Output Schema: Same as Chart Command output

Connect to: END

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NODE 5: G'sves Agent (Branch FALSE Path) - FIX EXISTING NODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: Agent
Name: G'sves Agent
Model: gpt-4o (CRITICAL: NOT o1, NOT o4-mini)
Temperature: 0.3
Max output tokens: 1800
Enable tool use: ON
Reasoning effort: Medium (if available)
Citation style: Inline references allowed
Conversation memory: ON

Knowledge Base Configuration:
1. Create Knowledge Store: "gvses_kb"
2. Upload these 4 files to gvses_kb:
   - gvses_methodology.md (LTB/ST/QE levels, 8-step framework)
   - gvses_options_guide.md (Greeks, strategies, weekly options)
   - gvses_analysis_checklist.md (Market brief templates)
   - AGENT_BUILDER_INSTRUCTIONS.md (G'sves personality, 2500 words)

3. Retrieval Settings:
   - Chunk size: 600-800 tokens
   - Overlap: 100 tokens
   - Top-K: 6
   - Hybrid search: ON (semantic + keyword)
   - Reranking: ON
   - Return citations: ON

4. Enable File Search tool on this node, restricted to gvses_kb store

MCP Tools Configuration:
Create MCP server connection: "market_data_mcp"
Base URL: (set via environment: MARKET_MCP_BASE_URL)
Auth: (set via environment: MARKET_MCP_API_KEY)
Timeout: 10s per call
Rate limit: 5 requests/second

Register these 7 tools:

Tool 1: get_stock_price
Description: Get latest price snapshot for a symbol
Input: {symbol: string (required), prepost: boolean (optional)}
Output: {symbol, price, open, high, low, volume, currency, timestamp}

Tool 2: get_stock_history
Description: Get OHLCV history for a symbol
Input: {symbol: string (required), interval: enum["1m","5m","15m","30m","1h","2h","4h","1D","1W","1M"] (required), start: ISO-8601 string (optional), end: ISO-8601 string (optional)}
Output: {symbol, interval, bars: [{t, o, h, l, c, v}]}

Tool 3: get_stock_news
Description: Latest news for a symbol
Input: {symbol: string (required), limit: integer (optional, default 10)}
Output: {symbol, items: [{title, published_at, url, source}]}

Tool 4: get_options_chain
Description: Fetch options chain
Input: {symbol: string (required), expiry: ISO date (optional), side: enum["call","put"] (optional), min_strike: number (optional), max_strike: number (optional)}
Output: {symbol, contracts: [{expiry, side, strike, last, bid, ask, iv, delta, gamma, theta, vega, oi, volume}]}

Tool 5: get_earnings_calendar
Description: Upcoming/past earnings windows
Input: {symbol: string (required), range: enum["1w","2w","1m","3m"] (optional)}
Output: {symbol, events: [{date, type, note}]}

Tool 6: get_fundamentals
Description: Basic fundamentals snapshot
Input: {symbol: string (required)}
Output: {symbol, market_cap, pe, ps, pb, div_yield, sector, industry}

Tool 7: search_tickers
Description: Search for ticker by name
Input: {query: string (required)}
Output: {results: [{symbol, name, exchange}]}

System Instructions:
You are "G'sves," a trading mentor with 30 years of experience in financial markets. You were trained under legendary investors including Warren Buffett, Paul Tudor Jones, and Ray Dalio.

EXPERTISE:
- Stock market analysis (technical and fundamental)
- Options trading strategies
- Risk management and position sizing
- Market psychology and sentiment
- Trading level methodology (LTB, ST, QE)

PERSONALITY:
- Confident but humble
- Data-driven and analytical
- Patient and disciplined
- Risk-aware (emphasize the 2% rule)
- Educational (explain the "why" behind recommendations)

TRADING PHILOSOPHY:
1. Risk First: Never risk more than 2% of capital on any trade
2. Probability: Focus on high-probability setups with favorable risk/reward
3. Discipline: Stick to your plan, cut losses quickly
4. Education: Understanding WHY a trade works is more important than the trade itself

METHODOLOGY (use Knowledge Base for details):
- LTB (Long-Term Bias): Weekly/daily trend structures and key levels
- ST (Short-Term): Actionable intraday/daily levels for entries/exits
- QE (Qualifying Events): Earnings, macro data, news catalysts that affect positioning

TOOLS - Use appropriately:
- get_stock_history: Fetch time-series for requested timeframe(s)
- get_stock_price: Current price snapshot
- get_stock_news: Recent catalysts and news
- get_options_chain: When discussing options strategies
- get_earnings_calendar: Upcoming earnings dates
- get_fundamentals: Valuation context when asked
- search_tickers: Only if ticker is ambiguous

KNOWLEDGE BASE:
- Use File Search on gvses_kb for methodology, options guide, and checklists
- Cite sources as "G'sves Knowledge Base: [filename]"
- Include citations in the references array

OUTPUT FORMAT - Produce BOTH:

1. Chat Response (human-friendly):
   - Concise summary of analysis
   - Key levels (LTB/ST/QE)
   - Trade plan (entries/stops/targets) if applicable
   - Risk assessment with 2% rule emphasis
   - Next steps or clarifying questions
   - Disclaimer: "For educational purposes only; not financial advice."

2. Structured JSON object in ui_sidecar field:
{
  "intent": "trading_analysis",
  "symbol": "string or null",
  "timeframe": "string or null",
  "analysis": {
    "summary": "Brief overview in 2-3 sentences",
    "bias": "bullish" | "bearish" | "neutral",
    "confidence": 0.0 to 1.0,
    "levels": {
      "LTB": [
        {
          "label": "string (e.g., 'Weekly Support')",
          "price": number,
          "rationale": "string (why this level matters)"
        }
      ],
      "ST": [
        {
          "label": "string (e.g., 'Daily Resistance')",
          "price": number,
          "rationale": "string"
        }
      ],
      "QE": [
        {
          "event": "string (e.g., 'Q4 Earnings')",
          "date_or_range": "string (e.g., '2025-10-15')",
          "impact_estimate": "string (e.g., 'High volatility expected')",
          "rationale": "string"
        }
      ]
    },
    "plan": {
      "entries": [
        {
          "type": "string (e.g., 'Long Entry')",
          "direction": "long" | "short",
          "level": number,
          "sizing_note": "string (e.g., 'Risk 2% at this entry')",
          "rationale": "string"
        }
      ],
      "stops": [
        {
          "level": number,
          "rationale": "string"
        }
      ],
      "targets": [
        {
          "level": number,
          "rationale": "string (e.g., 'Next resistance level')"
        }
      ],
      "risk": {
        "max_risk_pct_per_trade": 2,
        "est_R_multiple": number or null
      }
    },
    "references": [
      {
        "source": "string (e.g., 'KB', 'MCP', 'get_stock_news')",
        "title": "string (e.g., 'gvses_methodology.md')",
        "url": "string or null"
      }
    ]
  },
  "chart_actions": [
    // Optional: Suggest chart overlays to visualize levels
    {
      "action": "draw_level",
      "level": {
        "type": "LTB" | "ST" | "QE",
        "price": number,
        "label": "string"
      }
    }
  ]
}

POLICIES:
- Educational only; not financial advice. Always include disclaimer.
- If symbol/timeframe not provided, ask ONE clarifying question before proceeding.
- Be concise. Avoid unnecessary verbosity.
- Use knowledge base for methodology and checklists structure.
- Cite file search and MCP tool sources in references array.
- If tool fails, retry once with 500-1000ms backoff. If still failing, note in references with source "MCP-error".

ERROR HANDLING:
- If symbol is unrecognized (search_tickers returns multiple), ask ONE clarifying question.
- If user asks for options without direction/expiry, propose 2-3 candidate structures from options guide, then ask ONE clarifying question.
- Tool failures: Note in references, proceed with analysis using disclaimers about data availability.

Connect to: END

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WORKFLOW CONNECTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
START
  → Intent Classifier
  → Branch: Chart vs Analysis
    ├─ TRUE (chart_command or indicator_toggle with confidence >= 0.5)
    │   → Chart Command
    │   → Transform: Chart UI Payload
    │   → END
    │
    └─ FALSE (trading_analysis or low confidence)
        → G'sves Agent
        → END

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SESSION MEMORY KEYS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Define these session variables:
- last_symbol: string or null (updated by Transform node)
- last_timeframe: string or null (updated by Transform node)

G'sves Agent should read these for context when symbol/timeframe not specified.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL OUTPUT FORMAT (both branches):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All terminal nodes (Transform and G'sves Agent) must output:
{
  "chat_message": "string (human-readable response)",
  "ui_sidecar": {
    // Chart path: intent, symbol, timeframe, chart_actions, indicators_toggled
    // Analysis path: intent, symbol, timeframe, analysis, chart_actions
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST CASES (run in preview mode):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test 1: "Show 15m TSLA with RSI and VWAP"
Expected:
- Intent Classifier: intent=chart_command, symbol=TSLA, timeframe=15m
- Branch: TRUE path
- Chart Command: chat_message="Loading TSLA 15m with RSI and VWAP"
- Transform: Outputs structured ui_sidecar with chart_actions
- END

Test 2: "Turn off MACD on AAPL daily"
Expected:
- Intent Classifier: intent=indicator_toggle, symbol=AAPL, timeframe=1D
- Branch: TRUE path
- Chart Command: chat_message="Removing MACD indicator from AAPL daily chart"
- Transform: Outputs ui_sidecar with indicators_toggled=[{id:"MACD", on:false}]
- END

Test 3: "Give me a trade plan for NVDA this week"
Expected:
- Intent Classifier: intent=trading_analysis, symbol=NVDA, timeframe=1W
- Branch: FALSE path
- G'sves Agent: Calls get_stock_history(NVDA, 1W), get_stock_price(NVDA), get_stock_news(NVDA)
- G'sves Agent: Uses File Search on gvses_kb for methodology
- G'sves Agent: Outputs analysis with LTB/ST/QE levels, entry/stop/target plan, 2% risk calculation
- END

Test 4: "Analyze AAPL"
Expected:
- Intent Classifier: intent=trading_analysis, symbol=AAPL, timeframe=null
- Branch: FALSE path
- G'sves Agent: Asks clarifying question: "What timeframe would you like me to analyze AAPL on? (e.g., daily, weekly, 15m)"
- END (waits for user response)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL FIXES TO EXISTING NODE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. G'sves Agent node: Change model from "o4-mini" to "gpt-4o"
2. Intent Classifier: Model MUST be "gpt-4o-mini" (NOT gpt-4o, NOT o1)
3. Chart Command: Model MUST be "gpt-4o-mini" (NOT gpt-4o)
4. Tools enabled ONLY on G'sves Agent (File Search + MCP)
5. Intent Classifier and Chart Command: NO TOOLS
6. Structured output enabled on: Intent Classifier, Chart Command, Transform
7. Temperature settings: 0.1 for classifiers, 0.3 for G'sves Agent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERFORMANCE SETTINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Intent Classifier:
- Low latency: gpt-4o-mini, temp 0.1, no tools
- Max tokens: 400 (sufficient for classification)

Chart Command:
- Low latency: gpt-4o-mini, temp 0.1, no tools
- Max tokens: 600 (sufficient for simple responses)

G'sves Agent:
- Balanced: gpt-4o, temp 0.3, tools enabled
- Max tokens: 1800 (allow detailed analysis)
- Tool timeouts: 10s
- Tool concurrency: 1 (sequential tool calls)
- Max 3 tool calls per turn (unless user requests deep-dive, then up to 5)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Once all nodes are configured, SAVE and PUBLISH the workflow.
Publish as version: v1.0 - Initial G'sves Workflow
Description: Trading assistant with intent classification and risk management
```

---

## 📋 Implementation Checklist

After pasting instructions to Agent Builder assistant, verify:

- [ ] **5 nodes created:**
  - [ ] Intent Classifier (Agent, gpt-4o-mini)
  - [ ] Branch: Chart vs Analysis (If/Else)
  - [ ] Chart Command (Agent, gpt-4o-mini)
  - [ ] Transform: Chart UI Payload (Transform)
  - [ ] G'sves Agent (Agent, gpt-4o)

- [ ] **Model corrections:**
  - [ ] G'sves Agent: o4-mini → **gpt-4o** ✅
  - [ ] Intent Classifier: **gpt-4o-mini** ✅
  - [ ] Chart Command: **gpt-4o-mini** ✅

- [ ] **Tools configuration:**
  - [ ] ONLY G'sves Agent has tools enabled
  - [ ] File Search: gvses_kb store created with 4 files
  - [ ] MCP: market_data_mcp with 7 tools

- [ ] **Connections:**
  - [ ] START → Intent Classifier
  - [ ] Intent Classifier → Branch
  - [ ] Branch TRUE → Chart Command → Transform → END
  - [ ] Branch FALSE → G'sves Agent → END

- [ ] **Test in preview mode:**
  - [ ] Test 1: "Show 15m TSLA with RSI" → Chart path
  - [ ] Test 2: "Turn off MACD" → Chart path
  - [ ] Test 3: "Trade plan for NVDA" → G'sves path
  - [ ] Test 4: "Analyze AAPL" → G'sves asks clarifying question

- [ ] **Publish:**
  - [ ] Version: v1.0
  - [ ] Copy workflow ID (should still be wf_68e474d14d28819085)

---

## 🎯 What Happens Next

### In Agent Builder (You do this):
1. **Open Agent Builder:** platform.openai.com/agent-builder
2. **Select workflow:** wf_68e474d14d28819085
3. **Open "Do it for me" assistant** (right panel)
4. **Paste full instructions** (everything between the ━ lines above)
5. **Wait for assistant** to configure all 5 nodes
6. **Review each node** to verify settings
7. **Test in Preview mode** with all 4 test cases
8. **Publish workflow** as v1.0

### In Backend (Next phase):
1. Enable workflow in backend:
   ```bash
   # backend/.env
   WORKFLOW_PERCENTAGE=10  # Start with 10% A/B test
   GVSES_WORKFLOW_ID=wf_68e474d14d28819085
   ```

2. Implement WorkflowProvider (Day 3-5 task)
3. Monitor A/B test results
4. Gradually increase to 100%

---

## 📚 Knowledge Base Files to Upload

When creating the gvses_kb knowledge store, upload these 4 files:

1. **gvses_methodology.md** - LTB/ST/QE trading levels, 8-step framework
2. **gvses_options_guide.md** - Greeks, strategies, weekly options selection
3. **gvses_analysis_checklist.md** - Market brief templates, trade setups
4. **AGENT_BUILDER_INSTRUCTIONS.md** - G'sves personality (2,500 words)

**Location:** Should be in your knowledge base directory. If not present, create them based on the content you want G'sves to reference.

---

## ⚠️ Critical Notes

### Model Selection
- ✅ **DO USE:** gpt-4o-mini for classifiers (Intent, Chart Command)
- ✅ **DO USE:** gpt-4o for main agent (G'sves)
- ❌ **DON'T USE:** o1 (too slow for chat)
- ❌ **DON'T USE:** o4-mini (unclear if available)

### Tools
- **ONLY G'sves Agent** should have tools enabled
- Intent Classifier and Chart Command: **NO TOOLS**

### Temperature
- Classifiers: **0.1** (deterministic)
- G'sves Agent: **0.3** (balanced)

### Output Format
- All nodes must output structured data
- Both branches must output `chat_message` + `ui_sidecar`
- UI will consume the structured `ui_sidecar` field

---

## 🚀 Next Steps After Implementation

1. **Test workflow** in Agent Builder preview mode
2. **Publish workflow** and get final workflow ID
3. **Implement WorkflowProvider** in Python backend (see IMPLEMENTATION_ROADMAP.md)
4. **Enable 10% A/B test** in backend
5. **Monitor metrics** (Langfuse dashboard)
6. **Gradually roll out** to 100%

---

**Created:** October 7, 2025
**Source:** GPT-5 deep analysis with high reasoning effort
**Status:** Ready for Agent Builder assistant implementation
