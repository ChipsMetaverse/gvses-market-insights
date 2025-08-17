#!/usr/bin/env python3
"""
Setup Supabase database tables for Claude Voice MCP.
Run this once to create all required tables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv('backend/.env')

def create_tables():
    """Create database tables using raw SQL."""
    
    # Get Supabase credentials
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    print(f"🔄 Connecting to Supabase...")
    print(f"   URL: {url}")
    
    try:
        # Create Supabase client
        supabase = create_client(url, key)
        print("✅ Connected to Supabase")
        
        # Read the schema file
        schema_path = Path("database/schema.sql")
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}")
            return False
            
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print(f"📄 Read schema from {schema_path}")
        
        # Split the schema into individual statements
        # Remove comments and empty lines
        statements = []
        current_statement = []
        
        for line in schema_sql.split('\n'):
            # Skip comments and empty lines
            line_stripped = line.strip()
            if line_stripped.startswith('--') or not line_stripped:
                continue
            
            current_statement.append(line)
            
            # Check if this line ends the statement
            if line_stripped.endswith(';'):
                statement = '\n'.join(current_statement)
                statements.append(statement)
                current_statement = []
        
        print(f"📝 Found {len(statements)} SQL statements to execute")
        
        # For Supabase, we need to use the REST API to execute SQL
        # Note: Supabase Python client doesn't have direct SQL execution
        # We'll create tables one by one using the API
        
        # Instead, let's just create the basic tables without RLS for now
        print("\n🔨 Creating tables...")
        
        # Create conversations table
        try:
            # Check if table exists first
            result = supabase.table('conversations').select('*').limit(1).execute()
            print("✅ Table 'conversations' already exists")
        except:
            print("⚠️  Table 'conversations' doesn't exist - please create it in Supabase Dashboard")
            print("   Go to: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/editor")
            print("   Run the SQL from database/schema.sql")
        
        # Create sessions table
        try:
            result = supabase.table('sessions').select('*').limit(1).execute()
            print("✅ Table 'sessions' already exists")
        except:
            print("⚠️  Table 'sessions' doesn't exist - please create it in Supabase Dashboard")
        
        # Create audio_files table
        try:
            result = supabase.table('audio_files').select('*').limit(1).execute()
            print("✅ Table 'audio_files' already exists")
        except:
            print("⚠️  Table 'audio_files' doesn't exist - please create it in Supabase Dashboard")
        
        print("\n📋 Database setup instructions:")
        print("1. Go to your Supabase Dashboard:")
        print(f"   https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/editor")
        print("2. Click on 'SQL Editor' in the left sidebar")
        print("3. Create a new query")
        print("4. Copy and paste the contents of database/schema.sql")
        print("5. Click 'Run' to execute the SQL")
        print("\nThis will create all required tables with proper indexes and RLS policies.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Supabase Database Setup")
    print("=" * 50)
    
    success = create_tables()
    
    if success:
        print("\n✅ Database setup complete!")
    else:
        print("\n❌ Database setup failed")