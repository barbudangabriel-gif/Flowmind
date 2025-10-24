# FlowMind AI Agent Instructions

**Project:** Options analytics platform with FastAPI backend, React 19 frontend  
**Last Updated:** October 24, 2025

---

## 📋 Table of Contents
1. [Session Start Protocol](#session-start-protocol)
2. [Architecture Patterns](#architecture-patterns)
3. [BuilderV2 Page - Build Tab](#builderv2-page---build-tab)
4. [Strategy Engine Proposal](#strategy-engine-proposal)
5. [Developer Workflows](#developer-workflows)
6. [External APIs](#external-apis)
7. [Common Pitfalls](#common-pitfalls)
8. [Key Files](#key-files)

---

## Session Start Protocol

### MANDATORY: Every New Session
1. **Read `PROJECT_TASKS.md`** - Get active/backlog tasks
2. **Display task list** - Show priorities, status, time estimates
3. **Wait for user** - Let user choose which task to work on
4. **Track progress** - Update checkboxes as work progresses

### MANDATORY: Before UI Implementation
1. **Clarify requirements** - Ask about sections/tabs/components needed
2. **Propose structure** - Show what goes where
3. **Wait for confirmation** - Get explicit "da"/"yes"
4. **Document structure** - Add comment at top of file
5. **Never implement without approval** - Lesson learned: BuilderV2Page (Oct 22) required 228-line deletion due to no upfront agreement

### Development Style (Romanian workflow)
- **Concis + vizual**: Arată implementarea, nu doar explica
- **Iterativ**: Livrează mic → verifică → ajustează
- **Transparent**: Raportează probleme imediat
- **Feedback-driven**: Corectează după fiecare ciclu
- **Autonom**: Mergi înainte fără confirmări inutile

---

## Architecture Patterns

### Project Structure
- **Backend:** FastAPI (`backend/server.py`), routers in `backend/routers/` + `backend/app/routers/`
- **Frontend:** React 19 (`frontend/src/App.js`), pages in `pages/`, Zustand stores, Craco build
- **Storage:** Redis primary (TTL cache), fallback to in-memory, MongoDB for mindfolios
- **External APIs:** TradeStation (OAuth, options chains), Unusual Whales (flow, 17 verified endpoints)

### 1. Redis Fallback System (`backend/redis_fallback.py`)
Zero-downtime caching - app continues if Redis unavailable.
```python
# Three modes:
# TEST_MODE=1 → Shared AsyncTTLDict (test consistency)
# FM_FORCE_FALLBACK=1 → Force in-memory (dev)
# Normal → Try Redis, fallback to in-memory on failure

await get_kv()  # Returns Redis OR AsyncTTLDict
```
**CRITICAL:** Always use `from redis_fallback import get_kv`, NEVER import Redis directly.

### 2. FIFO Position Tracking (`backend/mindfolios.py`)
Tax-compliant realized P&L for options/stock positions.
```python
# BUY adds to lots queue, SELL consumes from front (First-In-First-Out)
# Example: BUY 100@250 + BUY 50@260 → SELL 120@270
# Consumes: 100@250 + 20@260 → Realized $2,200, Remaining 30@260
```
**Functions:** `calculate_positions()`, `get_mindfolio_transactions()`  
**NEVER modify positions directly** - always add transactions and recompute.

### 3. Dark Theme Enforcement
No light mode support (removed to simplify codebase).
```javascript
// frontend/src/App.js - ThemeProvider always isDarkMode: true
useEffect(() => { document.documentElement.classList.add('dark'); }, []);
```
**Rule:** All Tailwind classes MUST be dark variants (`bg-slate-800`, `text-white`)  
**NEVER use:** `isDarkMode ?` ternaries or light classes (`bg-white`, `text-gray-800`)

### 4. Python 3.12 Indentation Rules
**CRITICAL:** Project recently fixed 5,314 lines across 12 files for Python 3.12 compliance.
- **Standard:** 4-space indentation (enforced by Black, Ruff)
- **VS Code:** Must have `"editor.detectIndentation": false` (configured in `.vscode/settings.json`)
- **Pre-commit:** Black + Ruff hooks block non-compliant commits
- **Never use:** 1-space, 2-space, or tabs

### 5. Unusual Whales API Integration
**CRITICAL ANTI-HALLUCINATION GUARD:** AI models frequently generate fake UW endpoints!

#### ✅ VERIFIED ENDPOINTS (17 total - Oct 21, 2025)

**Stock Options Data (5 endpoints):**
```python
GET /stock/{ticker}/option-contracts   # 500+ contracts with IV, OI, volume
GET /stock/{ticker}/spot-exposures     # 300-410 GEX records (PRE-CALCULATED!)
GET /stock/{ticker}/greeks             # Delta, Gamma, Theta, Vega
GET /stock/{ticker}/options-volume     # Volume metrics, call/put ratios
GET /stock/{ticker}/info               # Company metadata, sector, earnings
```

**Market Screening & Alerts (2 endpoints):**
```python
GET /screener/stocks?limit=10          # Unified GEX+IV+Greeks (POWERFUL!)
GET /alerts?noti_type=market_tide      # Real-time market tide events
```

**Insider Trading (5 endpoints):**
```python
GET /insider/trades                    # All insider trades
GET /insider/{ticker}                  # Ticker-specific insider activity
GET /insider/recent                    # Recent insider trades
GET /insider/buys                      # Insider buys only
GET /insider/sells                     # Insider sells only
```

**Dark Pool (2 endpoints):**
```python
GET /darkpool/{ticker}                 # 500 dark pool trades per ticker!
GET /darkpool/recent                   # Recent dark pool activity
```

**Earnings (3 endpoints):**
```python
GET /earnings/{ticker}                 # Earnings history
GET /earnings/today                    # Today's earnings
GET /earnings/week                     # This week's earnings
```

#### ❌ HALLUCINATED ENDPOINTS (DO NOT USE - 404 errors)
```python
❌ /api/flow-alerts, /api/market/tide, /api/options-flow
❌ /api/market/overview, /api/congress/trades
❌ /api/stock/{ticker}/last-state, /api/stock/{ticker}/ohlc
```

#### Implementation Details
- **Service:** `backend/unusual_whales_service_clean.py` (17 methods implemented)
- **Documentation:** `UW_API_FINAL_17_ENDPOINTS.md` (complete reference with examples)
- **Auth:** `Authorization: Bearer {token}` header (NOT query param)
- **Rate limit:** 1.0s delay between requests
- **Discovery:** 150+ endpoint variations tested, 8 tickers validated

---

## BuilderV2 Page - Build Tab

### Overview (Oct 24, 2025)
**Status:** ✅ Complete interactive P&L chart with optimized layout  
**File:** `frontend/src/pages/BuilderV2Page.jsx` (1538 lines)  
**Purpose:** Unified builder interface with Build/Optimize/Strategy/Flow tabs

### Build Tab - Interactive P&L Chart
Full-width SVG chart (1000x400px responsive) for Long Call strategy visualization.

**Chart Specifications:**
- **Dimensions:** viewBox="0 0 1000 400", preserveAspectRatio="none"
- **Price Range:** $100-$330 (230 points, extended loss zone)
- **P&L Range:** -$5,000 to $12,000 (smoother profit angle)
- **Padding:** { top: 20, right: 1, bottom: 40, left: 70 }
- **Colors:** Profit (cyan #06b6d4), Loss (red #dc2626), gradients 0.85 opacity

**Features:**
✅ Real-time mouse tracking with coordinate transformation  
✅ Tooltip follows P&L curve with dynamic positioning  
✅ Price label at top margin, P&L value with colored dot on curve  
✅ Vertical white line tracking mouse X position  
✅ Current price line (white dashed), breakeven line (cyan), chance line (orange)  
✅ Compact metrics row (Net Debit, Max Loss/Profit, Chance, Breakeven)

**Chart Optimization Techniques (Learned from Oct 24 session):**
1. **Extend loss zone:** Reduce xMin (140 → 100) to push profit curve right
2. **Smooth profit angle:** Increase yMax (7000 → 12000) for gentler slope
3. **Maximize width:** Reduce padding.right (10 → 1px) for 99% fill
4. **Raise chart area:** Reduce padding.bottom (60 → 40px) to separate from X-axis
5. **Tooltip positioning:** Use percentage-based calc: `(viewBoxX / 1000) * 100%`

**Interactive Tooltip Implementation:**
```javascript
// Mouse tracking with viewBox coordinate transformation
onMouseMove={(e) => {
  const rect = svg.getBoundingClientRect();
  const viewBoxX = (e.clientX - rect.left) * (1000 / rect.width);
  const price = xMin + ((viewBoxX - padding.left) / chartWidth) * xRange;
  const pnl = price < strike ? -premium : (price - strike) * 100 - premium;
  setTooltip({ show: true, x: e.clientX, y: e.clientY, viewBoxX, price, pnl });
}}

// Tooltip follows curve (not fixed top/bottom)
<div style={{
  left: `${(viewBoxX / 1000) * 100}%`,
  top: `${(scaleY(pnl) / 400) * 100}%`,
  transform: 'translate(10px, -50%)'
}}>
```

**Next Steps (Pending Implementation):**
- [ ] Layer system: Table, Graph, P/L, Greeks tabs with button switching
- [ ] Strategy Card → Build Tab integration (state transfer)
- [ ] Backend connection for live TradeStation options data
- [ ] Dynamic strategy switching (currently hardcoded Long Call)
- [ ] Universal Strategy Engine (see Strategy Engine Proposal section)

---

## Strategy Engine Proposal

### Problem: Manual Approach = 34,500 Lines
Building 69 strategies manually would require:
- 69 strategies × 500 lines each = **34,500 lines of code**
- Separate components for StrategyCard (360x180) and Build Tab (1000x400)
- Duplicate P&L logic, chart rendering, Greeks calculations
- Maintenance nightmare (color change = update 69 files)

**User quote:** "cum crezi ca vom reusi noi sa facem cardurile pentru toate 69 de strategii si functionalitatea de open in builder sa vina in builder cu alte dimensiuni? una cate una ca imbatranim?"

### Solution: Generative System = 2,550 Lines (93% reduction)

**Architecture:**
```
strategies.json (1500 lines)
    ↓ defines 69 strategies declaratively
StrategyEngine.js (500 lines)
    ↓ universal P&L calculator + Greeks
StrategyChart.jsx (400 lines)
    ↓ single component, card OR full size
UniversalStrategyCard.jsx (150 lines)
    ↓ reusable wrapper with "Open in Builder"
```

**Key Components:**

1. **strategies.json** - Declarative config
```json
{
  "long_call": {
    "name": "Long Call",
    "legs": [{ "type": "call", "action": "buy", "quantity": 1 }],
    "pnl_formula": {
      "below_strike": "-premium",
      "above_strike": "(price - strike) * 100 - premium"
    },
    "breakeven": "strike + (premium / 100)",
    "max_profit": "unlimited",
    "max_loss": "premium"
  }
}
```

2. **StrategyEngine.js** - Universal calculator
```javascript
class StrategyEngine {
  generatePnLCurve(priceMin, priceMax, step = 1) {
    // Parse formula from config, calculate P&L for each price
  }
  calculateGreeks(currentPrice, volatility, daysToExpiry) {
    // Black-Scholes for each leg, sum results
  }
  calculateBreakeven() {
    // Evaluate breakeven formula with variable substitution
  }
}
```

3. **StrategyChart.jsx** - Size-responsive component
```javascript
<StrategyChart 
  strategyId="long_call"
  size="card"     // 360x180 for Optimize tab
  size="full"     // 1000x400 for Build tab
/>
```

**Benefits:**
✅ Add new strategy: 30 lines JSON (not 500 lines React)  
✅ Color change: Update once, all 69 strategies inherit  
✅ Backend reusable: Same engine for API calculations  
✅ Consistent visuals: Same gradients, tooltips, animations

**Implementation Plan:** 4 phases, 4 weeks (vs. 6 months manual)  
**Full details:** See `STRATEGY_ENGINE_PROPOSAL.md`

---

## External APIs

### Unusual Whales API Integration
**Status:** ✅ 17 verified endpoints operational (Oct 21, 2025)  
**Service:** `backend/unusual_whales_service_clean.py`

**Flow Data Integration:**
- **Options Flow:** Used in BuilderV2 Flow tab for real-time flow monitoring
- **Dark Pool:** 500 trades per ticker for institutional activity tracking
- **Insider Trading:** 5 endpoints for corporate insider buys/sells
- **Market Screening:** Unified GEX+IV+Greeks for strategy discovery

### TradeStation OAuth & API Integration
**✅ COMPLETE WORKING SOLUTION (Oct 23-24, 2025)**  
**Status:** Connected and operational in LIVE mode with real accounts

#### Configuration (.env)
```bash
# OAuth Credentials
TS_CLIENT_ID=XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj
TS_CLIENT_SECRET=NsAIybzKV6GbYGqQZwF0cHypdXfwiDYL5-EY4nRXEbIy748Zp-FdeuDXJIu6Jhwk
TS_REDIRECT_URI=https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/oauth/tradestation/callback

# CRITICAL: Both variables required for mode switching
TS_MODE=LIVE
TRADESTATION_MODE=LIVE  # app/routers/tradestation.py checks this!

# API URLs (LIVE mode)
TS_BASE_URL=https://api.tradestation.com
TS_AUTH_URL=https://signin.tradestation.com/authorize
TS_TOKEN_URL=https://signin.tradestation.com/oauth/token

# Scopes (verified working)
TS_SCOPE=openid offline_access MarketData ReadAccount Trade OptionSpreads Matrix

# Token settings
TS_HTTP_TIMEOUT=15
TS_REFRESH_SKEW=60
```

#### CRITICAL: OAuth Requirements
1. **`audience` parameter REQUIRED** - Without this, API returns 401
   ```python
   # backend/app/services/tradestation.py - auth_url()
   params = {
       "response_type": "code",
       "client_id": TS_CLIENT_ID,
       "audience": "https://api.tradestation.com",  # MUST INCLUDE!
       "redirect_uri": redirect_uri,
       "scope": TS_SCOPE,
       "state": state,
   }
   ```

2. **Async token persistence** - Tokens stored in Redis/fallback cache
   ```python
   # All token functions are async:
   await set_token(user_id, token)
   token = await get_cached_token(user_id)
   token = await get_valid_token(user_id)  # Auto-refreshes if needed
   ```

3. **Mode switching** - `TRADESTATION_MODE` controls API base URL
   ```python
   # backend/app/routers/tradestation.py
   TS_MODE = os.getenv("TRADESTATION_MODE", "SIMULATION")
   if TS_MODE == "LIVE":
       TS_API_BASE = "https://api.tradestation.com/v3"
   else:
       TS_API_BASE = "https://sim-api.tradestation.com/v3"
   ```

#### OAuth Flow (LIVE mode)
1. User visits: `https://{codespace}/api/ts/login`
2. Redirects to TradeStation with `audience=https://api.tradestation.com`
3. User authenticates + 2FA
4. Callback: `https://{codespace}/api/oauth/tradestation/callback?code=...`
5. Token exchange + save to Redis
6. Success page displays (3s auto-redirect)

#### Verified Working Endpoints
```bash
# Accounts (returns LIVE or SIM based on TRADESTATION_MODE)
GET /api/tradestation/accounts
Response: {"Accounts": [{"AccountID": "11775499", "AccountType": "Margin", ...}]}

# Balances
GET /api/tradestation/accounts/{account_id}/balances
Response: {"Balances": [{"CashBalance": "...", "BuyingPower": "...", ...}]}

# Positions (real-time P&L)
GET /api/tradestation/accounts/{account_id}/positions
Response: {"Positions": [{"Symbol": "TSLA", "Quantity": 100, "UnrealizedProfitLoss": "11281.97", ...}]}

# Options Chain (NEW - Oct 24, 2025)
GET /api/tradestation/options/chains/{symbol}?strikeCount=10
Response: {"Expirations": [...], "Strikes": [...], "Calls": [...], "Puts": [...]}
```

#### Connection Status (Oct 24, 2025)
✅ **OAuth Flow:** Fully functional with 2FA authentication  
✅ **Token Persistence:** Survives backend restarts via Redis cache  
✅ **Live Accounts:** Connected to real TradeStation accounts (11775499, 210MJP11)  
✅ **Options Data:** Access to real-time options chains, strikes, premiums  
✅ **Real-time Positions:** Live P&L tracking for stocks and options  
✅ **Account Balances:** Cash balance, buying power, equity values

#### Authentication Header
All endpoints require: `X-User-ID: default` (or custom user_id)
```bash
curl -H "X-User-ID: default" http://localhost:8000/api/tradestation/accounts
```

#### SIMULATOR vs LIVE Mode
**DNS BLOCK:** `sim-signin.tradestation.com` is BLOCKED on Codespaces/some networks
- **SIMULATOR:** Returns accounts with "SIM" prefix (SIM2765178M, SIM2765179F)
- **LIVE:** Returns real account IDs (11775499, 210MJP11)
- **Switch:** Change both `TS_MODE` and `TRADESTATION_MODE` + restart backend

#### Router Mounting
```python
# backend/server.py
from app.routers.tradestation import router as ts_data_router
app.include_router(ts_data_router, prefix="/api")  # Mounts /api/tradestation/*
```

#### Token Persistence Implementation
- **Storage:** Redis (primary) → AsyncTTLDict (fallback)
- **TTL:** 60 days (max refresh token lifetime)
- **Cache key:** `ts_token:{user_id}`
- **Survives:** Backend restarts (if Redis available)

#### Common Errors & Fixes
| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Missing `audience` param | Add to auth_url() |
| DNS_PROBE_FINISHED_NXDOMAIN | sim-signin.tradestation.com blocked | Use LIVE mode |
| "Not authenticated" | TRADESTATION_MODE != TS_MODE | Set both variables |
| Token lost on restart | Not using async persistence | Await set_token/get_cached_token |
| Returns SIM accounts in LIVE | TRADESTATION_MODE=SIMULATION | Set to LIVE + restart |

---

## Common Pitfalls

1. **Redis confusion:** Always `from redis_fallback import get_kv`, never direct Redis imports
2. **Dark theme violations:** Never use `isDarkMode ?` ternaries or light classes
3. **URL hardcoding:** Frontend must use `process.env.REACT_APP_BACKEND_URL`
4. **UW API hallucinations:** Only use 17 verified endpoints in `unusual_whales_service_clean.py`
5. **Indentation:** Must be 4-space (Python 3.12 strict enforcement)
6. **FIFO integrity:** Never modify positions - always add transactions and recompute
7. **TradeStation OAuth:** 
   - Missing `audience` parameter causes 401 errors
   - Must set BOTH `TS_MODE` and `TRADESTATION_MODE`
   - SIMULATOR domain blocked on Codespaces - use LIVE mode
   - Token functions must be awaited (async)

---

## Backend Development
```bash
cd backend
python -m uvicorn server:app --reload --port 8000

# Quality gates (CI/CD compliance):
pytest -q --maxfail=1 --disable-warnings
ruff check . && ruff format --check
mypy . --ignore-missing-imports
bandit -ll -r . -x tests
pip-audit --strict
```

### Frontend Development
```bash
cd frontend
npm start  # Uses Craco (craco.config.js)

# Quality gates:
npm run lint
npm run build
npm audit --audit-level=high
```

### Docker Compose
```bash
docker-compose up  # Backend :8000, Redis :6379
# Uses: python -m uvicorn server:app --reload (not app.main:app)
```

### Integration Tests
Root-level `*_test.py` files test against deployed backend:
```bash
python backend_test.py
python options_backend_test.py
python tradestation_integration_test.py
```
**Pattern:** `BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8000")`

---

## Naming Conventions

- **Services:** `*_service.py` (e.g., `unusual_whales_service.py`)
- **Routers:** `backend/routers/*.py` OR `backend/app/routers/*.py`
- **AI Agents:** `*_agent.py` (e.g., `investment_scoring_agent.py`)
- **Integration Tests:** Root `*_test.py` (e.g., `backend_test.py`)
- **Unit Tests:** `backend/tests/test_*.py`

---

## Critical Environment Variables

```bash
# Backend (backend/.env)
REDIS_URL=redis://localhost:6379/0
FM_FORCE_FALLBACK=1              # Force in-memory cache
FM_REDIS_REQUIRED=1              # Fail if Redis unavailable
TEST_MODE=1                      # Shared in-memory for tests
MONGO_URL=mongodb://...
TS_CLIENT_ID/TS_CLIENT_SECRET/TS_REDIRECT_URI
UW_API_TOKEN or UNUSUAL_WHALES_API_KEY

# Frontend (frontend/.env.local)
REACT_APP_BACKEND_URL=http://localhost:8000  # NEVER hardcode!
```

---

## Common Pitfalls

1. **Redis confusion:** Always `from redis_fallback import get_kv`, never direct Redis imports
2. **Dark theme violations:** Never use `isDarkMode ?` ternaries or light classes
3. **URL hardcoding:** Frontend must use `process.env.REACT_APP_BACKEND_URL`
4. **UW API hallucinations:** Only use 17 verified endpoints in `unusual_whales_service_clean.py`
5. **Indentation:** Must be 4-space (Python 3.12 strict enforcement)
6. **FIFO integrity:** Never modify positions - always add transactions and recompute
7. **TradeStation OAuth:** 60-day refresh cycle, callback URLs must match portal config

---

## Key Files Reference

**Architecture:**
- `backend/server.py` (972 lines) - Main FastAPI app, router mounting
- `backend/redis_fallback.py` (96 lines) - Cache abstraction, fallback logic
- `backend/mindfolios.py` (1133 lines) - FIFO algorithm, position tracking
- `frontend/src/App.js` (250 lines) - React entry, dark theme, routing

**Services:**
- `backend/services/builder_engine.py` - 54+ strategies, Greeks
- `backend/services/quality.py` - Spread quality scoring
- `backend/unusual_whales_service_clean.py` - 17 verified UW endpoints

**Documentation:**
- `PROJECT_TASKS.md` - Task tracker (1537 lines, 6-month roadmap)
- `DEVELOPMENT_GUIDELINES.md` - Romanian workflow rules
- `UW_API_FINAL_17_ENDPOINTS.md` - Complete UW API reference
- `PYTHON312_INDENT_PROJECT_COMPLETE.md` - Indentation fix history
- `DARK_THEME_ONLY_VALIDATION.md` - Dark theme migration details

**CI/CD:**
- `.gitlab-ci.yml` (475 lines) - Security gates, SAST, dependency scanning
- `backend/pyproject.toml` - Ruff config (E4/E7/E9/F errors only)
- `backend/.pre-commit-config.yaml` - Pre-commit hooks

---

## API Endpoints Quick Reference

### Builder (`/api/builder`)
- `POST /price` - Calculate strategy pricing & Greeks
- `POST /historical` - Backtest strategy over time

### Options (`/api/options`)
- `GET /chain?symbol=TSLA&expiry=2025-11-15` - Options chain
- `GET /expirations?symbol=TSLA` - Available expirations
- `GET /gex?symbol=TSLA&dte=30` - Gamma Exposure
- `GET /spot/{symbol}` - Current stock price

### Flow (`/api/flow`)
- `GET /summary?limit=24&minPremium=25000` - Flow summary
- `GET /live?symbol=TSLA` - Real-time flow
- `GET /historical?symbol=TSLA&days=7` - Historical flow

### Mindfolio (`/api/mindfolios`)
- `GET /` - List all mindfolios
- `POST /` - Create mindfolio
- `GET /{id}` - Get details
- `PATCH /{id}` - Update
- `DELETE /{id}` - Delete

---

## When Making Changes

1. **Backend API:** Update integration test in root `*_test.py`
2. **Dependencies:** Update `requirements.txt`/`package.json`, run audits
3. **External API:** Add client in `integrations/`, follow `ts_client.py` pattern
4. **New routes:** Add router in `routers/`, mount in `server.py`
5. **Frontend features:** Follow page-based organization in `pages/`
6. **Tasks:** Update `PROJECT_TASKS.md` checkboxes

---

**When in doubt:** Check `redis_fallback.py` for cache patterns, `mindfolios.py` for FIFO logic, `server.py` for router organization, `unusual_whales_service_clean.py` for UW API patterns.
