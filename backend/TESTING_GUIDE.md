# Historical Data Implementation - Testing Guide

This guide walks you through testing the new database-backed lazy loading architecture.

## 📋 Prerequisites Checklist

- [x] Supabase account and project created
- [x] `.env` file configured with Supabase credentials
- [x] Alpaca API credentials in `.env`
- [ ] Database migration executed
- [ ] Redis running (optional but recommended)
- [ ] Backend server running

---

## 🚀 Step-by-Step Testing

### Step 1: Run Database Migration

The migration creates 3 tables: `historical_bars`, `data_coverage`, and `api_call_log`.

**Option A: Supabase Dashboard (Recommended)**
```bash
# 1. Open Supabase SQL Editor
https://app.supabase.com/project/<your-project>/sql/new

# 2. Copy contents of this file:
backend/supabase_migrations/004_historical_data_tables.sql

# 3. Paste into SQL Editor and click "Run"
```

**Option B: Supabase CLI**
```bash
cd backend
supabase db push
```

**Option C: Direct psql**
```bash
# Get DATABASE_URL from Supabase dashboard
psql $DATABASE_URL < backend/supabase_migrations/004_historical_data_tables.sql
```

**Verify migration:**
```sql
-- Run this in Supabase SQL Editor
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('historical_bars', 'data_coverage', 'api_call_log');
```

You should see all 3 tables listed.

---

### Step 2: Start Redis (Optional)

Redis provides L1 caching (fastest tier). If Redis isn't available, the system falls back to L2 (Supabase) only.

**Mac/Linux:**
```bash
# Install if needed
brew install redis  # Mac
# OR
sudo apt-get install redis  # Ubuntu

# Start Redis
redis-server

# Verify running
redis-cli ping
# Should return: PONG
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**Skip Redis:**
System will work without Redis, using Supabase as primary cache.

---

### Step 3: Start Backend Server

```bash
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

**Verify server is running:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

Keep this terminal open.

---

### Step 4: Run Test Suite

Open a **new terminal** and run:

```bash
cd backend
python3 test_historical_data_implementation.py
```

**Expected Output:**

```
╔════════════════════════════════════════════════════════════════════════════╗
║            HISTORICAL DATA IMPLEMENTATION TEST SUITE                       ║
╚════════════════════════════════════════════════════════════════════════════╝

TEST 1: Database Connection & Schema
✅ Table 'historical_bars' exists and is accessible
✅ Table 'data_coverage' exists and is accessible
✅ Table 'api_call_log' exists and is accessible
✅ Database connection verified

TEST 2: HistoricalDataService (3-Tier Caching)
✅ HistoricalDataService initialized
✅ First request: 21 bars in 823ms
✅ Second request: 21 bars in 18ms
✅ Cache speedup: 45.7x faster

TEST 3: API Endpoint (/api/intraday)
✅ Backend server is running
✅ Standard mode: 21 bars fetched
ℹ️  Cache tier: api
ℹ️  Duration: 847.3ms
✅ Lazy loading mode: 452 bars fetched
ℹ️  Cache tier: database
✅ API endpoint tests passed

TEST 4: Performance Benchmarks
...

Overall: 4/4 tests passed
🎉 All tests passed! Backend implementation is working correctly.
```

**If tests fail:**
- ❌ Database errors → Check Step 1 (migration)
- ❌ Service errors → Check Step 2 (Redis, optional)
- ❌ API errors → Check Step 3 (server running)

---

### Step 5: Pre-warm Database (Initial Data Load)

This populates the database with top 20 symbols for instant loading.

**Full pre-warming (all symbols):**
```bash
cd backend
python3 -m backend.scripts.prewarm_data
```

**Expected output:**
```
🔥 DATA PRE-WARMING STARTED
Symbols: 20
Intervals: 3
Total datasets: 60

📊 Processing TSLA...
  → 5m (5-minute bars for short-term trading): 60 days of history
  ✅ TSLA 5m: 4,680 bars (2,341ms)
  → 1h (1-hour bars for medium-term analysis): 365 days of history
  ✅ TSLA 1h: 2,535 bars (1,892ms)
  → 1d (Daily bars for long-term investing): 2555 days of history
  ✅ TSLA 1d: 1,750 bars (1,156ms)

...

🎉 PRE-WARMING COMPLETED
Symbols processed: 20/20
Total bars stored: 136,500
Duration: 187.3s
```

**Custom pre-warming (specific symbols):**
```bash
# Just 3 symbols
python3 -m backend.scripts.prewarm_data --symbols AAPL TSLA NVDA

# Just daily data
python3 -m backend.scripts.prewarm_data --intervals 1d

# Combination
python3 -m backend.scripts.prewarm_data --symbols AAPL MSFT --intervals 5m 1h
```

---

### Step 6: Test API with Pre-warmed Data

Now test the API with symbols that were pre-warmed:

```bash
# This should be FAST (sub-200ms from database cache)
curl "http://localhost:8000/api/intraday?symbol=AAPL&interval=5m&days=60"
```

**Response:**
```json
{
  "symbol": "AAPL",
  "interval": "5m",
  "data_source": "database",  ← From L2 cache!
  "bars": [...],
  "count": 4680,
  "cache_tier": "database",
  "duration_ms": 23.5  ← Sub-200ms! ✅
}
```

**Test lazy loading (date range):**
```bash
curl "http://localhost:8000/api/intraday?symbol=TSLA&interval=1h&startDate=2024-01-01&endDate=2024-02-01"
```

---

### Step 7: Monitor Performance

**Check database size:**
```sql
-- Run in Supabase SQL Editor
SELECT
  pg_size_pretty(pg_total_relation_size('historical_bars')) as total_size,
  COUNT(*) as total_bars
FROM historical_bars;
```

**Check cache metrics:**
```bash
# View API call logs
curl "http://localhost:8000/api/intraday?symbol=AAPL&interval=5m&days=60" | jq '.cache_tier'
```

**Expected metrics after pre-warming:**
- Initial load: ~60 API calls (one-time)
- Subsequent requests: 0 API calls (100% cache hits)
- Response time: 20-200ms (vs 300-500ms before)
- Database size: ~146MB (20 symbols × 3 intervals)

---

## 🎯 Success Criteria

✅ **All 4 test suites pass**
✅ **Pre-warming completes without errors**
✅ **Database contains 100k+ bars**
✅ **API responses < 200ms for cached symbols**
✅ **Cache hit rate > 90%**
✅ **No API calls for repeated symbol requests**

---

## 🐛 Troubleshooting

### Issue: "Tables don't exist"
**Solution:** Run Step 1 (database migration)

### Issue: "Redis unavailable"
**Solution:** Either:
- Start Redis (Step 2)
- OR ignore warning (system works without Redis)

### Issue: "Backend server not running"
**Solution:** Start server (Step 3)

### Issue: "No bars returned"
**Possible causes:**
1. Invalid symbol (try AAPL, TSLA, NVDA)
2. Weekend/market closed (Alpaca has no data)
3. Network issue connecting to Alpaca API

### Issue: "Slow performance"
**Check:**
1. Database migration ran successfully
2. Data is pre-warmed (Step 5)
3. Supabase indexes created (part of migration)

### Issue: "API rate limit"
**Solution:**
- Pre-warming hit rate limit (200/min)
- Wait 1 minute and retry
- Reduce symbols: `--symbols AAPL TSLA NVDA`

---

## 📊 Expected Performance Improvements

### Before (API-only):
- Every request: 300-500ms
- 1000 chart views: 1000 API calls
- Risk of rate limiting

### After (Database-backed):
- First request (cold): 500-1000ms (fetch + store)
- Cached request (warm): 20-200ms (from database)
- 1000 chart views: ~10 API calls (99% reduction!)
- No rate limiting risk

---

## 🔄 Incremental Updates (Cron Setup)

To keep data up-to-date, set up incremental updates:

**Manual update:**
```bash
python3 -m backend.scripts.update_recent_data
```

**Cron job (update every 15 min during market hours):**
```cron
# Add to crontab: crontab -e
*/15 9-16 * * 1-5 cd /app/backend && python3 -m backend.scripts.update_recent_data >> /var/log/app/data_updates.log 2>&1
```

---

## ✅ Next Steps After Testing

Once all tests pass:

1. ✅ **Backend is production-ready**
2. → Continue with frontend (React hook for lazy loading)
3. → Set up cron jobs for incremental updates
4. → Deploy to production
5. → Monitor cache hit rates and performance

---

## 📞 Support

If you encounter issues:
1. Check logs in terminal
2. Review error messages
3. Verify .env credentials
4. Check Supabase dashboard for table existence
5. Ensure Alpaca API keys are valid

Good luck! 🚀
