https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/oauth/tradestation/callback
## FlowMind AI Agent Quick Reference

### Project Overview
FlowMind is an options analytics platform (FastAPI backend, React 19 frontend, Redis/MongoDB storage) for building options strategies, monitoring real-time flow, and managing portfolios with FIFO-based P&L tracking.

### Architecture Overview
- **Backend:** FastAPI (`backend/server.py`), routers in `backend/routers/` and `backend/app/routers/`, services in `backend/services/`, AI agents as `*_agent.py`
- **Frontend:** React 19 monolith (`frontend/src/App.js`), feature pages in `pages/`, Zustand stores in `stores/`, craco for build config
- **Storage:** Redis (primary cache with TTL-based keys), fallback to in-memory `AsyncTTLDict`, MongoDB (portfolios), SQLite (alternative)
- **External APIs:** TradeStation (OAuth, options chains, spot prices), Unusual Whales (flow/news/congress with rate limiting and demo fallback)

### Critical Architectural Patterns

#### 1. Redis Fallback System (`backend/redis_fallback.py`)
**The "why":** Zero-downtime caching - application continues if Redis fails or is unavailable
```python
# Three operational modes:
# 1. TEST_MODE=1 → Shared AsyncTTLDict instance (for consistent test state)
# 2. FM_FORCE_FALLBACK=1 → Force in-memory (dev/test)
# 3. Normal → Try Redis, fallback to in-memory on connection failure

await get_kv()  # Returns Redis client OR AsyncTTLDict
```
**Used everywhere:** All caching (`bt_cache_integration.py`, `portfolios.py`, `iv_service/`), never direct Redis imports

#### 2. FIFO Position Tracking (`backend/portfolios.py`)
**The "why":** Tax-compliant realized P&L calculation for options/stock positions
```python
# Algorithm: BUY adds to lots queue, SELL consumes from front (First-In-First-Out)
# Realized P&L = (sell_price - buy_price) * qty per consumed lot
# Example: BUY 100@250 + BUY 50@260 → SELL 120@270 consumes 100@250 + 20@260
# Result: Realized $2,200, Remaining: 30@260
```
**Key functions:** `calculate_positions()`, `get_portfolio_transactions()` - positions computed from transactions, not stored

#### 3. Dark Theme Enforcement (`DARK_THEME_ONLY_VALIDATION.md`)
**The "why":** Consistent UX, no light mode support (removed toggle to simplify codebase)
```javascript
// frontend/src/App.js - ThemeProvider always returns isDarkMode: true
useEffect(() => { document.documentElement.classList.add('dark'); }, []);
```
**Rule:** All Tailwind classes must be dark variants (`bg-slate-800`, `text-white`) - no conditional `isDarkMode ?` ternaries

#### 4. Integration Test Pattern (Root `*_test.py` files)
**The "why":** Verify real API behavior against deployed backend, not mocks
```python
# Pattern used in backend_test.py, options_backend_test.py, etc:
BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8000")
response = requests.post(f"{BACKEND_URL}/api/builder/price", json=payload)
# Tests verify real responses, data structures, and error handling
```
**NOT for unit tests** - those go in `backend/tests/` using pytest with fixtures

### Developer Workflows

#### Backend Development
```bash
cd backend
python -m uvicorn server:app --reload --port 8000  # Main server entry
# Alternative: python -m uvicorn app.main:app --reload --port 8000

# Quality gates (matches CI/CD):
pytest -q --maxfail=1 --disable-warnings
ruff check . && ruff format --check
mypy . --ignore-missing-imports
bandit -ll -r . -x tests  # Security scan, low-level or higher
pip-audit --strict  # Dependency vulnerabilities
```

#### Frontend Development
```bash
cd frontend
npm start  # Uses craco (configured in craco.config.js)

# Quality gates:
npm run lint  # ESLint
npm run build  # Production build
npm audit --audit-level=high  # Only fail on high/critical
```

#### Docker Compose (Full Stack)
```bash
docker-compose up  # Backend on :8000, Redis on :6379
# Backend uses: python -m uvicorn server:app --reload (not app.main:app)
```

### Naming Conventions (Discoverable via File Patterns)
- **Services:** `*_service.py` (e.g., `unusual_whales_service.py`, `portfolio_service.py`)
- **Routers:** `backend/routers/*.py` (feature routers) OR `backend/app/routers/*.py` (OAuth, auth)
- **AI Agents:** `*_agent.py` (e.g., `investment_scoring_agent.py`, `technical_analysis_agent.py`)
- **Integration Tests:** Root `*_test.py` (e.g., `backend_test.py`, `builder_backend_test.py`)
- **Unit Tests:** `backend/tests/test_*.py` (pytest convention)

### Critical Environment Variables
```bash
# Backend (backend/.env)
REDIS_URL=redis://localhost:6379/0  # Optional (has fallback)
FM_FORCE_FALLBACK=1                 # Force in-memory cache (dev/test)
FM_REDIS_REQUIRED=1                 # Fail fast if Redis unavailable
TEST_MODE=1                         # Shared in-memory instance for tests
MONGO_URL=mongodb://...             # Required for portfolio persistence
TS_CLIENT_ID/TS_CLIENT_SECRET/TS_REDIRECT_URI  # TradeStation OAuth
UW_API_TOKEN or UNUSUAL_WHALES_API_KEY         # Unusual Whales API

# Frontend (frontend/.env.local)
REACT_APP_BACKEND_URL=http://localhost:8000  # API base URL (never hardcode!)
```

### API Router Organization
**Two mounting patterns exist** (historical reasons):
1. `backend/routers/*.py` - Mounted with `/api` prefix in `server.py`
2. `backend/app/routers/*.py` - Mounted with `/api` prefix or pre-configured prefix

**Router registration in `server.py`:**
```python
app.include_router(options_router, prefix="/api")  # backend/routers/options.py
app.include_router(ts_auth_router, prefix="/api")  # backend/app/routers/tradestation_auth.py
app.include_router(geopolitical_router)            # Already has /api/geopolitical prefix
```

### Common Pitfalls
1. **Redis confusion:** Always use `from redis_fallback import get_kv`, never direct Redis imports
2. **Dark theme violations:** Never use `isDarkMode ?` ternaries or light Tailwind classes (`bg-white`, `text-gray-800`)
3. **URL hardcoding:** Frontend must use `process.env.REACT_APP_BACKEND_URL`, not `http://localhost:8000`
4. **TradeStation token expiry:** 60-day refresh cycle, handled in `tradestation_auth.py` or `app/routers/tradestation_auth.py`
5. **Unusual Whales rate limits:** 1.0s delay between requests (`rate_limit_delay`), always implement demo fallback
6. **Test mode:** Integration tests need real backend, unit tests use `TEST_MODE=1` for shared cache
7. **FIFO integrity:** Never modify positions directly - always add transactions and recompute via `calculate_positions()`

### Key Files for Understanding Architecture
- `backend/server.py` (961 lines) - Main FastAPI app, router mounting, service initialization
- `backend/redis_fallback.py` (98 lines) - Cache abstraction, fallback logic, singleton pattern
- `backend/portfolios.py` (1133 lines) - FIFO algorithm, position calculation, transaction tracking
- `backend/services/builder_engine.py` - Options strategy engine (54+ strategies, Greeks)
- `backend/services/quality.py` - Spread quality scoring (liquidity, spread width, risk metrics)
- `frontend/src/App.js` (250 lines) - React app entry, dark theme provider, routing
- `DARK_THEME_ONLY_VALIDATION.md` - Dark theme migration details and validation results
- `DEVELOPMENT_GUIDELINES.md` - Romanian workflow rules (iterative, feedback-driven)

---
**When in doubt:** Check `redis_fallback.py` for cache patterns, `portfolios.py` for FIFO logic, `server.py` for router organization, and root `*_test.py` files for integration test examples.

### MongoDB Collections

**Note**: FlowMind uses **Redis** for primary storage with optional MongoDB for persistence. Schema defined in `backend/portfolios.py`.

#### Portfolio Model
```python
{
  "id": "uuid-string",
  "name": "My Trading Portfolio",
  "cash_balance": 10000.0,
  "status": "ACTIVE",  # ACTIVE, PAUSED, CLOSED
  "modules": [
    {
      "module": "IV_SERVICE",
      "budget": 5000.0,
      "max_risk_per_trade": 500.0,
      "daily_loss_limit": 1000.0,
      "autotrade": false
    }
  ],
  "created_at": "2025-10-13T14:30:00Z",
  "updated_at": "2025-10-13T14:30:00Z"
}
```

#### Transaction Model (FIFO-based)
```python
{
  "id": "uuid-string",
  "portfolio_id": "portfolio-uuid",
  "account_id": "optional-account-id",
  "datetime": "2025-10-13T14:30:00Z",
  "symbol": "TSLA",
  "side": "BUY",  # BUY or SELL
  "qty": 100.0,
  "price": 250.50,
  "fee": 1.0,
  "currency": "USD",
  "notes": "Opening position",
  "created_at": "2025-10-13T14:30:00Z"
}
```

#### Position Model (Computed from Transactions)
```python
{
  "symbol": "TSLA",
  "qty": 100.0,
  "cost_basis": 25051.0,  # Total cost including fees
  "avg_cost": 250.51,     # cost_basis / qty
  "unrealized_pnl": 125.0,  # Requires market price
  "market_value": 25175.0   # Requires market price
}
```

### Redis Key Patterns

FlowMind uses Redis with TTL-based caching and fallback to in-memory storage:

```python
# Portfolio data
pf:{portfolio_id}                    # Portfolio object
pf:list                              # List of all portfolio IDs
pf:{portfolio_id}:stats              # Portfolio statistics
pf:{portfolio_id}:transactions       # List of transaction IDs
pf:{portfolio_id}:positions          # Current positions

# Transactions
tx:{transaction_id}                  # Transaction object

# Cache keys (from redis_fallback.py)
flow:summary:{limit}                 # Flow summary (TTL: 60s)
bt:{strategy_hash}                   # Backtest results (TTL: 300s)
chain:{symbol}:{expiry}              # Options chain (TTL: 60s)
```

### SQLite Schema (Alternative Storage)

For deployments without Redis, FlowMind supports SQLite (`backend/database.py`):

```sql
-- Core tables
CREATE TABLE portfolios (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  base_currency TEXT DEFAULT 'USD',
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE accounts (
  id INTEGER PRIMARY KEY,
  portfolio_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  broker TEXT,
  currency TEXT DEFAULT 'USD',
  FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

CREATE TABLE transactions (
  id INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL,
  datetime TEXT NOT NULL,
  symbol TEXT NOT NULL,
  side TEXT CHECK (side IN ('BUY','SELL')),
  qty REAL NOT NULL,
  price REAL NOT NULL,
  fee REAL DEFAULT 0,
  currency TEXT DEFAULT 'USD',
  notes TEXT,
  FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- Indexes for performance
CREATE INDEX idx_tx_account ON transactions(account_id);
CREATE INDEX idx_tx_symbol ON transactions(symbol);
CREATE INDEX idx_tx_datetime ON transactions(datetime);
```

### FIFO Position Calculation

**Critical Algorithm** (`backend/portfolios.py`):
```python
# Positions calculated from transactions using FIFO (First-In-First-Out)
# BUY: Add to lots queue
# SELL: Consume lots from front of queue
# Realized P&L = (sell_price - buy_price) * qty per consumed lot
```

**Example Flow**:
1. BUY 100 TSLA @ $250 → Lot: [100 @ $250]
2. BUY 50 TSLA @ $260 → Lots: [100 @ $250, 50 @ $260]
3. SELL 120 TSLA @ $270 → Consume 100 @ $250 + 20 @ $260
4. Realized P&L: (270-250)*100 + (270-260)*20 = $2200
5. Remaining: [30 @ $260]

### Storage Strategy

- **Development**: Redis with `FM_FORCE_FALLBACK=1` → In-memory `AsyncTTLDict`
- **Testing**: `TEST_MODE=1` → Shared in-memory instance
- **Production**: Redis cluster with MongoDB backup for audit trail
- **Failover**: Automatic fallback to in-memory if Redis unavailable

## �🔑 Critical Developer Knowledge

### 1. Options Strategy Engine

**Builder System** (`backend/services/builder_engine.py`):
- Supports 54+ options strategies (calls, puts, spreads, condors, butterflies, iron condors)
- Multi-leg position construction with Greeks calculation (Delta, Gamma, Theta, Vega)
- Pricing endpoint: `POST /api/builder/price` accepts legs array with strike/expiration/type
- Quality scoring: `backend/services/quality.py` evaluates spread quality, risk metrics

**Frontend Builder** (`frontend/src/pages/BuilderPage.jsx`):
- Debounced pricing updates (500ms) to avoid API spam
- Interactive P&L charts via Plotly.js
- Strike rail visualization component (StrikeRailPro)
- Historical backtesting via `POST /api/builder/historical`

### 2. External API Integration Patterns

**TradeStation OAuth Flow**:
```python
# backend/tradestation_auth.py or app/routers/tradestation_auth.py
# Robust token management with refresh logic
# Environment: TS_CLIENT_ID, TS_CLIENT_SECRET, TS_REDIRECT_URI
# Modes: SIMULATION (sim-api.tradestation.com) vs LIVE (api.tradestation.com)

# OAuth Callback endpoints:
# Primary: /api/oauth/tradestation/callback (app/routers/oauth.py)
# Legacy: /api/ts/callback (app/routers/tradestation_auth.py)

# IMPORTANT: Callback URLs must be configured in TradeStation Developer Portal
# SIMULATOR: HTTP allowed (e.g., http://localhost:8000/api/oauth/tradestation/callback)
# LIVE: HTTPS required (e.g., https://flowmind.com/api/oauth/tradestation/callback)
```

**Unusual Whales Service** (`backend/unusual_whales_service.py`):
- **Plan:** API - Advanced ($375/month) - Token: `5809ee6a-bcb6-48ce-a16d-9f3bd634fd50`
- **Auth:** `Authorization: Bearer {token}` header (NOT query param)
- **Base URL:** `https://api.unusualwhales.com/api`
- **Rate limiting:** 1.0s delay between requests (graceful degradation)

**VERIFIED Working Endpoints** (October 21, 2025):
```python
# Options Chain (500+ contracts with volume, OI, IV, premiums)
GET /stock/{ticker}/option-contracts
# Use case: Replace TradeStation options chain

# Gamma Exposure (345+ GEX records with gamma/charm/vanna)
GET /stock/{ticker}/spot-exposures
# Use case: Direct GEX data - no calculation needed

# Stock Info (company metadata, earnings, sector)
GET /stock/{ticker}/info

# Market Alerts (real-time tide events, premium flows)
GET /alerts
# Filter by noti_type: "market_tide"

# Greeks (Delta, Gamma, Theta, Vega)
GET /stock/{ticker}/greeks
```

**Endpoints that DON'T work** (404 errors - likely Enterprise-only):
- ❌ `/api/flow-alerts` → Use `/alerts` instead
- ❌ `/api/stock/{ticker}/last-state` → Use `/option-contracts` for pricing
- ❌ `/api/market/tide` → Use `/alerts?noti_type=market_tide` instead

**Critical:** See `UW_API_ADVANCED_PLAN_WORKING_ENDPOINTS.md` for complete documentation

### 3. Testing Philosophy

**Root-level test files** (`*_test.py`): Integration tests against deployed backend
- Pattern: `BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "https://...")`
- Tests verify **real API responses**, not mocks
- Common test flow: Make request → Verify status → Check structure → Validate data

**Backend unit tests** (`backend/tests/`): Pytest-based with fixtures
- In-memory fallback mode: Set `TEST_MODE=1` env var for shared `AsyncTTLDict` instance
- Redis cache tests: `test_backtest_cache.py` uses shared `_test_kv_instance`

### 4. Quality Gates & Pre-commit

**GitLab CI Pipeline** (`.gitlab-ci.yml`):
- **Frontend**: ESLint, build, `npm audit --audit-level=high`
- **Backend**: ruff (lint), mypy (types), bandit (security), pip-audit, pytest
- **SAST**: GitLab security templates (dependency scanning, container scanning)
- **Strictness**: Zero tolerance on high-severity issues (`SEC_MAX_CRITICAL=0`)

**Local Pre-commit Hooks**:
```bash
cd backend && pre-commit install
cd frontend && npx husky install

# Run manually:
cd backend && pre-commit run --all-files
cd frontend && npm run lint
bandit -ll -r . && pip-audit --strict            # Security
```

**Frontend**:
```bash
cd frontend
npm run lint                                      # ESLint
npm run build                                     # Production build
npm audit --audit-level=high                     # Dependency audit
```

**Integration Tests** (from root):
```bash
python backend_test.py           # Full backend API test suite
python options_backend_test.py   # Options-specific tests
python tradestation_integration_test.py  # TradeStation OAuth flow
```

## 🎨 Code Conventions

### API Response Structure

**Standard Success**:
```json
{"status": "success", "data": {...}}
```

**Error Handling**:
```python
raise HTTPException(status_code=400, detail="Descriptive error message")
```

### Router Organization

- Use `APIRouter` with prefix and tags: `router = APIRouter(prefix="/api/options", tags=["options"])`
- Mount routers in `server.py` with `/api` prefix
- Health checks at top-level: `/health`, `/healthz`, `/readyz`

### Frontend State Management

- **Zustand stores** (`frontend/src/stores/`): Global state (user, portfolios)
- **React hooks** for local state
- **SWR** (`swr` package) for data fetching with caching

## 📚 Key Files to Reference

- **Architecture docs**: `FlowMind_Options_Module_Blueprint.md`, `PLATFORM_GUIDE.md`
- **Security/CI**: `ENTERPRISE_SECURITY_GATES.md`, `QUALITY_GATES.md`, `.gitlab-ci.yml`
- **API documentation**: `TRADESTATION_SETUP_GUIDE.md`, `UW_API_PRO_TIER_DOCUMENTATION.md`
- **Development guidelines**: `DEVELOPMENT_GUIDELINES.md` (Romanian - iterative workflow rules)

## 🔄 When Making Changes

1. **Backend API changes**: Update corresponding integration test in `*_test.py`
2. **New dependencies**: Update `requirements.txt` (backend) or `package.json` (frontend), run audits
3. **External API integration**: Add client in `integrations/`, follow `ts_client.py` pattern
4. **New routes**: Add router in `routers/`, mount in `server.py`, add health check
5. **Frontend features**: Follow page-based organization (`pages/`), use existing API patterns

## � API Endpoints Reference

### Builder Endpoints (`/api/builder`)

**POST /api/builder/price** - Calculate strategy pricing & Greeks
```json
Request:
{
  "symbol": "TSLA",
  "expiry": "2025-02-21",
  "legs": [
    {"type": "CALL", "strike": 250, "side": "BUY", "qty": 1}
  ],
  "spot": 250.0,
  "iv_mult": 1.0,
  "range_pct": 0.15,
  "dte": 30
}

Response:
{
  "maxProfit": 5000.0,
  "maxLoss": -250.0,
  "breakevens": [252.5],
  "greeks": {
    "delta": 0.55,
    "gamma": 0.03,
    "theta": -0.15,
    "vega": 0.25
  },
  "pnlData": [[240, -250], [250, 0], [260, 750], ...],
  "quality": {
    "score": 75,
    "buckets": {"spread": 0.1, "liquidity": 0.8},
    "flags": ["tight_spread", "good_liquidity"]
  }
}
```

**POST /api/builder/historical** - Backtest strategy over time
```json
Request:
{
  "legs": [{"type": "CALL", "strike": 250, "side": "BUY", "qty": 1}],
  "symbol": "TSLA",
  "daysBack": 365
}

Response:
{
  "dates": ["2024-10-13", "2024-10-14", ...],
  "pnl": [125.50, 150.75, ...],
  "spot_prices": [248.5, 252.0, ...]
}
```

### Options Endpoints (`/api/options`)

**GET /api/options/chain?symbol=TSLA&expiry=2025-11-15** - Options chain data
```json
Response:
{
  "symbol": "TSLA",
  "spot": 250.5,
  "expirations": ["2025-11-15", "2025-11-22", ...],
  "strikes": [
    {
      "strike": 250,
      "calls": {"bid": 5.20, "ask": 5.40, "mid": 5.30, "iv": 0.42, "oi": 2500, "volume": 850},
      "puts": {"bid": 4.80, "ask": 5.00, "mid": 4.90, "iv": 0.45, "oi": 3200, "volume": 650}
    },
    ...
  ]
}
```
- Fallback to demo data if TradeStation unavailable
- Use `dev=1` query param to force demo mode
- Demo data: 13 strikes (ATM ±6 × $5 steps)

**GET /api/options/expirations?symbol=TSLA** - Available expiration dates
```json
Response:
{
  "expirations": [
    "2025-10-20",
    "2025-10-27",
    "2025-11-03",
    ...
  ]
}
```

**GET /api/options/gex?symbol=TSLA&dte=30** - Gamma Exposure calculation
```json
Response:
{
  "symbol": "TSLA",
  "total_gex": 125000000,
  "call_gex": 85000000,
  "put_gex": 40000000,
  "strikes": [
    {"strike": 240, "gex": 5000000, "oi": 15000},
    {"strike": 250, "gex": 25000000, "oi": 35000},
    ...
  ],
  "zero_gamma_level": 248.5
}
```
- Alternative: Use `expiry=2025-11-15` instead of `dte`

**GET /api/options/spot/TSLA** - Current stock price
```json
Response:
{
  "symbol": "TSLA",
  "price": 250.75,
  "timestamp": "2025-10-13T14:30:00Z",
  "source": "TradeStation"
}
```

**GET /api/options/provider/status** - Check data provider health
```json
Response:
{
  "provider": "TradeStation",
  "status": "connected",
  "mode": "live",
  "last_update": "2025-10-13T14:30:00Z"
}
```

### Flow Endpoints (`/api/flow`)

**GET /api/flow/summary?limit=24&minPremium=25000** - Options flow summary
```json
Response:
{
  "timestamp": "2025-10-13T14:30:00Z",
  "items": [
    {
      "symbol": "TSLA",
      "bull_premium": 450000,
      "bear_premium": 280000,
      "net_premium": 170000,
      "trades": 15,
      "sweeps_pct": 0.42,
      "blocks_pct": 0.18
    },
    ...
  ],
  "source": "UnusualWhales"
}
```
- Default `limit=24`, `minPremium=25000`
- Graceful fallback to demo data if UW API fails

**GET /api/flow/live?symbol=TSLA&minPremium=25000** - Live options flow
```json
Response:
{
  "symbol": "TSLA",
  "rows": [
    {
      "timestamp": "2025-10-13T14:28:45Z",
      "strike": 250,
      "expiry": "2025-11-15",
      "kind": "CALL",
      "side": "BUY",
      "quantity": 500,
      "price": 5.30,
      "premium": 265000,
      "is_sweep": true,
      "builder_link": "/builder?symbol=TSLA&strike=250&expiry=2025-11-15&type=call"
    },
    ...
  ]
}
```
- Real-time if `UW_LIVE=1` env var set
- Includes deep-links to Builder for one-click strategy creation
- Falls back to demo data for testing

**GET /api/flow/historical?symbol=TSLA&days=7** - Historical flow data
```json
Response:
{
  "symbol": "TSLA",
  "start_date": "2025-10-06",
  "end_date": "2025-10-13",
  "daily_summary": [
    {
      "date": "2025-10-13",
      "total_premium": 5250000,
      "bull_premium": 3200000,
      "bear_premium": 2050000,
      "trade_count": 142
    },
    ...
  ]
}
```
- Use `days=7` for lookback or `start`/`end` (ISO format)

**GET /api/flow/news?symbol=TSLA** - Market news
**GET /api/flow/congress?symbol=TSLA** - Congress trades
**GET /api/flow/insiders?symbol=TSLA** - Insider activity
```json
Response (news example):
{
  "symbol": "TSLA",
  "items": [
    {
      "timestamp": "2025-10-13T12:00:00Z",
      "headline": "Tesla Q3 Earnings Beat Estimates",
      "source": "Bloomberg",
      "sentiment": "positive",
      "url": "https://..."
    },
    ...
  ]
}
```
- All use Unusual Whales API
- Optional `symbol` filter (omit for all symbols)

### Optimize Endpoints (`/api/optimize`)

**GET /api/optimize/suggest?symbol=TSLA&sentiment=bullish&dte=30** - Strategy recommendations
```
Params:
- symbol: Stock ticker
- sentiment: bullish/bearish/neutral
- target_price: Optional price target
- budget: Max capital (USD)
- dte: Days to expiration
- risk_bias: 0 (balanced), negative (conservative), positive (aggressive)
```
```json
Response:
{
  "symbol": "TSLA",
  "current_price": 250.5,
  "sentiment": "bullish",
  "recommendations": [
    {
      "strategy_name": "Bull Call Spread",
      "strategy_id": "bull-call-spread",
      "legs": [
        {"type": "CALL", "strike": 250, "side": "BUY", "qty": 1},
        {"type": "CALL", "strike": 270, "side": "SELL", "qty": 1}
      ],
      "expected_return": 0.45,
      "max_risk": 500,
      "max_profit": 1500,
      "probability_profit": 0.62,
      "capital_required": 500
    },
    ...
  ]
}
```

### Portfolio Endpoints (`/api/portfolios`)

**GET /api/portfolios** - List all portfolios
**POST /api/portfolios** - Create portfolio
**GET /api/portfolios/{id}** - Get portfolio details
**PATCH /api/portfolios/{id}** - Update portfolio
**DELETE /api/portfolios/{id}** - Delete portfolio

MongoDB-backed, includes positions and performance tracking.

### Health Endpoints

**GET /health** - Basic health check
**GET /healthz** - Kubernetes-style health
**GET /readyz** - Readiness probe (checks dependencies)

## �💡 Pro Tips

- **Debugging API calls**: Check `backend/server.py` startup logs for integration client status
- **Mock data fallback**: Most services gracefully return demo data on API failures
- **Performance**: Use Redis for production, in-memory for dev/test (via `FM_FORCE_FALLBACK`)
- **Options pricing**: Black-Scholes implementation in `backend/services/bs.py` (if exists) or strategy engine
- **Chart issues**: Frontend BuilderPage debounces pricing at 500ms, increase if API slow
- **Testing endpoints**: All integration tests in root `*_test.py` files use `REACT_APP_BACKEND_URL` env var
