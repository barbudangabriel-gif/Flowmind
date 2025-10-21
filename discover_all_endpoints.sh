#!/bin/bash
TOKEN="5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE="https://api.unusualwhales.com/api"

echo "🔍 DISCOVERING ALL UW API ENDPOINTS - Advanced Plan"
echo "===================================================="
echo

working_endpoints=()

test_endpoint() {
  local endpoint=$1
  local description=$2
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN" --max-time 5)
  if [ "$status" = "200" ]; then
    echo "  ✅ $endpoint"
    working_endpoints+=("$endpoint|$description")
    return 0
  fi
  return 1
}

# ===========================================
# STOCK/TICKER ENDPOINTS
# ===========================================
echo "📊 STOCK/TICKER ENDPOINTS:"
test_endpoint "/stock/TSLA/info" "Company info, sector, market cap, earnings"
test_endpoint "/stock/TSLA/greeks" "Options Greeks (Delta, Gamma, Theta, Vega)"
test_endpoint "/stock/TSLA/option-contracts" "Full options chain (500+ contracts)"
test_endpoint "/stock/TSLA/spot-exposures" "Gamma exposure data (345+ records)"
test_endpoint "/stock/TSLA/earnings" "Earnings data"
test_endpoint "/stock/TSLA/dividends" "Dividend history"
test_endpoint "/stock/TSLA/splits" "Stock splits"
test_endpoint "/stock/TSLA/quote" "Real-time quote"
test_endpoint "/stock/TSLA/ohlc" "OHLC historical data"
test_endpoint "/stock/TSLA/historical" "Historical prices"
test_endpoint "/stock/TSLA/volume" "Volume data"
test_endpoint "/stock/TSLA/volatility" "Volatility metrics"
test_endpoint "/stock/TSLA/iv" "Implied volatility"
test_endpoint "/stock/TSLA/options-volume" "Options volume data"
test_endpoint "/stock/TSLA/options-oi" "Options open interest"
test_endpoint "/stock/TSLA/flow" "Options flow"
test_endpoint "/stock/TSLA/unusual-activity" "Unusual options activity"
test_endpoint "/stock/TSLA/darkpool" "Dark pool trades"
test_endpoint "/stock/TSLA/block-trades" "Block trades"
test_endpoint "/stock/TSLA/analyst-ratings" "Analyst ratings"
test_endpoint "/stock/TSLA/price-targets" "Price targets"
test_endpoint "/stock/TSLA/institutional" "Institutional holdings"
test_endpoint "/stock/TSLA/institutional-holdings" "Institutional holdings detail"
test_endpoint "/stock/TSLA/insider-trades" "Insider trades"
test_endpoint "/stock/TSLA/insider-holdings" "Insider holdings"
test_endpoint "/stock/TSLA/congress-trades" "Congress trades"
test_endpoint "/stock/TSLA/news" "Company news"
test_endpoint "/stock/TSLA/sentiment" "Sentiment analysis"
test_endpoint "/stock/TSLA/social" "Social media mentions"
test_endpoint "/stock/TSLA/fundamentals" "Fundamental data"
test_endpoint "/stock/TSLA/financials" "Financial statements"
test_endpoint "/stock/TSLA/balance-sheet" "Balance sheet"
test_endpoint "/stock/TSLA/income-statement" "Income statement"
test_endpoint "/stock/TSLA/cash-flow" "Cash flow statement"

echo
echo "🎯 MARKET/GENERAL ENDPOINTS:"
test_endpoint "/alerts" "Custom alerts & market tide events"
test_endpoint "/market/overview" "Market overview"
test_endpoint "/market/summary" "Market summary"
test_endpoint "/market/movers" "Market movers"
test_endpoint "/market/gainers" "Top gainers"
test_endpoint "/market/losers" "Top losers"
test_endpoint "/market/active" "Most active"
test_endpoint "/market/volume" "Market volume"
test_endpoint "/market/sectors" "Sector performance"
test_endpoint "/market/indices" "Market indices"
test_endpoint "/market/tide" "Market tide data"
test_endpoint "/market/sentiment" "Market sentiment"

echo
echo "📈 SCREENER ENDPOINTS:"
test_endpoint "/screener" "General screener"
test_endpoint "/screener/stocks" "Stock screener"
test_endpoint "/screener/options" "Options screener"
test_endpoint "/screener/etf" "ETF screener"
test_endpoint "/screener/unusual" "Unusual activity screener"
test_endpoint "/screener/flow" "Flow screener"
test_endpoint "/screener/earnings" "Earnings screener"
test_endpoint "/screener/darkpool" "Dark pool screener"

echo
echo "🏦 ETF ENDPOINTS:"
test_endpoint "/etf" "ETF list"
test_endpoint "/etf/list" "ETF list detailed"
test_endpoint "/etf/SPY" "ETF info"
test_endpoint "/etf/SPY/info" "ETF detailed info"
test_endpoint "/etf/SPY/holdings" "ETF holdings"
test_endpoint "/etf/SPY/performance" "ETF performance"
test_endpoint "/etf/SPY/flows" "ETF flows"

echo
echo "🏛️ INSTITUTIONAL/INSIDER/CONGRESS:"
test_endpoint "/insider/trades" "All insider trades"
test_endpoint "/insider/TSLA" "Insider trades for ticker"
test_endpoint "/insider/recent" "Recent insider trades"
test_endpoint "/congress/trades" "Congress trades"
test_endpoint "/congress/TSLA" "Congress trades for ticker"
test_endpoint "/congress/recent" "Recent congress trades"
test_endpoint "/institutional" "Institutional data"
test_endpoint "/institutional/trades" "Institutional trades"
test_endpoint "/institutional/holdings" "Institutional holdings"
test_endpoint "/institutional/TSLA" "Institutional data for ticker"

echo
echo "🌑 DARKPOOL ENDPOINTS:"
test_endpoint "/darkpool" "All dark pool trades"
test_endpoint "/darkpool/TSLA" "Dark pool trades for ticker"
test_endpoint "/darkpool/recent" "Recent dark pool trades"
test_endpoint "/darkpool/summary" "Dark pool summary"

echo
echo "💰 OPTIONS/FLOW ENDPOINTS:"
test_endpoint "/options" "Options data"
test_endpoint "/options/flow" "Options flow"
test_endpoint "/options/unusual" "Unusual options activity"
test_endpoint "/options/expiries" "Options expiries"
test_endpoint "/options/expiries/TSLA" "Expiries for ticker"
test_endpoint "/option-contracts" "All option contracts"
test_endpoint "/option-contracts/TSLA251024C00450000" "Specific contract"
test_endpoint "/flow" "General flow"
test_endpoint "/flow/TSLA" "Flow for ticker"
test_endpoint "/flow/recent" "Recent flow"
test_endpoint "/flow/summary" "Flow summary"

echo
echo "📰 NEWS & SOCIAL:"
test_endpoint "/news" "All news"
test_endpoint "/news/TSLA" "News for ticker"
test_endpoint "/news/recent" "Recent news"
test_endpoint "/social" "Social data"
test_endpoint "/social/sentiment" "Social sentiment"
test_endpoint "/social/trending" "Trending on social"
test_endpoint "/social/TSLA" "Social data for ticker"
test_endpoint "/reddit" "Reddit data"
test_endpoint "/reddit/trending" "Reddit trending"
test_endpoint "/twitter" "Twitter data"
test_endpoint "/twitter/sentiment" "Twitter sentiment"

echo
echo "📊 DATA/UTILITY ENDPOINTS:"
test_endpoint "/tickers" "All tickers"
test_endpoint "/tickers/list" "Ticker list"
test_endpoint "/symbols" "Symbol list"
test_endpoint "/trending" "Trending tickers"
test_endpoint "/most-active" "Most active tickers"
test_endpoint "/unusual" "Unusual activity"
test_endpoint "/whale-trades" "Whale trades"
test_endpoint "/calendar" "Events calendar"
test_endpoint "/calendar/earnings" "Earnings calendar"
test_endpoint "/calendar/dividends" "Dividends calendar"
test_endpoint "/calendar/splits" "Stock splits calendar"
test_endpoint "/calendar/ipos" "IPO calendar"

echo
echo "===================================================="
echo "✅ TOTAL WORKING ENDPOINTS: ${#working_endpoints[@]}"
echo "===================================================="

# Save to file
echo "Saving results to uw_all_endpoints.txt..."
> uw_all_endpoints.txt
for entry in "${working_endpoints[@]}"; do
  IFS='|' read -r endpoint description <<< "$entry"
  echo "$endpoint | $description" >> uw_all_endpoints.txt
done

echo "✅ Results saved to uw_all_endpoints.txt"
