#!/usr/bin/env python3
"""
Create tables using Supabase RPC function.
First we need to create an RPC function that can execute SQL.
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv('backend/.env')

def create_tables():
    """Create tables using Supabase."""
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    print(f"🔄 Connecting to Supabase...")
    print(f"   URL: {url}")
    
    try:
        supabase = create_client(url, key)
        print("✅ Connected to Supabase")
        
        # Since we can't execute raw SQL with anon key, let's create the tables
        # using a different approach - we'll check what exists and provide the SQL
        
        print("\n📊 Checking current database status...")
        
        tables = {
            'conversations': False,
            'sessions': False, 
            'audio_files': False
        }
        
        for table_name in tables.keys():
            try:
                result = supabase.table(table_name).select('count', count='exact').execute()
                tables[table_name] = True
                print(f"✅ Table '{table_name}' exists with {result.count} rows")
            except Exception as e:
                if "does not exist" in str(e):
                    print(f"❌ Table '{table_name}' does not exist")
                else:
                    print(f"⚠️  Table '{table_name}': {str(e)[:50]}")
        
        # Check if all tables exist
        if all(tables.values()):
            print("\n✅ All required tables already exist!")
            return True
        
        # Generate SQL for missing tables
        missing_tables = [name for name, exists in tables.items() if not exists]
        
        if missing_tables:
            print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
            print("\n" + "="*60)
            print("📋 MANUAL SETUP REQUIRED")
            print("="*60)
            print("\nPlease execute the following SQL in your Supabase Dashboard:")
            print(f"🔗 https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/sql/new")
            print("\n```sql")
            
            if 'conversations' in missing_tables:
                print("""-- Create conversations table
CREATE TABLE conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID NOT NULL,
  user_id TEXT,
  role TEXT CHECK (role IN ('user', 'assistant')) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
""")
            
            if 'sessions' in missing_tables:
                print("""-- Create sessions table
CREATE TABLE sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb,
  is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);
""")
            
            if 'audio_files' in missing_tables:
                print("""-- Create audio_files table
CREATE TABLE audio_files (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID NOT NULL,
  user_id TEXT,
  file_url TEXT NOT NULL,
  duration_seconds FLOAT,
  mime_type TEXT DEFAULT 'audio/webm',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audio_files_session_id ON audio_files(session_id);
""")
            
            print("```")
            print("\n" + "="*60)
            print("\n📝 Steps to complete setup:")
            print("1. Click the link above to open Supabase SQL Editor")
            print("2. Copy the SQL code above")
            print("3. Paste it in the SQL Editor")
            print("4. Click 'Run' to execute")
            print("5. Run this script again to verify tables were created")
            
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Supabase Table Setup")
    print("=" * 50)
    
    success = create_tables()
    
    if success:
        print("\n✅ All tables are ready!")
    else:
        print("\n⚠️  Manual setup required - see instructions above")