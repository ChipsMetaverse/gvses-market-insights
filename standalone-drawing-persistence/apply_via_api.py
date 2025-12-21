#!/usr/bin/env python3
"""
Apply migration by executing SQL statements one by one via Supabase client
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ Missing credentials")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print("🚀 Applying user_drawings table...")

# Read the SQL file
with open('create_user_drawings_table.sql', 'r') as f:
    sql = f.read()

# Try to execute via REST API
try:
    # Use Supabase management API
    import requests

    # Execute SQL via PostgREST
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    # Try to create table by inserting directly
    # Since we can't execute raw SQL via REST API, let's verify the table doesn't exist
    # and provide clear instructions

    print("⚠️  Cannot execute raw SQL via Supabase Python client")
    print("📋 Please use ONE of these methods:")
    print()
    print("=" * 80)
    print("METHOD 1: Supabase Dashboard (Recommended - 2 minutes)")
    print("=" * 80)
    print()
    print("1. Open: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/sql/new")
    print("2. Paste the SQL from: create_user_drawings_table.sql")
    print("3. Click 'Run'")
    print()
    print("=" * 80)
    print("METHOD 2: psql Command Line")
    print("=" * 80)
    print()
    print("Get your database password from:")
    print("https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/settings/database")
    print()
    print("Then run:")
    print("PGPASSWORD='your_password' psql -h db.cwnzgvrylvxfhwhsqelc.supabase.co \\")
    print("  -U postgres -d postgres -f create_user_drawings_table.sql")
    print()
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
