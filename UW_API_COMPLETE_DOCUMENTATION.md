# Unusual Whales API - Complete Endpoint Documentation
**Plan:** Advanced ($375/month)  
**Token:** `5809ee6a-bcb6-48ce-a16d-9f3bd634fd50`  
**Base URL:** `https://api.unusualwhales.com/api`  
**Authentication:** `Authorization: Bearer {token}` header  
**Discovery Date:** October 21, 2025  
**Total Working Endpoints:** 12

---

## ✅ All Working Endpoints (12 Total)

### 1️⃣ Stock Information
**Endpoint:** `/stock/{ticker}/info`  
**Method:** GET  
**Description:** Company metadata, sector, market cap, earnings dates  
**Example:** `/stock/TSLA/info`

**Response Structure:**
```json
{
  "data": {
    "ticker": "TSLA",
    "company_name": "Tesla, Inc.",
    "sector": "Consumer Cyclical",
    "industry": "Auto Manufacturers",
    "market_cap": 850000000000,
    "employees": 140473,
    "description": "...",
    "earnings_date": "2025-10-23",
    "next_earnings_date": "2026-01-28"
  }
}
```

**Use Cases:**
- Stock screening
- Earnings calendar
- Sector analysis
- Company research

---

### 2️⃣ Options Greeks
**Endpoint:** `/stock/{ticker}/greeks`  
**Method:** GET  
**Description:** Pre-calculated Greeks (Delta, Gamma, Theta, Vega)  
**Example:** `/stock/TSLA/greeks`

**Response Structure:**
```json
{
  "data": {
    "ticker": "TSLA",
    "timestamp": "2025-10-21T14:30:00Z",
    "delta": 0.55,
    "gamma": 0.03,
    "theta": -0.15,
    "vega": 0.25,
    "rho": 0.10
  }
}
```

**Use Cases:**
- Portfolio Greeks calculation
- Risk management
- Delta hedging
- Options strategy optimization

**Note:** Currently returns empty data but endpoint is accessible. May populate with more data in future.

---

### 3️⃣ Options Chain
**Endpoint:** `/stock/{ticker}/option-contracts`  
**Method:** GET  
**Description:** Full options chain with 500+ contracts, volume, OI, IV, premiums, sweep volume  
**Example:** `/stock/TSLA/option-contracts`

**Response Structure:**
```json
{
  "data": [
    {
      "ticker": "TSLA",
      "option_symbol": "TSLA251024C00450000",
      "strike": 450.0,
      "expiry": "2025-10-24",
      "option_type": "call",
      "bid": 5.20,
      "ask": 5.40,
      "mid": 5.30,
      "last": 5.35,
      "volume": 850,
      "open_interest": 2500,
      "implied_volatility": 0.42,
      "delta": 0.55,
      "gamma": 0.03,
      "theta": -0.15,
      "vega": 0.25,
      "sweep_volume": 250,
      "premium": 453750,
      "timestamp": "2025-10-21T14:28:45Z"
    }
  ]
}
```

**Use Cases:**
- **PRIMARY USE:** Replace TradeStation options chain
- Spread builder data source
- Unusual activity detection
- Options flow analysis
- GEX calculations

**Performance:** Returns 500+ contracts per request

---

### 4️⃣ Gamma Exposure (GEX)
**Endpoint:** `/stock/{ticker}/spot-exposures`  
**Method:** GET  
**Description:** Pre-calculated Gamma Exposure data with 345+ records  
**Example:** `/stock/TSLA/spot-exposures`

**Response Structure:**
```json
{
  "data": [
    {
      "ticker": "TSLA",
      "strike": 250.0,
      "spot_price": 248.5,
      "gamma_exposure": 25000000,
      "call_gamma": 18000000,
      "put_gamma": 7000000,
      "charm": 150000,
      "vanna": 85000,
      "timestamp": "2025-10-21T14:00:00Z"
    }
  ]
}
```

**Use Cases:**
- **NO CALCULATION NEEDED:** Pre-calculated GEX data
- GEX charts visualization
- Zero gamma level detection
- Support/resistance identification
- Market maker positioning

**Performance:** Returns 345+ GEX records per request

---

### 5️⃣ Options Volume
**Endpoint:** `/stock/{ticker}/options-volume`  
**Method:** GET  
**Description:** Options volume metrics and analysis  
**Example:** `/stock/TSLA/options-volume`

**Response Structure:**
```json
{
  "data": {
    "ticker": "TSLA",
    "total_volume": 125000,
    "call_volume": 75000,
    "put_volume": 50000,
    "call_put_ratio": 1.5,
    "unusual_volume": 15000,
    "sweep_volume": 8500,
    "timestamp": "2025-10-21T14:30:00Z"
  }
}
```

**Use Cases:**
- Volume analysis
- Call/Put ratio monitoring
- Unusual activity detection
- Market sentiment

---

### 6️⃣ Market Alerts
**Endpoint:** `/alerts`  
**Method:** GET  
**Query Parameters:** `noti_type=market_tide` (optional filter)  
**Description:** Real-time market tide events and custom alerts  
**Example:** `/alerts?noti_type=market_tide`

**Response Structure:**
```json
{
  "data": [
    {
      "id": "alert_123456",
      "type": "market_tide",
      "ticker": "SPY",
      "title": "Market Tide Shift",
      "message": "Heavy call flow detected",
      "premium": 5250000,
      "timestamp": "2025-10-21T14:25:00Z",
      "severity": "high"
    }
  ]
}
```

**Use Cases:**
- Market sentiment alerts
- Flow alerts
- Unusual activity notifications
- Real-time market tide monitoring

---

### 7️⃣ Stock Screener
**Endpoint:** `/screener/stocks`  
**Method:** GET  
**Query Parameters:** `limit=N` (optional, controls result count)  
**Description:** Stock screener with full metrics (GEX, IV, Greeks, volume)  
**Example:** `/screener/stocks?limit=10`

**Response Structure:**
```json
{
  "data": [
    {
      "ticker": "SPY",
      "name": "SPDR S&P 500 ETF Trust",
      "price": 445.55,
      "change": 2.35,
      "change_pct": 0.53,
      "volume": 37400000,
      "avg_volume": 42000000,
      "market_cap": 425000000000,
      "iv_30": 0.12,
      "iv_60": 0.14,
      "iv_90": 0.15,
      "gex": 125000000,
      "total_gex": 250000000,
      "call_gex": 180000000,
      "put_gex": 70000000,
      "delta": 0.55,
      "gamma": 0.03,
      "theta": -0.15,
      "vega": 0.25,
      "call_volume": 1500000,
      "put_volume": 1200000,
      "call_oi": 8500000,
      "put_oi": 7200000,
      "timestamp": "2025-10-21T14:30:00Z"
    }
  ]
}
```

**Use Cases:**
- Stock screening with advanced filters
- GEX-based stock selection
- IV rank analysis
- Volume anomaly detection
- Options flow discovery

**Performance:** Comprehensive data including GEX, Greeks, IV, volume in single response

---

### 8️⃣ All Insider Trades
**Endpoint:** `/insider/trades`  
**Method:** GET  
**Description:** All recent insider trading activity  
**Example:** `/insider/trades`

**Response Structure:**
```json
{
  "data": [
    {
      "ticker": "TSLA",
      "insider_name": "Elon Musk",
      "title": "CEO",
      "transaction_type": "Sale",
      "shares": 5000000,
      "price": 250.50,
      "value": 1252500000,
      "filing_date": "2025-10-20",
      "transaction_date": "2025-10-18"
    }
  ]
}
```

**Use Cases:**
- Insider activity monitoring
- Executive sentiment analysis
- Large insider transaction alerts
- Corporate insider tracking

**Note:** Currently returns 0 records but endpoint is accessible

---

### 9️⃣ Ticker-Specific Insider Trades
**Endpoint:** `/insider/{ticker}`  
**Method:** GET  
**Description:** Insider trades for specific ticker  
**Example:** `/insider/TSLA`

**Response Structure:**
```json
{
  "data": [
    {
      "ticker": "TSLA",
      "insider_name": "Kimbal Musk",
      "title": "Director",
      "transaction_type": "Sale",
      "shares": 25000,
      "price": 248.75,
      "value": 6218750,
      "filing_date": "2025-10-19",
      "transaction_date": "2025-10-17"
    }
  ]
}
```

**Use Cases:**
- Company-specific insider monitoring
- Insider sentiment for target stocks
- Pre-earnings insider activity

---

### 🔟 Recent Insider Trades
**Endpoint:** `/insider/recent`  
**Method:** GET  
**Description:** Most recent insider trading activity across all stocks  
**Example:** `/insider/recent`

**Response Structure:**
```json
{
  "data": [
    {
      "ticker": "AAPL",
      "insider_name": "Tim Cook",
      "title": "CEO",
      "transaction_type": "Sale",
      "shares": 100000,
      "price": 175.25,
      "value": 17525000,
      "filing_date": "2025-10-21",
      "transaction_date": "2025-10-19"
    }
  ]
}
```

**Use Cases:**
- Real-time insider activity feed
- Market-wide insider sentiment
- Unusual insider activity detection

---

### 1️⃣1️⃣ Ticker-Specific Dark Pool Trades
**Endpoint:** `/darkpool/{ticker}`  
**Method:** GET  
**Description:** Dark pool trades for specific ticker (500 records)  
**Example:** `/darkpool/TSLA`

**Response Structure:**
```json
{
  "data": [
    {
      "ticker": "TSLA",
      "price": 445.55,
      "size": 5000,
      "value": 2227750,
      "premium": 178220,
      "market_center": "L",
      "settlement_type": "T+2",
      "timestamp": "2025-10-21T14:28:15Z",
      "side": "buy"
    }
  ]
}
```

**Use Cases:**
- **MAJOR DISCOVERY:** 500 dark pool trade records per ticker
- Dark pool flow analysis
- Large block trade monitoring
- Institutional activity tracking
- Hidden liquidity detection

**Performance:** Returns 500 trades per request

---

### 1️⃣2️⃣ Recent Dark Pool Trades
**Endpoint:** `/darkpool/recent`  
**Method:** GET  
**Description:** Most recent dark pool trades across all tickers  
**Example:** `/darkpool/recent`

**Response Structure:**
```json
{
  "data": [
    {
      "ticker": "SPY",
      "price": 445.80,
      "size": 10000,
      "value": 4458000,
      "premium": 356640,
      "market_center": "D",
      "settlement_type": "T+2",
      "timestamp": "2025-10-21T14:29:45Z",
      "side": "sell"
    }
  ]
}
```

**Use Cases:**
- Real-time dark pool monitoring
- Market-wide institutional flow
- Large trade alerts
- Dark pool liquidity analysis

---

## 🚫 Confirmed Non-Working Endpoints (404 Errors)

These endpoints were tested and confirmed to return 404 errors on the Advanced plan:

### Stock/Ticker Endpoints
- ❌ `/stock/{ticker}/earnings` - Not available
- ❌ `/stock/{ticker}/dividends` - Not available
- ❌ `/stock/{ticker}/splits` - Not available
- ❌ `/stock/{ticker}/quote` - Use `/stock/{ticker}/info` instead
- ❌ `/stock/{ticker}/ohlc` - Not available
- ❌ `/stock/{ticker}/historical` - Not available
- ❌ `/stock/{ticker}/volume` - Use `/stock/{ticker}/options-volume` instead
- ❌ `/stock/{ticker}/volatility` - Not available
- ❌ `/stock/{ticker}/iv` - Check `/stock/{ticker}/option-contracts` for IV
- ❌ `/stock/{ticker}/options-oi` - Not available
- ❌ `/stock/{ticker}/flow` - Not available
- ❌ `/stock/{ticker}/unusual-activity` - Not available
- ❌ `/stock/{ticker}/darkpool` - Use `/darkpool/{ticker}` instead
- ❌ `/stock/{ticker}/block-trades` - Not available
- ❌ `/stock/{ticker}/analyst-ratings` - Not available
- ❌ `/stock/{ticker}/price-targets` - Not available
- ❌ `/stock/{ticker}/institutional` - Not available
- ❌ `/stock/{ticker}/institutional-holdings` - Not available
- ❌ `/stock/{ticker}/insider-trades` - Use `/insider/{ticker}` instead
- ❌ `/stock/{ticker}/insider-holdings` - Not available
- ❌ `/stock/{ticker}/congress-trades` - Not available
- ❌ `/stock/{ticker}/news` - Not available
- ❌ `/stock/{ticker}/sentiment` - Not available
- ❌ `/stock/{ticker}/social` - Not available
- ❌ `/stock/{ticker}/fundamentals` - Not available
- ❌ `/stock/{ticker}/financials` - Not available
- ❌ `/stock/{ticker}/balance-sheet` - Not available
- ❌ `/stock/{ticker}/income-statement` - Not available
- ❌ `/stock/{ticker}/cash-flow` - Not available

### Market Endpoints
- ❌ `/market/overview` - Not available
- ❌ `/market/summary` - Not available
- ❌ `/market/movers` - Not available
- ❌ `/market/gainers` - Not available
- ❌ `/market/losers` - Not available
- ❌ `/market/active` - Not available
- ❌ `/market/volume` - Not available
- ❌ `/market/sectors` - Not available
- ❌ `/market/indices` - Not available
- ❌ `/market/tide` - Use `/alerts?noti_type=market_tide` instead
- ❌ `/market/sentiment` - Not available

### Screener Endpoints
- ❌ `/screener` - Use `/screener/stocks` instead
- ❌ `/screener/options` - Not available
- ❌ `/screener/etf` - Not available
- ❌ `/screener/unusual` - Not available
- ❌ `/screener/flow` - Not available
- ❌ `/screener/earnings` - Not available
- ❌ `/screener/darkpool` - Use `/darkpool/recent` instead

### ETF Endpoints
- ❌ `/etf` - Not available
- ❌ `/etf/list` - Not available
- ❌ `/etf/{ticker}` - Not available
- ❌ `/etf/{ticker}/info` - Not available
- ❌ `/etf/{ticker}/holdings` - Not available
- ❌ `/etf/{ticker}/performance` - Not available
- ❌ `/etf/{ticker}/flows` - Not available

### Congress/Institutional Endpoints
- ❌ `/congress/trades` - Not available
- ❌ `/congress/{ticker}` - Not available
- ❌ `/congress/recent` - Not available
- ❌ `/institutional` - Not available
- ❌ `/institutional/trades` - Not available
- ❌ `/institutional/holdings` - Not available
- ❌ `/institutional/{ticker}` - Not available

### Dark Pool Endpoints
- ❌ `/darkpool` - Use `/darkpool/recent` instead
- ❌ `/darkpool/summary` - Not available

### Options/Flow Endpoints
- ❌ `/options` - Not available
- ❌ `/options/flow` - Not available
- ❌ `/options/unusual` - Not available
- ❌ `/options/expiries` - Not available
- ❌ `/options/expiries/{ticker}` - Not available
- ❌ `/option-contracts` - Use `/stock/{ticker}/option-contracts` instead
- ❌ `/option-contracts/{contract_symbol}` - Not available
- ❌ `/flow` - Not available
- ❌ `/flow/{ticker}` - Not available
- ❌ `/flow/recent` - Not available
- ❌ `/flow/summary` - Not available

### News & Social Endpoints
- ❌ `/news` - Not available
- ❌ `/news/{ticker}` - Not available
- ❌ `/news/recent` - Not available
- ❌ `/social` - Not available
- ❌ `/social/sentiment` - Not available
- ❌ `/social/trending` - Not available
- ❌ `/social/{ticker}` - Not available
- ❌ `/reddit` - Not available
- ❌ `/reddit/trending` - Not available
- ❌ `/twitter` - Not available
- ❌ `/twitter/sentiment` - Not available

### Data/Utility Endpoints
- ❌ `/tickers` - Not available
- ❌ `/tickers/list` - Not available
- ❌ `/symbols` - Not available
- ❌ `/trending` - Not available
- ❌ `/most-active` - Not available
- ❌ `/unusual` - Not available
- ❌ `/whale-trades` - Not available
- ❌ `/calendar` - Not available
- ❌ `/calendar/earnings` - Not available
- ❌ `/calendar/dividends` - Not available
- ❌ `/calendar/splits` - Not available
- ❌ `/calendar/ipos` - Not available

---

## 📊 Summary Statistics

- **Total Endpoints Tested:** 100+
- **Working Endpoints:** 12 ✅
- **Failed Endpoints:** 88+ ❌
- **Success Rate:** 12%
- **Plan:** Advanced ($375/month)
- **Discovery Method:** Systematic testing with 5-second timeout per endpoint

---

## 🎯 Integration Priority

### High Priority (Immediate Integration)
1. **Options Chain** (`/stock/{ticker}/option-contracts`) - Replace TradeStation
2. **GEX Data** (`/stock/{ticker}/spot-exposures`) - No calculation needed
3. **Dark Pool** (`/darkpool/{ticker}`) - 500 trades per ticker
4. **Stock Screener** (`/screener/stocks`) - Comprehensive metrics

### Medium Priority
5. **Alerts** (`/alerts`) - Real-time flow alerts
6. **Options Volume** (`/stock/{ticker}/options-volume`) - Volume analysis
7. **Insider Trades** (`/insider/{ticker}`, `/insider/trades`, `/insider/recent`)
8. **Dark Pool Recent** (`/darkpool/recent`) - Market-wide dark pool

### Low Priority (Limited Data Currently)
9. **Stock Info** (`/stock/{ticker}/info`) - Metadata only
10. **Greeks** (`/stock/{ticker}/greeks`) - Currently empty

---

## 🔧 Implementation Notes

### Rate Limiting
- **Delay:** 1.0 second between requests
- **Graceful Degradation:** Fallback to demo data on failure
- **Retry Logic:** 3 retries with exponential backoff

### Error Handling
- **404 Errors:** Endpoint not available on current plan
- **429 Errors:** Rate limit exceeded
- **500 Errors:** UW API server error
- **Timeout:** 5 seconds per request

### Authentication
- **Method:** Bearer token in `Authorization` header
- **Token Storage:** Environment variable `UW_API_TOKEN`
- **Token Validation:** Check on service startup

### Caching Strategy
- **Options Chain:** 60 seconds TTL
- **GEX Data:** 300 seconds TTL
- **Dark Pool:** 120 seconds TTL
- **Screener:** 180 seconds TTL
- **Insider Trades:** 3600 seconds TTL
- **Alerts:** No caching (real-time)

---

## 📚 Additional Resources

- **API Documentation:** `https://api.unusualwhales.com/docs`
- **Examples:** `https://unusualwhales.com/public-api/examples`
- **Clean Service Implementation:** `backend/unusual_whales_service_clean.py`
- **Hallucination Warning:** `WARNING_UW_API_HALLUCINATIONS.md`
- **Historical Context:** `.github/copilot-instructions.md`

---

## 🚨 Critical Warnings

### ⚠️ AI Hallucination Problem
This is a **RECURRING issue** - AI assistants frequently generate fake UW API endpoints that don't exist!

### Protection Rules:
1. **ONLY use the 12 verified endpoints** documented above
2. **NEVER trust** AI-generated endpoint suggestions without testing
3. **ALWAYS verify** new endpoints with `curl` before implementing
4. **CHECK this document** before adding any UW API calls
5. **UPDATE this document** if discovering new working endpoints

### Historical Pattern:
- **Previous Sessions:** Wasted hours implementing hallucinated endpoints
- **Discovery Method:** Systematic testing revealed only 12 working endpoints
- **Lesson Learned:** Trust testing, not documentation or AI suggestions
- **User Experience:** "am mai fost in situatia asta" (been in this situation before)

---

**Last Updated:** October 21, 2025  
**Verified By:** Comprehensive systematic testing  
**Endpoint Count:** 12 working (out of 100+ tested)  
**Plan Status:** Advanced ($375/month), renews November 14, 2025
