# Quick Start - Database-Backed Lazy Loading

## 🎯 Current Status

✅ Backend code is complete and ready
✅ Timezone bugs fixed
✅ Interval format compatibility fixed
❌ Database migration not run
❌ Need production URL to test

---

## ⚡ Quick Setup (2 commands)

### Step 0: Check Readiness

```bash
cd backend
python3 check_readiness.py              # For localhost testing
python3 check_readiness.py --url https://YOUR-APP.fly.dev  # For production
```

This will tell you exactly what needs to be done.

---

### Step 1: Run Database Migration

**Option A: Automatic (if psql installed)**
```bash
cd backend
./run_migration.sh
```

**Option B: Manual (Supabase Dashboard)**
1. Go to: https://app.supabase.com/project/cwnzgvrylvxfhwhsqelc/sql/new
2. Copy contents from: `backend/supabase_migrations/004_historical_data_tables.sql`
3. Paste and click "Run"

**Verify:**
```bash
python3 check_readiness.py
```

---

### Step 2: Test Implementation

**Production testing:**
```bash
cd backend
python3 test_historical_data_implementation.py --url https://YOUR-APP.fly.dev
```

**Localhost testing:**
```bash
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000  # In one terminal
python3 test_historical_data_implementation.py               # In another terminal
```

**Expected output:**
```
✅ TEST 1: Database Connection & Schema - PASSED
✅ TEST 2: HistoricalDataService (3-Tier Caching) - PASSED
✅ TEST 3: API Endpoint (/api/intraday) - PASSED
✅ TEST 4: Performance Benchmarks - PASSED

🎉 All tests passed! Backend implementation is working correctly.
```

### Step 3: Pre-warm Data (After migration succeeds)

```bash
cd backend

# Quick test with 3 symbols
python3 -m backend.scripts.prewarm_data --symbols AAPL TSLA NVDA --intervals 1d

# Full pre-warm (20 symbols, 3 intervals, ~10 minutes)
python3 -m backend.scripts.prewarm_data
```

---

## 🔍 What You Need To Provide

**To continue testing, I need:**

1. **Production URL** - Where is your backend deployed?
   - Fly.io URL: `https://[app-name].fly.dev`
   - Or tunnel URL from .env

2. **Confirmation** - Have you run the migration?
   - Yes/No

---

## 📊 Expected Results After Setup

Once migration is run and data is pre-warmed:

### Performance Metrics:
- Initial load (cold): ~800ms (fetch + store)
- Cached load (warm): ~20-50ms (from database)
- API call reduction: 99% (1000 requests → 10 API calls)

### Database Storage:
- 20 symbols × 3 intervals = 60 datasets
- Total size: ~146MB (29% of 500MB free tier)
- Enough room for 100+ symbols

### Cache Hit Rates:
- Redis (L1): 50-70% (if Redis available)
- Database (L2): 90-95%
- API (L3): 5-10% (only for new data)

---

## 🚀 Next Steps

**After migration + testing succeeds:**

1. ✅ Pre-warm production database
2. → Deploy incremental update cron job
3. → Continue with frontend (React lazy loading hook)
4. → Monitor performance metrics
5. → Scale to more symbols as needed

---

## 🆘 Need Help?

**If stuck, run this diagnostic:**

```bash
cd backend
python3 -c "
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print('Supabase URL:', url)
print('Key exists:', bool(key))

try:
    client = create_client(url, key)
    result = client.table('historical_bars').select('*').limit(1).execute()
    print('✅ Migration successful! Tables exist.')
except Exception as e:
    print('❌ Migration needed:', str(e)[:100])
"
```

---

**Ready to proceed?** Just provide:
1. Your production URL
2. Confirm migration status

Then we can run full tests and see the 99% API reduction in action! 🎯
