#!/usr/bin/env python3
"""
Execute SQL directly on Supabase using the REST API.
"""

import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def execute_sql():
    """Execute SQL statements via Supabase REST API."""
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    # SQL to create the tables
    sql = """
    -- Create conversations table
    CREATE TABLE IF NOT EXISTS conversations (
      id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
      session_id UUID NOT NULL,
      user_id TEXT,
      role TEXT CHECK (role IN ('user', 'assistant')) NOT NULL,
      content TEXT NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      metadata JSONB DEFAULT '{}'::jsonb
    );

    -- Create sessions table
    CREATE TABLE IF NOT EXISTS sessions (
      id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
      user_id TEXT,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      metadata JSONB DEFAULT '{}'::jsonb,
      is_active BOOLEAN DEFAULT true
    );

    -- Create audio_files table
    CREATE TABLE IF NOT EXISTS audio_files (
      id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
      session_id UUID NOT NULL,
      user_id TEXT,
      file_url TEXT NOT NULL,
      duration_seconds FLOAT,
      mime_type TEXT DEFAULT 'audio/webm',
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Add indexes
    CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
    CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_audio_files_session_id ON audio_files(session_id);
    """
    
    print(f"🔄 Executing SQL on Supabase...")
    print(f"   URL: {url}")
    
    # Unfortunately, the anon key doesn't have permission to create tables
    # We need to use the Supabase Dashboard or get a service role key
    
    print("\n⚠️  The anon key doesn't have permission to create tables.")
    print("\n📋 Please go to the Supabase Dashboard and run this SQL:")
    print(f"\n🔗 SQL Editor: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/sql/new")
    print("\n" + "="*60)
    print(sql)
    print("="*60)
    
    # Test if tables exist now
    from supabase import create_client
    
    try:
        supabase = create_client(url, key)
        print("\n🔍 Checking current table status...")
        
        tables = ['conversations', 'sessions', 'audio_files']
        existing = []
        missing = []
        
        for table in tables:
            try:
                result = supabase.table(table).select('count', count='exact').execute()
                existing.append(f"✅ {table} (rows: {result.count})")
            except Exception as e:
                if "does not exist" in str(e):
                    missing.append(f"❌ {table}")
                else:
                    missing.append(f"⚠️  {table}: {str(e)[:50]}")
        
        if existing:
            print("\nExisting tables:")
            for item in existing:
                print(f"  {item}")
        
        if missing:
            print("\nMissing tables:")
            for item in missing:
                print(f"  {item}")
                
    except Exception as e:
        print(f"\n❌ Error checking tables: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Supabase SQL Execution")
    print("=" * 50)
    
    execute_sql()