#!/usr/bin/env python3
"""
Execute Phase 1 Behavioral Coaching Migration using psycopg2
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# Load environment variables
load_dotenv()

def execute_migration():
    """Execute the Phase 1 migration SQL"""

    print("🚀 Phase 1 Behavioral Coaching Migration")
    print("=" * 60)

    # Check for database password
    db_password = os.getenv("SUPABASE_DB_PASSWORD")

    if not db_password:
        print("❌ SUPABASE_DB_PASSWORD not found in environment")
        print()
        print("To run this migration, you need the database password.")
        print()
        print("Get it from:")
        print("  1. Go to Supabase Dashboard → Settings → Database")
        print("  2. Copy the 'Database Password'")
        print("  3. Add to backend/.env: SUPABASE_DB_PASSWORD=your_password")
        print()
        print("OR run manually in Supabase SQL Editor:")
        print("  1. Go to https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc")
        print("  2. SQL Editor → New Query")
        print("  3. Paste contents of: backend/supabase_migrations/006_behavioral_coaching_phase1.sql")
        print("  4. Run")
        print()
        return False

    # Construct connection string
    project_ref = "cwnzgvrylvxfhwhsqelc"
    conn_string = f"postgresql://postgres.{project_ref}:{db_password}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

    print("📡 Connecting to Supabase PostgreSQL...")

    try:
        conn = psycopg2.connect(conn_string)
        conn.autocommit = False  # Use transactions
        cursor = conn.cursor()
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    # Read migration file
    migration_file = Path(__file__).parent / "supabase_migrations" / "006_behavioral_coaching_phase1.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        cursor.close()
        conn.close()
        return False

    print(f"📁 Reading migration: {migration_file.name}")

    with open(migration_file, 'r') as f:
        sql_content = f.read()

    print(f"📝 Loaded {len(sql_content):,} characters of SQL")
    print()
    print("🔨 Executing migration...")

    try:
        # Execute the entire SQL file at once
        cursor.execute(sql_content)
        conn.commit()

        print("✅ Migration executed successfully!")
        print()

        # Verify tables were created
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('trade_journal', 'weekly_insights', 'act_exercises',
                               'act_exercise_completions', 'behavioral_patterns',
                               'user_behavioral_settings', 'legal_disclaimers')
            ORDER BY table_name
        """)

        tables = cursor.fetchall()

        print("📋 Verified tables created:")
        for table in tables:
            print(f"   ✅ {table[0]}")

        # Check seed data
        cursor.execute("SELECT COUNT(*) FROM act_exercises")
        exercise_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM legal_disclaimers")
        disclaimer_count = cursor.fetchone()[0]

        print()
        print("📊 Seed data loaded:")
        print(f"   ✅ ACT Exercises: {exercise_count}")
        print(f"   ✅ Legal Disclaimers: {disclaimer_count}")
        print()

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


if __name__ == "__main__":
    success = execute_migration()

    if success:
        print("=" * 60)
        print("🎉 Phase 1 Migration Complete!")
        print()
        print("Next steps:")
        print("  1. Test API endpoints: python3 test_phase1_apis.py")
        print("  2. Begin frontend development")
        print()
        sys.exit(0)
    else:
        sys.exit(1)
