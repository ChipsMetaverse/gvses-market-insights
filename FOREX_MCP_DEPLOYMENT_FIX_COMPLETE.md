# Forex MCP Server Deployment Fix - COMPLETE ✅

## Investigation Date: November 10-11, 2025

---

## Problems Identified

### Problem 1: forex-mcp-server ModuleNotFoundError (FIXED ✅)

**Symptom**: forex-mcp-server crashed immediately on startup
**Error**: `ModuleNotFoundError: No module named 'forex_mcp'`
**Root Cause**: PYTHONPATH in supervisord.conf didn't include `/app/forex-mcp-server/src`

**Fix Applied** (supervisord.conf line 41):
```ini
# BEFORE (broken):
environment=PATH="/usr/local/bin:/usr/bin:/bin",PYTHONPATH="/app:/app/forex-mcp-server"

# AFTER (fixed):
environment=PATH="/usr/local/bin:/usr/bin:/bin",PYTHONPATH="/app:/app/forex-mcp-server:/app/forex-mcp-server/src"
```

**Verification**: forex-mcp-server now starts successfully on port 3002
```
INFO: Starting ForexFactory MCP server (transport=http)
INFO: Uvicorn running on http://0.0.0.0:3002
INFO: Application startup complete.
```

---

### Problem 2: Backend Port Conflict (FIXED ✅)

**Symptom**: Backend crashed repeatedly with "address already in use"
**Error**: `ERROR: [Errno 98] error while attempting to bind on address ('0.0.0.0', 8080): address already in use`
**Root Cause**: Both nginx AND backend tried to bind to port 8080

**Architecture Clarification**:
- **nginx**: Public-facing on port 8080 (external traffic)
- **backend**: Internal on port 8000 (nginx proxies to it)
- **nginx.conf** correctly points to `http://127.0.0.1:8000` for all proxies

**Fix Applied** (supervisord.conf line 21):
```ini
# BEFORE (broken):
environment=PATH="/usr/local/bin:/usr/bin:/bin",PYTHONPATH="/app:/app/backend",PORT="8080"

# AFTER (fixed):
environment=PATH="/usr/local/bin:/usr/bin:/bin",PYTHONPATH="/app:/app/backend",PORT="8000"
```

---

## Complete supervisord.conf Configuration

```ini
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:nginx]
command=nginx -g 'daemon off;'
autostart=true
autorestart=true
stderr_logfile=/var/log/app/nginx.err.log
stdout_logfile=/var/log/app/nginx.out.log

[program:backend]
directory=/app/backend
command=uvicorn mcp_server:app --host 0.0.0.0 --port %(ENV_PORT)s --workers 1 --limit-max-requests 1000
autostart=true
autorestart=true
priority=20
stderr_logfile=/var/log/app/backend.err.log
stdout_logfile=/var/log/app/backend.out.log
environment=PATH="/usr/local/bin:/usr/bin:/bin",PYTHONPATH="/app:/app/backend",PORT="8000"

[program:market-mcp-server]
directory=/app/market-mcp-server
command=node --max-old-space-size=512 --optimize-for-size index.js 3001
autostart=true
autorestart=true
priority=10
stderr_logfile=/var/log/app/mcp-server.err.log
stdout_logfile=/var/log/app/mcp-server.out.log
environment=PATH="/usr/local/bin:/usr/bin:/bin",NODE_ENV="production"

[program:forex-mcp-server]
directory=/app/forex-mcp-server
command=python src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002
autostart=true
autorestart=true
priority=10
stderr_logfile=/var/log/app/forex-mcp-server.err.log
stdout_logfile=/var/log/app/forex-mcp-server.out.log
environment=PATH="/usr/local/bin:/usr/bin:/bin",PYTHONPATH="/app:/app/forex-mcp-server:/app/forex-mcp-server/src"
```

---

## Port Allocation (Final)

| Service | Port | Binding | Purpose |
|---------|------|---------|---------|
| nginx | 8080 | Public (0.0.0.0) | Frontend & API proxy |
| backend | 8000 | Internal (localhost) | FastAPI server |
| market-mcp-server | 3001 | Internal (localhost) | Yahoo Finance data |
| forex-mcp-server | 3002 | Internal (localhost) | ForexFactory data |

---

## Expected Outcome After Deployment

1. ✅ **nginx** starts on port 8080 (public)
2. ✅ **backend** starts on port 8000 (internal)
3. ✅ **forex-mcp-server** starts on port 3002 (internal)
4. ✅ **market-mcp-server** starts on port 3001 (internal)
5. ✅ No port conflicts
6. ✅ HTTP health check passes
7. ✅ Application accessible at https://gvses-market-insights.fly.dev

---

## Deployment Commands

```bash
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp"
git add supervisord.conf
git commit -m "fix(deploy): correct backend port and forex-mcp-server PYTHONPATH"
fly deploy --app gvses-market-insights
```

---

## Verification Steps

### 1. Check Health Checks
```bash
fly checks list --app gvses-market-insights
```
**Expected**: Both TCP and HTTP checks **passing**

### 2. Check Supervisord Status
```bash
fly ssh console --app gvses-market-insights -C "supervisorctl status"
```
**Expected**: All 4 services showing **RUNNING**

### 3. Test Application
```bash
# Browser test
open https://gvses-market-insights.fly.dev

# API test
curl https://gvses-market-insights.fly.dev/api/forex/calendar?time_period=today

# Health check
curl https://gvses-market-insights.fly.dev/health
```

---

## Lessons Learned

1. **Python Module Resolution**: When running Python scripts in subdirectories with `src/package_name` structure, PYTHONPATH must include the `src/` directory for imports to work

2. **Port Management in Docker**: Always verify port allocation across all services:
   - Public-facing services: bind to 0.0.0.0
   - Internal services: can bind to 0.0.0.0 or 127.0.0.1 (nginx will proxy)
   - No overlapping ports

3. **Supervisord Variables**: Using `%(ENV_PORT)s` requires the environment variable to be set in the `environment=` line, not just in the shell or .env file

4. **nginx Proxy Architecture**:
   - nginx on public port (8080)
   - Backend services on internal ports (8000, 3001, 3002)
   - nginx proxies external requests to internal services

5. **Deployment Verification**: Always check:
   - Service error logs: `/var/log/app/<service>.err.log`
   - Supervisord logs: `/var/log/supervisor/supervisord.log`
   - Health check status: `fly checks list`
   - Actual service status: `supervisorctl status`

---

## Files Modified

1. **supervisord.conf** (2 changes):
   - Line 21: Changed `PORT="8080"` to `PORT="8000"` for backend
   - Line 41: Added `/app/forex-mcp-server/src` to PYTHONPATH for forex-mcp-server

---

## Status

- ✅ **Investigation**: COMPLETE
- ✅ **Root Causes Identified**: 2 issues found
- ✅ **Fixes Applied**: Both fixes implemented
- 🔄 **Deployment**: PENDING (ready to deploy)
- ⏳ **Verification**: PENDING (after deployment)

---

## Timeline

- **Nov 10, 2025**: Initial forex-mcp-server integration completed
- **Nov 11, 2025 01:14 UTC**: Deployment failed, investigation started with Playwright MCP
- **Nov 11, 2025 01:16 UTC**: Problem 1 identified (PYTHONPATH), fix applied, deployed
- **Nov 11, 2025 01:22 UTC**: Problem 2 identified (port conflict), fix applied
- **Nov 11, 2025**: Ready for final deployment

---

**Next Action**: Deploy and verify
