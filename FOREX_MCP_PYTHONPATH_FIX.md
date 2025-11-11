# Forex MCP Server PYTHONPATH Fix

## Investigation Date: November 10, 2025

---

## Problem Summary

After deploying the forex-mcp-server integration to Fly.io, the application was experiencing critical health check failures with HTTP responses failing despite TCP port 8080 being accessible.

---

## Investigation Using Playwright MCP

### Symptoms
1. **HTTP Health Check**: CRITICAL status with "gone" message
2. **TCP Health Check**: PASSING (port 8080 listening)
3. **Browser Navigation**: `ERR_HTTP_RESPONSE_CODE_FAILURE` when accessing https://gvses-market-insights.fly.dev

### Tools Used
- Playwright MCP for browser automation
- Fly.io SSH console for log inspection
- `fly status` and `fly checks list` commands

---

## Root Cause Analysis

### Step 1: Health Check Investigation
```bash
fly checks list --app gvses-market-insights
```

**Output**:
- `servicecheck-00-tcp-8080`: **passing** (TCP port listening)
- `servicecheck-01-http-8080`: **critical** (status: "gone", last updated 22h ago)

### Step 2: Supervisord Status Check
```bash
fly ssh console --app gvses-market-insights -C "supervisorctl status"
```

**Error**: `unix:///var/run/supervisor.sock no such file`
**Conclusion**: Supervisord wasn't running properly

### Step 3: Supervisord Log Analysis
```bash
fly ssh console --app gvses-market-insights -C "cat /var/log/supervisor/supervisord.log"
```

**Key Findings**:
```
2025-11-11 00:28:30,559 WARN exited: forex-mcp-server (exit status 1; not expected)
2025-11-11 00:28:40,922 INFO gave up: forex-mcp-server entered FATAL state, too many start retries too quickly
```

The forex-mcp-server crashed immediately and supervisord gave up after 5 retry attempts.

**Backend also crashing**: The backend process kept restarting every 10-20 seconds, likely because it was trying to connect to the failed forex-mcp-server.

### Step 4: Forex MCP Error Log
```bash
fly ssh console --app gvses-market-insights -C "tail -50 /var/log/app/forex-mcp-server.err.log"
```

**Root Cause Error**:
```python
Traceback (most recent call last):
  File "/app/forex-mcp-server/src/forex_mcp/server.py", line 26, in <module>
    from forex_mcp.settings import get_settings
ModuleNotFoundError: No module named 'forex_mcp'
```

---

## Technical Analysis

### The Problem

The forex-mcp-server directory structure:
```
/app/forex-mcp-server/
  src/
    forex_mcp/
      __init__.py
      server.py
      settings.py
      models/
      tools/
      services/
```

The `server.py` file at `/app/forex-mcp-server/src/forex_mcp/server.py` contains imports like:
```python
from forex_mcp.settings import get_settings
```

For Python to find the `forex_mcp` module, the PYTHONPATH must include `/app/forex-mcp-server/src`.

### Original supervisord.conf (INCORRECT):
```ini
[program:forex-mcp-server]
directory=/app/forex-mcp-server
command=python src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002
environment=PATH="/usr/local/bin:/usr/bin:/bin",PYTHONPATH="/app:/app/forex-mcp-server"
```

**Issue**: PYTHONPATH includes `/app/forex-mcp-server` but not `/app/forex-mcp-server/src`, so Python can't find the `forex_mcp` package.

### Fixed supervisord.conf (CORRECT):
```ini
[program:forex-mcp-server]
directory=/app/forex-mcp-server
command=python src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002
environment=PATH="/usr/local/bin:/usr/bin:/bin",PYTHONPATH="/app:/app/forex-mcp-server:/app/forex-mcp-server/src"
```

**Fix**: Added `/app/forex-mcp-server/src` to PYTHONPATH so Python can resolve `forex_mcp.*` imports.

---

## The Fix

### File Modified
- `/Volumes/WD My Passport 264F Media/claude-voice-mcp/supervisord.conf` (line 41)

### Change Applied
```diff
- environment=PATH="/usr/local/bin:/usr/bin:/bin",PYTHONPATH="/app:/app/forex-mcp-server"
+ environment=PATH="/usr/local/bin:/usr/bin:/bin",PYTHONPATH="/app:/app/forex-mcp-server:/app/forex-mcp-server/src"
```

---

## Expected Outcome After Fix

1. ✅ forex-mcp-server starts successfully on port 3002
2. ✅ Backend connects to forex-mcp-server without crashing
3. ✅ HTTP health check passes
4. ✅ Application accessible at https://gvses-market-insights.fly.dev
5. ✅ Economic Calendar component displays forex events

---

## Deployment Instructions

```bash
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp"
fly deploy --app gvses-market-insights
```

**Wait for deployment to complete**, then verify:

```bash
# Check app status
fly status --app gvses-market-insights

# Verify health checks
fly checks list --app gvses-market-insights

# Check logs
fly logs --app gvses-market-insights

# SSH and verify supervisord
fly ssh console --app gvses-market-insights -C "supervisorctl status"
```

All services should show **RUNNING** status.

---

## Testing After Deployment

### 1. Browser Test
Navigate to: https://gvses-market-insights.fly.dev

**Expected**: Application loads, Economic Calendar panel visible

### 2. API Test
```bash
curl "https://gvses-market-insights.fly.dev/api/forex/calendar?time_period=today"
```

**Expected**: JSON response with today's forex events

### 3. Health Check
```bash
fly checks list --app gvses-market-insights
```

**Expected**: Both TCP and HTTP checks showing **passing**

---

## Lessons Learned

1. **Python Module Resolution**: When running Python scripts in subdirectories, always ensure PYTHONPATH includes the directory containing the package.

2. **Supervisord Debugging**: Check these in order:
   - Supervisord log: `/var/log/supervisor/supervisord.log`
   - Service error logs: `/var/log/app/<service>.err.log`
   - Service output logs: `/var/log/app/<service>.out.log`

3. **Fly.io Health Checks**:
   - TCP check = port is listening
   - HTTP check = server responds correctly to HTTP requests
   - If TCP passes but HTTP fails → application startup issue

4. **Investigation Tools**:
   - Playwright MCP for browser testing
   - `fly ssh console` for direct log inspection
   - `fly checks list` for health check status

---

## Status

- **Investigation**: ✅ COMPLETE
- **Root Cause Identified**: ✅ YES (ModuleNotFoundError: No module named 'forex_mcp')
- **Fix Applied**: ✅ YES (Added /app/forex-mcp-server/src to PYTHONPATH)
- **Deployment**: 🔄 IN PROGRESS
- **Verification**: ⏳ PENDING

---

## Next Steps

1. ✅ Deploy fixed supervisord.conf
2. ⏳ Monitor deployment logs
3. ⏳ Verify all supervisord services running
4. ⏳ Test forex calendar API endpoint
5. ⏳ Confirm health checks passing
6. ⏳ Test with Playwright MCP
