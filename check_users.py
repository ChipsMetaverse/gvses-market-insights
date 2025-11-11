#!/usr/bin/env python3
"""Check for users in Supabase auth.users table"""

import os
from supabase import create_client, Client
from datetime import datetime

# Supabase credentials from mcp.json
SUPABASE_URL = "https://cwnzgvrylvxfhwhsqelc.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3bnpndnJ5bHZ4Zmh3aHNxZWxjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczOTE0MDY4MywiZXhwIjoyMDU0NzE2NjgzfQ.dBvzjwlJ4_4-NaNIVT1bGDlarYweLk8V7IRLnSGtC5I"

def main():
    # Create Supabase client with service role key (has admin access)
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("🔍 Checking for users in Supabase...\n")
    
    try:
        # Query auth.users table
        # Note: Using RPC call or direct SQL since auth.users is in auth schema
        # The Supabase Python client might need special handling for auth schema
        
        # Try to get users via admin API
        response = supabase.auth.admin.list_users()
        
        if response and hasattr(response, 'users'):
            users = response.users
            print(f"✅ Found {len(users)} users\n")
            
            if len(users) > 0:
                print("📊 User Details:")
                print("=" * 80)
                for i, user in enumerate(users[:20], 1):  # Show first 20
                    print(f"\n{i}. User ID: {user.id}")
                    print(f"   Email: {user.email}")
                    print(f"   Created: {user.created_at}")
                    print(f"   Last Sign In: {user.last_sign_in_at}")
                    print(f"   Email Confirmed: {user.email_confirmed_at is not None}")
                    if user.user_metadata:
                        print(f"   Metadata: {user.user_metadata}")
                
                if len(users) > 20:
                    print(f"\n... and {len(users) - 20} more users")
                
                # Statistics
                confirmed = sum(1 for u in users if u.email_confirmed_at)
                active = sum(1 for u in users if u.last_sign_in_at)
                
                print("\n" + "=" * 80)
                print("📈 Statistics:")
                print(f"   Total Users: {len(users)}")
                print(f"   Email Confirmed: {confirmed}")
                print(f"   Unconfirmed: {len(users) - confirmed}")
                print(f"   Active (has sign-in): {active}")
                print(f"   Inactive: {len(users) - active}")
            else:
                print("⚠️ No users found in database")
        else:
            print("⚠️ Could not retrieve users - response format unexpected")
            print(f"Response type: {type(response)}")
            if hasattr(response, '__dict__'):
                print(f"Response attributes: {dir(response)}")
                
    except Exception as e:
        print(f"❌ Error querying users: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Try alternative method - direct SQL query via PostgREST
        print("\n🔄 Trying alternative method via PostgREST...")
        try:
            # Note: auth.users might not be accessible via regular table queries
            # May need to use RPC function or admin API
            print("Note: auth.users table requires admin API access")
        except Exception as e2:
            print(f"Alternative method also failed: {e2}")

if __name__ == "__main__":
    main()

