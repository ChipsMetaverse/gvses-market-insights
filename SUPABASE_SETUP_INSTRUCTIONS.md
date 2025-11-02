# 🚀 Supabase Market Data Storage - Setup in Progress

## Phase 1: Foundation Setup

### Step 1: Upgrade to Supabase Pro ✅ (Your Action Required)

**You need to manually upgrade your Supabase plan:**

1. Open this link in your browser:
   ```
   https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/settings/billing
   ```

2. Click **"Upgrade to Pro"** button

3. Confirm payment method ($25/month)

4. Wait for upgrade confirmation (usually instant)

⏱️ **Time:** 2-3 minutes

---

### Step 2: Run SQL Migration ✅ (Execute Now)

**Execute the migration in Supabase SQL Editor:**

#### Option A: Via Supabase Dashboard (Recommended)

1. Open SQL Editor:
   ```
   https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/sql/new
   ```

2. Copy the ENTIRE contents of this file:
   ```
   /Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/supabase_migrations/001_market_data_tables.sql
   ```

3. Paste into the SQL Editor

4. Click **"Run"** button (bottom right)

5. Wait for success message (~30 seconds)

6. Verify tables created by running:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name LIKE 'market_data%'
   ORDER BY table_name;
   ```

   Expected output (should show ~25+ tables):
   ```
   market_data_daily
   market_data_daily_2005
   market_data_daily_2006
   ...
   market_data_daily_2025
   market_data_intraday
   market_data_intraday_2024_11
   market_data_intraday_2024_12
   ...
   symbols
   data_sync_log
   ```

#### Option B: Via Command Line (Alternative)

```bash
# Set your Supabase connection string
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.cwnzgvrylvxfhwhsqelc.supabase.co:5432/postgres"

# Run migration
psql $DATABASE_URL -f backend/supabase_migrations/001_market_data_tables.sql
```

⏱️ **Time:** 5 minutes

---

### Step 3: Test Database Access ✅ (Verify Now)

Run these test queries in SQL Editor to verify everything works:

#### Test 1: Check Storage Stats View
```sql
SELECT * FROM storage_stats;
```

Expected: Should return 3 rows (currently empty tables)

#### Test 2: Check Functions
```sql
SELECT * FROM get_latest_price('AAPL');
```

Expected: Empty result (no data yet, but function works)

#### Test 3: Insert Test Data
```sql
INSERT INTO market_data_daily (symbol, date, open, high, low, close, volume)
VALUES ('TEST', '2024-01-01', 100.00, 105.00, 99.00, 103.50, 1000000);

SELECT * FROM market_data_daily WHERE symbol = 'TEST';
```

Expected: Should return the inserted test record

#### Test 4: Clean Up Test Data
```sql
DELETE FROM market_data_daily WHERE symbol = 'TEST';
```

⏱️ **Time:** 2 minutes

---

## Phase 2: Data Population (Ready to Start)

### Option A: Quick Start - Priority Symbols Only (Recommended)

Populate just the top 30 symbols for immediate testing:

```bash
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend"

# Ensure dependencies are installed
pip install alpaca-py pandas supabase

# Run with priority symbols only (15 minutes)
python populate_market_data.py \
  --symbols AAPL MSFT GOOGL AMZN NVDA META TSLA \
            SPY QQQ IWM DIA \
            JPM BAC WFC GS \
            XOM CVX \
            JNJ UNH PFE \
            COST WMT HD \
            AMD INTC CSCO ORCL NFLX DIS \
  --years 10 \
  --batch-size 5 \
  --rate-limit 0.5
```

**What this does:**
- Fetches 10 years of daily data for 30 symbols
- Takes ~15 minutes
- Uses ~150 MB storage
- Respects API rate limits

**Monitor progress:**
```bash
# In another terminal
tail -f market_data_population.log
```

---

### Option B: Full Population - All Symbols (Overnight Job)

For complete historical data across all available symbols:

```bash
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend"

# Full 20-year backfill for all symbols (run overnight)
nohup python populate_market_data.py \
  --years 20 \
  --batch-size 50 \
  --rate-limit 0.3 \
  > population_full.log 2>&1 &

# Check progress
tail -f population_full.log
```

**What this does:**
- Fetches 20 years of data for ~100 symbols
- Takes ~8-12 hours
- Uses ~6 GB storage
- Runs in background

---

### Option C: Custom Symbol List

Create your own list:

```bash
# Create a custom symbol list
cat > my_symbols.txt << EOF
PLTR
COIN
RBLX
SNOW
ABNB
UBER
LYFT
ZM
DDOG
CRWD
EOF

# Run population
python populate_market_data.py \
  --symbols $(cat my_symbols.txt) \
  --years 5 \
  --rate-limit 0.5
```

---

## Phase 3: Verify Data Population

### Check Data Availability

```sql
-- Count records per symbol
SELECT 
  symbol,
  COUNT(*) AS record_count,
  MIN(date) AS first_date,
  MAX(date) AS last_date,
  MAX(date) - MIN(date) AS days_covered
FROM market_data_daily
GROUP BY symbol
ORDER BY record_count DESC;
```

### Check Storage Usage

```sql
SELECT * FROM storage_stats;
```

Expected after 30 symbols (10 years):
```
table_name        | total_size | data_size | index_size | row_count
------------------|------------|-----------|------------|----------
market_data_daily | 150 MB     | 100 MB    | 50 MB      | ~75,000
symbols           | 500 KB     | 300 KB    | 200 KB     | 30
```

### Query Sample Data

```sql
-- Get latest Apple data
SELECT * FROM market_data_daily 
WHERE symbol = 'AAPL' 
ORDER BY date DESC 
LIMIT 5;

-- Calculate returns
SELECT 
  symbol,
  date,
  close,
  LAG(close) OVER (PARTITION BY symbol ORDER BY date) AS prev_close,
  ROUND(((close - LAG(close) OVER (PARTITION BY symbol ORDER BY date)) / 
         LAG(close) OVER (PARTITION BY symbol ORDER BY date) * 100)::numeric, 2) AS daily_return
FROM market_data_daily
WHERE symbol = 'TSLA'
  AND date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;
```

---

## Phase 4: Set Up Daily Sync (After Initial Population)

### Create Cron Job (macOS/Linux)

```bash
# Edit crontab
crontab -e

# Add this line (runs at 5 PM ET Monday-Friday)
0 17 * * 1-5 cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend" && /usr/local/bin/python3 populate_market_data.py --years 0 >> /tmp/market_sync.log 2>&1
```

### Or Use GitHub Actions (Recommended for Production)

Create `.github/workflows/sync_market_data.yml`:

```yaml
name: Sync Market Data

on:
  schedule:
    # Run at 5 PM ET (9 PM UTC) Monday-Friday
    - cron: '0 21 * * 1-5'
  workflow_dispatch: # Allow manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install alpaca-py pandas supabase
      
      - name: Sync market data
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          ALPACA_API_KEY: ${{ secrets.ALPACA_API_KEY }}
          ALPACA_SECRET_KEY: ${{ secrets.ALPACA_SECRET_KEY }}
        run: |
          cd backend
          python populate_market_data.py --years 0 --batch-size 100
      
      - name: Check sync status
        run: |
          echo "Sync completed at $(date)"
```

---

## Monitoring Dashboard

### Create Custom Queries

Save these as **Saved Queries** in Supabase Dashboard:

#### 1. Daily Health Check
```sql
SELECT 
  'Total Symbols' AS metric,
  COUNT(*)::text AS value
FROM symbols WHERE is_active = true
UNION ALL
SELECT 
  'Total Records',
  COUNT(*)::text
FROM market_data_daily
UNION ALL
SELECT 
  'Storage Used',
  pg_size_pretty(pg_database_size(current_database()))
UNION ALL
SELECT 
  'Last Sync',
  MAX(sync_date)::text
FROM data_sync_log
UNION ALL
SELECT 
  'Stale Symbols (> 2 days)',
  COUNT(*)::text
FROM data_freshness
WHERE days_stale > 2;
```

#### 2. Top Movers Today
```sql
SELECT 
  symbol,
  close,
  daily_return,
  volume
FROM daily_summary
WHERE date = CURRENT_DATE - INTERVAL '1 day'
  AND daily_return IS NOT NULL
ORDER BY ABS(daily_return) DESC
LIMIT 10;
```

#### 3. Sync History
```sql
SELECT 
  sync_date,
  sync_type,
  symbols_updated,
  records_inserted,
  errors,
  duration_seconds,
  status
FROM data_sync_log
ORDER BY sync_date DESC
LIMIT 20;
```

---

## Integration with Backend Code

### Update Market Service to Use Supabase Cache

Create `backend/services/supabase_market_cache.py`:

```python
"""Supabase caching layer for market data"""

import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class SupabaseMarketCache:
    """Cache layer for market data using Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
    
    async def get_historical_bars(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[List[Dict]]:
        """Get historical bars from cache"""
        try:
            result = self.supabase.rpc(
                'get_historical_data',
                {
                    'p_symbol': symbol.upper(),
                    'p_start_date': start_date,
                    'p_end_date': end_date
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"✅ Cache HIT for {symbol}")
                return result.data
            
            logger.info(f"⚠️ Cache MISS for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Cache error for {symbol}: {e}")
            return None
    
    async def get_latest_price(self, symbol: str) -> Optional[Dict]:
        """Get latest price from cache"""
        try:
            result = self.supabase.rpc(
                'get_latest_price',
                {'p_symbol': symbol.upper()}
            ).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error fetching latest price for {symbol}: {e}")
            return None
```

### Integrate with Existing Code

Update `backend/services/market_service_factory.py`:

```python
from .supabase_market_cache import SupabaseMarketCache

# Add to MarketServiceFactory
cache = SupabaseMarketCache()

async def get_stock_bars_with_cache(symbol: str, timeframe: str, start: str, end: str):
    """Get bars with Supabase caching"""
    
    # Try cache first for daily data
    if timeframe in ['1Day', 'day', 'daily']:
        cached_data = await cache.get_historical_bars(symbol, start, end)
        if cached_data:
            return cached_data
    
    # Fallback to API
    data = await alpaca_client.get_bars(symbol, timeframe, start, end)
    
    # Store in cache for next time (async, don't block)
    if timeframe in ['1Day', 'day', 'daily']:
        asyncio.create_task(store_in_cache(symbol, data))
    
    return data
```

---

## Success Metrics

After completing setup, you should see:

✅ **Database:**
- 30+ symbols with 10 years data
- ~75,000 records
- ~150 MB storage used
- Sub-50ms query latency

✅ **Cost:**
- Supabase Pro: $25/month ✅
- API calls: Reduced to ~$0/month ✅
- Total savings: $33/month ✅

✅ **Performance:**
- Historical queries: 10x faster
- Cache hit rate: >90%
- Zero API rate limit errors

---

## Next Steps After Phase 1

1. ✅ **Phase 1 Complete** - Database setup ✅
2. ⏳ **Phase 2 In Progress** - Data population (15 min for priority symbols)
3. 📅 **Phase 3 Pending** - Backend integration (1-2 hours)
4. 📅 **Phase 4 Pending** - Daily sync automation (30 min)
5. 📅 **Phase 5 Pending** - Expand to all 10k symbols (1-2 weeks)

---

## Troubleshooting

### Issue: Migration fails with "permission denied"
**Solution:** Make sure you're using SERVICE_ROLE_KEY, not ANON_KEY

### Issue: Population script errors with "module not found"
**Solution:** 
```bash
pip install alpaca-py pandas supabase python-dotenv
```

### Issue: API rate limit errors
**Solution:** Increase delay:
```bash
python populate_market_data.py --rate-limit 1.0
```

### Issue: Queries are slow
**Solution:** Refresh materialized views:
```sql
SELECT refresh_market_views();
```

---

## Support

- 📚 [Full Analysis](SUPABASE_MARKET_DATA_STORAGE_ANALYSIS.md)
- 🚀 [Implementation Guide](SUPABASE_IMPLEMENTATION_GUIDE.md)
- 💾 [SQL Migration](backend/supabase_migrations/001_market_data_tables.sql)
- 🐍 [Population Script](backend/populate_market_data.py)

---

**Status:** ✅ Ready to Execute  
**Current Step:** Phase 1 - Foundation Setup  
**Action Required:** Run SQL migration in Supabase Dashboard

