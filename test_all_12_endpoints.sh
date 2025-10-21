#!/bin/bash
# Test all 12 verified UW API endpoints
# Run: bash test_all_12_endpoints.sh

TOKEN="5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE="https://api.unusualwhales.com/api"

echo "🧪 TESTING ALL 12 VERIFIED UW API ENDPOINTS"
echo "==========================================="
echo

test_count=0
success_count=0

test_endpoint() {
  local num=$1
  local endpoint=$2
  local description=$3
  
  test_count=$((test_count + 1))
  
  echo -n "$num. Testing $endpoint ... "
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" \
    -H "Authorization: Bearer $TOKEN" --max-time 10)
  
  if [ "$status" = "200" ]; then
    echo "✅ OK (200)"
    success_count=$((success_count + 1))
    
    # Get data count if available
    count=$(curl -s "$BASE$endpoint" -H "Authorization: Bearer $TOKEN" --max-time 10 | \
      jq -r 'if .data | type == "array" then .data | length elif .data | type == "object" then 1 else 0 end' 2>/dev/null)
    
    if [ "$count" != "null" ] && [ "$count" != "" ]; then
      echo "   📊 Data: $count records"
    fi
  else
    echo "❌ FAILED ($status)"
  fi
  
  # Rate limiting
  sleep 1.2
}

# Test all 12 endpoints
test_endpoint "1" "/stock/TSLA/info" "Stock info"
test_endpoint "2" "/stock/TSLA/greeks" "Options Greeks"
test_endpoint "3" "/stock/TSLA/option-contracts" "Options chain"
test_endpoint "4" "/stock/TSLA/spot-exposures" "Gamma exposure"
test_endpoint "5" "/stock/TSLA/options-volume" "Options volume"
test_endpoint "6" "/alerts" "Market alerts"
test_endpoint "7" "/screener/stocks?limit=5" "Stock screener"
test_endpoint "8" "/insider/trades" "All insider trades"
test_endpoint "9" "/insider/TSLA" "Insider trades (TSLA)"
test_endpoint "10" "/insider/recent" "Recent insider trades"
test_endpoint "11" "/darkpool/TSLA" "Dark pool (TSLA)"
test_endpoint "12" "/darkpool/recent" "Recent dark pool"

echo
echo "==========================================="
echo "📊 RESULTS: $success_count/$test_count endpoints working"
echo "==========================================="

if [ $success_count -eq 12 ]; then
  echo "✅ ALL 12 ENDPOINTS VERIFIED!"
  exit 0
else
  echo "⚠️ WARNING: Some endpoints failed!"
  exit 1
fi
