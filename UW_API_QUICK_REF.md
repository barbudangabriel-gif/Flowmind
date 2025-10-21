# ⚡ UW API Quick Reference

**Token:** `5809ee6a-bcb6-48ce-a16d-9f3bd634fd50`  
**Auth:** `Authorization: Bearer {token}`  
**Base:** `https://api.unusualwhales.com/api`

## Working Endpoints

```bash
# Options Chain (500+ contracts)
GET /stock/TSLA/option-contracts

# Gamma Exposure (345+ records)
GET /stock/TSLA/spot-exposures

# Stock Info
GET /stock/TSLA/info

# Market Alerts & Tide
GET /alerts

# Greeks (empty but accessible)
GET /stock/TSLA/greeks
```

## Quick Test

```bash
curl "https://api.unusualwhales.com/api/stock/TSLA/option-contracts" \
  -H "Authorization: Bearer 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50" | jq '.data | length'
```

## Use Cases

| Need | Endpoint | Replaces |
|------|----------|----------|
| Options Chain | `/stock/{ticker}/option-contracts` | TradeStation |
| GEX Chart | `/stock/{ticker}/spot-exposures` | Backend calculation |
| Market Flow | `/alerts` + filter `market_tide` | Flow service |
| Stock Info | `/stock/{ticker}/info` | Yahoo Finance |

## Next Step

Update `backend/unusual_whales_service.py` with these endpoints! See `UW_INTEGRATION_TASK_LIST.md`
