#!/bin/bash
TOKEN="5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE="https://api.unusualwhales.com/api"

echo "🔍 FINAL COMPREHENSIVE TEST - All Possible Endpoints"
echo "====================================================="
echo

working=0
total=0

test_endpoint() {
  local endpoint=$1
  total=$((total + 1))
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN" --max-time 5)
  if [ "$status" = "200" ]; then
    echo "  ✅ $status - $endpoint"
    working=$((working + 1))
    return 0
  else
    echo "  ❌ $status - $endpoint"
    return 1
  fi
}

# All possible endpoint variations
endpoints=(
  # Stock endpoints (already found)
  "/stock/TSLA/info"
  "/stock/TSLA/greeks"
  "/stock/TSLA/option-contracts"
  "/stock/TSLA/spot-exposures"
  
  # Alerts
  "/alerts"
  
  # Screener
  "/screener/stocks"
  
  # Insider
  "/insider/trades"
  "/insider/TSLA"
  
  # Congress
  "/congress/trades"
  "/congress/TSLA"
  
  # Darkpool
  "/darkpool"
  "/darkpool/TSLA"
  
  # Market data
  "/market/summary"
  "/market/movers"
  "/market/gainers"
  "/market/losers"
  
  # Tickers list
  "/tickers"
  "/tickers/list"
  "/symbols"
  
  # Historical
  "/historical/TSLA"
  
  # Flow
  "/flow"
  "/flow/TSLA"
  
  # Unusual activity
  "/unusual"
  "/unusual/TSLA"
  
  # Whale trades
  "/whale-trades"
  "/whale-trades/TSLA"
  
  # Greeks variations
  "/greeks"
  "/greeks/TSLA"
  
  # Sentiment
  "/sentiment"
  "/sentiment/TSLA"
)

for endpoint in "${endpoints[@]}"; do
  test_endpoint "$endpoint"
done

echo
echo "====================================================="
echo "📊 RESULTS: $working/$total endpoints working ($(echo "scale=1; $working*100/$total" | bc)%)"
echo "====================================================="
