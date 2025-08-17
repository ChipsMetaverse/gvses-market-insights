#!/usr/bin/env python3
"""Test Supabase connection."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Import Supabase
try:
    from supabase import create_client, Client
    print(f"✅ Supabase imported successfully")
    print(f"   Version: {__import__('supabase').__version__ if hasattr(__import__('supabase'), '__version__') else 'Unknown'}")
except ImportError as e:
    print(f"❌ Failed to import Supabase: {e}")
    sys.exit(1)

# Get credentials
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")

print(f"\n📋 Configuration:")
print(f"   URL: {url}")
print(f"   Key: {key[:20]}..." if key else "   Key: Not found")

if not url or not key:
    print("❌ Missing Supabase credentials")
    sys.exit(1)

# Try to create client
print(f"\n🔄 Creating Supabase client...")
try:
    # Simple client creation without any extra parameters
    supabase = create_client(url, key)
    print("✅ Client created successfully")
except Exception as e:
    print(f"❌ Failed to create client: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test basic operations
print(f"\n🔍 Testing database operations...")
try:
    # Try to query conversations table
    result = supabase.table('conversations').select('*').limit(1).execute()
    print(f"✅ Successfully queried conversations table")
    print(f"   Found {len(result.data)} records")
    
    # Try to query sessions table  
    sessions = supabase.table('sessions').select('*').limit(1).execute()
    print(f"✅ Successfully queried sessions table")
    print(f"   Found {len(sessions.data)} records")
    
    print(f"\n✅ Supabase is working correctly!")
    
except Exception as e:
    print(f"❌ Database operation failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)