# Unusual Whales API - Quick Reference Card
**For FlowMind Developers**

## 🔑 Authentication
```python
headers = {"Authorization": "Bearer 5809ee6a-bcb6-48ce-a16d-9f3bd634fd50"}
base_url = "https://api.unusualwhales.com/api"
```

## ✅ All 12 Working Endpoints

### 🎯 High-Priority (500+ records)
```python
# 1. Options Chain (500 contracts)
GET /stock/TSLA/option-contracts
# Returns: volume, OI, IV, premiums, sweep volume

# 2. Gamma Exposure (377+ records)
GET /stock/TSLA/spot-exposures
# Returns: pre-calculated gamma, charm, vanna

# 3. Dark Pool (500 trades)
GET /darkpool/TSLA
# Returns: price, volume, premium, market center
```

### 📊 Medium-Priority (50-100 records)
```python
# 4. Market Alerts (50+ events)
GET /alerts
GET /alerts?noti_type=market_tide

# 5. Insider Trades (46+ per ticker)
GET /insider/TSLA

# 6. Recent Dark Pool (100 trades)
GET /darkpool/recent
```

### 🔧 Utility Endpoints
```python
# 7. Stock Screener (configurable limit)
GET /screener/stocks?limit=10
# Returns: GEX, IV, Greeks, volume, price

# 8. Options Volume
GET /stock/TSLA/options-volume

# 9. Stock Info
GET /stock/TSLA/info

# 10. All Insider Trades
GET /insider/trades

# 11. Recent Insider Trades
GET /insider/recent

# 12. Greeks (currently empty)
GET /stock/TSLA/greeks
```

## 🐍 Python Usage

```python
from backend.unusual_whales_service_clean import unusual_whales_service

# Options chain (replace TradeStation)
contracts = await unusual_whales_service.get_option_contracts("TSLA")
# Returns: {"data": [500+ contracts]}

# GEX data (no calculation needed!)
gex = await unusual_whales_service.get_spot_exposures("TSLA")
# Returns: {"data": [377+ GEX records]}

# Dark pool (institutional flow)
darkpool = await unusual_whales_service.get_darkpool_ticker("TSLA")
# Returns: {"data": [500 trades]}

# Stock screener (unified metrics)
stocks = await unusual_whales_service.get_screener_stocks(limit=10)
# Returns: {"data": [10 stocks with GEX/IV/Greeks]}

# Insider trades (sentiment)
insiders = await unusual_whales_service.get_insider_ticker("TSLA")
# Returns: {"data": [46+ insider trades]}

# Market alerts (real-time)
alerts = await unusual_whales_service.get_alerts(noti_type="market_tide")
# Returns: {"data": [50+ alerts]}
```

## 🚫 Do NOT Use (404 Errors)

```python
# These are AI hallucinations - they DON'T EXIST:
❌ /api/flow-alerts
❌ /api/market/overview
❌ /api/market/tide
❌ /api/options/flow
❌ /api/stock/{ticker}/quote
❌ /api/stock/{ticker}/ohlc
❌ /api/congress/trades
❌ /api/stock/{ticker}/darkpool  # Use /darkpool/{ticker} instead
```

## ⚡ Rate Limiting

```python
# Delay 1.0 second between requests
import asyncio
await asyncio.sleep(1.0)

# Service auto-implements rate limiting
# No manual delay needed when using unusual_whales_service
```

## 📦 Caching Strategy

```python
# Recommended TTL values
OPTIONS_CHAIN_TTL = 60      # 1 minute (real-time)
GEX_DATA_TTL = 300           # 5 minutes
DARKPOOL_TTL = 120           # 2 minutes
SCREENER_TTL = 180           # 3 minutes
INSIDER_TTL = 3600           # 1 hour
ALERTS_TTL = 0               # No caching (real-time)
```

## 🧪 Testing

```bash
# Test all endpoints
python test_uw_12_endpoints.py

# Expected: 12/12 passing
# Data: 1,580+ total records
```

## 📚 Documentation

- **Complete Docs:** `UW_API_COMPLETE_DOCUMENTATION.md`
- **Discovery Summary:** `UW_API_DISCOVERY_SUMMARY.md`
- **Clean Service:** `backend/unusual_whales_service_clean.py`
- **AI Instructions:** `.github/copilot-instructions.md`

## ⚠️ Critical Rules

1. ✅ **ONLY use the 12 verified endpoints** above
2. ❌ **NEVER trust** AI-generated endpoint suggestions
3. ✅ **ALWAYS test** new endpoints with curl first
4. ✅ **CHECK this card** before implementing UW API calls
5. ✅ **USE** `unusual_whales_service_clean.py` - it's verified

## 🎯 Quick Wins

### Replace TradeStation
```python
# OLD: TradeStation options chain
chain = await ts_client.get_options_chain("TSLA")

# NEW: UW options chain (500+ contracts)
chain = await unusual_whales_service.get_option_contracts("TSLA")
```

### Add GEX (No Calculation!)
```python
# Pre-calculated GEX data
gex = await unusual_whales_service.get_spot_exposures("TSLA")
# Use directly for charts - no gamma calculation needed
```

### New Feature: Dark Pool Tracker
```python
# 500 dark pool trades per ticker
darkpool = await unusual_whales_service.get_darkpool_ticker("TSLA")
# Perfect for institutional flow monitoring
```

## 🔥 Data Highlights

- **Options Chain:** 500 contracts/ticker
- **GEX Data:** 377+ records with gamma/charm/vanna
- **Dark Pool:** 500 trades/ticker + 100 recent
- **Alerts:** 50+ real-time market events
- **Insider Trades:** 46+ per ticker
- **Screener:** Unified GEX/IV/Greeks/volume

---

**Last Updated:** October 21, 2025  
**Plan:** Advanced ($375/month)  
**Status:** All 12 endpoints verified  
**Test:** `python test_uw_12_endpoints.py`
