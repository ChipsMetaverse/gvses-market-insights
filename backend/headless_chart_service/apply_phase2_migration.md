# Phase 2 Migration Instructions

## Quick Apply via Supabase Dashboard

1. Go to your Supabase project: https://cwnzgvrylvxfhwhsqelc.supabase.co
2. Navigate to SQL Editor
3. Copy the contents of `migrations/phase2_supabase.sql`
4. Paste and execute in SQL Editor

## Or Apply via Supabase CLI

```bash
# Set up Supabase project link (one time)
supabase link --project-ref cwnzgvrylvxfhwhsqelc

# Apply the migration
supabase db push --file migrations/phase2_supabase.sql
```

## Migration Summary

This migration creates:
- `headless_workers` table - Tracks active worker instances
- `headless_job_leases` table - Manages exclusive job leases
- `headless_webhook_events` table - Tracks webhook delivery attempts
- Supporting indexes and constraints for performance

## Verification

After applying, verify tables exist:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'headless' 
AND table_name IN ('headless_workers', 'headless_job_leases', 'headless_webhook_events');
```

Should return 3 rows.