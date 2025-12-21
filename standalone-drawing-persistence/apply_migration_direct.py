#!/usr/bin/env python3
"""
Apply database migration directly using Supabase REST API
"""
import os
import requests
from dotenv import load_dotenv

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

# Execute SQL via Supabase REST API
print(f"🔌 Connecting to Supabase at {SUPABASE_URL}...")
print("🚀 Applying migration via REST API...")

# Use the query endpoint
url = f"{SUPABASE_URL}/rest/v1/rpc/exec"
headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

# Try direct SQL execution
import json
payload = json.dumps({"query": migration_sql})

try:
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code in [200, 201, 204]:
        print("✅ Migration applied successfully!")
    else:
        print(f"⚠️  REST API response: {response.status_code}")
        print(f"Response: {response.text}")

        # If REST API doesn't work, create table directly
        print("\n🔄 Trying alternative approach...")

        # Create the table using direct SQL via Python
        import urllib.parse

        # Parse the Supabase URL to get database connection details
        parsed = urllib.parse.urlparse(SUPABASE_URL)
        db_host = parsed.hostname.replace('supabase.co', 'db.supabase.co')

        print("⚠️  Direct database access not available via REST API")
        print("💡 Using Supabase Python SDK to create table...")

        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        # Create table using table creation via SDK
        print("Creating drawings table...")

        # Since we can't execute raw SQL, we'll verify if we can create via SDK
        # But this is limited - the best approach is manual SQL Editor
        raise Exception("Direct SQL execution not available - see manual instructions below")

except Exception as e:
    print(f"⚠️  Automated migration failed: {e}")
    print("\n" + "="*80)
    print("📋 PLEASE APPLY MIGRATION MANUALLY:")
    print("="*80)
    print("\n1. Open Supabase Dashboard:")
    print(f"   {SUPABASE_URL.replace('/v1', '')}/project/sql")
    print("\n2. Copy this SQL:")
    print("-"*80)
    print(migration_sql[:500] + "..." if len(migration_sql) > 500 else migration_sql)
    print("-"*80)
    print("\n3. Paste into SQL Editor and click 'Run'")
    print("\n4. Then run: python3 apply_migration_simple.py")
    print("="*80)
    exit(1)
