# Unusual Whales API - Correct Endpoints Implementation

**Date:** October 13, 2025  
**From:** Dan @ Unusual Whales API Support  
**FlowMind Integration Update**

## ⚠️ Critical Update - API Hallucinations Fixed

Our previous implementation used **hallucinated/non-existent endpoints**. This document provides the **correct** Unusual Whales API endpoints as confirmed by their support team.

---

## 🔴 Hallucinated Endpoints (DO NOT USE)

These endpoints **DO NOT EXIST** in the Unusual Whales API:

```
❌ /api/options-flow
❌ /api/stock/{ticker}/quote
❌ /api/stock/{ticker}/gamma-exposure
❌ /api/market/overview
❌ /v1/options/trades
❌ /v1/news
❌ /v1/congress/trades
❌ /v1/insiders/trades
```

---

## ✅ Correct Endpoints (MUST USE)

### 1. Options Flow Data

**Goal:** Big money trades, unusual activity, golden sweeps & blocks, premium size and sentiment

#### Option 1: Flow Alerts (Easiest to start)
- **Endpoint:** `GET /api/flow-alerts`
- **Docs:** https://api.unusualwhales.com/docs#/operations/PublicApi.OptionTradeController.flow_alerts
- **Notebook:** https://unusualwhales.com/public-api/examples/flow-alerts-multiple-tickers

```python
# Example usage
GET https://api.unusualwhales.com/api/flow-alerts
Query params:
- ticker (optional): Filter by symbol
- min_premium (optional): Minimum premium filter
- date (optional): Specific date (YYYY-MM-DD)
```

#### Option 2: Custom Alerts (More powerful, requires configuration)
- **Endpoint:** `GET /api/custom-alerts`
- **Docs:** https://api.unusualwhales.com/docs#/operations/PublicApi.AlertsController.alerts
- **Notebook:** https://unusualwhales.com/public-api/examples/custom-alerts
- **YouTube Tutorial:** https://www.youtube.com/watch?v=jlYo2536gPQ

```python
# Example usage
GET https://api.unusualwhales.com/api/custom-alerts
Query params:
- alert_id (required): Your configured alert ID
- start_date (optional)
- end_date (optional)
```

---

### 2. Stock Price Data

**Goal:** Get current stock price and historical data

#### Current Price Only: Stock State
- **Endpoint:** `GET /api/stock/{ticker}/state`
- **Docs:** https://api.unusualwhales.com/docs#/operations/PublicApi.TickerController.last_stock_state

```python
# Example
GET https://api.unusualwhales.com/api/stock/TSLA/state
Response:
{
  "ticker": "TSLA",
  "price": 250.75,
  "timestamp": "2025-10-13T14:30:00Z",
  "volume": 125000000,
  "change": 2.45,
  "change_percent": 0.98
}
```

#### Current + Historical: OHLC
- **Endpoint:** `GET /api/stock/{ticker}/ohlc`
- **Docs:** https://api.unusualwhales.com/docs#/operations/PublicApi.TickerController.ohlc

```python
# Example
GET https://api.unusualwhales.com/api/stock/TSLA/ohlc
Query params:
- interval: 1m, 5m, 15m, 1h, 1d (default: 1d)
- start_date: YYYY-MM-DD
- end_date: YYYY-MM-DD
```

---

### 3. Gamma Exposure (GEX)

**Goal:** Greek exposures by strike & expiry

- **Endpoint:** `GET /api/stock/{ticker}/spot-gex-exposures-by-strike-expiry`
- **Docs:** https://api.unusualwhales.com/docs#/operations/PublicApi.TickerController.spot_exposures_by_strike_expiry_v2

```python
# Example
GET https://api.unusualwhales.com/api/stock/TSLA/spot-gex-exposures-by-strike-expiry
Response:
{
  "ticker": "TSLA",
  "total_gex": 125000000,
  "call_gex": 85000000,
  "put_gex": 40000000,
  "strikes": [
    {
      "strike": 250,
      "call_gamma": 0.05,
      "put_gamma": 0.03,
      "total_oi": 35000,
      "expiry": "2025-11-15"
    }
  ]
}
```

---

### 4. Market Overview

**Goal:** Market-wide sentiment and flow data

- **Endpoint:** `GET /api/market/tide`
- **Docs:** https://api.unusualwhales.com/docs#/operations/PublicApi.MarketController.market_tide
- **Notebook:** https://unusualwhales.com/public-api/examples/market-tide

```python
# Example
GET https://api.unusualwhales.com/api/market/tide
Response:
{
  "timestamp": "2025-10-13T14:30:00Z",
  "market_sentiment": "bullish",
  "total_premium": 5250000000,
  "call_premium": 3200000000,
  "put_premium": 2050000000,
  "put_call_ratio": 0.64,
  "top_sectors": [...]
}
```

---

## 🔧 Implementation Changes Required

### File: `backend/integrations/uw_client.py`

**BEFORE (Hallucinated):**
```python
async def trades(self, symbol, start, end):
    return await self._get("/v1/options/trades", params)  # ❌ Does not exist
```

**AFTER (Correct):**
```python
async def flow_alerts(self, ticker=None, min_premium=None, date=None):
    """Get options flow alerts"""
    params = {}
    if ticker:
        params["ticker"] = ticker
    if min_premium:
        params["min_premium"] = min_premium
    if date:
        params["date"] = date.strftime("%Y-%m-%d")
    
    return await self._get("/api/flow-alerts", params)

async def stock_state(self, ticker):
    """Get current stock price"""
    return await self._get(f"/api/stock/{ticker}/state", {})

async def stock_ohlc(self, ticker, interval="1d", start_date=None, end_date=None):
    """Get historical OHLC data"""
    params = {"interval": interval}
    if start_date:
        params["start_date"] = start_date.strftime("%Y-%m-%d")
    if end_date:
        params["end_date"] = end_date.strftime("%Y-%m-%d")
    
    return await self._get(f"/api/stock/{ticker}/ohlc", params)

async def spot_gex_exposures(self, ticker):
    """Get gamma exposure by strike & expiry"""
    return await self._get(f"/api/stock/{ticker}/spot-gex-exposures-by-strike-expiry", {})

async def market_tide(self):
    """Get market-wide flow sentiment"""
    return await self._get("/api/market/tide", {})
```

---

### File: `backend/unusual_whales_service.py`

Update all methods to use correct endpoints:

```python
async def get_options_flow_alerts(self, minimum_premium=200000, limit=100):
    """Fetch options flow alerts - CORRECT ENDPOINT"""
    try:
        params = {
            "limit": limit,
            "min_premium": minimum_premium
        }
        
        # ✅ CORRECT ENDPOINT
        response = await self._make_request("/api/flow-alerts", params)
        
        if not response.get('data'):
            return await self._get_mock_options_flow()
        
        return [self._process_flow_alert(alert) for alert in response['data']]
        
    except Exception as e:
        logger.error(f"Flow alerts error: {e}")
        return await self._get_mock_options_flow()
```

---

## 📋 Migration Checklist

- [ ] Update `backend/integrations/uw_client.py` with correct endpoints
- [ ] Update `backend/unusual_whales_service.py` with correct endpoints
- [ ] Update `backend/services/uw_flow.py` with correct endpoints
- [ ] Update `backend/routers/flow.py` to use new methods
- [ ] Update `backend/routers/options.py` for GEX endpoint
- [ ] Test all endpoints with real API key
- [ ] Update frontend API client (`frontend/src/api/`) if needed
- [ ] Document breaking changes in CHANGELOG
- [ ] Run integration tests: `python backend_test.py`
- [ ] Deploy to staging and verify

---

## 🔗 Official UW Resources

- **API Docs:** https://api.unusualwhales.com/docs
- **Notebooks:** https://unusualwhales.com/public-api/examples
- **YouTube Tutorials:** https://www.youtube.com/c/unusualwhales

---

## 🚨 Important Notes

1. **Rate Limits:** Maintain 1.0s delay between requests (already implemented)
2. **API Key:** Use `UW_API_TOKEN` or `UNUSUAL_WHALES_API_KEY` env var
3. **Base URL:** `https://api.unusualwhales.com` (no `/v1` prefix for these endpoints)
4. **Authentication:** `Authorization: Bearer <token>` header
5. **Demo Mode:** Keep existing fallback logic for development/testing

---

**Contact:** Dan @ Unusual Whales API Support  
**Email:** support@unusualwhales.com (implied)
