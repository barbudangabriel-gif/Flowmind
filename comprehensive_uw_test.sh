#!/bin/bash
TOKEN="5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE="https://api.unusualwhales.com/api"

echo "🔍 COMPREHENSIVE UW API TEST - Advanced Plan"
echo "=============================================="
echo

# Stock/Ticker endpoints
echo "📊 STOCK/TICKER ENDPOINTS:"
endpoints_stock=(
  "/stock/TSLA/info"
  "/stock/TSLA/greeks"
  "/stock/TSLA/option-contracts"
  "/stock/TSLA/spot-exposures"
  "/stock/TSLA/earnings"
  "/stock/TSLA/dividends"
  "/stock/TSLA/splits"
  "/stock/TSLA/news"
  "/stock/TSLA/fundamentals"
  "/stock/TSLA/institutional"
  "/stock/TSLA/analyst-ratings"
)

for endpoint in "${endpoints_stock[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN")
  if [ "$status" = "200" ]; then
    echo "  ✅ $status - $endpoint"
  else
    echo "  ❌ $status - $endpoint"
  fi
done

echo
echo "🎯 MARKET/GENERAL ENDPOINTS:"
endpoints_market=(
  "/alerts"
  "/market/overview"
  "/market/sectors"
  "/market/indices"
  "/etf/list"
  "/etf/SPY/holdings"
  "/insider-trades"
  "/congress-trades"
  "/darkpool"
)

for endpoint in "${endpoints_market[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN")
  if [ "$status" = "200" ]; then
    echo "  ✅ $status - $endpoint"
  else
    echo "  ❌ $status - $endpoint"
  fi
done

echo
echo "💰 OPTIONS ENDPOINTS:"
endpoints_options=(
  "/option-contracts"
  "/option-contracts/TSLA251024C00450000"
  "/options/flow"
  "/options/unusual"
  "/options/expiries/TSLA"
)

for endpoint in "${endpoints_options[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN")
  if [ "$status" = "200" ]; then
    echo "  ✅ $status - $endpoint"
  else
    echo "  ❌ $status - $endpoint"
  fi
done

echo
echo "📈 SCREENER/DISCOVERY ENDPOINTS:"
endpoints_screener=(
  "/screener/stocks"
  "/screener/options"
  "/trending"
  "/most-active"
)

for endpoint in "${endpoints_screener[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN")
  if [ "$status" = "200" ]; then
    echo "  ✅ $status - $endpoint"
  else
    echo "  ❌ $status - $endpoint"
  fi
done

echo
echo "=============================================="
echo "Summary: Check results above for working endpoints"
