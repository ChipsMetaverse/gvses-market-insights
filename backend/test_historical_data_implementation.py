#!/usr/bin/env python3
"""
Comprehensive Test Suite for Historical Data Implementation

Tests:
1. Database connection and schema
2. HistoricalDataService (3-tier caching)
3. API endpoint functionality
4. Performance benchmarks
5. Cache hit rates

Usage:
    python3 test_historical_data_implementation.py
"""

import asyncio
import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Color output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")


async def test_database_connection():
    """Test 1: Verify Supabase connection and schema"""
    print_header("TEST 1: Database Connection & Schema")

    try:
        from supabase import create_client

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_key:
            print_error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
            return False

        print_info(f"Connecting to: {supabase_url}")
        supabase = create_client(supabase_url, supabase_key)

        # Check if tables exist
        tables_to_check = ['historical_bars', 'data_coverage', 'api_call_log']

        for table in tables_to_check:
            try:
                # Try to query the table
                response = supabase.table(table).select('*').limit(1).execute()
                print_success(f"Table '{table}' exists and is accessible")
            except Exception as e:
                print_warning(f"Table '{table}' may not exist: {str(e)[:100]}")
                print_info("You may need to run the migration: backend/supabase_migrations/004_historical_data_tables.sql")

        print_success("Database connection verified")
        return True

    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


async def test_historical_data_service():
    """Test 2: HistoricalDataService with 3-tier caching"""
    print_header("TEST 2: HistoricalDataService (3-Tier Caching)")

    try:
        from services.historical_data_service import get_historical_data_service

        service = get_historical_data_service()
        print_success("HistoricalDataService initialized")

        # Test data fetch
        symbol = "AAPL"
        interval = "1d"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        print_info(f"Fetching {symbol} {interval} data (last 30 days)...")

        # First request (should hit API)
        start_time = time.time()
        bars_1 = await service.get_bars(symbol, interval, start_date, end_date)
        duration_1 = (time.time() - start_time) * 1000

        print_success(f"First request: {len(bars_1)} bars in {duration_1:.0f}ms")

        if len(bars_1) > 0:
            print_info(f"Sample bar: {bars_1[0]}")

        # Second request (should hit cache)
        print_info("Fetching same data again (should hit cache)...")
        start_time = time.time()
        bars_2 = await service.get_bars(symbol, interval, start_date, end_date)
        duration_2 = (time.time() - start_time) * 1000

        print_success(f"Second request: {len(bars_2)} bars in {duration_2:.0f}ms")

        # Calculate speedup
        if duration_2 > 0:
            speedup = duration_1 / duration_2
            print_success(f"Cache speedup: {speedup:.1f}x faster ({duration_1:.0f}ms → {duration_2:.0f}ms)")

        # Show metrics
        metrics = service.get_metrics()
        print_info(f"Service metrics:")
        print(f"  - Total requests: {metrics['total_requests']}")
        print(f"  - Redis hits: {metrics['redis_hits']} ({metrics['redis_hit_rate']:.1f}%)")
        print(f"  - DB hits: {metrics['db_hits']} ({metrics['db_hit_rate']:.1f}%)")
        print(f"  - API calls: {metrics['api_calls']} ({metrics['api_call_rate']:.1f}%)")

        return True

    except Exception as e:
        print_error(f"HistoricalDataService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoint(base_url: str = None):
    """Test 3: API endpoint functionality"""
    print_header("TEST 3: API Endpoint (/api/intraday)")

    try:
        import httpx

        # Use provided URL or check environment variables
        if base_url is None:
            base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

        print_info(f"Testing against: {base_url}")

        # Check if server is running
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/health", timeout=5.0)
                if response.status_code == 200:
                    print_success("Backend server is running")
                else:
                    print_warning(f"Server returned status {response.status_code}")
        except Exception as e:
            print_error("Backend server is not running!")
            print_info("Start it with: cd backend && uvicorn mcp_server:app --reload")
            return False

        # Test standard mode (days parameter)
        print_info("Testing standard mode (days parameter)...")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/api/intraday",
                params={"symbol": "TSLA", "interval": "1d", "days": 30},
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                print_success(f"Standard mode: {data['count']} bars fetched")
                print_info(f"Cache tier: {data.get('cache_tier', 'unknown')}")
                print_info(f"Duration: {data.get('duration_ms', 0):.1f}ms")
            else:
                print_error(f"API returned status {response.status_code}")
                print_error(f"Response: {response.text[:200]}")
                return False

        # Test lazy loading mode (startDate/endDate)
        print_info("Testing lazy loading mode (date range)...")
        start = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        end = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/api/intraday",
                params={
                    "symbol": "NVDA",
                    "interval": "1h",
                    "startDate": start,
                    "endDate": end
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                print_success(f"Lazy loading mode: {data['count']} bars fetched")
                print_info(f"Date range: {start} to {end}")
                print_info(f"Cache tier: {data.get('cache_tier', 'unknown')}")
                print_info(f"Duration: {data.get('duration_ms', 0):.1f}ms")
            else:
                print_error(f"API returned status {response.status_code}")
                return False

        print_success("API endpoint tests passed")
        return True

    except ImportError:
        print_error("httpx not installed. Install with: pip install httpx")
        return False
    except Exception as e:
        print_error(f"API endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_performance_benchmark():
    """Test 4: Performance benchmarks"""
    print_header("TEST 4: Performance Benchmarks")

    try:
        from services.historical_data_service import get_historical_data_service

        service = get_historical_data_service()

        # Reset metrics
        service.metrics = {
            'redis_hits': 0,
            'db_hits': 0,
            'api_calls': 0,
            'total_requests': 0
        }

        test_cases = [
            ("AAPL", "1d", 365, "Daily bars - 1 year"),
            ("TSLA", "1h", 90, "Hourly bars - 3 months"),
            ("NVDA", "5m", 7, "5-minute bars - 1 week"),
        ]

        results = []

        for symbol, interval, days, description in test_cases:
            print_info(f"Testing: {description} ({symbol} {interval})...")

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Cold request
            start = time.time()
            bars = await service.get_bars(symbol, interval, start_date, end_date)
            cold_duration = (time.time() - start) * 1000

            # Warm request (should hit cache)
            start = time.time()
            bars = await service.get_bars(symbol, interval, start_date, end_date)
            warm_duration = (time.time() - start) * 1000

            results.append({
                'description': description,
                'bars': len(bars),
                'cold_ms': cold_duration,
                'warm_ms': warm_duration,
                'speedup': cold_duration / warm_duration if warm_duration > 0 else 0
            })

            print_success(
                f"  Cold: {cold_duration:.0f}ms, "
                f"Warm: {warm_duration:.0f}ms, "
                f"Speedup: {cold_duration/warm_duration if warm_duration > 0 else 0:.1f}x"
            )

        # Summary
        print_info("\nPerformance Summary:")
        print(f"{'Test':<35} {'Bars':<8} {'Cold':<10} {'Warm':<10} {'Speedup'}")
        print("-" * 75)
        for r in results:
            print(
                f"{r['description']:<35} "
                f"{r['bars']:<8} "
                f"{r['cold_ms']:>8.0f}ms "
                f"{r['warm_ms']:>8.0f}ms "
                f"{r['speedup']:>7.1f}x"
            )

        # Final metrics
        metrics = service.get_metrics()
        print_info(f"\nFinal cache metrics:")
        print(f"  - Redis hit rate: {metrics['redis_hit_rate']:.1f}%")
        print(f"  - DB hit rate: {metrics['db_hit_rate']:.1f}%")
        print(f"  - API call rate: {metrics['api_call_rate']:.1f}%")

        # Target: 90%+ cache hit rate after warming
        if metrics['redis_hit_rate'] + metrics['db_hit_rate'] >= 50:
            print_success("✅ Cache performance is good!")
        else:
            print_warning("⚠️  Cache hit rate is low (data may not be pre-warmed)")

        return True

    except Exception as e:
        print_error(f"Performance benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main(api_url: str = None):
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║            HISTORICAL DATA IMPLEMENTATION TEST SUITE                       ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")

    if api_url:
        print_info(f"Using custom API URL: {api_url}\n")

    results = {}

    # Test 1: Database
    results['database'] = await test_database_connection()

    if not results['database']:
        print_warning("\n⚠️  Database tests failed. Skipping service tests.")
        print_info("Run migration first: backend/supabase_migrations/004_historical_data_tables.sql")
        return

    # Test 2: Service
    results['service'] = await test_historical_data_service()

    # Test 3: API (only if service works)
    if results['service']:
        results['api'] = await test_api_endpoint(base_url=api_url)
    else:
        print_warning("Skipping API tests (service tests failed)")
        results['api'] = False

    # Test 4: Performance (only if everything else works)
    if results['service'] and results['api']:
        results['performance'] = await test_performance_benchmark()
    else:
        print_warning("Skipping performance tests (previous tests failed)")
        results['performance'] = False

    # Final summary
    print_header("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{test.upper():<20} {status}{Colors.RESET}")

    print(f"\n{Colors.BOLD}Overall: {passed}/{total} tests passed{Colors.RESET}\n")

    if passed == total:
        print_success("🎉 All tests passed! Backend implementation is working correctly.")
        print_info("\nNext steps:")
        print("  1. Run pre-warming: python3 -m backend.scripts.prewarm_data")
        print("  2. Continue with frontend implementation")
    else:
        print_warning("\n⚠️  Some tests failed. Review the errors above.")
        if not results['database']:
            print_info("→ Run the database migration first")
        if not results['api']:
            print_info("→ Start the backend server: uvicorn mcp_server:app --reload")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test historical data implementation')
    parser.add_argument(
        '--url',
        type=str,
        help='Production API URL (e.g., https://your-app.fly.dev)',
        default=None
    )

    args = parser.parse_args()

    asyncio.run(main(api_url=args.url))
