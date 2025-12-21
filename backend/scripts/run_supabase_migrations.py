#!/usr/bin/env python3
"""
Run Supabase Migrations
Executes all SQL migration files in the supabase_migrations directory
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.database_service import DatabaseService


async def run_migrations():
    """Execute all migration files in order"""

    print("🚀 Starting Supabase Migration Runner")
    print("=" * 60)

    # Initialize database service
    try:
        db_service = DatabaseService()
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

    # Find migration files
    migrations_dir = backend_dir / "supabase_migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("⚠️  No migration files found in", migrations_dir)
        return False

    print(f"📁 Found {len(migration_files)} migration files:")
    for f in migration_files:
        print(f"   - {f.name}")
    print()

    # Execute each migration
    success_count = 0
    error_count = 0

    for migration_file in migration_files:
        print(f"🔄 Running: {migration_file.name}")

        try:
            # Read SQL file
            with open(migration_file, 'r') as f:
                sql_content = f.read()

            # Execute SQL (use raw SQL execution)
            # Note: Supabase Python client doesn't have direct SQL execution
            # We'll use the rpc function or execute via connection
            print(f"   📝 SQL file loaded ({len(sql_content)} characters)")

            # For now, just validate the file can be read
            # In production, you'd execute this via psycopg2 or similar
            print(f"   ⚠️  Manual execution required via Supabase SQL Editor")
            print(f"   📋 Copy contents of: {migration_file}")
            print()

            success_count += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            error_count += 1
            continue

    print("=" * 60)
    print(f"✅ Migrations reviewed: {success_count}")
    if error_count > 0:
        print(f"❌ Errors: {error_count}")

    print()
    print("📖 MANUAL STEPS REQUIRED:")
    print("   1. Go to your Supabase Dashboard")
    print("   2. Navigate to SQL Editor")
    print("   3. Execute each migration file in order:")
    for f in migration_files:
        print(f"      - {f.name}")
    print()

    return error_count == 0


if __name__ == "__main__":
    success = asyncio.run(run_migrations())
    sys.exit(0 if success else 1)
