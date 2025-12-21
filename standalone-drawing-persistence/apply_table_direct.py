#!/usr/bin/env python3
"""
Apply user_drawings table directly via SQL execution
"""
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")

if not SUPABASE_URL:
    print("❌ Missing SUPABASE_URL in .env")
    exit(1)

# Parse URL to get project ref
parsed = urlparse(SUPABASE_URL)
project_ref = parsed.hostname.split('.')[0]

print("🔍 Supabase Project:", project_ref)
print("📋 To apply the user_drawings table:")
print("=" * 80)
print()
print("1. Open: https://supabase.com/dashboard/project/" + project_ref + "/sql/new")
print()
print("2. Copy and paste this SQL:")
print("-" * 80)

with open('create_user_drawings_table.sql', 'r') as f:
    sql = f.read()
    print(sql)

print("-" * 80)
print()
print("3. Click 'Run'")
print()
print("4. Verify: python3 apply_migration_simple.py")
print("=" * 80)
