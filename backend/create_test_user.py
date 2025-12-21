#!/usr/bin/env python3
"""
Create a test user in auth.users for integration testing
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def create_test_user():
    """Create test user in auth.users table"""

    url = os.getenv("SUPABASE_URL")
    # Must use SERVICE_ROLE_KEY to insert into auth.users
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    supabase: Client = create_client(url, key)

    test_user_id = "00000000-0000-0000-0000-000000000001"

    try:
        # Try to insert test user into auth.users
        # Note: Supabase's auth.users has specific required fields
        result = supabase.table("users").insert({
            "id": test_user_id,
        }).execute()

        print(f"✅ Test user created: {test_user_id}")
        return True

    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg or "duplicate" in error_msg:
            print(f"✅ Test user already exists: {test_user_id}")
            return True
        else:
            print(f"❌ Error creating test user: {error_msg}")
            print("\nNote: Supabase auth.users table has restricted access.")
            print("Alternative: Remove foreign key constraint from trade_journal table.")
            return False

if __name__ == "__main__":
    create_test_user()
