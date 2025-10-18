
## FlowMind AI Agent Quick Reference

### Project Overview
FlowMind is an options analytics platform (FastAPI backend, React frontend, MongoDB/Redis storage) for strategy building, real-time flow, and portfolio management. All code is dark-theme only.

### Architecture
- **Backend:** FastAPI (`backend/`), modular routers (`routers/`), business logic in `services/`, integrations in `integrations/`, AI in `*_agent.py`.
- **Frontend:** React (monolith `App.js`), feature pages in `pages/`, state in `stores/` (Zustand), API hooks in `api/`.
- **Data:** Redis (primary, fallback to in-memory), MongoDB (portfolios), SQLite (alt).
- **External APIs:** TradeStation (OAuth, options/spot), Unusual Whales (flow/news/congress, rate-limited, fallback to demo).

### Key Patterns & Conventions
- **STRICT: Dark theme only:** All UI uses hardcoded Tailwind dark classes (see `DARK_THEME_ONLY_VALIDATION.md`). NO theme toggles, NO light mode, ONLY dark theme.
- **CRITICAL: Python 3.12 Indent Compliance (Oct 18, 2025):**
  - **FIXED:** All 16 backend/services/*.py files now use proper 4-space indentation per Python 3.12 requirements
  - **Context:** Legacy 1-space indent caused IndentationError across entire backend/services/ directory
  - **Solution:** Manual fix via replace_string_in_file (3,525 lines fixed across 16 files, one-by-one)
  - **Files fixed:** bs.py, builder_engine.py, quality.py, optimize_engine.py, cache_decorators.py, calendar_backtest.py, historical_engine.py, options_gex.py, options_provider.py, ts_oauth.py, uw_flow.py, warmup.py, ws_connection_manager.py, providers/__init__.py, providers/ts_provider.py, providers/uw_provider.py
  - **Verification:** All files pass `python -m py_compile` and backend starts without ImportError
  - **Commits:** 16 individual commits in PR #4 (chore/build-only-checks-clean branch)
  - **Lesson learned:** Automated indent fixers (black, autopep8, brutal_reindent.py) cannot parse invalid syntax - manual fix required for cascading errors
  - **When encountering indent errors:** Use manual replace_string_in_file with 3-5 line context windows, fix section-by-section, verify with py_compile after each section
- **CRITICAL: ZERO EMOJI/ICONS POLICY - NEVER SHOW EMOJI IN UI:** 
  - **ABSOLUTELY FORBIDDEN** to add emojis, icons, or visual decorations in ANY user-facing UI/code
  - **DO NOT display emoji in responses** - Owner does not want to see emoji anywhere
  - Entire codebase is emoji-free (11,176 emoji removed on Oct 16, 2025)
  - This includes: 💰 💵 📊 ⚡ 🔌 📭 📦 📋 📤 🔍 🟢 🟡 🔴 and ALL other emoji
  - Violations will be rejected in code review
  - See `EMOJI_ELIMINATION_COMPLETE.md` for enforcement details
  - **When communicating with owner: Use plain text only, NO emoji in messages**
- **CRITICAL: NEVER use localhost links or Simple Browser**:
  - **DO NOT** attempt to open localhost URLs for user (http://localhost:3000, etc.)
  - **DO NOT** use `open_simple_browser` tool - it does not work in this environment
  - **Instead**: Provide direct file paths or instruct user to open files manually in their browser
  - User cannot access localhost links from AI responses
- **CRITICAL: Sidebar Section Completion Marking System:**
  - **Purpose:** Visual indicator system to track completed/finalized sidebar sections
  - **When section is FULLY COMPLETE and requires NO further changes:**
    - Mark section header with CYAN color: `text-cyan-400`
    - Apply to section title in `frontend/src/lib/nav.simple.js`
    - Example: `title: "Options Data"` gets cyan when all subsections finalized
  - **Default state:** Sections remain default color `text-[#94a3b8]` until explicitly marked complete
  - **Completion criteria:** All items working, all routes implemented, all subsections organized
  - **Benefits:** Quick visual scan to see what's done vs. needs work, prevents re-editing completed sections
  - **Implementation:** In SidebarSimple.jsx section header, add conditional: `${sec.isComplete ? 'text-cyan-400' : 'text-[#94a3b8]'}`
  - **Tracking:** Maintain list in this file of completed sections with completion date
  - **Example workflow:** 
    1. Build section fully (all routes, components, logic)
    2. Test all functionality
    3. Mark `isComplete: true` in nav config
    4. Section header turns cyan
    5. Do not modify unless critical bug
- **STRICT: Typography standard (DIFFERENTIATED):**
  - **Pages (content):** 9px/14.4px/500 (font-medium) - `text-[9px] leading-[14.4px] font-medium`
  - **Sidebar (navigation):** 13px/20.8px/500 (font-medium) - `text-[13px] leading-[20.8px] font-medium`
  - **Font family:** `Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial`
  - **Section headers:** font-semibold (600 weight)
  - **Text color:** rgb(252, 251, 255)
- **API:** All endpoints under `/api`. Use `APIRouter` with tags. Health: `/health`, `/healthz`, `/readyz`, `/api/health/redis`.
- **Request Validation:** Use Pydantic models from `backend/models/requests.py` (15+ models with custom validators).
- **Caching:** Use `backend/services/cache_decorators.py` for endpoint caching. Redis fallback via `redis_fallback.py` (`FM_FORCE_FALLBACK=1`).
- **WebSocket Streaming:** Real-time data via `backend/integrations/uw_websocket_client.py` with REST fallback.
- **Testing:** Root `*_test.py` files run integration tests against real backend. Use `TEST_MODE=1` for in-memory cache. Pytest for unit tests in `backend/tests/`.
- **Security:** Use `secrets` module (not `random`) for demo data generation. CWE-330 compliance enforced.
- **Emoji/Icons Policy (CRITICAL):**
  - **FORBIDDEN:** Never add emoji, icons, or decorative symbols without owner approval
  - **Rationale:** Professional UI, consistent branding, accessibility
  - **Enforcement:** CI/CD pipeline checks for emoji in code (see `.gitlab-ci.yml`)
  - **Exceptions:** Only documentation files that describe emoji removal process
  - **History:** 11,176 emoji removed across 529 files on October 16, 2025
- **Naming:**
  - Services: `*_service.py` (e.g. `unusual_whales_service.py`)
  - Routers: `routers/*.py` (feature-based)
  - Agents: `*_agent.py` (AI/ML)
  - Tests: `*_test.py` (integration), `test_*.py` (unit)
- **Frontend API:** Use `REACT_APP_BACKEND_URL` env var, never hardcode URLs.
- **Portfolio logic:** FIFO position calc in `backend/portfolios.py` (see docstring for algorithm).

### Developer Workflows
- **Backend:**
  - Run: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
  - Test: `pytest -q --maxfail=1 --disable-warnings`
  - Lint: `ruff check . && mypy . --ignore-missing-imports && bandit -ll -r . && pip-audit --strict`
- **Frontend:**
  - Run: `cd frontend && npm start`
  - Lint: `npm run lint`
  - Build: `npm run build`
- **Full stack:** `docker-compose up` (backend:8000, redis:6379)
- **CI:** See `.gitlab-ci.yml` for strict gates (no high-severity allowed).

### Integration & Data Flow
- **Options chain:** `/api/options/chain?symbol=...` (TradeStation, fallback demo)
- **Flow summary:** `/api/flow/summary` (Unusual Whales, fallback demo)
- **Builder pricing:** `/api/builder/price` (multi-leg, Greeks, quality)
- **Portfolio:** `/api/portfolios` (MongoDB, Redis, FIFO logic)
- **Caching:** TTL-based, keys like `chain:{symbol}:{expiry}`

### Common Pitfalls
- **CRITICAL: Always use dark theme classes (no toggles, no light mode, ONLY dark)**
- **CRITICAL: Never add icons/emojis unless explicitly requested by user**
- Redis may fallback to in-memory; always check `FM_FORCE_FALLBACK`
- TradeStation tokens expire; refresh logic in `tradestation_auth.py`
- Unusual Whales API is rate-limited; fallback to demo on error
- All integration tests use real backend, not mocks

### Key Files
- `backend/services/builder_engine.py` (strategy engine)
- `backend/services/quality.py` (spread scoring)
- `backend/redis_fallback.py` (cache logic)
- `backend/portfolios.py` (FIFO positions)
- `backend/models/requests.py` (Pydantic validation models)
- `backend/integrations/uw_websocket_client.py` (WebSocket streaming)
- `backend/performance_health_test.py` (load testing suite)
- `frontend/src/pages/BuilderPage.jsx` (main builder UI)
- `DARK_THEME_ONLY_VALIDATION.md`, `PLATFORM_GUIDE.md`, `FlowMind_Options_Module_Blueprint.md` (docs)

---
For more, see architecture diagrams and endpoint examples in this file, or reference the above docs. When in doubt, prefer existing patterns and check for fallback/demo logic in all integrations.

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
```

**Unusual Whales Service** (`backend/unusual_whales_service.py`):
- Rate limiting: 1.0s delay between requests (`self.rate_limit_delay`)
- Endpoints: `/api/flow/summary`, `/api/flow/live`, `/api/flow/historical`
- Error handling: Returns mock data on API failures (graceful degradation)

### 3. Testing Philosophy

**Root-level test files** (`*_test.py`): Integration tests against deployed backend
- Pattern: `BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "https://...")`
- Tests verify **real API responses**, not mocks
- Common test flow: Make request → Verify status → Check structure → Validate data

**Backend unit tests** (`backend/tests/`): Pytest-based with fixtures
- In-memory fallback mode: Set `TEST_MODE=1` env var for shared `AsyncTTLDict` instance
- Redis cache tests: `test_backtest_cache.py` uses shared `_test_kv_instance`

### 4. Environment Configuration

**Critical Env Vars**:
```bash
# Backend (backend/.env)
MONGO_URL=mongodb://...                    # Required for portfolio/monitor storage
TS_CLIENT_ID=...                          # TradeStation OAuth
TS_CLIENT_SECRET=...
TS_REDIRECT_URI=...
UW_API_TOKEN=... or UNUSUAL_WHALES_API_KEY=...  # Unusual Whales
REDIS_URL=redis://localhost:6379/0        # Optional with fallback
FM_FORCE_FALLBACK=1                       # Force in-memory cache
FM_REDIS_REQUIRED=1                       # Fail if Redis unavailable

# Frontend (frontend/.env.local)
REACT_APP_BACKEND_URL=http://localhost:8000  # API base URL
```

### 5. Caching Strategy

**Redis Fallback Pattern** (`backend/redis_fallback.py`):
```python
async def get_kv():
    if os.getenv("FM_FORCE_FALLBACK") == "1":
        return AsyncTTLDict()  # In-memory store
    # Try Redis, fallback to in-memory if connection fails
```
Used in: Backtest cache (`bt_cache_integration.py`), IV service (`iv_service/ts_client.py`)

## 🛠️ Development Workflows

### Running Locally

**Backend**:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
# Or: python -m uvicorn server:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
npm start  # Uses craco for extended config
# Or: yarn start
```

**Docker Compose** (full stack):
```bash
docker-compose up  # Backend on :8000, Redis on :6379
```

### Quality Gates (CI/CD)

**GitLab CI Pipeline** (`.gitlab-ci.yml`):
- **Frontend**: ESLint, build, `npm audit --audit-level=high`
- **Backend**: ruff (lint), mypy (types), bandit (security), pip-audit, pytest
- **SAST**: GitLab security templates (dependency scanning, container scanning)
- **Strictness**: Zero tolerance on high-severity issues (`SEC_MAX_CRITICAL=0`)

**Local Pre-commit** (`.pre-commit-config.yaml`):
```bash
cd backend && pre-commit install
cd frontend && npx husky install
```

### Testing Commands

**Backend**:
```bash
cd backend
pytest -q --maxfail=1 --disable-warnings          # Unit tests
ruff check . && mypy . --ignore-missing-imports  # Linting + types
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
python performance_health_test.py        # Load testing & health endpoints
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

### Naming Patterns

- **Services**: `*_service.py` (e.g., `unusual_whales_service.py`, `portfolio_service.py`)
- **Agents**: `*_agent.py` (AI/ML components: `investment_scoring_agent.py`)
- **Routers**: `routers/*.py` (feature-based: `options.py`, `flow.py`, `builder.py`)
- **Tests**: `*_test.py` (root-level integration), `test_*.py` (backend/tests/ unit)

## 🚨 Common Pitfalls

1. **API URL confusion**: Frontend uses `REACT_APP_BACKEND_URL` env var, not hardcoded URLs
2. **Redis dependency**: Always handle Redis connection failures gracefully via `redis_fallback.py`
3. **TradeStation token expiry**: Refresh tokens automatically in `tradestation_auth.py` (60-day expiry)
4. **Unusual Whales rate limits**: Respect `rate_limit_delay` in `UnusualWhalesService`
5. **Options chain data format**: TradeStation returns nested `expirations` array, handle empty chains
6. **Test mode conflicts**: Use `TEST_MODE=1` for shared cache instance in tests

## 📚 Key Files to Reference

- **Architecture docs**: `FlowMind_Options_Module_Blueprint.md`, `PLATFORM_GUIDE.md`
- **Security/CI**: `ENTERPRISE_SECURITY_GATES.md`, `QUALITY_GATES.md`, `.gitlab-ci.yml`
- **API documentation**: `TRADESTATION_SETUP_GUIDE.md`, `UW_API_PRO_TIER_DOCUMENTATION.md`
- **Development guidelines**: `DEVELOPMENT_GUIDELINES.md` (Romanian - iterative workflow rules)

## 🔄 When Making Changes

1. **Backend API changes**: Update corresponding integration test in `*_test.py`
2. **New dependencies**: Update `requirements.txt` (backend) or `package.json` (frontend), run audits
3. **External API integration**: Add client in `integrations/`, follow `uw_websocket_client.py` pattern
4. **New routes**: Add router in `routers/`, mount in `server.py`, add health check
5. **Frontend features**: Follow page-based organization (`pages/`), use existing API patterns
6. **Request models**: Add Pydantic models to `backend/models/requests.py` with validators
7. **Streaming features**: Use WebSocket with REST fallback pattern from `uw_websocket_client.py`
8. **Security**: Replace any `random` usage with `secrets` module for demo data generation

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
**GET /api/health/redis** - Redis cache health monitoring
```json
Response:
{
  "status": "healthy",
  "cache_mode": "Redis",
  "connection": "connected",
  "keys_count": 125,
  "memory_usage": "2.4MB",
  "response_time_ms": 1.5
}
```

## 💡 Pro Tips

- **Debugging API calls**: Check `backend/server.py` startup logs for integration client status
- **Mock data fallback**: Most services gracefully return demo data on API failures
- **Performance**: Use Redis for production, in-memory for dev/test (via `FM_FORCE_FALLBACK`)
- **Options pricing**: Black-Scholes implementation in `backend/services/bs.py` (if exists) or strategy engine
- **Chart issues**: Frontend BuilderPage debounces pricing at 500ms, increase if API slow
- **Testing endpoints**: All integration tests in root `*_test.py` files use `REACT_APP_BACKEND_URL` env var
- **WebSocket streaming**: Real-time feeds with automatic REST fallback on connection issues
- **Request validation**: Use Pydantic models from `backend/models/requests.py` for type safety
- **Health monitoring**: Use `/api/health/redis` for production monitoring and capacity planning
- **Security**: Always use `secrets` module for demo data, never `random` (CWE-330 compliance)
