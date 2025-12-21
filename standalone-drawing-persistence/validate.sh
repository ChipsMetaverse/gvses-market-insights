#!/bin/bash
# Quick validation script for drawing persistence system
# Run this before integration to ensure everything works

set -e  # Exit on error

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BOLD}🔍 Drawing Persistence System Validation${NC}\n"

# ============================================================================
# 1. Check Environment
# ============================================================================
echo -e "${BOLD}📋 Step 1: Checking environment...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}💡 Copy .env.example to .env and fill in your credentials${NC}"
    exit 1
fi

if ! grep -q "SUPABASE_URL=https://" .env; then
    echo -e "${RED}❌ SUPABASE_URL not configured in .env${NC}"
    exit 1
fi

if ! grep -q "SUPABASE_ANON_KEY=eyJ" .env; then
    echo -e "${RED}❌ SUPABASE_ANON_KEY not configured in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment configured${NC}\n"

# ============================================================================
# 2. Check Dependencies
# ============================================================================
echo -e "${BOLD}📦 Step 2: Checking dependencies...${NC}"

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${RED}❌ FastAPI not installed${NC}"
    echo -e "${YELLOW}💡 Run: pip install -r requirements.txt${NC}"
    exit 1
fi

if ! python3 -c "import supabase" 2>/dev/null; then
    echo -e "${RED}❌ Supabase client not installed${NC}"
    echo -e "${YELLOW}💡 Run: pip install -r requirements.txt${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All dependencies installed${NC}\n"

# ============================================================================
# 3. Validate Models
# ============================================================================
echo -e "${BOLD}🧪 Step 3: Validating Pydantic models...${NC}"

python3 models.py > /tmp/model_test.log 2>&1

if grep -q "✅ Trendline valid" /tmp/model_test.log; then
    echo -e "${GREEN}✅ Trendline model valid${NC}"
else
    echo -e "${RED}❌ Trendline validation failed${NC}"
    cat /tmp/model_test.log
    exit 1
fi

if grep -q "✅ Horizontal valid" /tmp/model_test.log; then
    echo -e "${GREEN}✅ Horizontal model valid${NC}"
else
    echo -e "${RED}❌ Horizontal validation failed${NC}"
    cat /tmp/model_test.log
    exit 1
fi

echo ""

# ============================================================================
# 4. Check Server (if running)
# ============================================================================
echo -e "${BOLD}🌐 Step 4: Checking server status...${NC}"

if curl -s http://localhost:8001/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running on port 8001${NC}"

    # Test database connection
    if curl -s http://localhost:8001/api/drawings/health | grep -q "healthy"; then
        echo -e "${GREEN}✅ Database connection healthy${NC}"
    else
        echo -e "${RED}❌ Database connection failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Server not running on port 8001${NC}"
    echo -e "${YELLOW}💡 Start with: python3 server.py${NC}"
    echo -e "${YELLOW}   Then run validation tests${NC}"
fi

echo ""

# ============================================================================
# 5. Summary
# ============================================================================
echo -e "${BOLD}📊 Validation Summary${NC}"
echo -e "${GREEN}✅ Environment: Configured${NC}"
echo -e "${GREEN}✅ Dependencies: Installed${NC}"
echo -e "${GREEN}✅ Models: Valid${NC}"

if curl -s http://localhost:8001/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Server: Running${NC}"
    echo -e "${GREEN}✅ Database: Connected${NC}"
    echo ""
    echo -e "${BOLD}🎉 System Ready!${NC}"
    echo -e "${YELLOW}Next step: Run tests with 'python3 test_api.py'${NC}"
else
    echo -e "${YELLOW}⚠️  Server: Not running${NC}"
    echo ""
    echo -e "${BOLD}📝 Next Steps:${NC}"
    echo "1. Apply schema.sql to Supabase (SQL Editor)"
    echo "2. Start server: python3 server.py"
    echo "3. Run tests: python3 test_api.py"
fi

echo ""
