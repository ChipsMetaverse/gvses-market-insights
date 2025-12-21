#!/bin/bash
# Apply user_drawings table to Supabase

cd "$(dirname "$0")"

# Load environment variables
source .env

echo "🔌 Connecting to Supabase database..."
echo "📄 Applying create_user_drawings_table.sql..."

# Use the Supabase database connection
# Note: Supabase requires database password, not API key
# You can find this in: Supabase Dashboard → Project Settings → Database → Connection string

# Try using the Supabase CLI method
cat create_user_drawings_table.sql | supabase db query --db-url "postgresql://postgres.cwnzgvrylvxfhwhsqelc:${SUPABASE_DB_PASSWORD}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

# Alternative: Use psql if database password is available
# PGPASSWORD="${SUPABASE_DB_PASSWORD}" psql -h db.cwnzgvrylvxfhwhsqelc.supabase.co -U postgres -d postgres -f create_user_drawings_table.sql
