# ⚠️ URGENT: Phase 2 Database Migration Required

## Current Status
The Phase 2 multi-worker coordination code is fully implemented but **cannot function** until the database migration is applied.

## Error When Starting Service
```
Failed to register worker: The schema must be one of the following: public, graphql_public
```

This error occurs because the `headless` schema and required tables don't exist yet.

## How to Apply Migration

### Option 1: Supabase Dashboard (Recommended)
1. Go to Supabase Dashboard: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc
2. Navigate to **SQL Editor**
3. Copy the entire contents of `migrations/phase2_supabase.sql`
4. Paste into the SQL Editor
5. Click **Run** to execute

### Option 2: Direct Database Connection
If you have database credentials:
```bash
psql "postgresql://[user]:[password]@db.cwnzgvrylvxfhwhsqelc.supabase.co:5432/postgres" \
  -f migrations/phase2_supabase.sql
```

## What the Migration Creates
- `headless` schema
- `headless_workers` table - Worker registration and tracking
- `headless_job_leases` table - Distributed job coordination  
- `headless_webhook_events` table - Webhook delivery tracking
- Supporting indexes and constraints
- Update triggers for timestamp management

## After Migration is Applied
Once the migration is successfully applied, the service will:
1. Register the worker in Supabase
2. Start heartbeat mechanism
3. Begin processing jobs with lease management
4. Enable orphan job recovery
5. Handle webhook notifications

## Verification
After applying the migration, verify it worked:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'headless';
```

Should return:
- headless_jobs
- headless_workers
- headless_job_leases
- headless_webhook_events

## Next Steps
1. Apply the migration using one of the methods above
2. Restart the service: `npm start`
3. Check worker registration: `curl http://localhost:3100/worker/stats`
4. Submit a test job to verify distributed processing