#!/bin/bash
# FlowMind Backend Test Suite
# Tests all major API endpoints and functionality

# Don't exit on error - continue testing all endpoints
set +e

API_URL="${1:-http://localhost:8000}"
USER_ID="default"

echo "════════════════════════════════════════════════════════"
echo "   FlowMind Backend Test Suite"
echo "════════════════════════════════════════════════════════"
echo "Testing API at: $API_URL"
echo "User ID: $USER_ID"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0
TOTAL=0

test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local expected_code="${3:-200}"
    local headers="${4:-}"
    
    TOTAL=$((TOTAL + 1))
    echo -n "Testing: $name ... "
    
    if [ -n "$headers" ]; then
        response=$(curl -s -w "\n%{http_code}" -H "$headers" "$API_URL$endpoint" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint" 2>&1)
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$status_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} ($status_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (expected $expected_code, got $status_code)"
        echo "  Response: $(echo "$body" | head -c 100)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. HEALTH CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Health endpoint" "/health" 200
test_endpoint "Healthz endpoint" "/healthz" 200
test_endpoint "Readiness check" "/readyz" 200
test_endpoint "Redis health" "/api/health/redis" 200
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. MINDFOLIO ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "List mindfolios" "/api/mindfolio" 200 "X-User-ID: $USER_ID"
test_endpoint "Mindfolio templates" "/api/mindfolio/templates" 200
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. OPTIONS ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Options expirations (AAPL)" "/api/options/expirations?symbol=AAPL" 200
test_endpoint "Spot price (TSLA)" "/api/options/spot/TSLA" 200
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. BUILDER ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Builder strategies" "/api/builder/strategies" 200
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. FLOW ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Flow summary" "/api/flow/summary?limit=5" 200
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. DASHBOARD ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Dashboard overview" "/api/dashboard/overview" 200
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. TRADESTATION ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# 307 redirect is expected - endpoint redirects to TradeStation OAuth page
test_endpoint "TradeStation login URL" "/api/ts/login" 307
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. CORE ENGINE ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Core engine status" "/api/core-engine/status" 200
test_endpoint "Core engine stats" "/api/core-engine/stats" 200
echo ""

echo "════════════════════════════════════════════════════════"
echo "   TEST SUMMARY"
echo "════════════════════════════════════════════════════════"
echo "Total Tests:  $TOTAL"
echo -e "Passed:       ${GREEN}$PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "Failed:       ${RED}$FAILED${NC}"
else
    echo -e "Failed:       ${GREEN}$FAILED${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠ Some tests failed - check output above${NC}"
    echo ""
    exit 1
fi
