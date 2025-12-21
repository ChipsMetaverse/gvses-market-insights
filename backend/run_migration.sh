#!/bin/bash
# Quick Migration Runner
# Executes the historical data migration on Supabase

set -e

echo "🔧 Historical Data Migration Runner"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "   Create backend/.env with SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check credentials
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "❌ Error: Missing Supabase credentials in .env"
    exit 1
fi

echo "📋 Migration file: supabase_migrations/004_historical_data_tables.sql"
echo "🎯 Target: $SUPABASE_URL"
echo ""

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo "❌ psql not found. Please install PostgreSQL client:"
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql-client"
    echo ""
    echo "Alternative: Run migration manually in Supabase dashboard"
    echo "   1. Go to: https://app.supabase.com/project/<your-project>/sql/new"
    echo "   2. Copy contents of: backend/supabase_migrations/004_historical_data_tables.sql"
    echo "   3. Paste and click 'Run'"
    exit 1
fi

# Extract database URL components
# Supabase format: https://xxxxx.supabase.co
PROJECT_ID=$(echo $SUPABASE_URL | sed 's/https:\/\///' | sed 's/.supabase.co//')
DB_URL="postgresql://postgres:$SUPABASE_SERVICE_ROLE_KEY@db.$PROJECT_ID.supabase.co:5432/postgres"

echo "🚀 Running migration..."
echo ""

# Run migration
if psql "$DB_URL" -f supabase_migrations/004_historical_data_tables.sql; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    echo "📊 Verify tables created:"
    echo "   python3 check_readiness.py"
    echo ""
    echo "🔥 Next step: Pre-warm data"
    echo "   python3 -m backend.scripts.prewarm_data --symbols AAPL TSLA NVDA"
else
    echo ""
    echo "❌ Migration failed"
    echo ""
    echo "💡 Try manual migration instead:"
    echo "   1. Go to: https://app.supabase.com/project/$PROJECT_ID/sql/new"
    echo "   2. Copy: backend/supabase_migrations/004_historical_data_tables.sql"
    echo "   3. Paste and click 'Run'"
    exit 1
fi
