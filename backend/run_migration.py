#!/usr/bin/env python3
"""
Run Supabase migration using direct database connection.
This script uses the service role key to execute DDL statements.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try importing psycopg2
try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    from psycopg2 import sql

def run_migration(migration_file: str):
    """Run a SQL migration file against Supabase database."""

    # Get database credentials from environment
    supabase_url = os.getenv('SUPABASE_URL', '')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not service_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env file")
        return False

    # Extract project reference from URL
    # Format: https://PROJECT_REF.supabase.co
    project_ref = supabase_url.split('//')[1].split('.')[0]

    # Connection string for Supabase
    # Uses the service role user (postgres) which has full privileges
    db_host = f"db.{project_ref}.supabase.co"
    db_name = "postgres"
    db_user = "postgres"

    # Note: Supabase uses the service role key as password for postgres user
    # But we need the actual database password from the dashboard
    print(f"🔗 Connecting to: {db_host}")
    print(f"📁 Running migration: {migration_file}")
    print()
    print("⚠️  Note: This script requires the database password from Supabase Dashboard")
    print("   Settings > Database > Connection Pooling > Password")
    print()

    db_password = input("Enter database password (or press Enter to skip): ").strip()

    if not db_password:
        print()
        print("💡 Alternative: Use Supabase Dashboard SQL Editor")
        print(f"   1. Visit: https://app.supabase.com/project/{project_ref}/sql/new")
        print(f"   2. Paste contents of: {migration_file}")
        print("   3. Click 'Run'")
        return False

    try:
        # Read migration SQL
        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        # Connect to database
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=5432
        )

        # Execute migration
        with conn.cursor() as cursor:
            print("⚡ Executing migration...")
            cursor.execute(migration_sql)
            conn.commit()

        print("✅ Migration completed successfully!")

        # Verify table was created
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = 'request_logs'
                AND table_schema = 'public'
            """)
            count = cursor.fetchone()[0]

            if count == 1:
                print("✅ Verified: request_logs table exists")
            else:
                print("⚠️  Warning: request_logs table not found after migration")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error running migration: {e}")
        return False

if __name__ == "__main__":
    migration_file = "supabase_migrations/002_request_logs.sql"

    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)

    success = run_migration(migration_file)
    sys.exit(0 if success else 1)
