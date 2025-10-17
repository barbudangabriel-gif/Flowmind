#!/bin/bash
# Smoke Tests - FlowMind Backend
# Usage: ./smoke_tests.sh

set -e  # Exit on first error

echo "═══════════════════════════════════════════════════════"
echo "🔍 FLOWMIND SMOKE TESTS"
echo "═══════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend not running on port 8000${NC}"
    echo ""
    echo "Start backend first:"
    echo "  cd backend"
    echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi

echo -e "${GREEN}✅ Backend is running${NC}"
echo ""

# Test counter
PASSED=0
FAILED=0

# Helper function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_key="$3"
    
    echo -n "Testing $name... "
    
    response=$(curl -s "$url")
    
    if echo "$response" | grep -q "$expected_key"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
        echo "  Response: $response"
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAILED++))
        echo "  Response: $response"
        echo "  Expected key: $expected_key"
    fi
    echo ""
}

# Run tests
echo "Running endpoint tests..."
echo ""

test_endpoint "Health Check" \
    "http://localhost:8000/health" \
    "ok"

test_endpoint "Flow Health" \
    "http://localhost:8000/api/flow/health" \
    "scope"

test_endpoint "Flow Snapshot TSLA" \
    "http://localhost:8000/api/flow/snapshot/TSLA" \
    "TSLA"

test_endpoint "TradeStation Status" \
    "http://localhost:8000/api/ts/status" \
    "authenticated"

test_endpoint "API Docs (Swagger)" \
    "http://localhost:8000/docs" \
    "Swagger"

# Summary
echo "═══════════════════════════════════════════════════════"
echo "📊 TEST SUMMARY"
echo "═══════════════════════════════════════════════════════"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test frontend connection: http://localhost:3000"
    echo "  2. Check API docs: http://localhost:8000/docs"
    echo "  3. Test OAuth flow: http://localhost:8000/api/ts/login"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Check backend logs:"
    echo "  tail -50 /tmp/backend_ts.log"
    exit 1
fi
