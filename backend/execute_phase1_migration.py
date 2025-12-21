#!/usr/bin/env python3
"""
Execute Phase 1 Behavioral Coaching Migration
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def execute_migration():
    """Execute the Phase 1 migration SQL"""

    print("🚀 Phase 1 Behavioral Coaching Migration")
    print("=" * 60)

    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role for admin operations

    if not url or not key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        return False

    print(f"📡 Connecting to Supabase: {url}")

    try:
        supabase: Client = create_client(url, key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    # Read migration file
    migration_file = Path(__file__).parent / "supabase_migrations" / "006_behavioral_coaching_phase1.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print(f"📁 Reading migration: {migration_file.name}")

    with open(migration_file, 'r') as f:
        sql_content = f.read()

    print(f"📝 Loaded {len(sql_content)} characters of SQL")

    # Split SQL into individual statements (simple split by semicolon)
    # Note: This is basic and may not handle all edge cases
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]

    print(f"🔨 Executing {len(statements)} SQL statements...")
    print()

    executed = 0
    errors = 0

    for i, statement in enumerate(statements, 1):
        # Skip comments and empty statements
        if statement.startswith('--') or not statement:
            continue

        # Get first 50 chars for logging
        preview = statement[:50].replace('\n', ' ').strip()
        print(f"  [{i}/{len(statements)}] {preview}...")

        try:
            # Execute via rpc query - Supabase allows raw SQL via RPC
            # We'll need to use the REST API directly for this
            # Alternative: Use psycopg2 with connection string

            # For Supabase, we can use the REST API's query endpoint
            # But the Python client doesn't expose raw SQL execution easily
            # We need to use psycopg2 instead

            print(f"      ⚠️  Supabase Python client doesn't support raw SQL")
            print(f"      Need to use psycopg2 or manual execution")
            break

        except Exception as e:
            print(f"      ❌ Error: {e}")
            errors += 1
            continue

    print()
    print("=" * 60)
    print()
    print("❗ ALTERNATIVE APPROACH NEEDED")
    print()
    print("The Supabase Python client doesn't support raw SQL execution.")
    print("To run this migration, you have two options:")
    print()
    print("OPTION 1: Supabase Dashboard (Recommended)")
    print("  1. Go to: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc")
    print("  2. Click 'SQL Editor' in the left sidebar")
    print("  3. Click 'New Query'")
    print("  4. Copy and paste the contents of:")
    print(f"     {migration_file}")
    print("  5. Click 'Run'")
    print()
    print("OPTION 2: psycopg2 (If you have PostgreSQL password)")
    print("  pip install psycopg2-binary")
    print("  psql postgresql://postgres:[PASSWORD]@cwnzgvrylvxfhwhsqelc.supabase.co:5432/postgres \\")
    print(f"    -f {migration_file}")
    print()
    print("The migration file is ready and contains:")
    print("  - 7 database tables (trade_journal, weekly_insights, etc.)")
    print("  - Row-Level Security policies")
    print("  - Database triggers for auto-computation")
    print("  - 5 pre-seeded ACT exercises")
    print("  - 4 pre-loaded legal disclaimers")
    print()

    return False  # Indicate manual execution needed


if __name__ == "__main__":
    success = execute_migration()

    if not success:
        print("⚠️  Migration not executed automatically")
        print("Please follow the manual steps above")
        sys.exit(1)
    else:
        print("✅ Migration completed successfully!")
        sys.exit(0)
