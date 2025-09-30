#!/usr/bin/env python3
"""Apply Phase 5 database migration to Supabase."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
backend_dir = Path(__file__).parent.parent
load_dotenv(backend_dir / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def check_migration_applied(supabase):
    """Check if Phase 5 migration has been applied."""
    try:
        # Check if ml_models table exists
        result = supabase.table('ml_models').select('id').limit(1).execute()
        print("✅ Phase 5 migration already applied - ml_models table exists")
        return True
    except Exception as e:
        if 'relation "public.ml_models" does not exist' in str(e):
            print("❌ Phase 5 migration not yet applied - ml_models table missing")
            return False
        else:
            print("⚠️ Error checking migration status: {}".format(e))
            return False

def read_migration_sql():
    """Read the Phase 5 migration SQL file."""
    migration_path = backend_dir.parent / 'supabase' / 'migrations' / '20250928000001_phase5_ml_columns.sql'
    if not migration_path.exists():
        raise FileNotFoundError("Migration file not found: {}".format(migration_path))
    
    with open(migration_path, 'r') as f:
        return f.read()

def main():
    """Main function to apply Phase 5 migration."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment")
        sys.exit(1)
    
    # Create Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # Check if migration is already applied
    if check_migration_applied(supabase):
        print("\n✅ Phase 5 database migration is already applied!")
        
        # Check for ML columns in pattern_events
        try:
            result = supabase.table('pattern_events').select('id, ml_confidence, ml_model_version').limit(1).execute()
            print("✅ ML columns exist in pattern_events table")
        except Exception as e:
            print("⚠️ ML columns may be missing from pattern_events: {}".format(e))
        
        return
    
    print("\n📝 Phase 5 migration needs to be applied")
    print("⚠️ Note: Direct SQL execution requires database credentials")
    print("\nTo apply the migration manually:")
    print("1. Access your Supabase dashboard")
    print("2. Go to SQL Editor")
    print("3. Run the migration from: supabase/migrations/20250928000001_phase5_ml_columns.sql")
    print("\nAlternatively, use supabase CLI:")
    print("  supabase db push")
    
    # Read and display migration summary
    try:
        migration_sql = read_migration_sql()
        lines = migration_sql.split('\n')
        
        print("\n📋 Migration Summary:")
        print("- Adds ML columns to pattern_events table")
        print("- Creates ml_models table for model registry")
        print("- Creates ml_predictions table for prediction logging")
        print("- Creates ml_features table for feature store")
        print("- Adds helper functions for ML operations")
        print("\nTotal SQL statements: ~20 ALTER/CREATE operations")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")

if __name__ == '__main__':
    main()