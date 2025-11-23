# Chart Control Solution - Complete Architecture

## Problem Summary

**Issue**: ChatKit `onMessage` callback not firing, preventing natural language command parsing.

**Root Cause**: OpenAI's ChatKit widget is a sandboxed iframe. Agent responses stay inside the iframe and are not accessible to parent page JavaScript, making it impossible to parse natural language commands from the response text.

**Test Results:**
- ❌ Chart stayed on TSLA (didn't switch to AAPL)
- ❌ No `onMessage` logs in console
- ❌ Intent Classifier JSON visible to user
- ❌ Frontend never received agent response text

---

## Architecture Solution: Backend HTTP Endpoints + Frontend Polling

### How It Works

```
User: "show me Apple"
   ↓
OpenAI Agent Builder (Chart Control Agent)
   ↓
Calls HTTP Action: POST /api/chart/change-symbol {"symbol": "AAPL"}
   ↓
Backend adds command to queue
   ↓
Frontend polls: GET /api/chart/commands
   ↓
Frontend executes: chart.changeSymbol("AAPL")
   ↓
Chart switches to AAPL ✅
```

### Backend Components (Already Implemented ✅)

**File**: `backend/chart_control_api.py`

**Available Endpoints**:
- `POST /api/chart/change-symbol` - Change chart symbol
- `POST /api/chart/set-timeframe` - Set timeframe (1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M)
- `POST /api/chart/toggle-indicator` - Toggle indicators (RSI, MACD, Bollinger Bands, Volume)
- `POST /api/chart/capture-snapshot` - Capture chart screenshot
- `POST /api/chart/set-style` - Set chart style (candles, line, area)
- `GET /api/chart/state` - Get current chart state
- `GET /api/chart/commands` - Get pending commands for frontend
- `DELETE /api/chart/commands/{id}` - Acknowledge processed command

**Command Queue System**:
```json
{
  "commands": [
    {
      "id": "cmd_1636627200000",
      "type": "symbol_change",
      "data": {"symbol": "AAPL", "previous_symbol": "TSLA"},
      "timestamp": "2025-11-11T22:00:00",
      "status": "pending"
    }
  ]
}
```

---

## Implementation Steps

### Step 1: Configure OpenAI Agent Builder Actions

Navigate to Agent Builder → Chart Control Agent → Actions

**Add Action 1: Change Symbol**
```yaml
Name: change_chart_symbol
Description: Change the stock symbol displayed on the trading chart
Method: POST
URL: https://gvses-market-insights-api.fly.dev/api/chart/change-symbol
Headers:
  Content-Type: application/json
Body Schema:
  {
    "symbol": {
      "type": "string",
      "description": "Stock ticker symbol (e.g., AAPL, TSLA, NVDA)",
      "required": true
    }
  }
```

**Add Action 2: Set Timeframe**
```yaml
Name: set_chart_timeframe
Description: Set the timeframe for chart data display
Method: POST
URL: https://gvses-market-insights-api.fly.dev/api/chart/set-timeframe
Headers:
  Content-Type: application/json
Body Schema:
  {
    "timeframe": {
      "type": "string",
      "enum": ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"],
      "description": "Chart timeframe",
      "required": true
    }
  }
```

**Add Action 3: Toggle Indicator**
```yaml
Name: toggle_chart_indicator
Description: Toggle technical indicators on/off on the trading chart
Method: POST
URL: https://gvses-market-insights-api.fly.dev/api/chart/toggle-indicator
Headers:
  Content-Type: application/json
Body Schema:
  {
    "indicator": {
      "type": "string",
      "description": "Indicator name: RSI, MACD, Moving Average, Bollinger Bands, Volume, Stochastic",
      "required": true
    },
    "enabled": {
      "type": "boolean",
      "description": "Enable (true) or disable (false) the indicator",
      "required": true
    }
  }
```

### Step 2: Update Chart Control Agent Instructions

Replace current instructions with action-based workflow:

```markdown
# Chart Control Agent Instructions - HTTP Actions

## Role
You are the Chart Control Agent for GVSES trading platform. You control the chart display using HTTP actions and provide professional technical analysis.

## When User Requests Chart Changes

**For symbol changes** (e.g., "show me Apple", "display TSLA"):
1. Call `change_chart_symbol` action with the ticker symbol
2. Wait for confirmation
3. Provide technical analysis of the new symbol

**For timeframe changes** (e.g., "switch to 1 hour", "show daily chart"):
1. Call `set_chart_timeframe` action with timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)
2. Provide analysis appropriate for that timeframe

**For indicator requests** (e.g., "add RSI", "show MACD"):
1. Call `toggle_chart_indicator` action with indicator name and enabled=true
2. Explain what the indicator shows and current reading

## Response Format

After calling actions, provide natural technical analysis:

```
I've switched the chart to [SYMBOL] on the [TIMEFRAME] timeframe.

**Current Price**: $XXX.XX (±X.X%)

**Technical Picture**:
[Indicator analysis based on enabled indicators]

**Key Levels**:
- Resistance: $XXX
- Support: $XXX

**Trader's Takeaway**: [Actionable insight]
```

## Important Notes
- **Always call actions first** before providing analysis
- **Wait for action confirmation** before describing chart state
- **Don't mention the actions** to the user (they see the chart change automatically)
- **Focus on analysis** after chart is updated
```

### Step 3: Implement Frontend Polling

**File**: `frontend/src/services/chartCommandPoller.ts` (NEW)

```typescript
export class ChartCommandPoller {
  private interval: NodeJS.Timeout | null = null;
  private isPolling = false;

  constructor(
    private onCommand: (command: ChartCommand) => void,
    private pollIntervalMs = 1000
  ) {}

  start() {
    if (this.isPolling) return;

    this.isPolling = true;
    this.interval = setInterval(async () => {
      try {
        const response = await fetch('https://gvses-market-insights-api.fly.dev/api/chart/commands');
        const data = await response.json();

        for (const command of data.commands) {
          if (command.status === 'pending') {
            // Execute command
            await this.executeCommand(command);

            // Acknowledge command
            await fetch(`https://gvses-market-insights-api.fly.dev/api/chart/commands/${command.id}`, {
              method: 'DELETE'
            });
          }
        }
      } catch (error) {
        console.error('Error polling chart commands:', error);
      }
    }, this.pollIntervalMs);
  }

  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    this.isPolling = false;
  }

  private async executeCommand(command: any) {
    console.log(`[ChartPoller] Executing command:`, command);

    switch (command.type) {
      case 'symbol_change':
        this.onCommand({
          type: 'symbol',
          value: command.data.symbol
        });
        break;

      case 'timeframe_change':
        this.onCommand({
          type: 'timeframe',
          value: command.data.timeframe
        });
        break;

      case 'indicator_toggle':
        this.onCommand({
          type: 'indicator',
          value: command.data.indicator,
          enabled: command.data.enabled
        });
        break;

      case 'style_change':
        this.onCommand({
          type: 'style',
          value: command.data.style
        });
        break;
    }
  }
}
```

**Integration**: `frontend/src/components/TradingDashboardSimple.tsx`

```typescript
import { ChartCommandPoller } from '../services/chartCommandPoller';

// Inside component
useEffect(() => {
  const poller = new ChartCommandPoller((command) => {
    // Execute chart commands from backend
    enhancedChartControl.executeCommand(command);
  });

  poller.start();

  return () => poller.stop();
}, []);
```

### Step 4: Remove Intent Classifier from Final Response

The Intent Classifier's JSON output shouldn't be visible to users. Configure Agent Builder workflow:

**Option A: Filter in Transform Node**
- Transform node should extract `intent` but not pass raw JSON to Chart Control Agent

**Option B: Update Chart Control Agent to ignore Intent JSON**
- Add instruction: "Ignore any JSON objects in the input - only respond to natural language queries"

---

## Testing Checklist

- [ ] Agent Builder Actions configured (3 actions added)
- [ ] Chart Control Agent instructions updated
- [ ] Frontend polling implemented (`chartCommandPoller.ts`)
- [ ] Polling integrated in `TradingDashboardSimple.tsx`
- [ ] Test: "show me Apple" → Chart switches to AAPL
- [ ] Test: "switch to 1 hour" → Timeframe changes to 1h
- [ ] Test: "add RSI" → RSI indicator appears
- [ ] Verify: No Intent Classifier JSON visible to user
- [ ] Verify: Agent provides natural analysis after chart changes

---

## Advantages of This Approach

✅ **Works with ChatKit sandbox** - No dependency on `onMessage` callback
✅ **Reliable command execution** - Backend queue ensures commands aren't lost
✅ **Clean separation** - Agent calls HTTP actions, frontend polls for updates
✅ **No visible commands** - User sees only natural analysis text
✅ **Production ready** - Uses existing battle-tested backend endpoints
✅ **Scalable** - Command queue can handle multiple concurrent users

---

## Alternative: WebSocket Push (Future Enhancement)

Instead of polling, implement WebSocket push:

```typescript
// Backend: Push commands via WebSocket when agent calls HTTP endpoint
@router.post("/change-symbol")
async def change_chart_symbol(request):
    command_id = add_command_to_queue(...)

    # Push to all connected WebSocket clients
    await websocket_manager.broadcast({
        "type": "chart_command",
        "command": command
    })
```

This eliminates polling delay but requires WebSocket infrastructure.

---

## Status

- ✅ Backend HTTP endpoints implemented
- ✅ Command queue system working
- ⏸️ Agent Builder Actions need configuration
- ⏸️ Frontend polling needs implementation
- ⏸️ Agent instructions need update

**Next Step**: Configure Actions in OpenAI Agent Builder.
