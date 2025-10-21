#!/bin/bash
TOKEN="5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE="https://api.unusualwhales.com/api"

echo "🔍 TESTING ADVANCED PLAN ENDPOINTS"
echo "======================================"
echo

working=()

test_endpoint() {
  local endpoint=$1
  local desc=$2
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN" --max-time 5)
  if [ "$status" = "200" ]; then
    echo "  ✅ $endpoint - $desc"
    working+=("$endpoint")
    # Get sample data
    curl -s "$BASE$endpoint" -H "Authorization: Bearer $TOKEN" | jq -r 'if .data then (.data | if type == "array" then .[0:2] else . end) else . end' | head -20
    echo "---"
    return 0
  fi
  return 1
}

echo "📊 FLOW & ALERTS (already tested):"
test_endpoint "/alerts" "All alerts"
test_endpoint "/alerts?limit=5" "Limited alerts"

echo
echo "🔄 VARIATIONS OF EXISTING:"
test_endpoint "/stock/TSLA/options" "Options (alt)"
test_endpoint "/stock/TSLA/contracts" "Contracts (alt)"
test_endpoint "/stock/TSLA/chain" "Chain (alt)"
test_endpoint "/stock/TSLA/gex" "GEX (alt)"
test_endpoint "/stock/TSLA/gamma" "Gamma (alt)"

echo
echo "📈 HISTORICAL DATA:"
test_endpoint "/stock/TSLA/option-contracts?date=2025-10-20" "Historical options"
test_endpoint "/stock/TSLA/spot-exposures?date=2025-10-20" "Historical GEX"

echo
echo "🎯 FILTERS & PARAMETERS:"
test_endpoint "/screener/stocks?limit=5" "Screener with params"
test_endpoint "/insider/trades?limit=5" "Insider with limit"
test_endpoint "/darkpool/TSLA?limit=10" "Darkpool limited"

echo
echo "🔥 PREMIUM/FLOW ENDPOINTS:"
test_endpoint "/premium-flow" "Premium flow"
test_endpoint "/flow-summary" "Flow summary"
test_endpoint "/flow-alerts" "Flow alerts"
test_endpoint "/unusual-activity" "Unusual activity"

echo
echo "📊 ANALYTICS:"
test_endpoint "/analytics/TSLA" "Analytics"
test_endpoint "/analytics/gex/TSLA" "GEX analytics"
test_endpoint "/analytics/flow/TSLA" "Flow analytics"

echo
echo "======================================"
echo "✅ TOTAL NEW ENDPOINTS FOUND: ${#working[@]}"
echo "======================================"

if [ ${#working[@]} -gt 0 ]; then
  echo
  echo "Working endpoints:"
  for ep in "${working[@]}"; do
    echo "  - $ep"
  done
fi
