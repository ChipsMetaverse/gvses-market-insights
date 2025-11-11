# Query Logs Investigation

**Date:** November 8, 2025

---

## 🔍 What I Found

### Query Logging Infrastructure

1. **Database Logging (Supabase)**
   - **Table:** `query_analytics`
   - **Endpoint:** `/api/analytics/queries`
   - **Status:** ✅ Endpoint exists, but returns empty `{}`
   - **Location:** `backend/services/database_service.py` - `log_query()` method
   - **Usage:** Called from `/api/messages` endpoint when messages are saved

2. **Log Files Found**
   - `market-mcp-server/mcp-server.log` - MCP server startup logs (minimal)
   - `backend/market_data_population.log` - Market data population logs
   - `backend/debug_chart_commands.log` - Debug script logs (local testing)

3. **Production Logs (Fly.io)**
   - Checked via `flyctl logs` - No query-related entries found
   - Only stock price API calls visible
   - No agent/orchestrate/voice-query endpoints being called

---

## ❓ Questions

**Where are the log files you're referring to?**

Possible locations:
1. **Supabase Database** - `query_analytics` table (currently empty)
2. **Local Log Files** - On your machine (not found in repo)
3. **Production Log Files** - On Fly.io machines (need SSH access)
4. **Application Logs** - stdout/stderr logs captured by Fly.io
5. **Frontend Logs** - Browser console logs or frontend log files

---

## 🔧 How to Access Query Logs

### Option 1: Supabase Database (If Queries Are Being Logged)
```sql
-- Query the analytics table directly
SELECT * FROM query_analytics 
ORDER BY timestamp DESC 
LIMIT 100;
```

### Option 2: Check Production Logs More Thoroughly
```bash
# Get all logs and search for query patterns
flyctl logs -a gvses-market-insights-api --no-tail | \
  grep -E "(query|Query|orchestrate|voice)" > query_logs.txt
```

### Option 3: Enable Query Logging
Currently, queries are only logged when:
- `/api/messages` endpoint is called (saves messages)
- This might not be called for agent queries

**Need to add logging to:**
- `/api/agent/orchestrate` endpoint
- `/api/agent/voice-query` endpoint

---

## 📋 Next Steps

1. **Clarify Location:** Where are the log files you mentioned?
2. **Check Database:** Query Supabase `query_analytics` table directly
3. **Add Logging:** If queries aren't being logged, add logging to agent endpoints
4. **Export Logs:** If logs exist elsewhere, export them for analysis

---

**Please let me know:**
- Where are these log files located?
- Are they in Supabase, local files, or production?
- What format are they in (JSON, text, database)?


