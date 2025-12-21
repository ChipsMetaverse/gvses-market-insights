#!/usr/bin/env python3
"""
Simple migration checker and manual instructions
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

print("🔍 Checking if 'user_drawings' table exists...")

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Check if table exists
try:
    result = supabase.table('user_drawings').select('id').limit(1).execute()
    print("✅ Table 'user_drawings' already exists!")
    print("🎉 No migration needed. Ready to run tests!")
    exit(0)
except Exception as e:
    error_message = str(e)
    if "does not exist" in error_message or "relation" in error_message or "not found" in error_message:
        print("⚠️  Table 'user_drawings' does not exist yet")
        print("\n📋 MIGRATION REQUIRED:")
        print("=" * 80)
        print("Please apply the migration manually via Supabase Dashboard:")
        print()
        print("1. Open: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc")
        print("2. Go to: SQL Editor")
        print("3. Click: New Query")
        print("4. Copy the contents of: backend/supabase_migrations/003_drawings_table.sql")
        print("5. Paste into the SQL Editor")
        print("6. Click: Run")
        print("7. Verify success message")
        print()
        print("=" * 80)
        print()
        print("After applying migration, run: python3 test_api.py")
        exit(1)
    else:
        print(f"❌ Unexpected error checking table: {e}")
        exit(1)
