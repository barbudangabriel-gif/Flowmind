# FlowMind Core Architecture v2.0

## 🎯 MASTER STRUCTURE (3 Pillars + Foundation)

```
📊 OVERVIEW
└── Dashboard

📈 STOCKS
└── Investment Scoring (AI stock analysis module)
    ├── Stock Scorer
    ├── Scanner
    └── Top Picks

💼 PORTFOLIOS
├── View All Portfolios
├── Create New Portfolio
└── [Each Portfolio Detail Page]
    ├── Overview / Positions / Transactions
    ├── Smart Rebalancing (per-portfolio module)
    └── Portfolio Charts (per-portfolio analytics)

📊 OPTIONS ANALYTICS (All options functionality)
├── 🔨 Options Builder (manual construction + 54+ strategy library)
├── 🎯 Options Optimizer (auto-suggest best strategies)
├── ⚡ IV Service (auto trading module)
│   ├── Iron Condor Scanner
│   ├── Calendar Scanner
│   ├── Diagonal Scanner
│   └── Double Diagonal Scanner
├── 💰 Sell Puts for Income (auto trading module)
│   ├── Cash-Secured Puts Engine
│   └── Covered Calls (activated when assigned)
├── 📈 Flow Summary (Unusual Whales)
├── 🌊 Dark Pool
├── 🏛️ Congress Trades
└── 🏢 Institutional Flows

🔧 SYSTEM
├── Trades (Preview Queue, Orders SIM/LIVE)
├── Analytics (Backtests, Verified Chains)
└── Data Providers (TradeStation, Unusual Whales)
```

---

## 🚀 THE 2 CORE TRADING MODULES

### 1. **IV Service** (Volatility-Based Auto Trading)
- **Parent Section:** OPTIONS ANALYTICS
- **Route:** `/options/iv-service` (flexible - can be tabs/pages)
- **Backend:** `backend/iv_service/`
- **Purpose:** Automated scanner for IV-based multi-leg strategies
- **Strategies Executed:**
  - Iron Condor
  - Calendar Spreads
  - Diagonal Spreads
  - Double Diagonal Spreads
- **Key Features:**
  - IV rank/percentile-based detection
  - Term structure analysis
  - Auto-optimization
  - Backtesting integration
  - Quality gates

### 2. **Sell Puts for Income** (Premium Harvesting Auto Trading)
- **Parent Section:** OPTIONS ANALYTICS
- **Route:** `/options/sell-puts` (flexible routing)
- **Backend:** `backend/options_selling_service.py`, `backend/sell_puts_engine.py`
- **Purpose:** Income generation via cash-secured puts + covered calls
- **Strategy Flow:**
  1. **Cash-Secured Puts** (primary) → Sell puts for premium
  2. **If Assigned** → Receive shares
  3. **Covered Calls** (secondary) → Sell calls against shares
- **Key Features:**
  - Delta: 0.25-0.30 typical
  - DTE: 20-40 days
  - IV Rank: >40
  - VIX gates: 15-25
  - Roll management (delta breach, DTE threshold)
  - Assignment detection → auto-switch to Covered Calls
  - Capital allocation modes (equal vs greedy)

**Important:** These are the ONLY 2 trading modules. Everything else is either:
- A tool (Builder, Optimizer)
- Market data (Flow, Dark Pool, Congress)
- A per-portfolio feature (Charts, Rebalancing)

---

## 📚 THE 54+ OPTIONS STRATEGIES (Library/Education)

**Location:** OPTIONS ANALYTICS → Options Builder  
**Purpose:** Educational reference + Templates for manual construction  
**Backend:** `backend/services/builder_engine.py`, `backend/options_calculator.py`

**Critical:** These are **NOT modules**. They are **strategy templates/vehicles** that users select when manually constructing trades in the Builder.

### Novice (6 strategies)
- Long Call, Long Put
- Covered Call, Cash-Secured Put
- Protective Put, Married Put

### Intermediate (12 strategies)
- Bull Put Spread, Bear Call Spread
- Bull Call Spread, Bear Put Spread
- Iron Condor, Iron Butterfly
- Long Put Butterfly, Long Call Butterfly
- Long Straddle, Long Strangle
- Short Put Butterfly, Short Call Butterfly

### Advanced (8 strategies)
- Short Put, Short Call
- Covered Short Straddle, Covered Short Strangle
- Short Straddle, Short Strangle
- Collar, Risk Reversal

### Expert (28+ strategies)
- Long/Short Synthetic Future
- Long/Short Combo
- Strip, Strap
- Double Diagonal (manual)
- Calendar Spread (manual)
- Diagonal Spread (manual)
- Jade Lizard, Big Lizard
- Reverse Iron Condor
- Christmas Tree (Put/Call)
- Broken Wing Butterfly
- Skip Strike Butterfly
- Ratio Spread (Call/Put)
- Backspread (Call/Put)
- Box Spread
- Conversion, Reversal
- Guts, Gut Spread
- Seagull, Albatross
- Butterfly with Skips
- Condor with Skips
- and more...

---

## 💼 PER-PORTFOLIO MODULES

These modules exist **inside each portfolio**, not at the global level:

### 1. Portfolio Charts (Analytics Module)
- **Location:** Inside portfolio detail view (tab or section)
- **Backend:** `backend/portfolio_charts_service.py`
- **Features:**
  - P&L over time
  - Greek exposure charts
  - Risk metrics dashboard
  - Performance attribution
  - Drawdown analysis

### 2. Smart Rebalancing (Optimization Module)
- **Location:** Inside portfolio detail view
- **Backend:** `backend/smart_rebalancing_service.py`
- **Features:**
  - AI-driven allocation suggestions
  - Risk-adjusted rebalancing
  - Tax-loss harvesting awareness
  - Drift detection
  - Optimal trade suggestions

### 3. Core Portfolio Functions
- **Location:** Portfolio detail main view
- **Backend:** `backend/portfolios.py`
- **Features:**
  - Positions (FIFO tracking)
  - Transactions (CRUD)
  - Cash management (add/withdraw funds)
  - Module allocation
  - Import CSV
  - Realized/Unrealized P&L

**Key Point:** Charts and Rebalancing are NOT global. Each portfolio instance has its own.

---

## 🗺️ FINAL SIDEBAR NAVIGATION

```javascript
// nav.simple.js structure

📊 Overview
└── Dashboard

📈 Stocks
└── Investment Scoring
    ├── Stock Scorer
    ├── Scanner
    └── Top Picks

💼 Portfolios
├── View All Portfolios
├── Create New Portfolio
├── [Dynamic: User's Portfolios]
│   └── Portfolio Detail
│       ├── Overview (positions, transactions)
│       ├── Charts (analytics module)
│       └── Rebalancing (optimization module)
└── TradeStation Account (if connected)

📊 Options Analytics
├── 🔨 Options Builder
│   └── Strategy Library (54+ templates dropdown)
├── 🎯 Options Optimizer
├── ⚡ IV Service
│   ├── Iron Condor Scanner
│   ├── Calendar Scanner
│   ├── Diagonal Scanner
│   └── Double Diagonal Scanner
├── 💰 Sell Puts for Income
│   ├── Cash-Secured Puts Engine
│   └── Covered Calls (when assigned)
├── 📈 Flow Summary (UW)
├── 🌊 Dark Pool
├── 🏛️ Congress Trades
└── 🏢 Institutional Flows

🔧 System
├── Trades
│   ├── Preview Queue
│   └── Orders (SIM / LIVE)
├── Analytics
│   ├── Backtests
│   └── Verified Chains
└── Data Providers
    ├── TradeStation
    └── Unusual Whales
```

---

## 📋 DEVELOPMENT RULES (Critical - Read Before Any Code)

### 1. **Stocks Pillar**
✅ **DO:**
- Enhance Investment Scoring features
- Add new stock metrics/scoring factors
- Improve scanner capabilities

❌ **DON'T:**
- Create "Stock Trading Module"
- Mix stock analysis with options
- Add portfolio features here

### 2. **Portfolios Pillar**
✅ **DO:**
- Enhance portfolio CRUD
- Add features to Charts or Rebalancing modules
- Improve transaction import
- Add new per-portfolio analytics

❌ **DON'T:**
- Create global portfolio analytics (it's per-portfolio)
- Mix trading strategies here
- Create "Portfolio Trading Module"

### 3. **Options Analytics Pillar**
✅ **DO:**
- Enhance Builder with new features
- Improve IV Service or Sell Puts modules
- Add new market intelligence (Flow, etc.)
- Extend strategy library (the 54+)

❌ **DON'T:**
- Create new trading modules (only 2 exist: IV Service + Sell Puts)
- Turn strategy templates into modules
- Create "Long Call Module" or "Iron Condor Module"

### 4. **Routes are Flexible**
- Can be separate pages: `/options/iv-service`
- Can be tabs: `/options/iv-service?strategy=iron-condor`
- Can be sub-pages: `/options/iv-service/iron-condor`
- **Decide per-module based on UX needs**

### 5. **Adding New Features**
Before coding, ask:
- Is this a stock feature? → Enhance Investment Scoring
- Is this a portfolio feature? → Add to Portfolio detail or per-portfolio modules
- Is this an options feature? → Add under Options Analytics
- Is this a new trading system? → **STOP. Review with team. Do we really need a 3rd module?**

### 6. **The 54+ Strategies**
- These are **templates**, NOT modules
- Live in Builder as a dropdown/library
- Used for:
  - Education (show what each strategy does)
  - Manual construction (user picks template)
- **Never** create a sidebar item for individual strategies

---

## 🔄 Example Workflows

### Workflow 1: IV Service Auto Trading
```
1. User: Options Analytics → IV Service → Iron Condor Scanner
2. System: Scans market, finds AAPL (IV Rank 55, term structure favorable)
3. User: Clicks "Review in Builder"
4. Builder: Pre-fills 4 legs based on scanner output
5. User: Adjusts strikes, reviews P&L chart
6. User: Saves to Portfolio Manager
7. Portfolio Charts: Starts tracking performance
8. Smart Rebalancing: May suggest position size adjustment
```

### Workflow 2: Sell Puts for Income (Full Cycle)
```
1. User: Options Analytics → Sell Puts for Income → CSP Engine
2. System: Suggests TSLA 0.28 delta put @ 35 DTE, premium $450
3. User: Approves → saved to Portfolio Manager
4. Market: Price drops, user gets assigned 100 shares
5. System: Detects assignment in portfolio
6. Module: Auto-switches to Covered Calls mode
7. System: Suggests 0.25 delta call @ 30 DTE, premium $300
8. User: Sells call → income cycle continues
9. Portfolio Charts: Tracks total premium collected
```

### Workflow 3: Manual Strategy via Builder
```
1. User: Options Analytics → Options Builder
2. User: Opens "Strategy Library" dropdown (54+ strategies)
3. User: Selects "Iron Butterfly" template
4. Builder: Pre-fills typical strikes (ATM, ±5, ±10)
5. User: Adjusts strikes, quantity
6. Builder: Calculates P&L, Greeks, quality score
7. User: Saves to Portfolio Manager
8. Smart Rebalancing: Suggests if position size fits allocation
9. Portfolio Charts: Tracks position over time
```

### Workflow 4: Investment Scoring → Options
```
1. User: Stocks → Investment Scoring → Scanner
2. System: Finds top 10 stocks with high scores
3. User: Clicks "Trade Options on AAPL"
4. System: Navigates to Options Analytics → Options Builder
5. Builder: Pre-fills symbol, fetches option chain
6. User: Selects strategy from library, constructs trade
7. User: Saves to Portfolio Manager
```

---

## ✅ THIS IS THE FOUNDATION

**All future development MUST align with this architecture.**

**The 3 Pillars are sacred:**
1. Stocks (Investment Scoring)
2. Portfolios (Manager + per-portfolio modules)
3. Options Analytics (Builder, Optimizer, 2 trading modules, market data)

**When in doubt:**
- Re-read this document
- Ask: "Which pillar does this belong to?"
- Challenge: "Is this really a new module, or an enhancement?"

**Remember:**
- Only 2 trading modules exist (IV Service, Sell Puts)
- 54+ strategies are templates, not modules
- Charts and Rebalancing are per-portfolio, not global
- Routes are flexible (pages, tabs, query params - decide per-feature)

**This document is the single source of truth for FlowMind architecture.**
