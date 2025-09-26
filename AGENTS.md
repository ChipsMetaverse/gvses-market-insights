# Repository Guidelines

## Project Structure & Module Organization
- Backend: `backend/`
  - FastAPI app: `backend/mcp_server.py`
  - Orchestrator: `backend/services/agent_orchestrator.py`
  - MCP clients/manager: `backend/mcp_client.py`, `backend/mcp_manager.py`
  - Services and tools: `backend/services/`, `backend/tools/`
  - Knowledge: `backend/training/json_docs/`, embedded KB: `backend/knowledge_base_embedded.json`
- Frontend: `frontend/`
  - Services (chart control, agent orchestrator): `frontend/src/services/`
  - Playwright-style demos/tests: `frontend/test_*.cjs`
- Test/utility scripts live alongside code: `test_*.py`, `test_*.sh`, `*.cjs`.

## Build, Test, and Development Commands
- Backend setup
  - `cd backend && pip install -r requirements.txt`
  - Run API: `uvicorn mcp_server:app --host 0.0.0.0 --port 8000`
- Frontend dev
  - `cd frontend && npm install && npm run dev` (default Vite dev server)
- Latency/TA smoke (examples)
  - `curl -sS -X POST http://localhost:8000/api/agent/orchestrate -H 'Content-Type: application/json' -d '{"query":"Get AAPL price"}'`
  - `node frontend/test_agent_chart_control.cjs`

## Coding Style & Naming Conventions
- Python: PEP8, 4-space indent, type hints required for new/edited functions. Prefer explicit names (e.g., `_process_query_responses`, `_extract_response_text`).
- TS/JS: Use descriptive names; keep files in `frontend/src/services/` small and single‑purpose. Prefer camelCase for functions and PascalCase for types.
- Keep feature flags/environment switches explicit (e.g., `USE_RESPONSES`, `OPENAI_API_KEY`).

## Testing Guidelines
- Backend: add targeted tests next to modules (e.g., `backend/test_*.py`). Keep tests fast; mock network when possible.
- Frontend: runnable demo tests in `frontend/test_*.cjs` (Playwright-style). Capture screenshots for visual changes.
- Name tests after the unit/feature under test: `test_<feature>.py` / `test_<feature>.cjs`.

## Commit & Pull Request Guidelines
- Commits: imperative, concise, scoped. Example: `feat(orchestrator): prefer output_text for Responses extraction`.
- PRs must include:
  - What changed and why; affected files/paths
  - How to run/verify (commands, screenshots/log snippets)
  - Any flags/env required (e.g., `USE_RESPONSES=true`)

## Security & Configuration Tips
- Required env: `OPENAI_API_KEY` (and optional `ALPACA_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`). Do not commit secrets.
- Prefer small models for summarization (`gpt-4o-mini`) and parallel tool execution for latency.

---

# AGENT ISSUES & FIXES REQUIRED

## Executive Summary
The agent currently has critical issues that prevent it from:
1. Answering general questions about companies
2. Automatically switching charts when discussing different symbols
3. Handling non-trading queries properly
4. Providing comprehensive market analysis with synchronized visualization

## Issue 1: Company Information Queries Return Trading Data
**Symptom:** When asked "What is PLTR?", the agent responds with price levels and trading analysis instead of explaining that PLTR is Palantir Technologies, a data analytics company.

**Root Cause:** Query routing in `backend/services/agent_orchestrator.py` misclassifies informational queries as price queries.

**Evidence:**
```python
# Line 3289-3293: Intent classification
if (any(term in ql for term in ["price", "quote", "cost", "worth", "value", "trading at", "how much is"]) 
    and len(query.split()) < 12
    and not any(term in ql for term in ["analysis", "technical", "news", "chart", "pattern"])):
    return "price-only"
```

**Files Affected:**
- `backend/services/agent_orchestrator.py` (lines 3285-3313)
- `backend/services/agent_orchestrator.py` (lines 342-396: `_maybe_answer_with_price_query`)

**Solution Required:**
```python
# Add BEFORE price-only check in _classify_intent (line 3286):
if any(phrase in ql for phrase in ["what is", "who is", "tell me about", "explain"]) and self._extract_symbol(query):
    # Check if asking about the company, not the price
    if not any(term in ql for term in ["price", "cost", "worth", "trading"]):
        return "company-info"
```

## Issue 2: Chart Does Not Sync with Query Symbol
**Symptom:** When discussing PLTR, the chart remains on TSLA. The agent analyzes one symbol but displays another.

**Root Cause:** Chart commands are not automatically generated when a symbol is detected in the query.

**Evidence:**
- Query: "What is PLTR"
- Response contains PLTR analysis
- Chart shows TSLA (no `LOAD:PLTR` command generated)
- No chart_commands in response JSON

**Files Affected:**
- `backend/services/agent_orchestrator.py` (lines 865-1055: `_build_chart_commands`)
- `backend/services/agent_orchestrator.py` (lines 879-883: chart intent keywords)
- `frontend/src/components/TradingDashboardSimple.tsx` (lines 427-432)

**Solution Required:**
```python
# In _build_chart_commands, ALWAYS generate LOAD command for detected symbol:
def _build_chart_commands(self, query: str, tool_results: Optional[Dict[str, Any]]) -> List[str]:
    commands = []
    primary_symbol = self._extract_primary_symbol(query, tool_results)
    
    # ALWAYS switch chart to the symbol being discussed
    if primary_symbol:
        commands.append(f"LOAD:{primary_symbol.upper()}")
    
    # Rest of existing logic...
```

## Issue 3: Overly Restrictive Query Routing
**Symptom:** Non-trading queries get rejected or misrouted. General questions receive no response or incorrect responses.

**Root Cause:** Multiple "fast paths" exit early before queries can reach the LLM.

**Evidence:**
```python
# Lines 3386-3393: Quick price response exits early
quick_price_response = await self._maybe_answer_with_price_query(query, conversation_history)
if quick_price_response:
    return quick_price_response  # NEVER REACHES LLM!
```

**Files Affected:**
- `backend/services/agent_orchestrator.py` (lines 3344-3438: `process_query`)
- `backend/services/agent_orchestrator.py` (lines 302-341: static templates)

**Solution Required:**
- Allow "general" intent queries to reach LLM
- Don't return early from fast paths unless absolutely certain
- Add fallback to LLM for unhandled queries

## Issue 4: System Prompt Bias Toward Trading
**Symptom:** Even when general queries reach the LLM, it responds with trading analysis because the system prompt configures it as a "trading assistant."

**Root Cause:** System prompt is too specialized for trading.

**Evidence:**
```python
# Lines 2214-2287: _build_system_prompt
base_prompt = """You are an AI trading assistant specialized in market analysis...
Focus on: price movements, technical indicators, support/resistance levels..."""
```

**Files Affected:**
- `backend/services/agent_orchestrator.py` (lines 2214-2287)

**Solution Required:**
```python
base_prompt = """You are a comprehensive financial assistant that can:
1. Explain what companies are and their business models
2. Provide market analysis and trading insights
3. Answer general questions about stocks and investing
4. Navigate charts and technical analysis

When asked "What is [TICKER]", first explain what the company does.
When asked about price or trading, provide market analysis.
Always generate chart commands to display the relevant symbol."""
```

## Issue 5: Chart Commands at Wrong Response Level
**Symptom:** Even when chart_commands are generated, frontend may not receive them properly.

**Root Cause:** Response structure inconsistency - commands may be nested in `data` instead of top-level.

**Evidence:**
- Frontend expects: `response.chart_commands`
- Backend might send: `response.data.chart_commands`

**Files Affected:**
- `backend/routers/agent_router.py` (line 38: chart_commands field)
- `backend/services/agent_orchestrator.py` (return statements in multiple locations)
- `frontend/src/components/TradingDashboardSimple.tsx` (lines 427-432)

**Solution Required:**
Ensure ALL return paths include chart_commands at the TOP level:
```python
return {
    "text": response_text,
    "chart_commands": commands,  # ALWAYS at top level
    "tools_used": tools_used,
    "data": {...},  # Additional data here
    "timestamp": datetime.now().isoformat()
}
```

## Issue 6: No Company Information Tool
**Symptom:** LLM has no tool to fetch company descriptions, so it defaults to price analysis.

**Root Cause:** Missing tool for company information in tool schemas.

**Files Affected:**
- `backend/services/agent_orchestrator.py` (lines 528-757: `_get_tool_schemas`)

**Solution Required:**
Add new tool schema:
```python
{
    "type": "function",
    "function": {
        "name": "get_company_info",
        "description": "Get company description, business model, and basic information",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., AAPL, TSLA)"
                }
            },
            "required": ["symbol"]
        }
    }
}
```

## Implementation Priority & Testing

### Priority 1: Fix Chart Synchronization (Immediate)
1. **Modify `_build_chart_commands`** to always generate LOAD command for detected symbols
2. **Ensure chart_commands at top level** of all responses
3. **Test:** Query "What is PLTR" should switch chart from TSLA to PLTR

### Priority 2: Fix Query Routing (High)
1. **Add company-info intent** to `_classify_intent`
2. **Remove early returns** that block general queries
3. **Test:** "What is PLTR" should explain the company, not just price

### Priority 3: Fix System Prompt (High)
1. **Update `_build_system_prompt`** to handle general queries
2. **Add instructions** for company explanations
3. **Test:** Various "What is X" queries should return company info

### Priority 4: Add Company Info Tool (Medium)
1. **Create `get_company_info` tool** with basic descriptions
2. **Add to tool schemas**
3. **Implement tool execution**
4. **Test:** Tool should be called for company queries

## Verification Commands

```bash
# Test company info query
curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query": "What is PLTR?"}' | jq

# Expected response should have:
# - text: Explaining Palantir Technologies
# - chart_commands: ["LOAD:PLTR"]

# Test chart switching
curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Microsoft"}' | jq .chart_commands
# Should return: ["LOAD:MSFT"]

# Test general query
curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?"}' | jq .text
# Should return explanation, not trading data
```

## Debug Logging to Add

```python
# In process_query after intent classification:
logger.info(f"Query: '{query}' → Intent: {intent}")
logger.info(f"Symbol detected: {self._extract_symbol(query)}")

# Before returning response:
logger.info(f"Response includes chart_commands: {bool(response.get('chart_commands'))}")
if response.get('chart_commands'):
    logger.info(f"Chart commands: {response['chart_commands']}")
```

## Success Criteria
✅ "What is PLTR?" returns company description AND switches chart to PLTR
✅ "What is artificial intelligence?" returns general explanation
✅ Chart always shows the symbol being discussed
✅ All queries get meaningful responses (no dead ends)
✅ Response time remains under SLA targets
