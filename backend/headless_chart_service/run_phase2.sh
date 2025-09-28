#!/bin/bash

echo "Phase 2 Deployment Script for Headless Chart Service"
echo "======================================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with Supabase credentials"
    exit 1
fi

# Load environment variables
source .env

echo "✅ Environment variables loaded"
echo "   SUPABASE_URL: ${SUPABASE_URL:0:30}..."
echo "   Worker ID: ${WORKER_ID:-auto-generated}"

# Build TypeScript
echo ""
echo "Building TypeScript..."
npm run build
if [ $? -eq 0 ]; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    exit 1
fi

# Instructions for database migration
echo ""
echo "📋 DATABASE MIGRATION REQUIRED:"
echo "================================"
echo "Please manually apply the Phase 2 migration:"
echo ""
echo "1. Go to Supabase Dashboard:"
echo "   ${SUPABASE_URL}"
echo ""
echo "2. Navigate to SQL Editor"
echo ""
echo "3. Copy contents of: migrations/phase2_supabase.sql"
echo ""
echo "4. Paste and execute in SQL Editor"
echo ""
echo "Press Enter when migration is complete..."
read

# Start the service
echo ""
echo "Starting Headless Chart Service with Worker ID: ${WORKER_ID:-auto}"
echo "================================================================"
npm start