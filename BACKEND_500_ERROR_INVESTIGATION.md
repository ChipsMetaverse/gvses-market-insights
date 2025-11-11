# Backend 500 Error Investigation Report
**Date:** 2025-11-05  
**Status:** ✅ ROOT CAUSE IDENTIFIED  
**Investigated via:** Playwright MCP + Backend Code Analysis

---

## Executive Summary

The production backend API (`gvses-market-insights-api.fly.dev`) is returning **500 errors** for multiple critical endpoints because **NO environment secrets are configured** on the Fly.io app. The backend requires at minimum the `OPENAI_API_KEY` environment variable to function.

---

## Evidence

### 1. Console Errors from Production App

From `https://gvses-market-insights.fly.dev` browser console:

```
❌ ChatKit session error: Error: Session failed: 500 {"detail":"OpenAI API key not configured"}
    at Object.getClientSecret (https://gvses-market-insights.fly.dev/assets/index-CM6UiJzc.js:71:24583)
    
Failed to load resource: 500 @ https://gvses-market-insights-api.fly.dev/api/chatkit/session
Failed to load resource: 500 @ https://gvses-market-insights-api.fly.dev/api/technical-indicators?symbol=AAPL&indicators=moving_averages&days=200
Failed to load resource: 500 @ https://gvses-market-insights-api.fly.dev/api/agent/tools/chart
Failed to load resource: 500 @ https://gvses-market-insights-api.fly.dev/api/conversations
```

### 2. Fly.io Secrets Verification

```bash
$ flyctl secrets list --app gvses-market-insights-api
NAME    DIGEST 

(empty - NO SECRETS CONFIGURED)
```

### 3. Backend Code Analysis

**File:** `backend/mcp_server.py`, lines 1988-1990

```python
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise HTTPException(status_code=500, detail="OpenAI API key not configured")
```

This code explicitly raises a 500 error when `OPENAI_API_KEY` is missing, which matches the error message seen in the console.

---

## Root Cause

**The `gvses-market-insights-api` Fly.io app has NO environment secrets configured.**

When the backend was deployed as a separate Fly.io app, the environment variables/secrets were not migrated from the original `gvses-market-insights` app (which was frontend-only after the split).

---

## Required Environment Variables

Based on code analysis (`backend/mcp_server.py` and service files), the following secrets are **REQUIRED**:

### 1. **OPENAI_API_KEY** (CRITICAL)
- **Used by:** ChatKit session, Agent Orchestrator, Vector Retriever, Agents SDK, Realtime SDK, Chart Image Analyzer
- **Impact if missing:** 500 errors on ALL agent/ChatKit endpoints
- **Source:** Lines 86, 704, 1643, 1715, 1988 in `backend/mcp_server.py`

### 2. **SUPABASE_URL** (OPTIONAL but recommended)
- **Used by:** Conversation persistence, market data caching
- **Impact if missing:** No conversation history, degraded performance
- **Source:** Line 80 in `backend/mcp_server.py`

### 3. **SUPABASE_ANON_KEY** (OPTIONAL but recommended)
- **Used by:** Supabase client authentication
- **Impact if missing:** No database access for caching/persistence
- **Source:** Line 81 in `backend/mcp_server.py`

### 4. **ALPACA_API_KEY** (OPTIONAL)
- **Used by:** Real-time market data via Alpaca
- **Impact if missing:** Falls back to alternative data sources
- **Source:** Lines 45-47 in `backend/alpaca_service.py`

### 5. **ALPACA_SECRET_KEY** (OPTIONAL)
- **Used by:** Alpaca API authentication
- **Impact if missing:** Alpaca service disabled
- **Source:** Lines 46-47 in `backend/alpaca_service.py`

---

## Fix Required

### Step 1: Set Critical Secrets on Fly.io

```bash
# Navigate to project directory
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp"

# Set OPENAI_API_KEY (REQUIRED - get from local .env or user)
flyctl secrets set OPENAI_API_KEY="sk-proj-..." --app gvses-market-insights-api

# Set Supabase credentials (OPTIONAL but recommended)
flyctl secrets set SUPABASE_URL="https://..." --app gvses-market-insights-api
flyctl secrets set SUPABASE_ANON_KEY="eyJh..." --app gvses-market-insights-api

# Set Alpaca credentials (OPTIONAL - only if real-time trading data needed)
flyctl secrets set ALPACA_API_KEY="..." --app gvses-market-insights-api
flyctl secrets set ALPACA_SECRET_KEY="..." --app gvses-market-insights-api
```

### Step 2: Verify Secrets Are Set

```bash
flyctl secrets list --app gvses-market-insights-api
```

Expected output:
```
NAME                DIGEST          
OPENAI_API_KEY      <digest>
SUPABASE_URL        <digest>
SUPABASE_ANON_KEY   <digest>
```

### Step 3: Restart Backend App (if needed)

Fly.io automatically restarts the app when secrets are set, but you can force a restart:

```bash
flyctl apps restart gvses-market-insights-api
```

### Step 4: Verify Fix

Navigate to `https://gvses-market-insights.fly.dev` and check:
1. No more 500 errors in browser console
2. ChatKit session connects successfully
3. Agent responses work
4. Chart control functions

---

## Testing Checklist

After setting secrets:

- [ ] **ChatKit Session:** `/api/chatkit/session` returns 200 (not 500)
- [ ] **Technical Indicators:** `/api/technical-indicators?symbol=AAPL` returns data (not 500)
- [ ] **Chart Tools:** `/api/agent/tools/chart` returns tools list (not 500)
- [ ] **Conversations:** `/api/conversations` creates conversation successfully (not 500)
- [ ] **Agent Response:** Sending a message triggers agent workflow correctly
- [ ] **Chart Control:** Saying "show me NVDA" switches chart to NVDA

---

## Impact Analysis

### Before Fix (Current State)
- ❌ ChatKit session fails → No voice/chat interface
- ❌ Agent orchestrator fails → No agent responses
- ❌ Chart tools fail → No chart control
- ❌ Conversations fail → No conversation history
- ❌ Technical indicators fail → No auto-fetch data
- ⚠️ Only static chart rendering works (no interactive features)

### After Fix (Expected State)
- ✅ ChatKit session connects successfully
- ✅ Agent provides market analysis
- ✅ Chart control via Agent Builder workflow v37
- ✅ Conversation history persists (if Supabase configured)
- ✅ Technical indicators auto-fetch
- ✅ Full interactive experience

---

## Additional Notes

### Why Did This Happen?

During the deployment separation (frontend → `gvses-market-insights`, backend → `gvses-market-insights-api`), the environment variables were not migrated. The original `gvses-market-insights` app (now frontend-only) may have had secrets configured, but when the new backend app was created, it started with an empty secrets configuration.

### Prevention for Future Deployments

1. **Always verify secrets after deployment:**
   ```bash
   flyctl secrets list --app <app-name>
   ```

2. **Create a `.env.example` file** in the repository to document required variables (without actual values):
   ```bash
   OPENAI_API_KEY=sk-proj-...
   SUPABASE_URL=https://...
   SUPABASE_ANON_KEY=eyJh...
   ALPACA_API_KEY=...
   ALPACA_SECRET_KEY=...
   ```

3. **Add deployment checklist** to CI/CD or deployment scripts to ensure secrets are configured.

---

## Conclusion

**Root Cause:** Missing `OPENAI_API_KEY` and other environment secrets on `gvses-market-insights-api` Fly.io app.

**Fix:** Set secrets using `flyctl secrets set` commands above.

**Priority:** 🔴 **CRITICAL** - App is non-functional without this fix.

**User Action Required:** User must provide the actual secret values (from local `.env` file or OpenAI dashboard) to set on Fly.io, as these are not accessible to the AI assistant.

---

**Next Steps:**
1. User sets secrets on Fly.io using commands above
2. Verify secrets are configured: `flyctl secrets list --app gvses-market-insights-api`
3. Test production app at `https://gvses-market-insights.fly.dev`
4. Verify all 500 errors are resolved

