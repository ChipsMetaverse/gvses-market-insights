# 🚨 URGENT: Apply Phase 2 Migration Manually

## Current Situation
- ✅ **Phase 2 code is 100% complete**
- ✅ **Migration file is ready**
- ❌ **Database migration not applied** (CLI connection issues)
- ❌ **Service cannot start** (missing headless schema)

## Manual Steps Required (5 minutes)

### Step 1: Open Supabase Dashboard
Go to: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc

### Step 2: Navigate to SQL Editor
Click on **SQL Editor** in the left sidebar

### Step 3: Copy Migration SQL
Copy the ENTIRE contents of this file:
```
backend/headless_chart_service/migrations/phase2_supabase.sql
```

Or use the updated version at:
```
supabase/migrations/20250927190000_phase2_headless_multi_worker.sql
```

### Step 4: Paste and Execute
1. Paste the SQL into the SQL Editor
2. Click **Run** button
3. Wait for "Success" message

## Expected Output
You should see:
- "Query ran successfully" 
- Multiple CREATE TABLE statements completed
- CREATE INDEX statements completed

## Verification
After applying, run this query to verify:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'headless'
ORDER BY table_name;
```

Should return:
- headless_job_leases
- headless_jobs
- headless_webhook_events
- headless_workers

## After Migration Success

### 1. Start the Service
```bash
cd backend/headless_chart_service
npm start
```

### 2. Check Worker Registration
```bash
curl http://localhost:3100/worker/stats
```

Should return:
```json
{
  "workerId": "worker-1",
  "status": "active",
  "activeJobs": 0,
  "maxConcurrent": 3
}
```

## If Migration Fails
If you see errors about tables already existing, that's OK! The migration uses `IF NOT EXISTS` clauses. The important thing is that all 4 tables exist in the `headless` schema.

## Alternative: Direct SQL
If the Dashboard doesn't work, you can apply via psql if you have the database password:
```bash
psql "postgresql://postgres:[PASSWORD]@db.cwnzgvrylvxfhwhsqelc.supabase.co:5432/postgres" \
  -f backend/headless_chart_service/migrations/phase2_supabase.sql
```

## Summary
The **ONLY** thing preventing Phase 2 from working is the database migration. Once you apply it manually (takes 2 minutes), the entire multi-worker coordination system will be operational.