# 🎯 FlowMind - Options Analytics Platform

**Last Updated:** November 3, 2025  
**Repository:** github.com/barbudangabriel-gif/Flowmind  
**Status:** Active Development + Production Ready  
**Tech Stack:** FastAPI + React 19 + Redis + Docker

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Features](#core-features)
4. [Backend Services](#backend-services)
5. [Frontend Components](#frontend-components)
6. [External Integrations](#external-integrations)
7. [Data Models](#data-models)
8. [File Structure](#file-structure)
9. [Deployment](#deployment)

---

## 🎯 Overview

**FlowMind** este o platformă avansată de analiză pentru trading cu opțiuni, construită pentru **un singur utilizator (Gabriel)** - tool personal de trading, nu SaaS.

### Key Characteristics:
- **Single-user system** - No authentication/multi-tenancy
- **Personal trading tool** - Built for Gabriel's workflow
- **Broker integration** - TradeStation, Tastytrade, IBKR
- **Real-time data** - Live options flow, Greeks, GEX
- **Portfolio tracking** - FIFO accounting, P&L calculation
- **Strategy builder** - 54+ options strategies with visualization

---

## 🏗️ Architecture

### Tech Stack

```
Frontend:
├── React 19 (latest)
├── Tailwind CSS (dark theme only)
├── Zustand (state management)
├── React Router v7
└── Craco (build customization)

Backend:
├── FastAPI (Python 3.11)
├── Redis (primary cache, TTL-based)
├── AsyncTTLDict (fallback cache)
├── MongoDB (mindfolios, optional)
└── Docker Compose (deployment)

External APIs:
├── TradeStation (OAuth, options chains, balances)
├── Unusual Whales (options flow, dark pool, insider trades)
└── Future: Tastytrade, Interactive Brokers
```

### Architecture Patterns

1. **Redis Fallback System** (`backend/redis_fallback.py`)
   - Zero-downtime caching
   - App continues if Redis unavailable
   - Three modes: Redis → AsyncTTLDict → In-memory

2. **FIFO Position Tracking** (`backend/mindfolio.py`)
   - Tax-compliant realized P&L
   - First-In-First-Out lot tracking
   - Transaction-based position calculation

3. **Dark Theme Enforcement**
   - No light mode support (removed)
   - All Tailwind classes are dark variants
   - Consistent UI across all pages

4. **Master Mindfolio System** (NEW - Nov 2-3, 2025)
   - Auto-sync with broker APIs
   - Position/cash transfer between portfolios
   - 3 masters (TradeStation, Tastytrade, IBKR)

---

## 🚀 Core Features

### 1. 📊 Mindfolio Management

**Purpose:** Portfolio tracking with FIFO accounting

**Features:**
- Create multiple portfolios (mindfolios)
- Track positions with cost basis
- Calculate realized/unrealized P&L
- Module allocation (budget per strategy)
- Transaction history
- JSON backup system

**Files:**
- `backend/mindfolio.py` (2,666 lines)
- `frontend/src/pages/MindfolioDetailNew.jsx`
- `frontend/src/pages/MindfoliosList.jsx`

**Endpoints:**
```
GET    /api/mindfolio                    # List all
POST   /api/mindfolio                    # Create
GET    /api/mindfolio/{id}               # Get details
PATCH  /api/mindfolio/{id}               # Update
DELETE /api/mindfolio/{id}               # Delete
POST   /api/mindfolio/import-from-tradestation
POST   /api/mindfolio/{id}/import-ytd
GET    /api/mindfolio/templates          # 4 templates
```

### 2. 🏦 Master Mindfolio System (NEW)

**Purpose:** Auto-sync broker accounts with specialized portfolios

**Architecture:**
- 3 Master Mindfolios (one per broker)
- Each master mirrors its broker account
- Users create specialized mindfolios (LEAPS Strategy, Wheel, etc.)
- Transfer positions + cash from masters to specialized

**Backend:** 827 lines
- Extended Mindfolio model (6 new fields)
- PositionTransfer + CashTransfer models
- BrokerSyncService (336 lines)
- 4 new endpoints

**Frontend:** 624 lines
- PositionTransferModal.jsx (245 lines)
- CashTransferModal.jsx (199 lines)
- Master badges (purple "Master", green "Auto-Sync")
- "Sync Now" button

**Endpoints:**
```
POST /api/mindfolio/master/create
POST /api/mindfolio/transfer/position
POST /api/mindfolio/transfer/cash
POST /api/mindfolio/master/{id}/sync
```

### 3. 🎨 Builder - Strategy Visualization

**Purpose:** Interactive options strategy builder with P&L charts

**Features:**
- 54+ predefined strategies
- Interactive P&L visualization (SVG charts)
- Real-time Greeks calculation
- Multiple chart types (P&L, Greeks, probability)
- Risk metrics (max profit/loss, breakeven)

**Files:**
- `frontend/src/pages/BuilderV2Page.jsx` (1,538 lines)
- `backend/services/builder_engine.py`
- `backend/routers/builder.py`

**Tabs:**
- **Build:** Interactive P&L chart (1000x400px)
- **Optimize:** Strategy cards grid (360x180px each)
- **Strategy:** Strategy details + comparisons
- **Flow:** Real-time options flow integration

**Endpoints:**
```
POST /api/builder/price              # Calculate pricing
POST /api/builder/historical         # Backtest
GET  /api/builder/strategies         # List strategies
```

### 4. 📈 Options Data & Analysis

**Purpose:** Real-time options data from multiple sources

**Features:**
- Options chains (strikes, premiums, Greeks)
- Gamma Exposure (GEX) calculations
- Implied Volatility (IV) tracking
- Spot price data
- Historical options data

**Files:**
- `backend/routers/options.py`
- `backend/services/options_gex.py`
- `backend/services/providers/ts_provider.py`

**Endpoints:**
```
GET /api/options/chain?symbol=TSLA&expiry=2025-11-15
GET /api/options/expirations?symbol=TSLA
GET /api/options/gex?symbol=TSLA&dte=30
GET /api/options/spot/{symbol}
```

### 5. 🌊 Options Flow Monitoring

**Purpose:** Real-time institutional options activity

**Features:**
- Live options flow (Unusual Whales)
- Dark pool trades (500+ per ticker)
- Insider trading activity (5 endpoints)
- Market tide alerts
- Flow summary dashboard

**Files:**
- `backend/unusual_whales_service_clean.py` (17 verified endpoints)
- `frontend/src/pages/FlowPage.jsx`
- `frontend/src/pages/LiveFlowPage.jsx`

**Endpoints:**
```
GET /api/flow/summary?limit=24&minPremium=25000
GET /api/flow/live?symbol=TSLA
GET /api/flow/historical?symbol=TSLA&days=7
```

### 6. 💼 Account Balance Pages (NEW - Nov 2, 2025)

**Purpose:** Real-time broker account balances

**Features:**
- 7 account types implemented:
  - TradeStation: Equity, Futures
  - Tastytrade: Equity, Futures, Crypto
  - Interactive Brokers: Equity, Futures
- Aggregate Account view (combines all brokers)
- Live balance updates via WebSocket
- InfoTooltip component for metric explanations

**Files:**
- `frontend/src/pages/AccountDetailPage.jsx` (615 lines)
- `backend/app/routers/brokers_mock.py` (329 lines)

**Structure:**
```
Futures Account:
├── 3 Main Cards (Futures Value, Cash Balance, Total Equity)
├── 9 Metrics (Net Liquidation, Buying Power, P&L, etc.)
└── InfoTooltip hover system

Equity Account:
├── Portfolio Overview (3 cards)
├── Stocks Tab (positions table)
└── Options Tab (options positions)

Crypto Account:
└── TODO: Structure pending user data
```

### 7. 🎯 Templates System (NEW - Nov 2, 2025)

**Purpose:** Quick mindfolio creation with pre-configured strategies

**Templates:**
1. 📈 **Day Trading** ($25k, HIGH risk)
   - MOMENTUM_SCANNER ($15k budget)
   - BREAKOUT_TRADER ($10k budget)
   
2. 💰 **Options Selling** ($50k, MEDIUM risk)
   - SELL_PUTS_ENGINE ($30k budget)
   - COVERED_CALLS ($20k budget)
   
3. 🏦 **Long-term Investing** ($10k, LOW risk)
   - VALUE_INVESTOR ($7k budget)
   - DIVIDEND_COLLECTOR ($3k budget)
   
4. 📝 **Blank Template** ($10k, CUSTOM risk)
   - Empty modules (user customizes)

**Files:**
- `frontend/src/components/MindfolioTemplateModal.jsx` (245 lines)
- `backend/mindfolio.py` (templates endpoint)

**Endpoint:**
```
GET /api/mindfolio/templates    # Returns 4 templates
```

### 8. 🔐 TradeStation Integration

**Purpose:** OAuth authentication + live trading data

**Features:**
- OAuth 2.0 flow (with 2FA support)
- LIVE mode (real accounts) + SIM mode
- Account balances, positions, orders
- Options chains with strikes/premiums
- Real-time P&L tracking
- Token persistence (Redis cache, 60-day refresh)

**Files:**
- `backend/app/services/tradestation.py`
- `backend/app/routers/tradestation.py`

**Endpoints:**
```
GET /api/ts/login                        # OAuth start
GET /api/oauth/tradestation/callback     # OAuth callback
GET /api/tradestation/accounts
GET /api/tradestation/accounts/{id}/balances
GET /api/tradestation/accounts/{id}/positions
GET /api/tradestation/options/chains/{symbol}
```

**Critical Config:**
```bash
TS_CLIENT_ID=...
TS_CLIENT_SECRET=...
TS_REDIRECT_URI=https://your-domain.com/api/oauth/tradestation/callback
TS_MODE=LIVE                    # or SIMULATION
TRADESTATION_MODE=LIVE          # MUST match TS_MODE!
```

### 9. 📊 Dashboard

**Purpose:** Overview of portfolio + market status

**Features:**
- Portfolio summary (total value, P&L)
- Market overview (SPY, VIX, top movers)
- System status indicators
- Alert counts

**Files:**
- `frontend/src/pages/Dashboard.jsx`
- `backend/routers/dashboard.py`

**Endpoint:**
```
GET /api/dashboard/overview
```

---

## 🔧 Backend Services

### Core Services

1. **builder_engine.py** - 54+ strategies, Greeks calculations
2. **options_gex.py** - Gamma Exposure calculations
3. **quality.py** - Spread quality scoring
4. **broker_sync.py** - Master mindfolio auto-sync (NEW)
5. **tradestation.py** - TradeStation API client
6. **unusual_whales_service_clean.py** - 17 verified UW endpoints

### Infrastructure

1. **redis_fallback.py** - Zero-downtime cache fallback
2. **server.py** - Main FastAPI app (972 lines)
3. **mindfolio.py** - FIFO accounting, portfolio tracking (2,666 lines)

### Providers

1. **ts_provider.py** - TradeStation data provider
2. **uw_provider.py** - Unusual Whales data provider

---

## 🎨 Frontend Components

### Pages (17 total)

```
frontend/src/pages/
├── Dashboard.jsx                    # Main dashboard
├── HomePage.jsx                     # Landing page
├── BuilderV2Page.jsx                # Strategy builder (1,538 lines)
├── MindfoliosList.jsx               # Portfolio list
├── MindfolioDetailNew.jsx           # Portfolio details
├── AccountDetailPage.jsx            # Broker balances (615 lines)
├── FlowPage.jsx                     # Options flow
├── LiveFlowPage.jsx                 # Real-time flow
├── StrategyChartTestPage.jsx        # Chart testing
└── ... (8 more)
```

### Components (25+ reusable)

```
frontend/src/components/
├── StrategyChart.jsx                # Universal P&L chart
├── PositionTransferModal.jsx        # Master mindfolio transfers (245 lines)
├── CashTransferModal.jsx            # Cash transfers (199 lines)
├── MindfolioTemplateModal.jsx       # Templates (245 lines)
├── StrategyCard.jsx                 # Strategy preview cards
├── BuilderChart.jsx                 # Legacy builder chart
├── InfoTooltip.jsx                  # Hover explanations
└── ... (18 more)
```

### Hooks & Context

```
frontend/src/hooks/
├── useWebSocket.js                  # WebSocket management
├── useExpirations.js                # Fetch expirations
└── useOptionsSelling.js             # Options selling logic

frontend/src/context/
└── WebSocketContext.jsx             # Global WebSocket state
```

---

## 🔌 External Integrations

### 1. Unusual Whales API

**Status:** ✅ 17 verified endpoints (Oct 21, 2025)

**Categories:**
- **Stock Options** (5 endpoints): contracts, exposures, Greeks, volume, info
- **Screening** (2 endpoints): stocks screener, market alerts
- **Insider Trading** (5 endpoints): trades, recent, buys, sells
- **Dark Pool** (2 endpoints): ticker trades, recent activity
- **Earnings** (3 endpoints): ticker history, today, this week

**Auth:** `Authorization: Bearer {token}` header

**Rate Limit:** 1.0s delay between requests

**Documentation:** `UW_API_FINAL_17_ENDPOINTS.md`

### 2. TradeStation API

**Status:** ✅ OAuth operational, LIVE mode connected

**Features:**
- OAuth 2.0 with 2FA
- Real accounts (11775499, 210MJP11)
- Options chains, balances, positions
- Orders execution (future)

**Auth:** `audience=https://api.tradestation.com` (REQUIRED!)

**Token:** 60-day refresh cycle, stored in Redis

### 3. Future Integrations

- **Tastytrade API** - Planned (similar to TS)
- **Interactive Brokers API** - Planned (TWS/Gateway)

---

## 📊 Data Models

### Core Models (Pydantic v2)

```python
# Mindfolio
class Mindfolio(BaseModel):
    id: str
    name: str
    broker: str                        # "TradeStation" | "Tastytrade" | "IBKR"
    environment: str                   # "SIM" | "LIVE"
    account_type: str                  # "Equity" | "Margin" | "Futures" | "Crypto"
    account_id: Optional[str]
    cash_balance: float
    starting_balance: float
    status: str                        # "ACTIVE" | "ARCHIVED"
    
    # Master Mindfolio fields (NEW)
    is_master: bool = False
    auto_sync: bool = False
    last_sync: Optional[str]
    sync_status: str                   # "idle" | "syncing" | "error"
    allocated_to: List[str] = []
    received_from: Optional[str]
    
    modules: List[ModuleAllocation]
    created_at: str
    updated_at: str

# Position
class Position(BaseModel):
    symbol: str
    qty: float
    cost_basis: float
    avg_cost: float

# Transaction
class Transaction(BaseModel):
    id: str
    mindfolio_id: str
    datetime: str
    symbol: str
    side: str                          # "BUY" | "SELL"
    qty: float
    price: float
    fee: float = 0.0
    notes: str = ""
    created_at: str

# Position Transfer (NEW)
class PositionTransfer(BaseModel):
    id: str
    from_mindfolio_id: str
    to_mindfolio_id: str
    symbol: str
    quantity: float
    avg_cost: float
    transfer_value: float
    notes: str = ""
    created_at: str

# Cash Transfer (NEW)
class CashTransfer(BaseModel):
    id: str
    from_mindfolio_id: str
    to_mindfolio_id: str
    amount: float
    notes: str = ""
    created_at: str
```

### Redis Keys

```python
# Mindfolios
key_mindfolio(id)              = f"mindfolio:{id}"
key_mindfolio_list()           = "mindfolios"

# Transactions
key_transaction(tid)           = f"tx:{tid}"
key_mindfolio_transactions(pid)= f"mf:{pid}:transactions"

# Positions
key_mindfolio_positions(pid)   = f"mf:{pid}:positions"

# Transfers (NEW)
key_position_transfer(tid)     = f"transfer:position:{tid}"
key_cash_transfer(tid)         = f"transfer:cash:{tid}"
key_mindfolio_transfers(pid)   = f"mf:{pid}:transfers"

# TradeStation
key_ts_token(user_id)          = f"ts_token:{user_id}"
```

---

## 📁 File Structure

```
Flowmind/
├── backend/                           # FastAPI backend (Python 3.11)
│   ├── server.py                      # Main app (972 lines)
│   ├── mindfolio.py                   # Portfolio management (2,666 lines)
│   ├── redis_fallback.py              # Cache fallback (96 lines)
│   ├── routers/                       # API routes
│   │   ├── builder.py
│   │   ├── options.py
│   │   ├── dashboard.py
│   │   └── ... (8 more)
│   ├── app/
│   │   ├── routers/                   # Additional routes
│   │   │   ├── tradestation.py
│   │   │   └── brokers_mock.py        # Mock broker data (329 lines)
│   │   └── services/                  # Business logic
│   │       ├── builder_engine.py      # 54+ strategies
│   │       ├── options_gex.py
│   │       ├── broker_sync.py         # Master mindfolio sync (336 lines)
│   │       └── tradestation.py
│   ├── services/
│   │   ├── quality.py
│   │   └── providers/
│   │       ├── ts_provider.py
│   │       └── uw_provider.py
│   ├── unusual_whales_service_clean.py # 17 verified endpoints
│   └── tests/                         # Unit tests
│
├── frontend/                          # React 19 + Tailwind
│   ├── src/
│   │   ├── App.js                     # Main app (250 lines)
│   │   ├── pages/                     # 17 page components
│   │   │   ├── BuilderV2Page.jsx      # Strategy builder (1,538 lines)
│   │   │   ├── AccountDetailPage.jsx  # Broker balances (615 lines)
│   │   │   ├── MindfolioDetailNew.jsx
│   │   │   └── ... (14 more)
│   │   ├── components/                # 25+ reusable components
│   │   │   ├── PositionTransferModal.jsx   # 245 lines
│   │   │   ├── CashTransferModal.jsx       # 199 lines
│   │   │   ├── MindfolioTemplateModal.jsx  # 245 lines
│   │   │   └── ... (22 more)
│   │   ├── hooks/                     # Custom hooks
│   │   ├── context/                   # React Context
│   │   └── services/                  # API clients
│   ├── public/
│   ├── package.json
│   └── craco.config.js                # Build config
│
├── data/                              # JSON backups
│   └── mindfolios/                    # Mindfolio backups
│
├── .github/
│   └── copilot-instructions.md        # AI agent instructions (1,200+ lines)
│
├── docker-compose.yml                 # Backend + Redis
├── Dockerfile                         # Backend container
├── Caddyfile                          # Reverse proxy config
├── PROJECT_TASKS.md                   # Task tracker (2,103 lines)
├── DEVELOPMENT_GUIDELINES.md          # Romanian workflow rules
└── ... (100+ documentation files)
```

### Documentation Files (100+)

**Key Documentation:**
- `PROJECT_TASKS.md` - 6-month roadmap with checkboxes
- `.github/copilot-instructions.md` - Complete AI context
- `UW_API_FINAL_17_ENDPOINTS.md` - Unusual Whales API reference
- `OPTIONS_ANALYTICS_COMPLETE.md` - Options Risk Engine docs
- `DEVELOPMENT_GUIDELINES.md` - Workflow + conventions
- `DARK_THEME_ONLY_VALIDATION.md` - UI design system

---

## 🚀 Deployment

### Local Development

```bash
# Backend
cd backend
python -m uvicorn server:app --reload --port 8000

# Frontend
cd frontend
npm start

# Docker (Backend + Redis)
docker-compose up
```

### Production (VPS/Railway)

**Requirements:**
- Docker + Docker Compose
- Caddy (reverse proxy with auto-SSL)
- Git

**Deployment Steps:**

```bash
# 1. Clone repo
git clone https://github.com/barbudangabriel-gif/Flowmind.git /opt/flowmind
cd /opt/flowmind

# 2. Setup Caddy with auth
cp Caddyfile.with-auth /etc/caddy/Caddyfile
# Auth: Username=gabriel, Password=FlowMind2025!

# 3. Configure backend
cp backend/.env.example backend/.env
nano backend/.env  # Add API keys

# 4. Build frontend
cd frontend
npm install
echo 'REACT_APP_BACKEND_URL=http://localhost:8080' > .env.production
npm run build
cd ..

# 5. Start services
docker-compose up -d

# 6. Reload Caddy (auto-gets Let's Encrypt SSL)
systemctl reload caddy
```

**Security:**
- HTTP Basic Auth (username/password)
- Let's Encrypt SSL (auto-renewal)
- HSTS, XSS, CORS headers
- Docker container isolation

**Ports:**
- 80/443 (Caddy) → Frontend + API proxy
- 8000 (Docker) → FastAPI backend
- 6379 (Docker) → Redis

---

## 📊 Statistics (Nov 3, 2025)

### Codebase Metrics

```
Backend:
  • Python files: 50+
  • Total lines: ~15,000
  • API endpoints: 40+
  • Services: 8
  • Routers: 10
  • Tests: 14/14 passing (100%)

Frontend:
  • React components: 42+
  • Pages: 17
  • Hooks: 5
  • Total lines: ~10,000

Documentation:
  • Markdown files: 100+
  • Total lines: ~30,000
  • Main guide: copilot-instructions.md (1,200+ lines)
  • Task tracker: PROJECT_TASKS.md (2,103 lines)

Total Project:
  • Files: 500+
  • Lines of code: ~55,000
  • Development time: 6+ months
  • Contributors: 1 (Gabriel)
```

### Recent Achievements (Nov 2-3, 2025)

1. **Backend API:** 100% test coverage (14/14 endpoints)
2. **Master Mindfolio:** Complete implementation (1,451 lines)
3. **Templates System:** 4 predefined templates operational
4. **Import Fix:** Backend now error-free
5. **Account Pages:** 7 types implemented

**Total Code Added (Last 2 Days):** ~2,500 lines

---

## 🎯 Roadmap

### Completed (2025)
- ✅ Core mindfolio system with FIFO accounting
- ✅ TradeStation OAuth + live data integration
- ✅ Unusual Whales API (17 endpoints verified)
- ✅ Builder with 54+ strategies
- ✅ Master Mindfolio system (auto-sync)
- ✅ Templates system (4 predefined)
- ✅ Account Balance Pages (7 types)
- ✅ Dark theme UI (Tailwind CSS)
- ✅ Docker deployment setup
- ✅ Production-ready backend (100% tests pass)

### In Progress
- 🔄 Crypto account structure
- 🔄 Aggregate Account view
- 🔄 Real broker API connections (replace mocks)
- 🔄 Master Mindfolio testing

### Planned
- 📅 Tastytrade API integration
- 📅 Interactive Brokers API integration
- 📅 Options Risk Engine (Greeks limits, PoP validation)
- 📅 Strategy Engine (generative system for 69 strategies)
- 📅 5-year options backtest
- 📅 MongoDB watchlist feature
- 📅 WebSocket live updates
- 📅 Mobile responsive UI

---

## 🛠️ Development Tools

### Backend
- **FastAPI** - Modern async Python web framework
- **Pydantic v2** - Data validation
- **Redis** - Primary cache
- **Black** - Code formatting (4-space indent)
- **Ruff** - Fast Python linter
- **MyPy** - Static type checking
- **Pytest** - Unit testing
- **Bandit** - Security scanner
- **pip-audit** - Dependency vulnerability scanner

### Frontend
- **React 19** - Latest React version
- **Tailwind CSS** - Utility-first CSS
- **Zustand** - Lightweight state management
- **React Router v7** - Client-side routing
- **Craco** - Create React App Config Override
- **ESLint** - JavaScript linter
- **npm audit** - Dependency security

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Caddy** - Reverse proxy with auto-SSL
- **GitHub Actions** - CI/CD (future)

### Documentation
- **Markdown** - All documentation
- **Mermaid** - Diagrams (future)

---

## 🔐 Security

### Current Measures
- HTTP Basic Auth (production)
- Let's Encrypt SSL (auto-renewal)
- HSTS, XSS, CORS headers configured
- Docker container isolation
- SSH key-based authentication
- No hardcoded secrets (env variables)
- Redis password protection

### Security Scanning
- **Bandit** - Python security linter
- **pip-audit** - Python dependency scanner
- **npm audit** - JavaScript dependency scanner
- **Ruff** - Code quality + security

### TODO Security Enhancements
- [ ] Rate limiting on API endpoints
- [ ] CSRF protection
- [ ] JWT authentication (if multi-user needed)
- [ ] API key rotation automation
- [ ] Secrets management (Vault)
- [ ] Regular dependency updates
- [ ] Penetration testing

---

## 📞 Support & Maintenance

### Logs & Monitoring

```bash
# Backend logs
docker logs flowmind-backend-1 --tail 50 --follow

# Redis logs
docker logs flowmind-redis-1 --tail 50

# Caddy logs
journalctl -u caddy -f

# System status
/tmp/flowmind_status.sh
```

### Backup & Restore

```bash
# Mindfolio backups (auto-saved to JSON)
ls -lh /workspaces/Flowmind/data/mindfolios/

# Manual backup
curl -X POST http://localhost:8000/api/mindfolio/backup-all \
  -H "X-User-ID: default"

# Restore from backup
curl -X POST http://localhost:8000/api/mindfolio/restore-from-backup \
  -H "X-User-ID: default"

# Redis backup
docker exec flowmind-redis-1 redis-cli SAVE
docker cp flowmind-redis-1:/data/dump.rdb ./backup/
```

### Common Issues

1. **Backend won't start**
   - Check Docker logs: `docker logs flowmind-backend-1`
   - Verify .env file exists with API keys
   - Ensure ports 8000/6379 are free

2. **TradeStation OAuth fails**
   - Verify TS_CLIENT_ID/TS_CLIENT_SECRET
   - Check TRADESTATION_MODE matches TS_MODE
   - Ensure `audience` parameter in OAuth flow

3. **Redis connection lost**
   - App continues with in-memory fallback
   - Check Redis container: `docker ps`
   - Restart: `docker-compose restart redis`

4. **Frontend build fails**
   - Create .env.production with REACT_APP_BACKEND_URL
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check for TypeScript errors

---

## 📚 Additional Resources

### Documentation
- **Main Guide:** `.github/copilot-instructions.md`
- **Tasks:** `PROJECT_TASKS.md`
- **API Reference:** `UW_API_FINAL_17_ENDPOINTS.md`
- **Risk Engine:** `OPTIONS_ANALYTICS_COMPLETE.md`

### External Links
- **TradeStation API:** https://api.tradestation.com/docs
- **Unusual Whales:** https://unusualwhales.com/developers
- **React 19 Docs:** https://react.dev
- **FastAPI Docs:** https://fastapi.tiangolo.com

---

**Last Updated:** November 3, 2025  
**Version:** 1.0.0 (Production Ready)  
**Maintainer:** Gabriel Barbudan  
**License:** Private (Personal Use Only)

---

*This document provides a comprehensive overview of the FlowMind platform. For detailed implementation guides, see the respective documentation files.*
