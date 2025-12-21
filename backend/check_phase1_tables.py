#!/usr/bin/env python3
"""
Check if Phase 1 tables exist in Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def check_tables():
    """Check if Phase 1 tables exist"""

    print("🔍 Checking Phase 1 Tables")
    print("=" * 60)

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    supabase: Client = create_client(url, key)
    print("✅ Connected to Supabase")
    print()

    # List of expected tables
    expected_tables = [
        'trade_journal',
        'weekly_insights',
        'act_exercises',
        'act_exercise_completions',
        'behavioral_patterns',
        'user_behavioral_settings',
        'legal_disclaimers'
    ]

    print("Checking tables:")
    print()

    for table in expected_tables:
        try:
            # Try to query the table
            result = supabase.table(table).select("*").limit(1).execute()
            count_result = supabase.table(table).select("*", count="exact").limit(0).execute()
            count = count_result.count if hasattr(count_result, 'count') else '?'

            print(f"  ✅ {table:<30} ({count} rows)")

        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg or "42P01" in error_msg:
                print(f"  ❌ {table:<30} (does not exist)")
            else:
                print(f"  ⚠️  {table:<30} (error: {error_msg[:50]})")

    print()
    print("=" * 60)
    print()
    print("If tables are missing, run migration manually:")
    print("  1. Go to https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc")
    print("  2. SQL Editor → New Query")
    print("  3. Copy contents of: backend/supabase_migrations/006_behavioral_coaching_phase1.sql")
    print("  4. Paste and Run")
    print()


if __name__ == "__main__":
    check_tables()
