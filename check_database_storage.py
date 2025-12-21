#!/usr/bin/env python3
"""Check if the tested symbols are stored in Supabase database"""
import os
import sys
from dotenv import load_dotenv

# Load environment
sys.path.insert(0, '/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend')
load_dotenv('/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/.env')

from supabase import create_client

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY")
    sys.exit(1)

# Create client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test symbols
TEST_SYMBOLS = ['AMZN', 'GOOGL', 'MSFT', 'META', 'NFLX', 'DIS', 'TSLA']

print("="*80)
print("DATABASE STORAGE VERIFICATION")
print("="*80)

for symbol in TEST_SYMBOLS:
    print(f"\n{'='*80}")
    print(f"Checking: {symbol}")
    print('='*80)

    # Check data_coverage table
    try:
        coverage = supabase.table('data_coverage') \
            .select('*') \
            .eq('symbol', symbol) \
            .eq('interval', '1mo') \
            .execute()

        if coverage.data and len(coverage.data) > 0:
            cov = coverage.data[0]
            print(f"✅ Found in data_coverage:")
            print(f"   Earliest bar: {cov.get('earliest_bar')}")
            print(f"   Latest bar: {cov.get('latest_bar')}")
            print(f"   Total bars: {cov.get('total_bars')}")
            print(f"   Last fetched: {cov.get('last_fetched_at')}")
        else:
            print(f"❌ NOT found in data_coverage")

    except Exception as e:
        print(f"❌ Error checking data_coverage: {e}")

    # Count actual bars in historical_bars table
    try:
        bars = supabase.table('historical_bars') \
            .select('timestamp', count='exact') \
            .eq('symbol', symbol) \
            .eq('interval', '1mo') \
            .execute()

        bar_count = bars.count if hasattr(bars, 'count') else 0

        if bar_count and bar_count > 0:
            print(f"✅ Found {bar_count} monthly bars in historical_bars")

            # Get first and last bar
            first_bar = supabase.table('historical_bars') \
                .select('timestamp, open') \
                .eq('symbol', symbol) \
                .eq('interval', '1mo') \
                .order('timestamp', desc=False) \
                .limit(1) \
                .execute()

            last_bar = supabase.table('historical_bars') \
                .select('timestamp, close') \
                .eq('symbol', symbol) \
                .eq('interval', '1mo') \
                .order('timestamp', desc=True) \
                .limit(1) \
                .execute()

            if first_bar.data and last_bar.data:
                print(f"   First: {first_bar.data[0]['timestamp']} (open: ${first_bar.data[0]['open']:.2f})")
                print(f"   Last: {last_bar.data[0]['timestamp']} (close: ${last_bar.data[0]['close']:.2f})")
        else:
            print(f"❌ No bars found in historical_bars")

    except Exception as e:
        print(f"❌ Error checking historical_bars: {e}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("If symbols show '✅ Found in data_coverage' and monthly bars, they are cached!")
print("Next request will be served from Supabase L2 cache (~20-200ms)")
print("="*80)
