# FlowMind Options & Stock Scoring - Cartografie Completă
**Data:** November 3, 2025  
**Scop:** Mapare completă a tuturor componentelor pentru options trading și stock scoring

---

## 📊 1. OPTIONS SYSTEM - Componente

### 1.1 Routers (API Endpoints)

#### `backend/routers/options.py` (234 linii)
**Endpoint-uri:**
- `GET /api/options/gex?symbol=TSLA&expiry=2025-12-01`
  - Calculează Gamma Exposure (GEX)
  - Folosește `services/options_gex.py`
  
- `GET /api/options/expirations?symbol=TSLA`
  - Returnează date de expirare disponibile
  - Fallback: mock data (weekly/monthly)
  
- `GET /api/options/chain?symbol=TSLA&expiry=2025-12-01`
  - Options chain complet (calls + puts)
  - Demo mode: 13 strikes (±6 * $5), Bid/Ask/Mid, IV, OI, Volume

**Dependencies:**
- `services/options_gex.py` - GEX calculation
- `services/providers.py` - Data provider abstraction

---

#### `backend/routers/options_flow.py` (56 linii)
**Endpoint-uri:**
- `GET /api/options/flow/summary?symbol=SPY&days=7`
  - Flow summary (live + historical)
  - UW API integration: `uw.trades(symbol, start, end)`
  - Returns: `{live: 24, historical: 168, news: 0, congress: 0, insiders: 0}`

**Dependencies:**
- `unusual_whales_service.py` - UW client
- State management: `request.app.state.uw`

---

#### `backend/routers/options_overview.py`
**Scop:** Dashboard overview pentru options (TBD - verifică conținut)

---

#### `backend/routers/automation.py` (214 linii)
**Endpoint-uri:**
- `GET /api/automation/options/chain/{symbol}?source=yahoo`
  - Extract options chain din surse publice
  - Folosește Playwright scraping
  - Alternative sources: yahoo, cboe, nasdaq

**Dependencies:**
- `services/ui_automation.py` - OptionsChainExtractor class

---

### 1.2 Services (Business Logic)

#### `backend/services/options_gex.py`
**Funcții:**
- `compute_gex(symbol, expiry, dte)` - Gamma Exposure calculation
- `fetch_chain(provider, symbol)` - Options chain data fetching

**Algoritm GEX:**
```python
GEX = Σ (Gamma × Open Interest × Contract Multiplier × Spot Price²)
```

---

#### `backend/services/options_provider.py`
**Scop:** Abstract provider interface pentru options data
**Providers:**
- TradeStation API (primary)
- Yahoo Finance (fallback)
- Mock data (dev mode)

---

#### `backend/services/options_scanner.py` (353 linii - NON-FUNCTIONAL)
**Status:** ❌ Barchart scraping nu mai funcționează
**Metode:**
- `scan_high_iv_stocks(min_iv)` - High IV Rank stocks
- `get_options_chain(symbol, dte)` - Chain extraction
- `scan_unusual_volume(min_vol)` - Unusual volume detection
- `get_earnings_calendar(days)` - Upcoming earnings

**Problema:** Barchart a schimbat HTML structure
**Soluție:** Folosește UW API în loc de scraping

---

### 1.3 Core Engines

#### `backend/options_calculator.py`
**Classes:**
- `OptionType(Enum)` - CALL/PUT
- `OptionLeg` - Single leg definition
- `OptionsStrategyEngine` - Multi-leg strategy calculator

**Funcții:**
- `calculate_option_price(S, K, r, q, sigma, tau)` - Black-Scholes
- `calculate_greeks(position)` - Delta, Gamma, Theta, Vega, Rho

---

#### `backend/options_risk_engine.py` (800+ linii) ✅ OPERATIONAL
**Status:** ✅ Complete și testat (4 scenarii de validare)

**Classes:**
- `StrategyType(Enum)` - 15 strategii (Long Call, Iron Condor, etc.)
- `OptionPosition` - Single position model
- `RiskCheck` - Individual check result
- `ValidationResult` - Complete validation response
- `OptionsRiskEngine` - Main engine class

**Funcții cheie:**
```python
validate_options_trade(
    new_positions: List[OptionPosition],
    existing_positions: List[OptionPosition],
    portfolio_cash: float,
    risk_profile: str  # CONSERVATIVE, MODERATE, AGGRESSIVE
) -> ValidationResult
```

**Validări (10 total):**
1. **Greeks Limits** - Delta/Gamma/Theta/Vega portfolio limits
2. **Capital Requirements** - Debit cost vs cash available
3. **Probability Thresholds** - Min PoP (70%/60%/50% per risk profile)
4. **IV Rank Check** - Warning if IV < 50% for credit strategies
5. **Correlation Check** - Symbol concentration (>3 positions)
6. **Early Assignment Risk** - ITM short options near expiry
7. **Expiration Concentration** - >5 positions same date
8. **Strike Concentration** - >3 positions same strike
9. **Cost/Credit Detection** - Strategy classification
10. **Max Loss/Profit** - P&L boundaries

**Strategy Detection:**
- Long Call/Put, Short Call/Put
- Call Spread, Put Spread
- Iron Condor, Iron Butterfly
- Straddle, Strangle, Butterfly
- Calendar Spread, Diagonal Spread, Ratio Spread
- Custom (unknown patterns)

**Greeks Calculation:**
- Risk-neutral lognormal distribution
- Black-Scholes pricing
- Portfolio-level aggregation

**Probability Analysis:**
- PoP at expiration (lognormal CDF)
- Breakeven prices
- Early exit probabilities (50%/25% profit targets)

**API Integration:**
```python
# Endpoint: POST /api/mindfolio/{pid}/validate-options-trade
# Location: backend/mindfolio.py line 2579
@router.post("/{pid}/validate-options-trade")
async def validate_options_trade_endpoint(pid: str, body: ValidateOptionsTradeRequest):
    # Uses OptionsRiskEngine for validation
    # Returns: {passed: bool, checks: [...], strategy_info: {...}, greeks_impact: {...}}
```

**Frontend Integration:** ✅ Ready in `backend/mindfolio.py`
**TODO:** Frontend UI (AddPositionModal.jsx) needs validation display

---

#### `backend/options_strategy_charts.py`
**Class:** `OptionsStrategyChartGenerator`
**Scop:** Generate P&L charts pentru strategii options

---

#### `backend/options_selling_service.py` (302 linii)
**Funcții:**
- `options_analysis(query)` - Analyze options selling opportunities
- Monitor service pentru automated options selling
- Snapshot logging to MongoDB

---

#### `backend/expert_options_system.py`
**Scop:** Expert system pentru options recommendations (TBD)

---

### 1.4 Mindfolio Integration

#### `backend/mindfolio.py` (2666+ linii)
**Options-related endpoints:**

```python
# Line 2560: OptionPositionRequest model
class OptionPositionRequest(BaseModel):
    symbol: str
    option_type: str  # "call" or "put"
    action: str  # "buy" or "sell"
    strike: float
    expiry: str  # ISO format
    quantity: int
    premium: float
    volatility: float
    current_price: float

# Line 2579: Validate options trade
POST /api/mindfolio/{pid}/validate-options-trade
Body: ValidateOptionsTradeRequest
Response: {
    passed: bool,
    checks: [RiskCheck],
    strategy_info: {...},
    greeks_impact: {...},
    probability_analysis: {...}
}
```

**FIFO Position Tracking:**
- BUY transactions add to lots queue
- SELL transactions consume from front (First-In-First-Out)
- Tax-compliant realized P&L calculation

---

## 🎯 2. STOCK SCORING SYSTEM - Componente

### 2.1 Investment Scoring Agent

#### `backend/investment_scoring_agent.py` (1384 linii) ✅ OPERATIONAL
**Status:** ✅ Complete AI-powered scoring system

**Class:** `InvestmentScoringAgent`

**Signal Weights:**
```python
{
    "discount_opportunity": 0.35,  # Discount detection (highest weight)
    "options_flow": 0.20,           # Options sentiment
    "dark_pool": 0.15,              # Institutional activity
    "congressional": 0.10,          # Political insider info
    "risk_reward_ratio": 0.10,      # Risk/reward calculation
    "market_momentum": 0.05,        # Market indicators
    "premium_penalty": 0.05         # Penalty for premium positions
}
```

**Discount Thresholds:**
- RSI oversold: < 30
- Support distance: within 5%
- Pullback threshold: -10% from high
- P/E discount: < 0.8 * sector average

**Premium Thresholds:**
- RSI overbought: > 70
- Resistance distance: within 3%
- Rally threshold: +20% from low
- P/E premium: > 1.3 * sector average

**Risk/Reward Parameters:**
- Min reward ratio: 2:1
- Max risk: 8% from entry
- Optimal risk: 5% from entry

**Main Method:**
```python
async def generate_investment_score(
    symbol: str,
    user_context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Returns:
    {
        "symbol": "TSLA",
        "score": 0.78,  # 0-1 scale
        "recommendation": "BUY" | "HOLD" | "SELL",
        "confidence": "HIGH" | "MEDIUM" | "LOW",
        "signals": {
            "discount_opportunity": 0.85,
            "options_flow": 0.65,
            ...
        },
        "key_insights": [...],
        "risk_analysis": {...}
    }
    """
```

**Data Sources (UW API):**
1. Options flow (`uw.get_options_flow()`)
2. Dark pool (`uw.get_darkpool()`)
3. Congressional trades (`uw.get_congress_trades()`)
4. Stock info (`uw.get_stock_info()`)
5. Greeks (`uw.get_greeks()`)

**Scoring Algorithm:**
1. Fetch all UW data concurrently
2. Analyze each signal component
3. Calculate composite score (weighted sum)
4. Generate recommendation (BUY/HOLD/SELL)
5. Calculate confidence level
6. Extract key insights
7. Risk assessment

---

#### `backend/investment_scoring.py`
**Scop:** Lightweight scoring functions (TBD - verifică vs agent)

---

#### `backend/advanced_scoring_engine.py`
**Scop:** Advanced ML-based scoring (TBD)

---

#### `backend/app/services/fis_scoring.py`
**Scop:** FIS (Financial Intelligence Score) implementation
**Location:** Alternate app structure

---

#### `backend/services/scoring.py`
**Status:** ❌ Empty file
**TODO:** Consolidate sau delete

---

### 2.2 Geopolitical Integration

#### `backend/routers/geopolitical.py`
**Endpoint-uri:**

```python
GET /api/geopolitical/ticker-digest?symbol=TSLA&include_fis=true&include_options=true
# Returns: sentiment score + FIS score + options strategy suggestions

GET /api/geopolitical/mindfolio-digest?mindfolio_id={id}
# Returns: portfolio-wide sentiment analysis

GET /api/geopolitical/bullish-opportunities
# Returns: list of bullish stocks with strategy suggestions
```

**Integration:**
- Investment Scoring Agent (FIS)
- Options strategy recommendations
- Geopolitical sentiment analysis

---

## 🔗 3. UNUSUAL WHALES API INTEGRATION

### 3.1 Service Implementation

#### `backend/unusual_whales_service_clean.py` (740 linii) ✅ VERIFIED
**Status:** ✅ 17 endpoint-uri verificate (Oct 21, 2025)

**Stock Data (5 endpoints):**
1. `/api/stock/{ticker}/info` - Company metadata (17 fields)
2. `/api/stock/{ticker}/greeks` - Options Greeks (135 records for SPY)
3. `/api/stock/{ticker}/option-contracts` - 500+ contracts with IV, OI, volume
4. `/api/stock/{ticker}/spot-exposures` - PRE-CALCULATED GEX (300-410 records)
5. `/api/stock/{ticker}/options-volume` - Volume metrics

**Screeners (1 endpoint):**
6. `/api/screener/stocks?limit=10` - Unified GEX+IV+Greeks screener

**Alerts (1 endpoint):**
7. `/api/alerts?noti_type=market_tide` - Market alerts & tide events

**Insider Trading (5 endpoints):**
8. `/api/insider/trades` - All insider trades
9. `/api/insider/{ticker}` - Ticker-specific insider activity
10. `/api/insider/recent` - Recent trades
11. `/api/insider/buys` - Buy transactions only
12. `/api/insider/sells` - Sell transactions only

**Dark Pool (2 endpoints):**
13. `/api/darkpool/{ticker}?limit=500` - Ticker dark pool trades
14. `/api/darkpool/recent?limit=100` - Market-wide dark pool

**Earnings (3 endpoints):**
15. `/api/earnings/{ticker}` - Historical earnings (61 for TSLA)
16. `/api/earnings/today` - Today's announcements
17. `/api/earnings/week` - This week's calendar

**Authentication:** `Authorization: Bearer {token}` (header)
**Rate Limit:** 1.0s delay between requests
**Base URL:** `https://api.unusualwhales.com/api`

---

### 3.2 Usage în FlowMind

**Location 1: `backend/routers/flow.py`**
```python
from unusual_whales_service import UnusualWhalesService

service = UnusualWhalesService()
# Used in: flow_summary, flow_live, flow_historical, dark_pool, etc.
```

**Location 2: `backend/routers/options_flow.py`**
```python
# Access via app state
uw = request.app.state.uw
trades_live = await uw.trades(symbol, start, end)
```

**Location 3: `backend/investment_scoring_agent.py`**
```python
self.uw_service = UnusualWhalesService()
uw_data = await self._fetch_uw_data(symbol)
```

**Location 4: `backend/server.py`**
```python
# Line 113 (commented out)
# investment_scoring_agent = InvestmentScoringAgent()
```

---

## 📐 4. DATA FLOW DIAGRAMS

### 4.1 Options Trade Flow

```
User Request (Frontend)
    ↓
POST /api/mindfolio/{pid}/validate-options-trade
    ↓
mindfolio.py:validate_options_trade_endpoint()
    ↓
OptionsRiskEngine.validate_options_trade()
    ↓
┌─────────────────────────────────────────┐
│ 1. Strategy Detection (15 types)        │
│ 2. Greeks Calculation (Black-Scholes)   │
│ 3. Capital Requirements Check           │
│ 4. Probability Analysis (PoP)           │
│ 5. IV Rank Check (for credit)          │
│ 6. Correlation Detection                │
│ 7. Early Assignment Risk                │
│ 8. Expiration Concentration             │
│ 9. Strike Concentration                 │
│ 10. Max Loss/Profit Calculation         │
└─────────────────────────────────────────┘
    ↓
ValidationResult {passed, checks, strategy_info, greeks_impact, probability_analysis}
    ↓
Response to Frontend
```

---

### 4.2 Stock Scoring Flow

```
User Request (Frontend)
    ↓
POST /api/investment-scoring/analyze?symbol=TSLA
    ↓
InvestmentScoringAgent.generate_investment_score()
    ↓
┌────────────────────────────────────────┐
│ Parallel UW API Calls:                 │
│ 1. get_options_flow()                  │
│ 2. get_darkpool()                      │
│ 3. get_congress_trades()               │
│ 4. get_stock_info()                    │
│ 5. get_greeks()                        │
└────────────────────────────────────────┘
    ↓
Signal Component Analysis
    ↓
┌────────────────────────────────────────┐
│ 1. Discount Opportunity (35%)          │
│    - RSI oversold check                │
│    - Support distance                  │
│    - Pullback detection                │
│    - P/E discount                      │
│                                        │
│ 2. Options Flow (20%)                  │
│    - Call/Put ratio                    │
│    - Unusual activity                  │
│    - Premium sentiment                 │
│                                        │
│ 3. Dark Pool (15%)                     │
│    - Institutional buying/selling      │
│                                        │
│ 4. Congressional (10%)                 │
│    - Insider political trades          │
│                                        │
│ 5. Risk/Reward Ratio (10%)             │
│    - Entry/Stop/Target calculation     │
│                                        │
│ 6. Market Momentum (5%)                │
│                                        │
│ 7. Premium Penalty (5%)                │
└────────────────────────────────────────┘
    ↓
Composite Score Calculation (weighted sum)
    ↓
Recommendation Generation (BUY/HOLD/SELL)
    ↓
Confidence Level (HIGH/MEDIUM/LOW)
    ↓
Response: {score, recommendation, confidence, signals, insights, risk_analysis}
```

---

### 4.3 Options Data Fetch Flow

```
Frontend: GET /api/options/chain?symbol=TSLA&expiry=2025-12-01
    ↓
backend/routers/options.py:get_options_chain()
    ↓
services/options_gex.py:fetch_chain()
    ↓
services/providers.py:get_provider()
    ↓
┌──────────────────────────────────┐
│ Provider Selection:              │
│ 1. TradeStation API (primary)    │
│ 2. Yahoo Finance (fallback)      │
│ 3. Mock Data (dev mode)          │
└──────────────────────────────────┘
    ↓
Options Chain Data {calls: [...], puts: [...], expirations: [...]}
    ↓
GEX Calculation (if requested)
    ↓
Response to Frontend
```

---

## 📊 5. SISTEM DE FIȘIERE - Structură

```
backend/
├── routers/                          # API Endpoints
│   ├── options.py                    # GEX, chain, expirations (234 lines)
│   ├── options_flow.py               # Flow summary (56 lines)
│   ├── options_overview.py           # Dashboard overview
│   ├── automation.py                 # Playwright chain extraction (214 lines)
│   ├── geopolitical.py               # Sentiment + FIS integration
│   ├── flow.py                       # UW flow data
│   └── builder.py, optimize.py       # Strategy building
│
├── services/                         # Business Logic
│   ├── options_gex.py                # GEX calculation
│   ├── options_provider.py           # Provider abstraction
│   ├── options_scanner.py            # Barchart scraping (NON-FUNCTIONAL)
│   ├── scoring.py                    # Empty (TODO: consolidate)
│   ├── ui_automation.py              # Playwright extraction
│   └── simple_news_scraper.py        # News scraping (WORKING)
│
├── Core Engines
│   ├── options_calculator.py         # Black-Scholes, Greeks
│   ├── options_risk_engine.py        # Validation engine (800+ lines) ✅
│   ├── options_strategy_charts.py    # P&L chart generation
│   ├── options_selling_service.py    # Automated selling (302 lines)
│   ├── expert_options_system.py      # Expert recommendations
│   ├── investment_scoring_agent.py   # AI scoring (1384 lines) ✅
│   ├── investment_scoring.py         # Lightweight scoring
│   └── advanced_scoring_engine.py    # ML scoring
│
├── Unusual Whales Integration
│   ├── unusual_whales_service_clean.py  # 17 endpoints (740 lines) ✅
│   └── unusual_whales_service.py        # Legacy (1674 lines)
│
├── Mindfolio System
│   └── mindfolio.py                  # FIFO, options validation (2666+ lines)
│
└── Models
    ├── models/requests.py            # OptionType, OptionsChainRequest
    └── options_risk_engine.py        # OptionPosition, ValidationResult
```

---

## 🎯 6. STATUS FUNCȚIONALITATE

### ✅ OPERATIONAL (Ready to Use)

| Component | Status | Lines | Purpose |
|-----------|--------|-------|---------|
| Options Risk Engine | ✅ | 800+ | Multi-leg validation, Greeks, PoP |
| Investment Scoring Agent | ✅ | 1384 | AI-powered stock scoring |
| UW API Service | ✅ | 740 | 17 verified endpoints |
| Options Router | ✅ | 234 | GEX, chain, expirations |
| Options Flow Router | ✅ | 56 | Flow summary via UW |
| Mindfolio Options Validation | ✅ | 2666+ | POST /validate-options-trade |
| News Scraper | ✅ | 237 | Finviz news (15+ articles) |

---

### ⚠️ NEEDS WORK

| Component | Status | Issue | Solution |
|-----------|--------|-------|----------|
| Options Scanner | ❌ | Barchart HTML changed | Use UW screener API |
| Earnings Scraper | ❌ | Finviz calendar broken | Use UW earnings API |
| Scoring Service | ❌ | Empty file | Consolidate or delete |
| Options Overview Router | ⚠️ | Needs verification | Check implementation |
| Expert Options System | ⚠️ | TBD | Define requirements |

---

### 🔄 INTEGRATION GAPS

1. **Frontend → Options Risk Engine**
   - Backend: ✅ Complete (POST /validate-options-trade)
   - Frontend: ❌ AddPositionModal.jsx needs UI for validation display

2. **UW API → Options Scanner**
   - UW has screener endpoint (`/api/screener/stocks`)
   - Replace broken Barchart scraping with UW API calls

3. **UW API → Earnings Data**
   - UW has 3 earnings endpoints (ticker, today, week)
   - Create FastAPI wrapper endpoints

4. **Investment Scoring → Frontend**
   - Backend: ✅ Complete (InvestmentScoringAgent)
   - Frontend: ⚠️ Needs widget/page for score display

---

## 🚀 7. RECOMANDĂRI NEXT STEPS

### Priority 1: Fix Options Scanner
```python
# Replace backend/services/options_scanner.py with UW API wrapper
class OptionsScanner:
    def __init__(self):
        self.uw = UnusualWhalesService()
    
    async def scan_high_iv_stocks(self, min_iv: int = 50, limit: int = 10):
        """Use UW screener instead of Barchart"""
        result = await self.uw.get_screener(limit=limit)
        # Filter by IV rank
        return [stock for stock in result['data'] if stock['iv_rank'] >= min_iv]
```

### Priority 2: Earnings API Wrapper
```python
# Add to backend/routers/earnings.py (NEW FILE)
@router.get("/earnings/{ticker}")
async def get_earnings(ticker: str):
    uw = UnusualWhalesService()
    return await uw.get_earnings(ticker)

@router.get("/earnings/today")
async def get_earnings_today():
    uw = UnusualWhalesService()
    return await uw.get_earnings_today()

@router.get("/earnings/week")
async def get_earnings_week():
    uw = UnusualWhalesService()
    return await uw.get_earnings_week()
```

### Priority 3: Frontend Options Validation UI
```jsx
// frontend/src/components/AddPositionModal.jsx
// Add RiskCheckRow component for validation display
const RiskCheckRow = ({ check }) => {
  const icon = { BLOCKER: '🚫', WARNING: '⚠️', INFO: 'ℹ️', PASS: '✅' }[check.level];
  return (
    <div className={`flex items-start gap-2 py-2 ${check.level === 'BLOCKER' ? 'text-red-500' : ''}`}>
      <span>{icon}</span>
      <div>
        <div className="font-medium">{check.check_name}</div>
        <div className="text-sm text-gray-400">{check.message}</div>
      </div>
    </div>
  );
};
```

### Priority 4: Investment Scoring Widget
```jsx
// frontend/src/components/StockScoreCard.jsx
// Display FIS score from InvestmentScoringAgent
<div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-3">
  <div className="text-base text-white mb-2">Investment Score</div>
  <div className="text-[18px] text-green-400">{score.toFixed(2)}</div>
  <div className="text-xs text-gray-400">{recommendation}</div>
  <div className="text-xs text-blue-400">Confidence: {confidence}</div>
</div>
```

---

## 📚 8. DOCUMENTAȚIE EXTERNĂ

**Complete API Documentation:**
- `UW_API_FINAL_17_ENDPOINTS.md` - UW API reference
- `OPTIONS_ANALYTICS_COMPLETE.md` - Options risk engine docs
- `AUTOMATION_SYSTEM_COMPLETE.md` - Automation features status

**Architecture Docs:**
- `.github/copilot-instructions.md` - Complete project guide
- `FLOWMIND_OVERVIEW.md` - System overview (912 lines)
- `PROJECT_TASKS.md` - Task tracker with priorities

---

## ✅ CONCLUZIE

**Ce avem functional:**
- ✅ Options Risk Engine - validation completă pentru 15 strategii
- ✅ Investment Scoring Agent - AI scoring cu 7 signal components
- ✅ Unusual Whales API - 17 endpoint-uri verificate
- ✅ Options data flow - GEX, chain, expirations, flow summary
- ✅ Mindfolio integration - FIFO tracking, options validation endpoint

**Ce trebuie îmbunătățit:**
- ❌ Options Scanner - replace Barchart cu UW API
- ❌ Earnings Scraper - use UW earnings endpoints
- ⚠️ Frontend integration - validation UI, scoring widget

**Flux de lucru recomandat:**
1. Replace broken scrapers cu UW API wrappers
2. Add earnings router cu 3 endpoint-uri UW
3. Frontend UI pentru options validation
4. Frontend widget pentru investment scoring
5. Dashboard integration pentru toate datele

**Total linii de cod analizate:** ~10,000+ linii across 30+ files
