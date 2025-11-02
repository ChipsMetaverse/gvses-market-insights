# Agent Chart Control Issue - Root Cause Analysis

## 🔴 **Problem Statement**
User reports: "doesn't seem like the agent can control the lightweight chart or can even see what is loaded."

When user asks "Map out my supports and resistance. On the chart", the agent:
- ❌ Returns JSON instead of executing chart commands
- ❌ Doesn't know what symbol is currently loaded (TSLA)
- ❌ Doesn't reference or use chart snapshot with vision analysis
- ❌ Asks user to specify ticker symbol despite chart clearly showing TSLA

## 🔍 **Root Cause Analysis**

### 1. **System Prompt Blind Spot**
The agent's system prompt (`_build_system_prompt`) doesn't inform the LLM about:
- What symbol/chart is currently visible to the user
- That chart snapshots are captured and available
- That vision analysis of the chart has already been performed
- How to generate chart commands for drawing

**Evidence:**
```python
# Lines 3085-3200 in agent_orchestrator.py
def _build_system_prompt(self, retrieved_knowledge: str = "") -> str:
    base_prompt = """You are G'sves, expert market analyst...
    # NO MENTION OF:
    # - Current chart context
    # - Chart snapshot availability
    # - Drawing command syntax
    # - Vision analysis results
```

### 2. **Missing Chart Context Injection**
The query processing flow doesn't inject current chart state:

**Current Flow:**
1. User: "Map out my supports and resistance. On the chart"
2. Agent receives query WITHOUT chart context
3. Agent doesn't know TSLA is loaded
4. Agent asks: "which stock, ETF, or index?"

**Should Be:**
1. User: "Map out my supports and resistance. On the chart"
2. System injects: "Current chart: TSLA 1D timeframe, snapshot available"
3. Agent knows context and proceeds with analysis
4. Agent generates: `SUPPORT:430.00 SUPPORT:448.00 RESISTANCE:460.00`

### 3. **Chart Snapshot Available But Not Used**
The backend captures chart snapshots with vision analysis:

**Evidence from TradingChart.tsx (lines 502-525):**
```typescript
// Capture chart snapshot 500ms after data loads
setTimeout(async () => {
  const canvas = chartContainerRef.current?.querySelector('canvas')
  if (canvas) {
    const imageBase64 = canvas.toDataURL('image/png').split(',')[1]
    await fetch('/api/agent/chart-snapshot', {
      method: 'POST',
      body: JSON.stringify({
        symbol: symbol,
        timeframe: '1D',
        image_base64: imageBase64,
        auto_analyze: true  // Vision analysis performed!
      })
    })
    console.log(`Chart snapshot captured for ${symbol}`)
  }
}, 500)
```

**But this data is never provided to the agent during conversations!**

### 4. **Tool Dispatch vs. Direct Drawing**
When user says "draw support and resistance", the agent should either:

**Option A:** Use `detect_chart_patterns` tool
- Calls backend
- Backend analyzes chart image with vision
- Returns drawing commands
- Frontend executes commands

**Option B:** Directly generate commands (FASTER)
- Agent already has chart context
- Agent knows symbol and timeframe
- Agent generates commands immediately: `SUPPORT:430.00 SUPPORT:448.00 RESISTANCE:460.00`
- No tool call needed

**Current behavior:** Neither! Agent asks for symbol.

### 5. **RealtimeChatKit Command Flow Broken**
The RealtimeChatKit processes commands but relies on agent generating proper syntax:

**RealtimeChatKit.tsx (lines 122-148):**
```typescript
if (message.role === 'assistant' && message.content) {
  // Check for drawing commands
  if (AgentResponseParser.containsDrawingCommands(message.content)) {
    const chartCommands = AgentResponseParser.parseResponse(message.content);
    chartCommands.forEach(command => {
      onChartCommand?.(command); // Executes via enhancedChartControl
    });
  }
}
```

**Agent needs to output:**
```
I'll draw the support and resistance levels on your TSLA chart.

SUPPORT:430.00 "200-day MA support"
SUPPORT:448.00 "Recent consolidation zone"
RESISTANCE:460.00 "Previous resistance from breakout"
```

**Instead outputs:**
```json
{"intent":"chart_command","symbol":"","confidence":"high"}
```

## 📋 **Required Fixes**

### Fix 1: Inject Chart Context into Query Processing

**File:** `backend/services/agent_orchestrator.py`
**Location:** `process_query` method (line ~3344)

Add before processing:
```python
async def process_query(
    self, 
    query: str, 
    conversation_history: Optional[List[Dict[str, str]]] = None,
    chart_context: Optional[Dict[str, Any]] = None  # NEW PARAMETER
) -> Dict[str, Any]:
    # Inject chart context if available
    if chart_context:
        context_str = f"\n\n[CURRENT CHART STATE: Symbol={chart_context.get('symbol')}, " \
                     f"Timeframe={chart_context.get('timeframe')}, " \
                     f"Snapshot Available={'Yes' if chart_context.get('snapshot_id') else 'No'}]"
        query = query + context_str
```

### Fix 2: Update System Prompt with Chart Drawing Instructions

**File:** `backend/services/agent_orchestrator.py`
**Location:** `_build_system_prompt` method (line ~3085)

Add section:
```python
CHART DRAWING & VISUALIZATION:
When user requests chart analysis, support/resistance levels, or pattern identification:
1. Check if chart context is provided in the query (look for [CURRENT CHART STATE: ...])
2. If chart context is present, you KNOW what symbol is loaded - don't ask!
3. To draw on the chart, output commands in this format:

SUPPORT:<price> "<description>"
RESISTANCE:<price> "<description>"
TRENDLINE:<start_price>,<start_time>:<end_price>,<end_time> "<description>"
FIBONACCI:<high_price>,<high_time>:<low_price>,<low_time> "<description>"

Example response:
"I'll draw the key levels on your TSLA chart.

SUPPORT:430.00 "200-day moving average - strong support"
SUPPORT:448.00 "Recent consolidation zone"
RESISTANCE:460.00 "Previous breakout resistance"

The support at $430 is critical as it aligns with the 200-day MA..."

4. For pattern requests ("head and shoulders", "triangle"), call detect_chart_patterns tool
5. Chart commands are extracted and executed automatically - embed them naturally in your response
```

### Fix 3: Frontend - Pass Chart Context to Backend

**File:** `frontend/src/components/TradingDashboardSimple.tsx` or `RealtimeChatKit.tsx`
**Location:** When sending messages to agent

Modify API call to include chart context:
```typescript
const agentResponse = await agentOrchestratorService.sendQuery(
  userTranscript,
  conversationHistoryRef.current.slice(-10),
  {
    chart_context: {
      symbol: selectedSymbol,  // e.g., "TSLA"
      timeframe: selectedTimeframe,  // e.g., "1D"
      snapshot_id: currentSnapshot?.id,
      has_analysis: !!currentSnapshot?.analysis
    }
  }
);
```

### Fix 4: Add Chart Context to API Route

**File:** `backend/routers/agent_router.py`
**Location:** `/orchestrate` endpoint

Update request model:
```python
class OrchestrationRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = []
    chart_context: Optional[Dict[str, Any]] = None  # NEW

@router.post("/orchestrate")
async def orchestrate_query(request: OrchestrationRequest):
    result = await orchestrator.process_query(
        request.query,
        request.conversation_history,
        chart_context=request.chart_context  # Pass through
    )
    return result
```

### Fix 5: Enhance ChartCommandExtractor

**File:** `backend/services/chart_command_extractor.py`

Ensure it can extract inline commands from natural language:
```python
def extract_from_text(self, text: str) -> List[str]:
    """Extract chart commands embedded in agent response text"""
    commands = []
    
    # Patterns to match
    patterns = [
        r'SUPPORT:(\d+\.?\d*)\s*"([^"]+)"',
        r'RESISTANCE:(\d+\.?\d*)\s*"([^"]+)"',
        r'TRENDLINE:([^"]+)"([^"]+)"',
        # ... etc
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            commands.append(self._format_command(pattern, match))
    
    return commands
```

## 🎯 **Expected Behavior After Fixes**

### Test Case 1: Support/Resistance Request
```
User: "Map out my supports and resistance. On the chart"

Agent Response (with fixes):
"I'll draw the key support and resistance levels on your TSLA chart.

SUPPORT:430.00 "200-day moving average - strong institutional support"
SUPPORT:448.00 "Recent consolidation zone from last week"
RESISTANCE:460.00 "Previous breakout level - watch for rejection here"
RESISTANCE:472.00 "All-time high resistance"

Currently TSLA is trading at $456.51 (+3.7%), right between the $448 support 
and $460 resistance. This is a consolidation zone - watch for a breakout above 
$460 or breakdown below $448 for the next move."

Result: Lines appear on chart automatically
```

### Test Case 2: Pattern Detection
```
User: "Show me the head and shoulders pattern"

Agent Response (with fixes):
"I see a potential head and shoulders pattern forming on your TSLA chart. 
Let me highlight it for you."

[Calls detect_chart_patterns tool with vision analysis]
[Tool returns drawing commands]
[Commands executed on chart]

"The pattern shows:
- Left shoulder: $452 (Oct 28)
- Head: $462 (Nov 1)  
- Right shoulder: $456 (Nov 4)
- Neckline: $448

If TSLA breaks below the $448 neckline, the target would be $440 
(measured move of $14)."

Result: Pattern automatically drawn on chart with labels
```

## 📊 **Implementation Priority**

1. **High Priority (Immediate)**:
   - Fix 2: Update system prompt with chart drawing instructions
   - Fix 3: Pass chart context from frontend
   - Fix 4: Add chart_context parameter to API

2. **Medium Priority**:
   - Fix 1: Inject chart context into query
   - Fix 5: Enhance command extractor

3. **Low Priority** (Nice to have):
   - Add chart context to conversation history for multi-turn
   - Cache recent snapshots for faster retrieval
   - Add keyboard shortcuts for common drawing commands

## 🧪 **Testing Checklist**

After fixes, test these scenarios:
- [ ] "Draw support and resistance" - should work without asking for symbol
- [ ] "Show me the triangle pattern" - should detect on current chart
- [ ] "Add Fibonacci retracement from high to low" - should draw automatically
- [ ] "What's the current price?" - should reference loaded symbol
- [ ] Switch symbols (TSLA → AAPL) - agent should notice context change
- [ ] "Delete all drawings" - should work with current chart
- [ ] Vision analysis integration - snapshot data used in responses

## 📝 **Related Files**

**Backend:**
- `backend/services/agent_orchestrator.py` (main fixes)
- `backend/routers/agent_router.py` (API route)
- `backend/services/chart_command_extractor.py` (command parsing)
- `backend/services/chart_snapshot_store.py` (snapshot retrieval)

**Frontend:**
- `frontend/src/components/RealtimeChatKit.tsx` (send chart context)
- `frontend/src/components/TradingDashboardSimple.tsx` (track chart state)
- `frontend/src/services/enhancedChartControl.ts` (command execution)
- `frontend/src/services/agentResponseParser.ts` (command extraction)

---

**Status:** Analysis complete, ready for implementation
**Estimated Effort:** 2-3 hours for all fixes
**Impact:** High - Restores core chart interaction functionality

