# Migration Status Report
**Date**: January 9, 2025
**Migration**: 002_request_logs.sql
**Status**: ⚠️ **Pending Manual Execution**

---

## 📋 Current Situation

The request telemetry instrumentation is **complete and ready**, but the database migration needs to be run manually because:

✅ **Completed**:
- Request logging code instrumented in `backend/mcp_server.py`
- Migration SQL file created at `backend/supabase_migrations/002_request_logs.sql`
- Supabase credentials verified in `backend/.env`
- Migration copied to `supabase/migrations/20251109000002_request_logs.sql`

⚠️ **Blocked**:
- Migration cannot be run via Supabase CLI (migration history mismatch)
- Python/REST API cannot execute DDL (CREATE TABLE) statements
- Requires either: database password OR Supabase Dashboard access

---

## 🎯 Action Required: Run the Migration

### Option 1: Supabase Dashboard SQL Editor (Recommended - 2 minutes)

**Steps**:
1. Visit: https://app.supabase.com/project/cwnzgvrylvxfhwhsqelc/sql/new

2. Paste this SQL:

```sql
-- ============================================
-- Request Logging Schema
-- Supabase PostgreSQL Migration
-- Version: 1.1
-- Date: 2025-11-09
-- ============================================

-- Ensure UUID extension is available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Request Logs Table
-- ============================================

CREATE TABLE IF NOT EXISTS request_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event TEXT NOT NULL,
    request_id TEXT,
    path TEXT,
    method TEXT,
    client_ip TEXT,
    forwarded_for TEXT,
    user_agent TEXT,
    session_id TEXT,
    user_id TEXT,
    duration_ms NUMERIC(12, 3),
    cost_summary JSONB,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Helpful indexes for querying request history
CREATE INDEX IF NOT EXISTS idx_request_logs_created_at
    ON request_logs (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_request_logs_event
    ON request_logs (event);

CREATE INDEX IF NOT EXISTS idx_request_logs_request_id
    ON request_logs (request_id)
    WHERE request_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_request_logs_user_id
    ON request_logs (user_id)
    WHERE user_id IS NOT NULL;
```

3. Click **"Run"** button

4. Verify success: Run `python3 backend/verify_migration.py`

---

### Option 2: psql Command Line (If you have database password)

```bash
# Get database password from Supabase Dashboard:
# Settings > Database > Connection Pooling > Password

psql 'postgresql://postgres:[YOUR_PASSWORD]@db.cwnzgvrylvxfhwhsqelc.supabase.co:5432/postgres' \
  -f backend/supabase_migrations/002_request_logs.sql
```

---

## 🧪 Verification After Running Migration

Once you've run the migration, verify it worked:

```bash
cd backend
python3 verify_migration.py
```

**Expected output**:
```
✅ request_logs table exists and is accessible!
   Current row count: 0
📋 Verifying table schema...
✅ Can insert records into request_logs
✅ Can delete records from request_logs
🎉 Migration verification complete! Everything works correctly.
```

---

## 🔍 Testing the Telemetry System

After migration is complete, test the instrumented endpoints:

### 1. Start the Backend Server

```bash
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

### 2. Make Test Requests

```bash
# Test market overview endpoint
curl http://localhost:8000/api/market-overview

# Test voice signed URL endpoint
curl http://localhost:8000/elevenlabs/signed-url
```

### 3. Check Logs Were Written

```python
# Run this Python script to see recent logs
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

# Get last 10 requests
result = client.table('request_logs')\
    .select('*')\
    .order('created_at', desc=True)\
    .limit(10)\
    .execute()

for log in result.data:
    print(f"{log['created_at']}: {log['method']} {log['path']} - {log['duration_ms']}ms")
```

---

## 📊 What the Migration Creates

**Table**: `request_logs`
- Stores every request to instrumented endpoints
- Tracks timing, metadata, and errors
- Enables analytics queries

**Columns**:
- `id` - UUID primary key
- `event` - Event type (e.g., "api.market_overview", "api.signed_url")
- `request_id` - Unique request identifier for tracing
- `path` - API endpoint path
- `method` - HTTP method (GET, POST, etc.)
- `client_ip` - Client IP address
- `forwarded_for` - X-Forwarded-For header
- `user_agent` - Client user agent
- `session_id` - Voice/chat session ID (if applicable)
- `user_id` - User ID (if authenticated)
- `duration_ms` - Request duration in milliseconds
- `cost_summary` - API costs (JSONB)
- `payload` - Request/response metadata (JSONB)
- `created_at` - Timestamp

**Indexes**:
- `idx_request_logs_created_at` - Fast time-range queries
- `idx_request_logs_event` - Filter by event type
- `idx_request_logs_request_id` - Trace specific requests
- `idx_request_logs_user_id` - Per-user analytics

---

## 🎯 Next Steps After Migration

Once migration is complete:

1. ✅ Run verification script
2. ✅ Test instrumented endpoints
3. ✅ Confirm logs are being written
4. 📊 Build analytics queries (optional)
5. 🔧 Instrument additional endpoints (optional)

---

## 📁 Files Created

- `backend/supabase_migrations/002_request_logs.sql` - Migration SQL
- `backend/verify_migration.py` - Verification script
- `backend/run_migration.py` - Alternative runner (requires DB password)
- `supabase/migrations/20251109000002_request_logs.sql` - CLI copy
- `MIGRATION_STATUS.md` - This file

---

## 🆘 Troubleshooting

**Issue**: "relation does not exist" error
**Solution**: Run the migration using Option 1 or 2 above

**Issue**: "permission denied" error
**Solution**: Make sure you're using the Supabase Dashboard (has full permissions)

**Issue**: Migration runs but table doesn't show up
**Solution**: Refresh the Supabase Dashboard, check you're in the right project

---

**Status**: 🟡 Waiting for manual migration execution
**Time Required**: ~2 minutes
**Difficulty**: Easy (copy/paste in web UI)
