#!/usr/bin/env python3
"""
Apply database migration to Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
    exit(1)

# Read migration SQL
migration_path = "../backend/supabase_migrations/003_drawings_table.sql"
print(f"📖 Reading migration from {migration_path}...")

with open(migration_path, 'r') as f:
    migration_sql = f.read()

print(f"✅ Migration SQL loaded ({len(migration_sql)} bytes)")

# Connect to Supabase
print(f"🔌 Connecting to Supabase at {SUPABASE_URL}...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Apply migration
print("🚀 Applying migration...")
try:
    # Execute the migration SQL
    result = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
    print("✅ Migration applied successfully!")
    print(result)
except Exception as e:
    # Try alternative approach: execute via PostgREST
    print("⚠️  RPC method not available, trying direct SQL execution...")
    try:
        # Split SQL into individual statements
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

        for i, statement in enumerate(statements, 1):
            if statement.startswith('--') or not statement:
                continue
            print(f"📝 Executing statement {i}/{len(statements)}...")
            result = supabase.postgrest.rpc('exec_sql', {'query': statement}).execute()
            print(f"✅ Statement {i} completed")

        print("✅ All migration statements applied successfully!")
    except Exception as e2:
        print(f"❌ Migration failed: {e2}")
        print("\n💡 Please apply the migration manually:")
        print("1. Go to Supabase Dashboard → SQL Editor")
        print(f"2. Copy contents of {migration_path}")
        print("3. Paste and click Run")
        exit(1)

# Verify table was created
print("\n🔍 Verifying 'drawings' table exists...")
try:
    result = supabase.table('drawings').select('*').limit(1).execute()
    print("✅ Table 'drawings' exists and is accessible!")
except Exception as e:
    print(f"❌ Failed to verify table: {e}")
    print("\n💡 Please verify the migration was applied correctly in Supabase Dashboard")
    exit(1)

print("\n🎉 Migration complete! Run tests with: python3 test_api.py")
