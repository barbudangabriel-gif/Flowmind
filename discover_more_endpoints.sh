#!/bin/bash
TOKEN="5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE="https://api.unusualwhales.com/api"

echo "🔍 SEARCHING FOR MORE UW API ENDPOINTS"
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
    return 0
  fi
  return 1
}

echo "📊 MARKET DATA:"
test_endpoint "/market/overview" "Market overview"
test_endpoint "/market/summary" "Market summary"
test_endpoint "/market/tide" "Market tide"
test_endpoint "/market/movers" "Market movers"
test_endpoint "/market/sectors" "Sectors"
test_endpoint "/indices" "Market indices"

echo
echo "📈 OPTIONS DATA:"
test_endpoint "/options/flow" "Options flow"
test_endpoint "/options/unusual" "Unusual options"
test_endpoint "/flow" "General flow"
test_endpoint "/flow/TSLA" "Flow for ticker"
test_endpoint "/unusual" "Unusual activity"
test_endpoint "/options/expirations/TSLA" "Expirations"

echo
echo "🏛️ CONGRESS & INSTITUTIONAL:"
test_endpoint "/congress" "Congress trades"
test_endpoint "/congress/trades" "Congress trades list"
test_endpoint "/congress/TSLA" "Congress trades ticker"
test_endpoint "/institutional" "Institutional"
test_endpoint "/institutional/TSLA" "Institutional ticker"
test_endpoint "/13f" "13F filings"

echo
echo "📰 NEWS & SOCIAL:"
test_endpoint "/news" "All news"
test_endpoint "/news/TSLA" "News for ticker"
test_endpoint "/social/TSLA" "Social data"
test_endpoint "/sentiment" "Market sentiment"
test_endpoint "/trending" "Trending tickers"

echo
echo "💰 ETF DATA:"
test_endpoint "/etf" "ETF list"
test_endpoint "/etf/SPY" "ETF data"
test_endpoint "/etf/SPY/holdings" "ETF holdings"

echo
echo "📊 CALENDAR & EVENTS:"
test_endpoint "/calendar" "Events calendar"
test_endpoint "/calendar/earnings" "Earnings calendar"
test_endpoint "/calendar/dividends" "Dividends calendar"
test_endpoint "/earnings" "Earnings data"
test_endpoint "/earnings/TSLA" "Earnings for ticker"

echo
echo "🔥 ADDITIONAL STOCK DATA:"
test_endpoint "/stock/TSLA/historical" "Historical prices"
test_endpoint "/stock/TSLA/quote" "Real-time quote"
test_endpoint "/stock/TSLA/ohlc" "OHLC data"
test_endpoint "/stock/TSLA/fundamentals" "Fundamentals"
test_endpoint "/stock/TSLA/financials" "Financials"
test_endpoint "/stock/TSLA/analyst-ratings" "Analyst ratings"
test_endpoint "/stock/TSLA/institutional" "Institutional holdings"

echo
echo "🎯 SCREENERS & FILTERS:"
test_endpoint "/screener" "General screener"
test_endpoint "/screener/options" "Options screener"
test_endpoint "/screener/etf" "ETF screener"
test_endpoint "/screener/unusual" "Unusual screener"

echo
echo "💎 SPECIAL DATA:"
test_endpoint "/whale-trades" "Whale trades"
test_endpoint "/block-trades" "Block trades"
test_endpoint "/sweep-alerts" "Sweep alerts"
test_endpoint "/gamma-exposure" "Gamma exposure"

echo
echo "======================================"
echo "✅ NEW ENDPOINTS FOUND: ${#working[@]}"
echo "======================================"

if [ ${#working[@]} -gt 0 ]; then
  echo
  echo "Working endpoints:"
  for ep in "${working[@]}"; do
    echo "  - $ep"
  done
fi
