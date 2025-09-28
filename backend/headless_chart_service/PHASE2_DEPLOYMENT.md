# Phase 2 Multi-Worker Coordination - Deployment Guide

## ✅ Completed Implementation

All Phase 2 code has been successfully implemented:
- Worker registration and heartbeat system
- Distributed job leasing mechanism
- Orphan job recovery
- Server integration with new endpoints
- Database migration files

## 🚀 Deployment Steps

### 1. Environment Configuration ✅
The `.env` file has been created with:
```bash
SUPABASE_URL=https://cwnzgvrylvxfhwhsqelc.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<configured>
SUPABASE_SCHEMA=headless
WORKER_ID=worker-1
```

### 2. Database Migration 📋

**Option A: Via Supabase Dashboard (Recommended)**
1. Go to: https://cwnzgvrylvxfhwhsqelc.supabase.co
2. Navigate to **SQL Editor**
3. Copy contents of `migrations/phase2_supabase.sql`
4. Paste and execute

**Option B: Via SQL Client**
If you have a PostgreSQL client configured:
```sql
-- Run the contents of migrations/phase2_supabase.sql
```

**What the migration creates:**
- `headless.headless_workers` - Worker registration table
- `headless.headless_job_leases` - Job lease management
- `headless.headless_webhook_events` - Webhook tracking
- Supporting indexes and constraints

### 3. Build and Start Service

```bash
# Build TypeScript
npm run build

# Start first worker
npm start

# Or use the helper script
./run_phase2.sh
```

### 4. Verify Worker Registration

```bash
# Check worker status
curl http://localhost:3100/worker/stats

# Expected response:
{
  "workerId": "worker-1",
  "hostname": "your-machine",
  "status": "active",
  "activeJobs": 0,
  "maxConcurrent": 3,
  "utilization": 0,
  "timestamp": 1234567890
}
```

### 5. Test Job Distribution

```bash
# Submit a test render job
curl -X POST http://localhost:3100/render \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "timeframe": "1D",
    "commands": ["show price"],
    "priority": 100
  }'

# Check distributed stats
curl http://localhost:3100/distributed/stats
```

### 6. Test Multi-Worker Coordination

Open a second terminal:
```bash
# Start second worker
WORKER_ID=worker-2 PORT=3101 npm start
```

Submit multiple jobs and observe distribution across workers.

### 7. Test Orphan Recovery

```bash
# Manually trigger orphan recovery
curl -X POST http://localhost:3100/distributed/recover-orphans

# Check response
{
  "message": "Orphan recovery triggered"
}
```

## 📊 New Monitoring Endpoints

- `GET /worker/stats` - Current worker statistics
- `GET /distributed/stats` - Distributed queue overview
- `POST /distributed/recover-orphans` - Manual orphan recovery
- `GET /webhooks/stats` - Webhook delivery statistics

## 🔍 Verification Checklist

- [ ] Database migration applied successfully
- [ ] Service starts without errors
- [ ] Worker registers in Supabase
- [ ] Jobs can be submitted via `/render`
- [ ] Worker stats endpoint responds
- [ ] Distributed stats show queue status
- [ ] Multiple workers coordinate without duplication

## 🐛 Troubleshooting

### Service won't start
- Check `.env` file exists and has correct credentials
- Verify database migration was applied
- Check logs for specific error messages

### Worker not registering
- Verify Supabase connection
- Check `headless_workers` table exists
- Ensure WORKER_ID is unique

### Jobs not processing
- Check worker has capacity (`/worker/stats`)
- Verify no leases are stuck (`/distributed/stats`)
- Trigger orphan recovery if needed

### Database connection issues
- Verify SUPABASE_URL is correct
- Check network connectivity
- Ensure service role key has proper permissions

## 📝 Next Steps

After successful deployment:
1. Monitor worker performance
2. Test failover scenarios
3. Configure production worker count
4. Set up monitoring alerts
5. Document operational procedures

## 🎉 Success Indicators

You'll know Phase 2 is working when:
- Multiple workers show as "active" in stats
- Jobs distribute across workers
- No job duplication occurs
- Failed workers release jobs automatically
- Orphan recovery reclaims stuck jobs

## 📚 Additional Resources

- `PHASE2_COMPLETE.md` - Technical implementation details
- `HEADLESS_ARCHITECTURE.md` - Overall system design
- `apply_phase2_migration.md` - Migration instructions
- `.env.example` - Environment variable reference