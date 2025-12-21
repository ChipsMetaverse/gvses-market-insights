#!/usr/bin/env python3
"""
Quick Readiness Check - Historical Data Implementation

Checks if you're ready to run full tests:
1. Database migration executed?
2. Backend server running?
3. Environment variables configured?

Usage:
    python3 check_readiness.py
    python3 check_readiness.py --url https://your-app.fly.dev
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check_env_vars():
    """Check required environment variables"""
    print(f"\n{BOLD}{BLUE}1. Environment Variables{RESET}")

    required = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_SERVICE_ROLE_KEY': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
        'ALPACA_API_KEY': os.getenv('ALPACA_API_KEY'),
        'ALPACA_SECRET_KEY': os.getenv('ALPACA_SECRET_KEY')
    }

    all_good = True
    for key, value in required.items():
        if value:
            print(f"{GREEN}✅ {key}: Set{RESET}")
        else:
            print(f"{RED}❌ {key}: Missing{RESET}")
            all_good = False

    return all_good

def check_database_migration():
    """Check if migration has been executed"""
    print(f"\n{BOLD}{BLUE}2. Database Migration{RESET}")

    try:
        from supabase import create_client

        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not url or not key:
            print(f"{RED}❌ Cannot check - missing credentials{RESET}")
            return False

        supabase = create_client(url, key)

        # Check each table
        tables = ['historical_bars', 'data_coverage', 'api_call_log']
        all_exist = True

        for table in tables:
            try:
                supabase.table(table).select('*').limit(1).execute()
                print(f"{GREEN}✅ Table '{table}' exists{RESET}")
            except Exception as e:
                print(f"{RED}❌ Table '{table}' missing{RESET}")
                all_exist = False

        if not all_exist:
            print(f"\n{YELLOW}📋 To run migration:{RESET}")
            print("   1. Go to: https://app.supabase.com/project/<your-project>/sql/new")
            print("   2. Copy: backend/supabase_migrations/004_historical_data_tables.sql")
            print("   3. Paste and click 'Run'\n")

        return all_exist

    except Exception as e:
        print(f"{RED}❌ Database connection failed: {str(e)[:100]}{RESET}")
        return False

def check_server_running(url=None):
    """Check if backend server is accessible"""
    print(f"\n{BOLD}{BLUE}3. Backend Server{RESET}")

    import httpx
    import asyncio

    async def check():
        if url is None:
            test_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        else:
            test_url = url

        print(f"   Checking: {test_url}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{test_url}/health", timeout=5.0)

                if response.status_code == 200:
                    data = response.json()
                    print(f"{GREEN}✅ Server is running{RESET}")
                    print(f"   Status: {data.get('status', 'unknown')}")
                    print(f"   Service mode: {data.get('service_mode', 'unknown')}")
                    return True
                else:
                    print(f"{YELLOW}⚠️  Server responded with status {response.status_code}{RESET}")
                    return False

        except Exception as e:
            print(f"{RED}❌ Server not accessible: {str(e)[:100]}{RESET}")
            print(f"\n{YELLOW}💡 To start server:{RESET}")
            print("   cd backend && uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000")
            return False

    return asyncio.run(check())

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Check readiness for historical data testing')
    parser.add_argument('--url', type=str, help='Production API URL', default=None)
    args = parser.parse_args()

    print(f"\n{BOLD}{BLUE}{'=' * 70}{RESET}")
    print(f"{BOLD}{BLUE}READINESS CHECK - Historical Data Implementation{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 70}{RESET}")

    results = {}

    # Check environment
    results['env'] = check_env_vars()

    # Check database
    results['db'] = check_database_migration()

    # Check server
    results['server'] = check_server_running(url=args.url)

    # Summary
    print(f"\n{BOLD}{BLUE}{'=' * 70}{RESET}")
    print(f"{BOLD}{BLUE}SUMMARY{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 70}{RESET}\n")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for check, result in results.items():
        status = f"{GREEN}✅ READY{RESET}" if result else f"{RED}❌ NOT READY{RESET}"
        print(f"{check.upper():<20} {status}")

    print(f"\n{BOLD}Status: {passed}/{total} checks passed{RESET}\n")

    if passed == total:
        print(f"{GREEN}🎉 You're ready to run full tests!{RESET}\n")
        print(f"{BOLD}Next step:{RESET}")
        if args.url:
            print(f"   python3 test_historical_data_implementation.py --url {args.url}")
        else:
            print(f"   python3 test_historical_data_implementation.py")
        print()
    else:
        print(f"{YELLOW}⚠️  Please complete the failed checks above before testing.{RESET}\n")

        if not results['db']:
            print(f"{BOLD}Quick migration command:{RESET}")
            print("   Open Supabase dashboard → SQL Editor → Paste migration SQL → Run")

        if not results['server'] and args.url:
            print(f"\n{BOLD}Testing production:{RESET}")
            print(f"   No need to start local server if testing production at {args.url}")

if __name__ == "__main__":
    main()
