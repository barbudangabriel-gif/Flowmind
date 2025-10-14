# 🏦 TradeStation API Endpoints - FlowMind

## 📋 Overview

FlowMind integrează TradeStation pentru:
- Autentificare OAuth 2.0
- Conturi și balanțe
- Poziții și tranzacții
- Date de piață (options chains, quotes)
- Streaming real-time (în dezvoltare)

## 🔐 Authentication Endpoints

### Status: ✅ Robust System Available (`backend/app/routers/tradestation_auth.py`)

| Endpoint | Method | Descriere | Status |
|----------|--------|-----------|--------|
| `/api/auth/tradestation/status` | GET | Auth status + token expiry | ✅ Production |
| `/api/auth/tradestation/init` | POST | Initialize tokens (post-OAuth) | ✅ Production |
| `/api/auth/tradestation/refresh` | POST | Manual token refresh | ✅ Production |
| `/api/auth/tradestation/health` | GET | Service health check | ✅ Production |
| `/api/auth/tradestation/logout` | DELETE | Clear user tokens | ✅ Production |

### Legacy Endpoints (`backend/server.py` - pentru compatibilitate)

| Endpoint | Method | Descriere | Status |
|----------|--------|-----------|--------|
| `/api/auth/tradestation/login` | GET | Generate OAuth URL | ⚠️ Legacy |
| `/api/auth/tradestation/callback` | POST | OAuth callback handler | ⚠️ Legacy |

**Recomandare:** Folosește robust system (`/api/auth/tradestation/*`) în loc de legacy.

## 💼 Account & Balance Endpoints

| Endpoint | Method | Descriere | Response |
|----------|--------|-----------|----------|
| `/api/tradestation/accounts` | GET | Lista conturi utilizator | `{accounts: [...]}` |
| `/api/tradestation/accounts/{id}/balances` | GET | Balanțe cont | `{cash, buying_power, equity}` |
| `/api/tradestation/balances/{id}` | GET | Balanțe (alias) | Same as above |

**Exemple:**
```bash
# Get accounts
GET /api/tradestation/accounts

# Get balances
GET /api/tradestation/accounts/ABC12345/balances
```

## 📊 Positions Endpoints

| Endpoint | Method | Descriere | Response |
|----------|--------|-----------|----------|
| `/api/tradestation/accounts/{id}/positions` | GET | Poziții active | `{data: [positions]}` |
| `/api/tradestation/positions/{id}` | GET | Poziții (alias) | Same as above |

**Position Object:**
```json
{
  "account_id": "ABC12345",
  "symbol": "AAPL",
  "asset_type": "Stock",
  "quantity": 100,
  "average_price": 175.50,
  "current_price": 180.25,
  "market_value": 18025.00,
  "unrealized_pnl": 475.00,
  "unrealized_pnl_percent": 2.71,
  "position_type": "LONG"
}
```

## 🧪 Testing Endpoints

| Endpoint | Method | Descriere | Status |
|----------|--------|-----------|--------|
| `/api/tradestation/connection/test` | GET | Test API connectivity | ✅ Available |

## 📡 Streaming Endpoints

| Endpoint | Method | Descriere | Status |
|----------|--------|-----------|--------|
| `/api/tradestation/stream/{symbol}` | GET | Real-time OHLCV stream | 🚧 In Development |

**Parameters:**
- `symbol`: Stock/ETF ticker (e.g., SPY)
- `tf`: Timeframe (default: "D" - daily)
- `limit`: Number of bars (default: 500)

**Status:** Demo structure ready, waiting for TradeStation streaming API integration.

## 🔧 Token Management Architecture

### Robust System (`backend/app/services/tradestation.py`)

**Features:**
- ✅ MongoDB persistence + in-memory cache
- ✅ Automatic token refresh (60s before expiry)
- ✅ Retry logic with exponential backoff
- ✅ Concurrent request deduplication (lock per user)
- ✅ Observability (logging + metrics ready)

**Token Flow:**
1. User completes OAuth → Frontend receives tokens
2. Frontend calls `/api/auth/tradestation/init` → Backend stores tokens
3. Backend auto-refreshes tokens 60s before expiry
4. Frontend can query `/api/auth/tradestation/status` for expiry time
5. Frontend can force refresh via `/api/auth/tradestation/refresh`

**Token Storage:**
- **Memory:** `_TOKENS` dict (fast access)
- **MongoDB:** `ts_tokens` collection (persistence)
- **Expiry:** Token expiry stored as Unix timestamp (`exp_ts`)

## 📝 Environment Variables

```bash
# TradeStation API
TRADESTATION_API_KEY=your_client_id
TRADESTATION_API_SECRET=your_client_secret
TRADESTATION_REDIRECT_URI=http://localhost:3000/auth/callback

# TradeStation Mode
TS_MODE=simulation  # or "live" for production

# TradeStation Base URLs
TS_BASE_URL=https://api.tradestation.com  # or sim-api for simulation

# Token Settings
TOKEN_SKEW_SECONDS=60  # Refresh 60s before expiry
HTTP_TIMEOUT=8.0  # API request timeout
```

## 🚀 Usage Examples

### 1. Check Authentication Status

```bash
curl http://localhost:8000/api/auth/tradestation/status
```

**Response:**
```json
{
  "authenticated": true,
  "expires_in": 3245,  // seconds until expiry
  "expires_at": 1729017845,  // Unix timestamp
  "needs_refresh": false,
  "status": "valid",
  "timestamp": 1729014600
}
```

### 2. Get Accounts

```bash
curl http://localhost:8000/api/tradestation/accounts \
  -H "Authorization: Bearer <token>"
```

### 3. Get Positions

```bash
curl http://localhost:8000/api/tradestation/accounts/ABC12345/positions \
  -H "Authorization: Bearer <token>"
```

### 4. Manual Token Refresh

```bash
curl -X POST http://localhost:8000/api/auth/tradestation/refresh \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "ok": true,
  "message": "Token refreshed successfully",
  "exp_ts": 1729018745,
  "expires_in": 3600
}
```

## 🎯 Integration Status

| Component | Status | Notes |
|-----------|--------|-------|
| OAuth Flow | ✅ Production | Robust token management |
| Account Data | ✅ Production | Accounts + balances |
| Positions | ✅ Production | Real-time positions |
| Options Chains | ✅ Production | Via `/api/options/*` endpoints |
| Quotes/Pricing | ✅ Production | Via options chain data |
| Streaming | 🚧 Development | Structure ready |
| Order Execution | ❌ Not Started | Future feature |

## 🔍 Related Files

**Backend:**
- `backend/app/routers/tradestation_auth.py` - Robust auth router
- `backend/app/services/tradestation.py` - Token management service
- `backend/app/deps/tradestation.py` - FastAPI dependencies
- `backend/server.py` - Legacy endpoints (compatibility)
- `backend/tradestation_client.py` - API client

**Frontend:**
- `frontend/src/services/tradestationAuth.js` - Auth service
- `frontend/src/components/TradestationConnect.js` - Connection UI

**Tests:**
- `tradestation_integration_test.py` - Integration tests
- `tradestation_auth_test.py` - Auth flow tests
- `tradestation_positions_test.py` - Positions tests
- `tradestation_balances_test.py` - Balance tests

## 💡 Best Practices

### Token Refresh Strategy

**Frontend:**
1. Check `/auth/tradestation/status` every 5 minutes
2. If `needs_refresh: true` → call `/auth/tradestation/refresh`
3. Update Authorization header with new token

**Backend:**
1. Auto-refresh 60s before expiry (handled automatically)
2. Use dependency injection for token validation
3. Return 401 if token expired → frontend should re-auth

### Error Handling

```javascript
try {
  const response = await fetch('/api/tradestation/accounts', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (response.status === 401) {
    // Token expired - refresh or re-auth
    await refreshToken();
  } else if (response.status === 503) {
    // Service disabled (security audit mode)
    showMessage('TradeStation temporarily unavailable');
  }
} catch (error) {
  console.error('TradeStation API error:', error);
}
```

## 🔒 Security Notes

- ✅ Tokens stored in MongoDB (not exposed in API responses)
- ✅ Token refresh uses secure endpoints
- ✅ CORS configured for frontend origin only
- ✅ Rate limiting ready (via middleware)
- ⚠️ Service can be disabled via environment flag (`TS_DISABLED=1`)

## 📚 Documentation Links

- **TradeStation API Docs:** https://api.tradestation.com/docs
- **OAuth 2.0 Flow:** See `EMAIL_TRADESTATION_OAUTH_REQUEST.md`
- **Setup Guide:** See `TRADESTATION_SETUP_GUIDE.md`

---

**Last Updated:** October 14, 2025  
**Status:** Production Ready (Streaming in development)  
**Maintainer:** FlowMind Backend Team
