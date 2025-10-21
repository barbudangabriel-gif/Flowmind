#!/bin/bash
TOKEN="5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"
BASE="https://api.unusualwhales.com/api"

echo "🧪 Testing UW API Endpoints..."
echo

endpoints=(
  "/stock/TSLA/option-contracts"
  "/stock/TSLA/spot-exposures"
  "/stock/TSLA/info"
  "/alerts"
  "/stock/TSLA/greeks"
)

for endpoint in "${endpoints[@]}"; do
  echo -n "Testing: $endpoint ... "
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$endpoint" -H "Authorization: Bearer $TOKEN")
  if [ "$status" = "200" ]; then
    echo "✅ $status OK"
  else
    echo "❌ $status FAIL"
  fi
done

echo
echo "Total endpoints: ${#endpoints[@]}"
