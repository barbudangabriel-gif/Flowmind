# FlowMind Strategy Modules Architecture

## SIDEBAR STRUCTURE

### 1. **Stocks** (Stock Analysis & Scoring)
**Module:** Investment Scoring Agent
- **Path:** `/stocks/scoring`
- **Backend:** `backend/investment_scoring_agent.py`
- **Description:** AI-powered stock analysis and ranking
- **Features:**
 - Multi-factor scoring (Fundamental + Technical + Sentiment)
 - Top picks generation
 - Watchlist scanner
 - Stock scoring dashboard

### 2. **Strategy** (Options Trading Modules)
**Auto Trading Engines:**

#### 2.1 **IV Service** (Implied Volatility Trading)
- **Path:** `/screener/iv`
- **Backend:** `backend/iv_service/`
- **Description:** Automated IV-based strategy scanner
- **Strategies:**
 - Iron Condor (main)
 - Calendar Spreads
 - Diagonal Spreads
 - Double Diagonal Spreads
- **Features:**
 - Auto-detection via IV rank/percentile
 - Term structure analysis
 - Multi-leg optimization
 - Backtesting integration

#### 2.2 **Sell Puts for Income** (Premium Income Module)
- **Path:** `/screener/sell-puts`
- **Backend:** `backend/options_selling_service.py`, `backend/sell_puts_engine.py`
- **Description:** Income-focused options selling system
- **Components:**
 - **Cash-Secured Puts** - Main (sell puts for premium)
 - **Covered Calls** - Secondary (if assigned, sell calls)
- **Features:**
 - Delta-based selection (0.25-0.30)
 - DTE management (20-40 days)
 - IV rank filtering (>40)
 - VIX range gates (15-25)
 - Roll management
 - Assignment tracking → auto Covered Calls

### 3. **Options Analytics** (Options Analysis Hub)
**All Options-Related Tools:**

#### 3.1 **Builder** (Strategy Constructor)
- **Path:** `/builder`
- **Backend:** `backend/services/builder_engine.py`, `backend/routers/builder.py`
- **Description:** Manual multi-leg options strategy builder
- **Features:**
 - Visual P&L charts
 - Greeks calculation
 - Multi-leg support
 - Real-time pricing
 - Quality scoring
 - Historical backtesting

#### 3.2 **Optimize** (Strategy Optimizer)
- **Path:** `/optimize`
- **Backend:** `backend/routers/optimize.py`
- **Description:** AI-powered strategy suggestions
- **Features:**
 - Sentiment-based recommendations
 - Risk/reward optimization
 - Budget-aware suggestions
 - Strategy ranking

#### 3.3 **Flow Analysis** (Unusual Whales Integration)
- **Path:** `/flow`
- **Backend:** `backend/routers/flow.py`, `backend/unusual_whales_service.py`
- **Data Source:** Unusual Whales API
- **Features:**
 - Options flow summary
 - Live flow feed
 - Historical flow
 - News & market events
 - Congress trades
 - Insider activity
 - Dark pool data

#### 3.4 **Options Chain** (TradeStation)
- **Path:** `/md/chain`
- **Backend:** TradeStation API integration
- **Features:**
 - Real-time option chains
 - Greeks by strike
 - Volume & Open Interest
 - IV surface

#### 3.5 **GEX (Gamma Exposure)**
- **Backend:** `backend/services/options_gex.py`
- **Features:**
 - Gamma exposure calculation
 - Zero-gamma levels
 - Market maker positioning

### 4. **Mindfolios** (Mindfolio Management)
**Mindfolio Manager Module:**

#### 4.1 **Mindfolio Manager**
- **Path:** `/mindfolios`
- **Backend:** `backend/mindfolios.py`
- **Features:**
 - Create/manage mindfolios
 - Track positions (FIFO)
 - Transaction history
 - P&L tracking (realized/unrealized)
 - Module allocation
 - Funds management

#### 4.2 **Smart Rebalancing** (AI Mindfolio Optimization)
- **Path:** `/mindfolio/rebalancing`
- **Backend:** `backend/smart_rebalancing_service.py`
- **Description:** AI-driven mindfolio rebalancing
- **Features:**
 - Optimal allocation suggestions
 - Risk-adjusted rebalancing
 - Tax-loss harvesting awareness
 - Module budget optimization

#### 4.3 **Mindfolio Analytics**
- **Path:** `/mindfolio/analytics`
- **Backend:** `backend/mindfolio_charts_service.py`
- **Features:**
 - P&L charts
 - Greek exposure
 - Risk metrics
 - Performance attribution
 - Module performance tracking

---

## OPTIONS STRATEGIES (54+ Pre-Defined Vehicles)

**Purpose:** Educational reference + Builder templates 
**Location:** Used in Builder (`/builder`) and Education/Reference 
**Backend:** `backend/options_calculator.py`

**Note:** These are pre-defined strategy templates/vehicles that users can:
1. Learn about (educational)
2. Use as templates in Builder
3. Reference when analyzing positions

### Novice Level (Beginner-Friendly)
- **Basic Directional:**
 - Long Call
 - Long Put
- **Income:**
 - Covered Call
 - Cash-Secured Put
 - Protective Put

### Intermediate Level
- **Credit Spreads:**
 - Bull Put Spread
 - Bear Call Spread
- **Debit Spreads:**
 - Bull Call Spread
 - Bear Put Spread
- **Neutral:**
 - Iron Butterfly
 - Iron Condor
 - Long Put Butterfly
 - Long Call Butterfly
- **Directional:**
 - Long Straddle
 - Long Strangle
 - Short Put Butterfly
 - Short Call Butterfly

### Advanced Level
- **Naked:**
 - Short Put
 - Short Call
- **Income:**
 - Covered Short Straddle
 - Covered Short Strangle
- **Neutral:**
 - Short Straddle
 - Short Strangle

### Expert Level
- **Synthetic:**
 - Long Synthetic Future
 - Short Synthetic Future
- **Arbitrage:**
 - Long Combo
 - Short Combo
- **Complex:**
 - Strip
 - Strap
 - Double Diagonal
 - Calendar Spreads (manual)
 - Diagonal Spreads (manual)
 - Jade Lizard
 - Big Lizard
 - Reverse Iron Condor
 - Christmas Tree Spread
 - Ratio Spreads
 - Backspread

---

## 🏗️ Sidebar Navigation Structure (Correct Hierarchy)

```
� Dashboard

💼 Account
└── Mindfolio Manager
 ├── View All Mindfolios
 ├── [Dynamic: User Mindfolios]
 └── + Create Mindfolio

 Stocks (Stock Analysis)
├── Investment Scoring
└── Scoring Scanner

 Strategy (Options Trading Modules)
├── IV Service (Auto Scanner)
│ ├── Iron Condor Scanner
│ ├── Calendar Scanner
│ ├── Diagonal Scanner
│ └── Double Diagonal Scanner
└── Sell Puts for Income
 ├── Cash-Secured Puts Engine
 └── Covered Calls (when assigned)

📐 Options Analytics (All Options Tools)
├── 🔨 Builder (Strategy Constructor)
├── Optimize (Strategy Suggestions)
├── Flow Analysis (Unusual Whales)
│ ├── Flow Summary
│ ├── Live Flow
│ ├── Historical Flow
│ ├── News & Events
│ ├── Congress Trades
│ └── Insider Activity
├── 🔗 Options Chain (TradeStation)
└── GEX (Gamma Exposure)

💼 Mindfolios (Mindfolio Management)
├── Mindfolio Manager (main)
├── ⚖️ Smart Rebalancing (AI)
└── Mindfolio Analytics

 Analytics
├── Backtests
└── Verified Chains

🔌 Data Providers
├── TradeStation
└── Unusual Whales
```

---

## Key Relationships & Data Flow

1. **Stocks (Investment Scoring)** → Identifies best stocks → Feed into Strategy modules
2. **Strategy (IV Service)** → Auto-scans setups → User reviews in Builder → Mindfolio tracks
3. **Strategy (Sell Puts)** → CSP sold → Assignment → Auto Covered Calls
4. **Options Analytics (Builder)** → Manual construction → Uses 54+ strategy templates → Mindfolio tracks
5. **Options Analytics (Optimize)** → AI suggestions → User builds in Builder → Mindfolio tracks
6. **Options Analytics (Flow)** → UW data → Identify opportunities → Build in Builder
7. **Mindfolios (Manager)** → Central hub tracking ALL positions from ALL modules
8. **Mindfolios (Smart Rebalancing)** → Analyzes mindfolio → Suggests allocation changes
9. **Mindfolios (Analytics)** → Visualizes performance → P&L, Greeks, Risk metrics

---

## 🔄 Workflow Example: Sell Puts for Income

```
1. Scanner identifies AAPL with IV Rank > 50, VIX = 18
2. Sell Puts Engine suggests 0.28 delta PUT @ 45 DTE
3. User approves → Position opened in Mindfolio Manager
4. Share price drops → Assigned 100 shares of AAPL
5. Module auto-switches to Covered Call mode
6. Covered Calls Engine suggests 0.25 delta CALL @ 35 DTE
7. User sells call → Income cycle continues
```

---

## UI/UX Notes

- **Stocks** = Separate section for stock analysis (Investment Scoring)
- **Strategy** = Auto trading modules (IV Service, Sell Puts)
- **Options Analytics** = All options-related tools (Builder, Optimize, Flow, Chain, GEX)
- **Mindfolios** = Mindfolio management section (Manager, Rebalancing, Analytics)
- **54+ Strategies** = Educational templates used in Builder + reference
- **Covered Calls** appear in Sell Puts ONLY when user has shares (assigned/owned)
- **Flow Analysis** = Umbrella for all Unusual Whales data (flow, news, congress, insiders, dark pool)
- **Builder** = Manual construction tool, **IV Service/Sell Puts** = Automated scanners
- Each module has its own config/settings page

## Clarifications

1. **Investment Scoring** is a STOCKS tool, NOT an options module
2. **Smart Rebalancing** is a MINDFOLIO tool, NOT a strategy module
3. **Options Analytics** is a HUB containing:
 - Builder (manual)
 - Optimize (AI suggestions)
 - Flow (UW data)
 - Chain (TS data)
 - GEX (gamma analysis)
4. **Strategy** section contains only AUTO trading engines:
 - IV Service (auto scanner)
 - Sell Puts for Income (auto engine with CSP + CC)
5. **54+ Strategies** are templates/vehicles for education and Builder use, NOT active modules
