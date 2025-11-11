# SOLUTION: Update Existing MCP Server ✅

## 🎉 **GOOD NEWS!**

The `gvses-mcp-sse-server` app **EXISTS and is RUNNING** on Fly.io!

**App Status**:
- ✅ Hostname: `gvses-mcp-sse-server.fly.dev`
- ✅ Status: Started (1 machine healthy)
- ✅ Health check passing: `{"status":"healthy","transport":"sse"}`
- ✅ Port: 3001 (Node.js)
- ✅ Last deployed: October 13, 2025

---

## 🛠️ **SOLUTION: Update MCP Server to Call Our Backend**

Instead of creating a new MCP bridge, we can **update the existing MCP server** to forward chart control requests to our backend.

### Architecture:
```
Agent Builder (Chart Control Agent)
    ↓ SSE/MCP Protocol
gvses-mcp-sse-server.fly.dev/sse
    ↓ chart_control tool called
    ↓ HTTP POST
gvses-market-insights.fly.dev/api/chatkit/chart-action
    ↓
Backend Agent Orchestrator
    ↓
Returns chart commands
    ↓ via MCP protocol
Agent Builder
    ↓
ChatKit UI
    ↓
Frontend parses & displays
```

---

## 📋 **Implementation Steps**

### Step 1: Locate MCP Server Code

The server should be in the project or a separate repo. Look for:
```bash
# Check if it's in current project
ls -la | grep mcp
find . -name "*mcp*server*" -type f

# Check workspace for separate MCP server project
ls -la ~/workspace/ | grep mcp
```

**Likely locations**:
- `/Volumes/WD My Passport 264F Media/claude-voice-mcp/mcp-server/`
- `/Volumes/WD My Passport 264F Media/gvses-mcp-sse-server/`
- Separate Git repo

### Step 2: Update MCP Server Code

The server needs to expose a `chart_control` tool that forwards to our backend.

**Example implementation** (Node.js/TypeScript):

```typescript
// File: mcp-server/src/tools/chartControl.ts

import { Tool } from '@modelcontextprotocol/sdk/types.js';

export const chartControlTool: Tool = {
  name: 'chart_control',
  description: 'Control charts, draw support/resistance levels, detect patterns, and perform technical analysis. Use this when users ask to: draw support and resistance, analyze charts, detect patterns, show trendlines, or any chart-related technical analysis.',
  inputSchema: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'The user\'s chart-related query'
      },
      session_id: {
        type: 'string',
        description: 'ChatKit session ID'
      },
      metadata: {
        type: 'object',
        description: 'Additional context'
      }
    },
    required: ['query']
  }
};

export async function handleChartControl(args: any): Promise<any> {
  const { query, session_id, metadata } = args;
  
  // Forward to our backend
  const response = await fetch('https://gvses-market-insights.fly.dev/api/chatkit/chart-action', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query,
      session_id,
      metadata
    })
  });
  
  const data = await response.json();
  
  // Return in MCP format
  return {
    content: [
      {
        type: 'text',
        text: data.text
      }
    ],
    metadata: {
      chart_commands: data.chart_commands,
      tools_used: data.data?.tools_used || []
    }
  };
}
```

### Step 3: Deploy Updated MCP Server

```bash
# Navigate to MCP server directory
cd /path/to/gvses-mcp-sse-server

# Test locally
npm run dev

# Deploy to Fly.io
flyctl deploy -a gvses-mcp-sse-server

# Verify deployment
flyctl status -a gvses-mcp-sse-server
flyctl logs -a gvses-mcp-sse-server -f
```

### Step 4: Test End-to-End

1. **Open ChatKit** at https://gvses-market-insights.fly.dev/
2. **Load TSLA chart**
3. **Type**: "draw support and resistance"
4. **Check backend logs**:
   ```bash
   flyctl logs -a gvses-market-insights -f | grep "CHATKIT ACTION"
   ```
5. **Expected**:
   - Backend receives request
   - Generates 9 chart commands
   - ChatKit displays response
   - Lines appear on chart

---

## 🧪 **Verification Checklist**

### Before Deployment:
- [ ] MCP server code updated with `chart_control` tool
- [ ] Tool forwards to `https://gvses-market-insights.fly.dev/api/chatkit/chart-action`
- [ ] Response formatted for MCP protocol
- [ ] Local testing passed

### After Deployment:
- [ ] MCP server health check passing
- [ ] Backend receives `[CHATKIT ACTION]` logs
- [ ] Chart commands generated
- [ ] Frontend displays lines on chart
- [ ] Multiple symbols tested (TSLA, AAPL, NVDA)

---

## 📊 **Current Status**

| Component | Status | Action Needed |
|-----------|--------|---------------|
| `gvses-mcp-sse-server` | ✅ Running | Update code to forward to backend |
| `gvses-market-insights` backend | ✅ Ready | No changes needed |
| Agent Builder config | ✅ Correct | Already pointing to MCP server |
| Frontend | ✅ Ready | Already parsing chart commands |

---

## 🎯 **Next Immediate Action**

**Find the MCP server source code:**

```bash
# Option 1: Check current workspace
cd "/Volumes/WD My Passport 264F Media"
find . -name "*mcp*server*" -type d

# Option 2: Check for separate repo
ls -la ~/ | grep mcp
ls -la ~/Documents/ | grep mcp

# Option 3: Check Git remotes
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp"
git remote -v | grep mcp
```

Once found:
1. Update `chart_control` tool to forward to backend
2. Deploy: `flyctl deploy -a gvses-mcp-sse-server`
3. Test with ChatKit
4. ✅ DONE!

---

**Status**: MCP server exists, needs code update  
**Estimated Time**: 1-2 hours  
**Confidence**: HIGH - clear path forward  
**Last Updated**: November 3, 2025

