#!/usr/bin/env python3
"""
Create simplified tables in Supabase without auth dependencies.
"""

import os
import httpx
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv('backend/.env')

def create_simplified_tables():
    """Create simplified tables without auth.users dependency."""
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    print(f"🔄 Connecting to Supabase...")
    
    # SQL statements to create tables (simplified without auth.users)
    sql_statements = [
        """
        CREATE TABLE IF NOT EXISTS conversations (
          id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
          session_id UUID NOT NULL,
          user_id TEXT,
          role TEXT CHECK (role IN ('user', 'assistant')) NOT NULL,
          content TEXT NOT NULL,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          metadata JSONB DEFAULT '{}'::jsonb
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS sessions (
          id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
          user_id TEXT,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          metadata JSONB DEFAULT '{}'::jsonb,
          is_active BOOLEAN DEFAULT true
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS audio_files (
          id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
          session_id UUID NOT NULL,
          user_id TEXT,
          file_url TEXT NOT NULL,
          duration_seconds FLOAT,
          mime_type TEXT DEFAULT 'audio/webm',
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        # Create indexes
        "CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);",
        "CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_audio_files_session_id ON audio_files(session_id);",
    ]
    
    # We need to use the Supabase REST API to execute SQL
    # The service role key would be needed for direct SQL execution
    # For now, let's use httpx to call the Supabase SQL endpoint
    
    # Get the service role key if available (usually not in anon key)
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if service_key:
        print("✅ Using service role key for SQL execution")
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json"
        }
        
        # Execute SQL via REST API
        for i, sql in enumerate(sql_statements):
            try:
                response = httpx.post(
                    f"{url}/rest/v1/rpc/exec_sql",
                    headers=headers,
                    json={"query": sql}
                )
                if response.status_code == 200:
                    print(f"✅ Statement {i+1} executed successfully")
                else:
                    print(f"⚠️  Statement {i+1} failed: {response.text}")
            except Exception as e:
                print(f"⚠️  Statement {i+1} error: {e}")
    else:
        print("\n⚠️  Service role key not found - cannot execute SQL directly")
        print("\n📋 Manual setup required:")
        print("1. Go to your Supabase SQL Editor:")
        print(f"   https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/sql/new")
        print("\n2. Copy and paste this SQL:\n")
        print("-- Create tables for Claude Voice MCP")
        for sql in sql_statements[:3]:  # Just the CREATE TABLE statements
            print(sql)
        print("\n3. Click 'Run' to execute the SQL")
        
        # Still try to test the connection
        try:
            supabase = create_client(url, key)
            print("\n✅ Supabase client connection is working!")
            
            # List all accessible tables
            print("\n📊 Checking for existing tables...")
            
            # Try to access each table to see if it exists
            tables_to_check = ['conversations', 'sessions', 'audio_files']
            existing_tables = []
            
            for table_name in tables_to_check:
                try:
                    # Try to select from the table
                    result = supabase.table(table_name).select('count', count='exact').execute()
                    existing_tables.append(table_name)
                    print(f"✅ Table '{table_name}' exists (count: {result.count})")
                except Exception as e:
                    if "does not exist" in str(e):
                        print(f"❌ Table '{table_name}' does not exist")
                    else:
                        print(f"⚠️  Table '{table_name}' error: {e}")
            
            if existing_tables:
                print(f"\n✅ Found {len(existing_tables)} existing tables: {', '.join(existing_tables)}")
            else:
                print("\n⚠️  No tables found - please create them using the SQL above")
                
        except Exception as e:
            print(f"\n❌ Supabase connection error: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Supabase Table Creation")
    print("=" * 50)
    
    create_simplified_tables()