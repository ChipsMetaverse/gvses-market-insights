#!/bin/bash
# Phase 3 Regression Test Runner
# This script can be used locally or in CI/CD pipelines

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
HEADLESS_DIR="$SCRIPT_DIR/backend/headless_chart_service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Phase 3 Regression Test Suite${NC}"
echo "================================"

# Function to check if a service is running
check_service() {
    local url=$1
    local name=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is running"
        return 0
    else
        echo -e "${RED}✗${NC} $name is not running"
        return 1
    fi
}

# Pre-flight checks
echo -e "\n${YELLOW}Pre-flight checks...${NC}"

SERVICES_OK=true

# Check backend service
if ! check_service "http://localhost:8000/health" "Backend service (port 8000)"; then
    echo "  Start with: cd backend && uvicorn mcp_server:app --port 8000"
    SERVICES_OK=false
fi

# Check headless service
if ! check_service "http://localhost:3100/health" "Headless service (port 3100)"; then
    echo "  Start with: cd backend/headless_chart_service && npm start"
    SERVICES_OK=false
fi

if [ "$SERVICES_OK" = false ]; then
    echo -e "\n${RED}ERROR: Required services are not running${NC}"
    echo "Please start the services and try again."
    exit 1
fi

# Run regression tests
echo -e "\n${YELLOW}Running Phase 3 regression tests...${NC}"
cd "$BACKEND_DIR"

# Check if Python dependencies are installed
if ! python3 -c "import httpx" 2>/dev/null; then
    echo -e "${YELLOW}Installing required Python packages...${NC}"
    pip install httpx
fi

# Run the test
if python3 test_phase3_regression.py; then
    echo -e "\n${GREEN}✅ All Phase 3 regression tests PASSED!${NC}"
    echo "Phase 3 implementation is stable and ready for deployment."
    
    # If in CI environment, save results
    if [ -n "$CI" ]; then
        echo -e "\n${YELLOW}Archiving test results for CI...${NC}"
        cp phase3_regression_results.json "$GITHUB_WORKSPACE/" 2>/dev/null || true
    fi
    
    exit 0
else
    echo -e "\n${RED}❌ Some regression tests FAILED${NC}"
    echo "Please review the failures above and fix issues before deployment."
    
    # If in CI environment, save failure results
    if [ -n "$CI" ]; then
        echo -e "\n${YELLOW}Archiving failure results for CI...${NC}"
        cp phase3_regression_results.json "$GITHUB_WORKSPACE/" 2>/dev/null || true
    fi
    
    exit 1
fi