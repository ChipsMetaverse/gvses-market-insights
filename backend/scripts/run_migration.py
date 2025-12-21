#!/usr/bin/env python3
"""
Database Migration Runner

Executes the historical data tables migration on Supabase.

Usage:
    python3 -m backend.scripts.run_migration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


def run_migration():
    """Run the database migration."""
    print("=" * 80)
    print("DATABASE MIGRATION RUNNER")
    print("=" * 80)

    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
        return 1

    print(f"\n✓ Connecting to: {supabase_url}")

    # Load migration SQL
    migration_file = Path(__file__).parent.parent / 'supabase_migrations' / '004_historical_data_tables.sql'

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return 1

    print(f"✓ Found migration: {migration_file.name}")

    with open(migration_file, 'r') as f:
        sql = f.read()

    print(f"✓ Loaded SQL ({len(sql)} characters)")

    # Connect to Supabase
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✓ Connected to Supabase")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return 1

    # Execute migration
    print("\n⚠️  NOTE: Supabase Python client doesn't support raw SQL execution")
    print("   You need to run the migration manually via Supabase dashboard:\n")
    print("   1. Go to: https://app.supabase.com/project/_/sql/new")
    print(f"   2. Copy SQL from: {migration_file}")
    print("   3. Paste and run in SQL Editor")
    print("\n   OR use the Supabase CLI:")
    print(f"   supabase db push")
    print("\n   OR execute directly via psql:")
    print(f"   psql $DATABASE_URL < {migration_file}")

    print("\n" + "=" * 80)
    print("Migration file ready - please run manually as shown above")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit_code = run_migration()
    sys.exit(exit_code)
