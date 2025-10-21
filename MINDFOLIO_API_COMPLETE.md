# 💼 Mindfolio API Endpoints - FlowMind

## Overview

FlowMind oferă un sistem complet de management portofoliu cu:
- Portofolii multi-cont (manual tracking)
- Integrare directă TradeStation (live positions)
- Tranzacții FIFO (First-In-First-Out)
- Realized & Unrealized P&L
- Module allocations (IV Service, Sell Puts, etc.)
- Import CSV
- Buckets system (organizare poziții)
- Analytics & equity curves

## 🏗️ Architecture

**Storage:**
- **Primary:** Redis (TTL-based cache)
- **Fallback:** In-memory `AsyncTTLDict` (când Redis indisponibil)
- **TradeStation:** Live API calls (nu se stochează local)

**FIFO Algorithm:**
```python
# Positions calculated from transactions using FIFO
# BUY: Add to lots queue [qty @ price]
# SELL: Consume lots from front of queue
# Realized P&L = (sell_price - buy_price) * qty per lot
```

**Example:**
1. BUY 100 AAPL @ $150 → Lot: [100 @ $150]
2. BUY 50 AAPL @ $160 → Lots: [100 @ $150, 50 @ $160]
3. SELL 120 AAPL @ $170 → Consume 100 @ $150 + 20 @ $160
4. Realized P&L: (170-150)*100 + (170-160)*20 = $2200
5. Remaining: [30 @ $160]

## Core Mindfolio Endpoints

### 1. List Mindfolios
```http
GET /api/mindfolios
```

**Response:**
```json
[
 {
 "id": "uuid-123",
 "name": "My Trading Account",
 "cash_balance": 25000.00,
 "status": "ACTIVE",
 "modules": [
 {
 "module": "IV_SERVICE",
 "budget": 10000.0,
 "max_risk_per_trade": 500.0,
 "daily_loss_limit": 1000.0,
 "autotrade": false
 }
 ],
 "created_at": "2025-10-01T10:00:00Z",
 "updated_at": "2025-10-14T15:30:00Z"
 }
]
```

### 2. Create Mindfolio
```http
POST /api/mindfolios
```

**Request:**
```json
{
 "name": "Options Trading 2025",
 "starting_balance": 50000.0,
 "modules": [
 {
 "module": "IV_SERVICE",
 "budget": 20000.0,
 "max_risk_per_trade": 1000.0,
 "daily_loss_limit": 2000.0,
 "autotrade": false
 }
 ]
}
```

**Response:** Same as List (single mindfolio object)

### 3. Get Mindfolio Details
```http
GET /api/mindfolios/{mindfolio_id}
```

### 4. Update Mindfolio
```http
PATCH /api/mindfolios/{mindfolio_id}
```

**Request:**
```json
{
 "name": "Updated Mindfolio Name",
 "status": "PAUSED"
}
```

### 5. Add/Remove Funds
```http
POST /api/mindfolios/{mindfolio_id}/funds
```

**Request:**
```json
{
 "amount": 5000.0,
 "action": "ADD" // or "REMOVE"
}
```

### 6. Allocate to Module
```http
POST /api/mindfolios/{mindfolio_id}/allocate
```

**Request:**
```json
{
 "module": "IV_SERVICE",
 "budget": 15000.0,
 "max_risk_per_trade": 750.0,
 "daily_loss_limit": 1500.0,
 "autotrade": true
}
```

## Statistics & Analytics

### 7. Mindfolio Stats
```http
GET /api/mindfolios/{mindfolio_id}/stats
```

**Response:**
```json
{
 "mindfolio_id": "uuid-123",
 "name": "My Trading Account",
 "cash_balance": 25000.00,
 "total_invested": 30000.00,
 "unrealized_pnl": 3500.00,
 "realized_pnl": 1200.00,
 "total_pnl": 4700.00,
 "return_percent": 15.67,
 "total_transactions": 45,
 "active_positions": 8,
 "symbols_traded": ["AAPL", "TSLA", "NVDA", "..."],
 "module_allocations": {
 "IV_SERVICE": {
 "budget": 10000.0,
 "used": 7500.0,
 "available": 2500.0,
 "pnl": 850.0
 }
 }
}
```

### 8. Equity Curve (JSON)
```http
GET /api/mindfolios/{mindfolio_id}/analytics/equity
```

**Query Params:**
- `start_date`: ISO date (optional)
- `end_date`: ISO date (optional)
- `interval`: "daily" | "weekly" | "monthly" (default: "daily")

**Response:**
```json
{
 "mindfolio_id": "uuid-123",
 "dates": ["2025-10-01", "2025-10-02", "..."],
 "equity": [50000, 50250, 50100, "..."],
 "cash": [25000, 24500, 24800, "..."],
 "invested": [25000, 25750, 25300, "..."],
 "realized_pnl": [0, 100, 150, "..."],
 "unrealized_pnl": [0, 150, -50, "..."],
 "total_return_percent": 2.5
}
```

### 9. Equity Curve (CSV Download)
```http
GET /api/mindfolios/{mindfolio_id}/analytics/equity.csv
```

**Returns:** CSV file with headers:
```csv
date,equity,cash,invested,realized_pnl,unrealized_pnl
2025-10-01,50000.00,25000.00,25000.00,0.00,0.00
2025-10-02,50250.00,24500.00,25750.00,100.00,150.00
```

## Transactions

### 10. List Transactions
```http
GET /api/mindfolios/{mindfolio_id}/transactions
```

**Query Params:**
- `symbol`: Filter by symbol (optional)
- `start_date`: ISO date (optional)
- `end_date`: ISO date (optional)
- `limit`: Number of results (default: 100)

**Response:**
```json
[
 {
 "id": "tx-uuid-456",
 "mindfolio_id": "uuid-123",
 "account_id": "broker_account_1",
 "datetime": "2025-10-14T14:30:00Z",
 "symbol": "AAPL",
 "side": "BUY",
 "qty": 100,
 "price": 175.50,
 "fee": 1.00,
 "currency": "USD",
 "notes": "Opening position",
 "created_at": "2025-10-14T14:30:05Z"
 }
]
```

### 11. Add Transaction
```http
POST /api/mindfolios/{mindfolio_id}/transactions
```

**Request:**
```json
{
 "datetime": "2025-10-14T14:30:00Z",
 "symbol": "TSLA",
 "side": "BUY",
 "qty": 50,
 "price": 250.75,
 "fee": 0.50,
 "account_id": "my_broker_account",
 "notes": "Entry on breakout"
}
```

**Validation:**
- `side`: Must be "BUY" or "SELL"
- `qty`: Must be > 0
- `price`: Must be > 0
- `datetime`: ISO 8601 format

### 12. Import CSV Transactions
```http
POST /api/mindfolios/{mindfolio_id}/import-csv
```

**Request:**
```json
{
 "csv_data": "datetime,symbol,side,qty,price,fee,notes\n2025-10-01T10:00:00Z,AAPL,BUY,100,150.00,1.00,Opening\n2025-10-02T11:00:00Z,AAPL,SELL,50,155.00,0.50,Partial close"
}
```

**CSV Format:**
```csv
datetime,symbol,side,qty,price,fee,notes,account_id
2025-10-01T10:00:00Z,AAPL,BUY,100,150.00,1.00,Opening,account1
2025-10-02T11:00:00Z,AAPL,SELL,50,155.00,0.50,Partial,account1
```

**Response:**
```json
{
 "status": "success",
 "imported": 2,
 "failed": 0,
 "errors": []
}
```

## 📍 Positions & P&L

### 13. Current Positions
```http
GET /api/mindfolios/{mindfolio_id}/positions
```

**Response:**
```json
[
 {
 "symbol": "AAPL",
 "qty": 150,
 "cost_basis": 22575.00,
 "avg_cost": 150.50,
 "unrealized_pnl": 2250.00,
 "market_value": 24825.00
 },
 {
 "symbol": "TSLA",
 "qty": 50,
 "cost_basis": 12537.50,
 "avg_cost": 250.75,
 "unrealized_pnl": -125.00,
 "market_value": 12412.50
 }
]
```

**Note:** `unrealized_pnl` și `market_value` necesită prețuri live (TradeStation API).

### 14. Realized P&L (Closed Positions)
```http
GET /api/mindfolios/{mindfolio_id}/realized-pnl
```

**Response:**
```json
[
 {
 "symbol": "NVDA",
 "realized": 1250.00,
 "trades": 3
 },
 {
 "symbol": "MSFT",
 "realized": -85.00,
 "trades": 1
 }
]
```

## 🏦 TradeStation Integration

### 15. TradeStation Positions Grid
```http
GET /api/mindfolios/positions-ts
```

**Descriere:** Obține poziții live din toate conturile TradeStation, grupate pe simbol.

**Response:**
```json
{
 "status": "success",
 "positions_grid": [
 {
 "symbol": "AAPL",
 "asset_type": "Stock",
 "total_quantity": 250,
 "weighted_avg_price": 173.45,
 "total_market_value": 43362.50,
 "total_unrealized_pnl": 875.00,
 "unrealized_pnl_percent": 2.06,
 "accounts": [
 {
 "account_id": "ABC12345",
 "account_name": "Trading Account 1",
 "quantity": 150,
 "avg_price": 170.50
 },
 {
 "account_id": "XYZ67890",
 "account_name": "IRA Account",
 "quantity": 100,
 "avg_price": 177.50
 }
 ]
 }
 ],
 "total_positions": 8,
 "total_accounts": 2,
 "timestamp": "2025-10-14T20:15:00Z"
}
```

**Features:**
- Multi-account aggregation
- Weighted average price calculation
- Real-time P&L from TradeStation
- Account-level breakdown per symbol

### 16. TradeStation Auth URL
```http
GET /api/mindfolios/ts/auth-url
```

**Response:**
```json
{
 "status": "success",
 "auth_url": "https://signin.tradestation.com/authorize?client_id=...",
 "state": "random_state_token",
 "message": "Navigate to auth_url to complete OAuth2 flow"
}
```

### 17. TradeStation OAuth Callback
```http
POST /api/mindfolios/ts/callback?code={auth_code}&state={state}
```

**Response:**
```json
{
 "status": "success",
 "message": "OAuth2 authentication completed successfully",
 "authenticated": true,
 "environment": "LIVE"
}
```

### 18. Subscribe to Live Quotes
```http
POST /api/mindfolios/ts/subscribe
```

**Request:**
```json
["AAPL", "TSLA", "NVDA"]
```

**Response:**
```json
{
 "status": "success",
 "subscribed_symbols": ["AAPL", "TSLA", "NVDA"],
 "message": "Subscribed to 3 symbols for live quotes",
 "polling_interval": "30s"
}
```

### 19. Unsubscribe from Quotes
```http
POST /api/mindfolios/ts/unsubscribe
```

**Request:**
```json
["AAPL", "TSLA"]
```

## Buckets System

**Buckets** = Organizarea pozițiilor în categorii (Long-term, Swing, Day Trade, etc.)

### 20. Get Mindfolio Buckets
```http
GET /api/mindfolios/{mindfolio_id}/buckets
```

**Response:**
```json
[
 {
 "id": "bucket-uuid-789",
 "mindfolio_id": "uuid-123",
 "name": "Long-term Holdings",
 "description": "Buy and hold positions",
 "symbols": ["AAPL", "MSFT", "GOOGL"],
 "color": "#4CAF50",
 "created_at": "2025-10-01T10:00:00Z"
 },
 {
 "id": "bucket-uuid-790",
 "mindfolio_id": "uuid-123",
 "name": "Swing Trades",
 "description": "2-4 week positions",
 "symbols": ["TSLA", "NVDA"],
 "color": "#FF9800",
 "created_at": "2025-10-05T12:00:00Z"
 }
]
```

### 21. Create Bucket
```http
POST /api/mindfolios/{mindfolio_id}/buckets
```

**Request:**
```json
{
 "name": "Day Trades",
 "description": "Intraday positions",
 "symbols": ["SPY", "QQQ"],
 "color": "#F44336"
}
```

## 🔧 Module Allocations

**Modules** = Sisteme automate de trading (IV Service, Sell Puts, etc.)

**Module Types:**
- `IV_SERVICE` - Implied Volatility strategies
- `SELL_PUTS` - Cash-secured puts
- `COVERED_CALLS` - Covered call writing
- `IRON_CONDOR` - Iron condor strategies
- `CUSTOM` - Custom strategies

**Allocation Structure:**
```json
{
 "module": "IV_SERVICE",
 "budget": 10000.0,
 "max_risk_per_trade": 500.0,
 "daily_loss_limit": 1000.0,
 "autotrade": false
}
```

**Usage Flow:**
1. Create mindfolio with `starting_balance`
2. Allocate funds to modules via `/allocate`
3. Module uses allocated `budget` for trades
4. Module respects `max_risk_per_trade` and `daily_loss_limit`
5. If `autotrade: true`, module executes automatically
6. View module performance in `/stats`

## Best Practices

### Mindfolio Management
1. **Separate mindfolios** pentru strategii diferite (Long-term, Options, Day Trading)
2. **Module allocations** pentru control strict al riscului
3. **Regular imports** din broker statements (CSV import)
4. **Track realized P&L** separat pentru tax reporting

### TradeStation Integration
1. **Auth flow:** OAuth2 via `/ts/auth-url` → callback → tokens stored
2. **Live positions:** Query `/positions-ts` pentru real-time data
3. **Multi-account:** Automatic aggregation across all TS accounts
4. **Quote subscriptions:** Use `/ts/subscribe` pentru live pricing

### Transaction Recording
1. **Consistent datetime:** Always use ISO 8601 format
2. **Include fees:** Accuratețe în P&L calculation
3. **Notes field:** Track strategy rationale
4. **Account_id:** Multi-broker support

### Analytics
1. **Equity curve:** Export CSV pentru analysis în Excel/Python
2. **Regular snapshots:** Daily equity tracking
3. **Module attribution:** Track P&L per strategy
4. **Risk monitoring:** Daily loss limits per module

## Security & Access Control

**Current:** Single-user system (no auth required)
**Future:** User authentication + mindfolio ownership validation

**Data Privacy:**
- Redis keys namespaced by mindfolio ID
- TradeStation tokens stored securely (MongoDB)
- No sensitive data in logs

## Performance Considerations

**Caching:**
- Mindfolio objects: In-memory + Redis
- TradeStation positions: Fresh API calls (not cached)
- Stats calculations: Computed on-demand

**Optimization:**
- FIFO calculations: O(n) per transaction
- Position aggregation: O(m) where m = unique symbols
- Equity curve: Pre-calculated daily snapshots (future enhancement)

## 🚧 Future Enhancements

- [ ] Real-time WebSocket updates for TS positions
- [ ] Benchmark comparison (SPY, QQQ)
- [ ] Risk metrics (Sharpe ratio, max drawdown)
- [ ] Tax lot optimization (FIFO vs LIFO)
- [ ] Multi-currency support
- [ ] Automated reconciliation with broker statements
- [ ] Mobile app push notifications

## 📁 Related Files

**Backend:**
- `backend/mindfolios.py` - Main router (1129 lines)
- `backend/mindfolio_service.py` - Business logic
- `backend/mindfolio_management_service.py` - Advanced features
- `backend/tradestation_client.py` - TS API integration

**Frontend:**
- `frontend/src/pages/Mindfolio.jsx` - Main mindfolio view
- `frontend/src/components/MindfolioGrid.jsx` - Positions grid
- `frontend/src/services/mindfolioAPI.js` - API client

**Tests:**
- `tradestation_mindfolio_test.py` - TS integration tests
- `backend/tests/test_mindfolios.py` - Unit tests

---

**Last Updated:** October 14, 2025 
**API Version:** 3.0.0 
**Status:** Production Ready 
