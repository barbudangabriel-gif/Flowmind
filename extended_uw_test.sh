#!/bin/bash
TOKEN="5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE="https://api.unusualwhales.com/api"

echo "🔍 EXTENDED UW API TEST"
echo "======================="
echo

# More stock endpoints
echo "📊 MORE STOCK ENDPOINTS:"
more_stock=(
  "/stock/TSLA/historical"
  "/stock/TSLA/quote"
  "/stock/TSLA/ohlc"
  "/stock/TSLA/price"
  "/stock/TSLA/volume"
  "/stock/TSLA/options"
  "/stock/TSLA/options/chain"
  "/stock/TSLA/options/flow"
  "/stock/TSLA/darkpool"
  "/stock/TSLA/institutional-holdings"
  "/stock/TSLA/insider-trades"
  "/stock/TSLA/congress-trades"
)

for endpoint in "${more_stock[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN" --max-time 5)
  if [ "$status" = "200" ]; then
    echo "  ✅ $status - $endpoint"
  else
    echo "  ❌ $status - $endpoint"
  fi
done

echo
echo "🎲 SCREENER VARIATIONS:"
screener_vars=(
  "/screener"
  "/screener/stocks?limit=10"
  "/screener/etf"
  "/screener/unusual-activity"
  "/screen/stocks"
  "/stocks/screener"
)

for endpoint in "${screener_vars[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN" --max-time 5)
  if [ "$status" = "200" ]; then
    echo "  ✅ $status - $endpoint"
  else
    echo "  ❌ $status - $endpoint"
  fi
done

echo
echo "📰 NEWS & SOCIAL:"
news_social=(
  "/news"
  "/news/TSLA"
  "/social/sentiment"
  "/social/trending"
  "/reddit/trending"
  "/twitter/sentiment"
)

for endpoint in "${news_social[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN" --max-time 5)
  if [ "$status" = "200" ]; then
    echo "  ✅ $status - $endpoint"
  else
    echo "  ❌ $status - $endpoint"
  fi
done

echo
echo "🏦 ETF & INSTITUTIONAL:"
etf_inst=(
  "/etf"
  "/etf/SPY"
  "/etf/SPY/info"
  "/institutional"
  "/institutional/TSLA"
  "/institutional/holdings"
)

for endpoint in "${etf_inst[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN" --max-time 5)
  if [ "$status" = "200" ]; then
    echo "  ✅ $status - $endpoint"
  else
    echo "  ❌ $status - $endpoint"
  fi
done

echo
echo "🏛️ CONGRESS & INSIDER:"
congress_insider=(
  "/congress"
  "/congress/trades"
  "/insider"
  "/insider/trades"
  "/insider/TSLA"
)

for endpoint in "${congress_insider[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN" --max-time 5)
  if [ "$status" = "200" ]; then
    echo "  ✅ $status - $endpoint"
  else
    echo "  ❌ $status - $endpoint"
  fi
done
