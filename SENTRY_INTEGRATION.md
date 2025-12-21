# Sentry Integration Guide
**Date**: November 11, 2025
**Version**: 1.0.0
**Status**: ✅ Implemented

---

## 📋 Overview

The GVSES Trading Dashboard now includes comprehensive error monitoring and performance tracking via Sentry. This integration provides:

- **Error Tracking**: Automatic capture of frontend and backend errors
- **Performance Monitoring**: Track request durations, database queries, and API calls
- **Session Replay**: Record user sessions when errors occur for debugging
- **Sentry MCP Integration**: Use Sentry's AI agent to analyze and fix issues directly from Claude Code

---

## 🎯 What's Included

### Frontend Integration
- ✅ Sentry React SDK (`@sentry/react`)
- ✅ Browser tracing integration for performance monitoring
- ✅ Session replay with error capture
- ✅ Custom error filtering for expected errors (WebSocket disconnects, etc.)
- ✅ Breadcrumb tracking for user actions

**Location**: `frontend/src/config/sentry.ts`

### Backend Integration
- ✅ Sentry Python SDK (`sentry-sdk>=2.47.0`)
- ✅ FastAPI integration for request tracing
- ✅ Logging integration for error events
- ✅ Custom error filtering for rate limits and expected errors
- ✅ Performance profiling

**Location**: `backend/config/sentry.py`

### MCP Integration
- ✅ Sentry MCP server configured in Claude Code
- ✅ OAuth authentication for seamless access
- ✅ 16+ tools for issue analysis and debugging

**Configuration**: `~/.claude.json` → `mcpServers.sentry`

---

## 🚀 Getting Started

### Step 1: Create Sentry Projects

1. **Sign up for Sentry** (if you haven't already):
   - Visit [sentry.io](https://sentry.io)
   - Create a free account or sign in

2. **Create Frontend Project**:
   - Navigate to: `Settings` → `Projects` → `Create Project`
   - Platform: **React**
   - Project name: `gvses-frontend`
   - Copy the DSN (looks like: `https://xxx@xxx.ingest.sentry.io/xxx`)

3. **Create Backend Project**:
   - Create another project
   - Platform: **Python** (FastAPI)
   - Project name: `gvses-backend`
   - Copy the DSN

### Step 2: Configure Environment Variables

#### Frontend `.env` file:
```bash
# Sentry Error Tracking
VITE_SENTRY_DSN=https://your-frontend-dsn@xxx.ingest.sentry.io/xxx
VITE_SENTRY_ENVIRONMENT=development  # or production
VITE_SENTRY_RELEASE=gvses-frontend@1.0.0
```

#### Backend `.env` file:
```bash
# Sentry Error Tracking
SENTRY_DSN=https://your-backend-dsn@xxx.ingest.sentry.io/xxx
SENTRY_ENVIRONMENT=development  # or production
SENTRY_RELEASE=gvses-backend@1.0.0
```

### Step 3: Verify Integration

#### Frontend Test:
```bash
cd frontend
npm run dev
# Open browser console and run:
# window.Sentry.captureMessage('Test from frontend')
```

Check your Sentry dashboard under the `gvses-frontend` project.

#### Backend Test:
```bash
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000

# In another terminal:
curl -X POST http://localhost:8000/api/test-sentry
```

Check your Sentry dashboard under the `gvses-backend` project.

---

## 🔧 Configuration Details

### Frontend Configuration

**File**: `frontend/src/config/sentry.ts`

**Key Features**:
- **Performance Monitoring**: 100% sample rate in dev, 10% in production
- **Session Replay**: Records sessions on errors for debugging
- **Error Filtering**: Filters out expected WebSocket/ElevenLabs disconnections
- **Custom Tags**: Adds framework, component, and build tags

**Usage Example**:
```typescript
import { captureError, captureMessage, addBreadcrumb } from './config/sentry';

// Capture an error with context
try {
  // risky operation
} catch (error) {
  captureError(error, {
    component: 'TradingChart',
    symbol: 'TSLA',
    timeframe: '1D'
  });
}

// Capture a message
captureMessage('User loaded chart', 'info');

// Add breadcrumb
addBreadcrumb('User clicked Buy button', 'user-action');
```

### Backend Configuration

**File**: `backend/config/sentry.py`

**Key Features**:
- **FastAPI Integration**: Automatic request tracing and error capture
- **Logging Integration**: Captures ERROR level logs as events
- **Performance Profiling**: 10% sample rate in production
- **Error Filtering**: Filters out rate limit errors and expected WebSocket issues

**Usage Example**:
```python
from config.sentry import capture_exception, capture_message, add_breadcrumb

# Capture an exception with context
try:
    # risky operation
    pass
except Exception as e:
    capture_exception(e, context={
        "endpoint": "/api/stock-price",
        "symbol": "TSLA",
        "user_id": "user123"
    })

# Capture a message
capture_message("Market data service initialized", level="info")

# Add breadcrumb
add_breadcrumb("Fetched stock price", category="api", data={"symbol": "TSLA"})
```

---

## 🤖 Sentry MCP Integration

The Sentry MCP server is now configured in Claude Code, giving you access to powerful debugging tools directly in your development environment.

### Available Tools

1. **Issue Analysis**:
   ```
   Tell me about the issues in gvses-frontend
   ```

2. **Error Search**:
   ```
   Check Sentry for errors in components/TradingChart.tsx
   ```

3. **Automated Fixes**:
   ```
   Use Sentry's Seer to analyze and propose a solution for issue FRONTEND-123
   ```

4. **Project Management**:
   ```
   Create a new Sentry project for the mobile app
   ```

5. **DSN Management**:
   ```
   List all DSNs for gvses-backend project
   ```

### Seer Integration

Sentry's AI agent (Seer) can automatically analyze issues and propose fixes:

```bash
# In Claude Code terminal:
claude

# Then ask:
"Use Sentry to diagnose the most recent error in gvses-frontend and propose a solution"
```

Seer provides:
- Root cause analysis
- Code-level fix recommendations
- Similar issue patterns
- Impact assessment

---

## 📊 Monitoring Best Practices

### 1. Set Up Alerts

Configure alerts in Sentry dashboard:
- **Critical Errors**: Notify on any 500 errors in production
- **Performance Degradation**: Alert when API response time > 2s
- **High Error Rate**: Notify when error rate > 1% of requests

### 2. Use Custom Context

Always add relevant context to errors:

```typescript
// Frontend
captureError(error, {
  symbol: currentSymbol,
  timeframe: selectedTimeframe,
  userId: user?.id,
  component: 'TradingChart'
});
```

```python
# Backend
capture_exception(e, context={
    "endpoint": request.url.path,
    "method": request.method,
    "user_id": user_id,
    "data_source": "alpaca"
})
```

### 3. Monitor Performance

Use Sentry's performance monitoring to track:
- API endpoint response times
- Database query durations
- External API calls (Alpaca, ElevenLabs)
- Frontend page load times

### 4. Review Session Replays

When errors occur, review session replays to understand:
- User actions leading to the error
- UI state at time of error
- Network requests and responses
- Console logs and breadcrumbs

---

## 🔍 Debugging Workflow

### When an Error Occurs in Production

1. **Get Notified**: Sentry email/Slack alert
2. **Open Issue in Sentry Dashboard**: View error details
3. **Use Sentry MCP in Claude Code**:
   ```
   Diagnose Sentry issue FRONTEND-456 and propose a solution
   ```
4. **Review Session Replay**: Understand user context
5. **Check Performance Impact**: View affected users/requests
6. **Use Seer for Automated Analysis**:
   ```
   Use Sentry's Seer to analyze issue FRONTEND-456
   ```
7. **Implement Fix**: Based on recommendations
8. **Mark Issue as Resolved**: In Sentry dashboard
9. **Monitor**: Verify fix doesn't introduce new issues

---

## 📈 Sample Rates

### Development
- **Error Sampling**: 100% (capture all errors)
- **Performance Tracing**: 100% (trace all requests)
- **Session Replay**: 100% on errors

### Production
- **Error Sampling**: 100% (capture all errors)
- **Performance Tracing**: 10% (sample 1 in 10 requests)
- **Session Replay**: 10% normal sessions, 100% on errors
- **Profiling**: 10% (sample 1 in 10 requests)

These rates can be adjusted in:
- Frontend: `frontend/src/config/sentry.ts`
- Backend: `backend/config/sentry.py`

---

## 🛡️ Privacy & Security

### Data Scrubbing

Sentry automatically scrubs sensitive data, but you should:

1. **Never log passwords or API keys**:
   ```typescript
   // ❌ Bad
   captureError(error, { apiKey: process.env.ALPACA_API_KEY });

   // ✅ Good
   captureError(error, { hasApiKey: !!process.env.ALPACA_API_KEY });
   ```

2. **Sanitize PII (Personally Identifiable Information)**:
   ```python
   # Use user IDs, not emails or names in public context
   capture_exception(e, context={
       "user_id": user.id,  # ✅ Good
       # "email": user.email  # ❌ Bad
   })
   ```

3. **Review Session Replays**: Ensure no sensitive data is visible

### Sentry Configuration

- **Data Residency**: Choose US or EU data centers in Sentry settings
- **Data Retention**: Configure in Sentry → Settings → Data Management
- **Access Control**: Use Sentry teams to limit who can view errors

---

## 📦 Deployment Checklist

### Pre-Deployment

- [x] Sentry projects created (frontend + backend)
- [ ] DSN environment variables set in production
- [ ] Sample rates configured for production
- [ ] Alerts configured in Sentry dashboard
- [ ] Team members invited to Sentry organization
- [ ] Session replay privacy reviewed

### Post-Deployment

- [ ] Verify errors are being captured
- [ ] Check performance metrics dashboard
- [ ] Test error alerting (trigger test error)
- [ ] Review first production errors
- [ ] Set up Slack/email notifications

---

## 🧪 Testing Sentry Integration

### Frontend Test

1. **Trigger a test error**:
   ```typescript
   // Add temporary button in TradingDashboardSimple.tsx
   <button onClick={() => {
     throw new Error('Test Sentry Frontend Integration');
   }}>
     Test Sentry
   </button>
   ```

2. **Check Sentry Dashboard**: Should see error within seconds

### Backend Test

1. **Add test endpoint** (already exists):
   ```python
   @app.post("/api/test-sentry")
   async def test_sentry():
       raise Exception("Test Sentry Backend Integration")
   ```

2. **Trigger test**:
   ```bash
   curl -X POST http://localhost:8000/api/test-sentry
   ```

3. **Check Sentry Dashboard**: Should see error within seconds

---

## 📚 Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [Sentry React SDK](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [Sentry MCP Server](https://docs.sentry.io/product/sentry-mcp/)
- [Seer AI Agent](https://docs.sentry.io/product/ai-in-sentry/seer/)

---

## 🔧 Troubleshooting

### "Sentry DSN not configured" Warning

**Problem**: Sentry shows warning but app works fine

**Solution**: This is expected in development without DSN. Add DSN to `.env` file or ignore warning.

### Session Replays Not Showing

**Problem**: Errors captured but no session replay

**Solution**:
1. Check `replaysOnErrorSampleRate` is set to `1.0`
2. Verify Sentry plan includes session replay
3. Check browser console for replay errors

### Performance Data Not Showing

**Problem**: Errors work but no performance metrics

**Solution**:
1. Verify `tracesSampleRate` is > 0
2. Check Sentry plan includes performance monitoring
3. Ensure FastAPI integration is active (backend)

### MCP Authentication Failed

**Problem**: Can't connect to Sentry MCP server

**Solution**:
1. Run: `claude mcp list` - verify sentry is configured
2. Run: `claude mcp remove sentry && claude mcp add --transport http sentry https://mcp.sentry.dev/mcp`
3. Restart Claude Code
4. Re-authenticate with OAuth

---

**Status**: ✅ Ready for use
**Next Steps**: Add DSN environment variables and test in development
