# FlowMind AI Agent Instructions

**Project:** Options analytics platform with FastAPI backend, React 19 frontend
**Last Updated:** November 1, 2025

**CRITICAL CONTEXT:**
- **Target User:** Single user (Gabriel) - personal trading tool
- **No multi-user support needed** - All features are for personal use only
- **No user authentication system** - Direct access, no login/signup flows
- **Development priority:** Functionality over scalability
- **Deploy once, use daily** - Not a SaaS product

---

## 📋 Table of Contents
1. Session Start Protocol
2. Architecture Patterns
3. Frontend Component Structure
4. BuilderV2 Page - Build Tab
5. Strategy Engine Proposal
6. TradeStation Import System (NEW - Oct 27, 2025)
7. Developer Workflows
8. External APIs
9. Common Pitfalls
10. Key Files

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
5. **Never implement without approval** - Lesson learned: BuilderV2Page (Oct 22)
   required 228-line deletion due to no upfront agreement

### Development Style (Romanian workflow)
- **Concis + vizual**: Arată implementarea, nu doar explica
- **Iterativ**: Livrează mic → verifică → ajustează
- **Transparent**: Raportează probleme imediat
- **Feedback-driven**: Corectează după fiecare ciclu
- **Autonom**: Mergi înainte fără confirmări inutile
- **Personal tool focus**: Build for Gabriel's workflow, not generic users

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
// Three modes:
// TEST_MODE=1 → Shared AsyncTTLDict (test consistency)
// FM_FORCE_FALLBACK=1 → Force in-memory (dev)
// Normal → Try Redis, fallback to in-memory on failure

await get_kv()  // Returns Redis OR AsyncTTLDict
```
**CRITICAL:** Always use `from redis_fallback import get_kv`, NEVER import Redis directly.

### 2. FIFO Position Tracking (`backend/mindfolios.py`)
Tax-compliant realized P&L for options/stock positions.
```python
// BUY adds to lots queue, SELL consumes from front (First-In-First-Out)
// Example: BUY 100@250 + BUY 50@260 → SELL 120@270
// Consumes: 100@250 + 20@260 → Realized $2,200, Remaining 30@260
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

---

## Frontend Component Structure

### Key Patterns
FlowMind uses a **page-based architecture** with reusable components and test pages for validation.

**Directory Structure:**
```
frontend/src/
├── pages/                          // Full-page components (routed)
│   ├── BuilderV2Page.jsx          // Main builder (Build/Optimize/Strategy/Flow tabs)
│   ├── StrategyChartTestPage.jsx  // Test page for StrategyChart validation
│   ├── MindfolioDetailNew.jsx     // Portfolio management
│   ├── FlowPage.jsx, LiveFlowPage.jsx
│   └── Dashboard.jsx, HomePage.jsx
├── components/                     // Reusable components
│   ├── StrategyChart.jsx          // Universal P&L chart (card OR full size)
│   ├── StrategyPicker.jsx         // Strategy selection UI
│   ├── BuilderChart.jsx           // Legacy builder chart
│   └── optimize/                  // Optimize tab components
│       ├── StrategyCard.jsx       // Strategy card (360x180)
│       └── StrategyOptimizeCard.jsx
├── hooks/                          // Custom React hooks
│   ├── useWebSocket.js            // WebSocket connection management
│   ├── useExpirations.js          // Fetch options expirations
│   └── useOptionsSelling.js       // Options selling logic
├── context/                        // React Context providers
│   └── WebSocketContext.jsx       // Global WebSocket state
└── api/                            // API client functions
    └── flow.js                     // Flow data API calls
```

### Component Communication Patterns

**1. Test Pages as Reference Implementations**
```javascript
// StrategyChartTestPage.jsx - ALWAYS check this first for working examples
// Shows card + full sizes, multiple strategies (Bull Call, Bear Call, Long Call, Long Put)
const params = {
  strategyId: 'long_call',
  currentPrice: 221.09,
  strikes: { strike: 220 },
  premiums: { premium: 3787.50 },
  volatility: 0.348,
  daysToExpiry: 420
};
<StrategyChart {...params} size="full" showProbability={false} />
```

**2. Backend URL Configuration - CRITICAL**
```javascript
// ALWAYS use environment variable, NEVER hardcode
const API = process.env.REACT_APP_BACKEND_URL || "";
// Alternative patterns seen in codebase:
const API = window.API_BASE || process.env.REACT_APP_BACKEND_URL || "";
```

**PRODUCTION BUILD REQUIREMENTS (Nov 1, 2025):**
- **MUST create `.env.production` before building for production**
- **MUST set `REACT_APP_BACKEND_URL=http://localhost:8080`** (Caddy proxy URL)
- **NEVER build with empty REACT_APP_BACKEND_URL** - causes runtime errors

```bash
# CORRECT production build process:
cd /opt/flowmind/frontend
echo 'REACT_APP_BACKEND_URL=http://localhost:8080' > .env.production
npm run build
systemctl reload caddy

# WRONG - causes "Cannot read properties of undefined" error:
REACT_APP_BACKEND_URL="" npm run build  # ❌ Empty string breaks API calls
```

**Why `http://localhost:8080`?**
- Frontend calls backend through Caddy reverse proxy (port 8080)
- NOT direct to Docker backend (port 8000)
- Caddyfile proxies `/api/*` to `http://localhost:8000` (Docker backend)
- Frontend → Caddy :8080 → Backend :8000

---

## Production Server Deployment (NEW - Nov 1, 2025)

### Complete Server Setup Steps

**1. Initial Server Setup**
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
apt install -y docker-compose-plugin

# Install Git
apt install -y git
```

**2. Install Caddy with Auth**
```bash
# Add Caddy repository
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list

# Install Caddy
apt update && apt install caddy

# Enable Caddy service
systemctl enable caddy
```

**3. Deploy FlowMind**
```bash
# Clone repository
cd /opt
git clone https://github.com/barbudangabriel-gif/Flowmind.git flowmind
cd flowmind

# Setup Caddy with HTTP Basic Auth
cp Caddyfile.with-auth /etc/caddy/Caddyfile
# Auth: Username=gabriel, Password=FlowMind2025!

# Create .env files (add TradeStation + UW API keys)
cp backend/.env.example backend/.env
nano backend/.env  # Add TS_CLIENT_ID, TS_CLIENT_SECRET, UW_API_TOKEN

# Build frontend
cd frontend
npm install
echo 'REACT_APP_BACKEND_URL=http://localhost:8080' > .env.production
npm run build
cd ..

# Start backend + Redis
docker-compose up -d

# Reload Caddy (will auto-get Let's Encrypt SSL)
systemctl reload caddy
```

**4. Verify Deployment**
```bash
# Check Docker containers
docker ps

# Check Caddy status
systemctl status caddy

# Test HTTPS (will prompt for auth)
curl -u gabriel:FlowMind2025! https://flowmindanalytics.ai/api/health

# View logs
docker-compose logs -f backend
journalctl -u caddy -f
```

**Security Notes:**
- ✅ HTTP Basic Auth protects entire site (frontend + API)
- ✅ Let's Encrypt SSL auto-renewal
- ✅ HSTS, XSS, CORS headers configured
- ✅ SSH key-based authentication (no password login)
- ✅ Docker containers isolated network

**Caddy Password Change:**
```bash
# Generate new password hash
docker run --rm caddy:latest caddy hash-password --plaintext "YOUR_NEW_PASSWORD"

# Update /etc/caddy/Caddyfile with new hash
nano /etc/caddy/Caddyfile

# Reload Caddy
systemctl reload caddy
```

**3. Size-Responsive Components**
```javascript
// StrategyChart.jsx supports two sizes:
<StrategyChart size="card" />   // 360x180 (Optimize tab strategy cards)
<StrategyChart size="full" />   // 1000x400 (Build tab full chart)
```

### Routing & Navigation
```javascript
// frontend/src/App.js - React Router v7
<Route path="/builder" element={<BuilderV2Page />} />
<Route path="/strategy-chart-test" element={<StrategyChartTestPage />} />
<Route path="/mindfolio/:id" element={<MindfolioDetailNew />} />
```

---

## Options Pricing Mathematics - CRITICAL IMPLEMENTATION

### Python 3.12 Indentation Rules
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
GET /stock/{ticker}/option-contracts   // 500+ contracts with IV, OI, volume
GET /stock/{ticker}/spot-exposures     // 300-410 GEX records (PRE-CALCULATED!)
GET /stock/{ticker}/greeks             // Delta, Gamma, Theta, Vega
GET /stock/{ticker}/options-volume     // Volume metrics, call/put ratios
GET /stock/{ticker}/info               // Company metadata, sector, earnings
```

**Market Screening & Alerts (2 endpoints):**
```python
GET /screener/stocks?limit=10          // Unified GEX+IV+Greeks (POWERFUL!)
GET /alerts?noti_type=market_tide      // Real-time market tide events
```

**Insider Trading (5 endpoints):**
```python
GET /insider/trades                    // All insider trades
GET /insider/{ticker}                  // Ticker-specific insider activity
GET /insider/recent                    // Recent insider trades
GET /insider/buys                      // Insider buys only
GET /insider/sells                     // Insider sells only
```

**Dark Pool (2 endpoints):**
```python
GET /darkpool/{ticker}                 // 500 dark pool trades per ticker!
GET /darkpool/recent                   // Recent dark pool activity
```

**Earnings (3 endpoints):**
```python
GET /earnings/{ticker}                 // Earnings history
GET /earnings/today                    // Today's earnings
GET /earnings/week                     // This week's earnings
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

## Options Risk Engine - HIGHEST PRIORITY (NEW - Nov 1, 2025)

### Overview
Comprehensive multi-leg options trade validation system with Greeks analysis, probability calculations, and risk limits.

**Status:** ✅ OPERATIONAL (800+ lines backend, tested with 4 scenarios)  
**Files:** 
- `backend/options_risk_engine.py` - Core validation engine
- `backend/mindfolio.py` - API endpoint (POST /{pid}/validate-options-trade)
- `test_options_risk_engine.py` - Test suite
- `OPTIONS_ANALYTICS_COMPLETE.md` - Complete documentation

### Key Features

#### 1. Strategy Detection & Classification
Automatically identifies 15 multi-leg strategy types:
```python
LONG_CALL, LONG_PUT, SHORT_CALL, SHORT_PUT     # Single leg
CALL_SPREAD, PUT_SPREAD                         # Vertical spreads
IRON_CONDOR, IRON_BUTTERFLY                     # 4-leg strategies
STRADDLE, STRANGLE, BUTTERFLY                   # Volatility plays
CALENDAR_SPREAD, DIAGONAL_SPREAD, RATIO_SPREAD  # Advanced
CUSTOM                                          # Unknown/complex
```

#### 2. Greeks Impact Analysis
Real-time portfolio Greeks calculation with configurable limits:
```python
class GreeksLimits:
    max_delta: 200.0      # Directional exposure limit
    max_gamma: 20.0       # Delta sensitivity limit
    max_vega: 500.0       # IV sensitivity limit ($)
    max_theta: 100.0      # Daily decay limit ($)

# Greeks are additive across positions
portfolio_greeks = current_greeks + new_trade_greeks
# BLOCKER if any limit exceeded
```

#### 3. Probability Analysis
Risk-neutral lognormal distribution for PoP calculations:
```python
# Probability of Profit at expiration
pop = calculate_pop_lognormal(current_price, breakeven, vol, dte)

# Early exit probabilities (50%/25% profit targets)
profit_50_prob = calculate_early_exit_prob(positions, 0.50)

# Returns: pop_expiration, breakeven_prices, profit_50/25_probability
```

#### 4. Risk Check Levels
Four severity levels control trade execution:
```python
class RiskLevel:
    BLOCKER = "BLOCKER"   # Trade cannot proceed (red)
    WARNING = "WARNING"   # Requires acknowledgment (yellow)
    INFO = "INFO"         # Informational only (blue)
    PASS = "PASS"         # No issues (green)
```

#### 5. Validation Checks (10 Total)
- **Greeks Limits:** Delta/Gamma/Theta/Vega portfolio limits
- **Capital Requirements:** Debit cost vs available cash
- **Probability Thresholds:** Min PoP based on risk profile (Conservative: 70%, Moderate: 60%, Aggressive: 50%)
- **IV Rank:** Warning if IV Rank < 50% for credit strategies
- **Correlation:** Symbol concentration (>3 positions warning)
- **Early Assignment:** ITM short options near expiration
- **Expiration Concentration:** >5 positions same expiration date
- **Strike Concentration:** >3 positions same strike
- **Cost/Credit Detection:** Debit vs credit strategy classification
- **Max Loss/Profit:** Strategy P&L boundaries

### API Endpoint Usage

```python
# POST /api/mindfolio/{pid}/validate-options-trade
# Request:
{
  "new_positions": [
    {
      "symbol": "TSLA",
      "option_type": "call",      # "call" or "put"
      "action": "buy",            # "buy" or "sell"
      "strike": 250.0,
      "expiry": "2025-12-01T16:00:00Z",
      "quantity": 1,
      "premium": 500.0,           # Per contract ($5 * 100)
      "volatility": 0.45,         # IV (0.45 = 45%)
      "current_price": 245.0      # Underlying price
    }
  ],
  "risk_profile": "MODERATE"      # CONSERVATIVE, MODERATE, AGGRESSIVE
}

# Response:
{
  "status": "success",
  "validation": {
    "passed": true,               # Overall pass/fail
    "checks": [                   # List of all checks
      {
        "check_name": "capital_requirement",
        "level": "PASS",          # BLOCKER, WARNING, INFO, PASS
        "message": "Capital requirement: $500 (5% of available)",
        "current_value": 500.0,
        "limit_value": 10000.0
      }
    ],
    "strategy_info": {
      "type": "long_call",
      "legs": 1,
      "estimated_cost": 500.0,
      "max_loss": 500.0,
      "max_profit": 0.0            # Unlimited for long call
    },
    "greeks_impact": {
      "current": {...},            # Current portfolio Greeks
      "new_trade": {...},          # New trade Greeks
      "combined": {                # Combined Greeks
        "delta": 0.47,
        "gamma": 0.0128,
        "theta": -0.23,
        "vega": 0.27,
        "rho": 0.08
      }
    },
    "probability_analysis": {
      "pop_expiration": 37.62,     # % probability of profit
      "breakeven_prices": [255.0],
      "profit_50_probability": 70.0,
      "profit_25_probability": 70.0,
      "current_price": 245.0
    }
  }
}
```

### Integration Pattern

```python
# In mindfolio router:
from options_risk_engine import (
    OptionsRiskEngine,
    OptionPosition,
    OptionType,
    ActionType,
    GreeksLimits,
)

# Initialize engine with custom limits
risk_engine = OptionsRiskEngine(greeks_limits=GreeksLimits())

# Validate trade
validation_result = await risk_engine.validate_options_trade(
    new_positions=new_positions,
    existing_positions=existing_options,  # From Redis
    portfolio_cash=mindfolio.cash_balance,
    risk_profile="MODERATE",
)

# Check result
if validation_result.passed:
    # Proceed with trade
else:
    # Show blockers to user
    blockers = [c for c in validation_result.checks if c.level == RiskLevel.BLOCKER]
```

### Frontend Integration (TODO)

**AddPositionModal.jsx** needs validation UI:
```jsx
const RiskCheckRow = ({ check }) => {
  const icon = { BLOCKER: '🚫', WARNING: '⚠️', INFO: 'ℹ️', PASS: '✅' }[check.level];
  const color = {
    BLOCKER: 'text-red-500',
    WARNING: 'text-yellow-500',
    INFO: 'text-blue-500',
    PASS: 'text-green-500',
  }[check.level];
  
  return (
    <div className="flex items-start gap-2 py-2">
      <span className="text-lg">{icon}</span>
      <div className="flex-1">
        <div className={`font-medium ${color}`}>{check.check_name}</div>
        <div className="text-sm text-slate-400">{check.message}</div>
      </div>
    </div>
  );
};
```

### TODO: Future Enhancements
- [ ] IV Rank backend integration (fetch from market data)
- [ ] 5-year options backtest (historical simulation)
- [ ] Custom risk profiles (per-mindfolio limits)
- [ ] Live options positions (fetch existing from Redis)
- [ ] Strategy library (pre-defined click-to-add)
- [ ] Monte Carlo early exit probabilities

**CRITICAL:** Always validate options trades through this engine before execution.

---

## Options Pricing Mathematics - CRITICAL IMPLEMENTATION

### Risk-Neutral Probability Distribution (MANDATORY)

**FlowMind uses mathematically correct risk-neutral pricing theory.**

#### Terminal Distribution (Fixed at Expiration T)

The probability overlay (blue curve) represents the **terminal distribution** at expiration T:

```javascript
// Risk-neutral lognormal PDF at expiration T (DOES NOT change with date slider)
function lognormalPdfTerminal(S, S0, sigma, T, r=0, q=0) {
  if (S <= 0 || T <= 0) return 0;
  const mu = Math.log(S0) + (r - q - 0.5 * sigma * sigma) * T;
  const variance = sigma * sigma * T;
  const x = Math.log(S);
  const exponent = -((x - mu) ** 2) / (2 * variance));
  return (1 / (S * Math.sqrt(2 * Math.PI * variance))) * Math.exp(exponent);
}
```

**Key Properties:**
- **Mode (peak)**: `S_mode = S0 * exp((r - q - 1.5*σ²)*T)` - **NOT at strike!**
- **Median**: `S_median = S0 * exp((r - q - 0.5*σ²)*T)`
- **Distribution is FIXED** - does not change when moving date slider
- Only the option value curve (green) changes with slider using `tau_remaining = T - t_selected`

#### Breeden-Litzenberger Density Extraction (ADVANCED)

When **live options chain data** is available, extract true risk-neutral density:

```javascript
// Extract RN density from option prices (captures real skew/smile)
function extractRNDensityFromChain(optionsChain, F, T, r) {
  // 1. Get forward price from put-call parity
  // F ≈ K + (C - P) * exp(r*T) for ATM strike K

  // 2. Interpolate C(K) across strikes (cubic spline or monotonic)
  const interpolatedCalls = interpolateCallPrices(optionsChain);

  // 3. Compute second derivative: f_T(K) = exp(r*T) * ∂²C/∂K²
  const densityPoints = [];
  for (let K of strikes) {
    const d2C_dK2 = numericalSecondDerivative(interpolatedCalls, K);
    const density = Math.exp(r * T) * d2C_dK2;
    densityPoints.push([K, density]);
  }

  // 4. Normalize over strike range (truncate at tails)
  const totalArea = trapezoidalIntegration(densityPoints);
  return densityPoints.map(([K, f]) => [K, f / totalArea]);
}
```

**When to use:**
- ✅ **Breeden-Litzenberger**: When live options chain available (captures IV skew/smile)
- ✅ **Lognormal fallback**: When no chain data or for smooth theoretical calculations
- **FlowMind implementation**: Start with lognormal (stable, fast). Add Breeden-Litzenberger later when chain integration complete.

#### Chance of Profit (PoP) Calculation

For Long Call, probability of profit at expiration:

```javascript
// P(S_T ≥ breakeven) where breakeven = K + premium_per_share
function probAboveTerminalPct(S0, X, sigma, T, r=0, q=0) {
  const variance = sigma * Math.sqrt(T);
  const d2 = (Math.log(S0 / X) + (r - q - 0.5 * sigma * sigma) * T) / variance;
  return normCDF(d2) * 100; // Return percentage
}

// Breakeven price for Long Call
const breakeven = strike + (premium / 100); // premium per share
const chanceOfProfit = probAboveTerminalPct(S0, breakeven, sigma, T, r, q);
```

#### Black-Scholes Option Valuation

```javascript
function blackScholesCall(S, K, r, q, sigma, tau) {
  if (tau <= 0) return Math.max(S - K, 0); // At expiration

  const d1 = (Math.log(S/K) + (r - q + 0.5*sigma*sigma)*tau) / (sigma*Math.sqrt(tau));
  const d2 = d1 - sigma*Math.sqrt(tau);

  return S * Math.exp(-q*tau) * normCDF(d1) - K * Math.exp(-r*tau) * normCDF(d2);
}

// P&L calculation
function pnlAtPrice(S, K, sigma, tauRemaining, premium, r=0, q=0) {
  const optionValue = blackScholesCall(S, K, r, q, sigma, tauRemaining) * 100;
  return optionValue - premium; // Per contract
}
```

#### UI Implementation Guidelines

**Date Slider Behavior:**
- **Slider value** (0-420 DTE): Represents time FROM today
- **Probability distribution**: Uses **fixed T** (total time to expiration) - never changes
- **Option value curve**: Uses `tau_remaining = T - (sliderValue/365)` - changes smoothly
- **At expiration** (slider at 420): Option value = payoff (intrinsic value only)
- **At today** (slider at 0): Option value = full Black-Scholes with T

**Visual Elements:**
- **Blue curve**: Terminal probability distribution (fixed)
- **Green curve**: Option value at selected date (dynamic)
- **Orange dashed**: Payoff at expiration (reference, hidden when at expiration)
- **White dashed**: Strike price (fixed vertical line)
- **Cyan line**: Breakeven price

**Sanity Checks (Example: AMZN)**
```
S0 = 224.21, K = 220, T ≈ 1.2y, σ ≈ 0.344, r ≈ q ≈ 0
Expected results:
- Premium per share: ~$39.33
- Breakeven: ~$259.33
- Chance of Profit: ~28-29%
- Mode (peak of distribution): ~$181-182 (NOT at strike!)
```

**CRITICAL: Never "cosmetically" adjust distributions to look pretty. Use mathematically correct risk-neutral formulas.**

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
- **Colors:** Profit (cyan 06b6d4), Loss (red dc2626), gradients 0.85 opacity

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

## Mindfolio Templates System (NEW - Nov 2, 2025)

### Overview
**Status:** ✅ Complete and operational
**Files:** 
- `backend/mindfolio.py` (GET /api/mindfolio/templates endpoint)
- `frontend/src/components/MindfolioTemplateModal.jsx` (245 lines)
- `frontend/src/pages/MindfoliosList.jsx` (modal integration)

**Purpose:** Quick mindfolio creation with pre-configured templates for common trading strategies

### Available Templates

#### 1. 📈 Day Trading ($25,000)
```python
{
  "id": "template_day_trading",
  "icon": "📈",
  "risk_level": "HIGH",
  "starting_balance": 25000.0,  # PDT rule minimum
  "modules": [
    {"module": "MOMENTUM_SCANNER", "budget": 15000, "max_risk": 500, "daily_limit": 1500},
    {"module": "BREAKOUT_TRADER", "budget": 10000, "max_risk": 300, "daily_limit": 1000}
  ],
  "recommended_for": "Experienced traders with time to monitor markets daily"
}
```

#### 2. 💰 Options Selling ($50,000)
```python
{
  "id": "template_options_selling",
  "icon": "💰",
  "risk_level": "MEDIUM",
  "starting_balance": 50000.0,
  "modules": [
    {"module": "SELL_PUTS_ENGINE", "budget": 30000, "max_risk": 1000, "daily_limit": 2000},
    {"module": "COVERED_CALLS", "budget": 20000, "max_risk": 500, "daily_limit": 1000}
  ],
  "recommended_for": "Income-focused investors seeking monthly cash flow"
}
```

#### 3. 🏦 Long-term Investing ($10,000)
```python
{
  "id": "template_longterm",
  "icon": "🏦",
  "risk_level": "LOW",
  "starting_balance": 10000.0,
  "modules": [
    {"module": "VALUE_INVESTOR", "budget": 7000, "max_risk": 1000, "daily_limit": 0},
    {"module": "DIVIDEND_COLLECTOR", "budget": 3000, "max_risk": 500, "daily_limit": 0}
  ],
  "recommended_for": "Passive investors with long-term horizon (5+ years)"
}
```

#### 4. 📝 Blank Template ($10,000)
```python
{
  "id": "template_blank",
  "icon": "📝",
  "risk_level": "CUSTOM",
  "starting_balance": 10000.0,
  "modules": [],  # Empty - user customizes
  "recommended_for": "Advanced users who want full control"
}
```

### Backend Implementation

**Endpoint:** `GET /api/mindfolio/templates`

```python
# backend/mindfolio.py (line ~520)
@router.get("/templates")
async def get_mindfolio_templates():
    """
    Get predefined mindfolio templates for quick setup.
    Returns 4 templates with icon, risk_level, starting_balance, modules.
    """
    templates = [
        {
            "id": "template_day_trading",
            "name": "Day Trading",
            "description": "Active trading with quick entries/exits...",
            "icon": "📈",
            "starting_balance": 25000.0,
            "modules": [...],
            "recommended_for": "...",
            "risk_level": "HIGH"
        },
        # ... 3 more templates
    ]
    return {"status": "success", "templates": templates, "count": len(templates)}
```

**Response Structure:**
```json
{
  "status": "success",
  "count": 4,
  "templates": [
    {
      "id": "template_day_trading",
      "name": "Day Trading",
      "description": "Active trading with quick entries/exits. Focus on momentum and technical analysis.",
      "icon": "📈",
      "starting_balance": 25000.0,
      "modules": [
        {
          "module": "MOMENTUM_SCANNER",
          "budget": 15000.0,
          "max_risk_per_trade": 500.0,
          "daily_loss_limit": 1500.0,
          "autotrade": false
        }
      ],
      "recommended_for": "Experienced traders with time to monitor markets daily",
      "risk_level": "HIGH"
    }
  ]
}
```

### Frontend Implementation

**Modal Component:** `frontend/src/components/MindfolioTemplateModal.jsx` (245 lines)

**Features:**
- **Template Selection Grid:** 4 cards with icon, risk level badge, starting balance, modules preview
- **Customization Form:** Name input, balance display, modules preview
- **Auto-fetch:** Fetches templates when modal opens
- **Dark Theme:** Slate-800/900 backgrounds, tailwind CSS
- **Lucid Emoji:** Only clean unicode emoji (no custom icons)
- **Risk Level Badges:**
  - HIGH: Red badge (`bg-red-500/20 text-red-400 border-red-500/30`)
  - MEDIUM: Yellow badge (`bg-yellow-500/20 text-yellow-400`)
  - LOW: Green badge (`bg-green-500/20 text-green-400`)
  - CUSTOM: Gray badge (`bg-gray-500/20 text-gray-400`)

**Usage Pattern:**
```jsx
// MindfoliosList.jsx
import MindfolioTemplateModal from '../components/MindfolioTemplateModal';

<button onClick={() => setShowTemplateModal(true)}>
  ✨ Create Mindfolio
</button>

<MindfolioTemplateModal
  isOpen={showTemplateModal}
  onClose={() => setShowTemplateModal(false)}
  onCreateFromTemplate={async (templateData) => {
    await pfClient.create(templateData.name, templateData.starting_balance);
    const data = await pfClient.list();
    setItems(data);
  }}
/>
```

**Flow:**
1. User clicks "✨ Create Mindfolio" button
2. Modal opens with 4 template cards
3. User selects template → customization form appears
4. User edits name (balance + modules from template)
5. User clicks "✓ Create Mindfolio"
6. API call: `POST /api/mindfolio` with template data
7. Modal closes, list refreshes

### Module Allocation from Templates

**IMPORTANT:** Templates define modules BUT don't auto-allocate them yet.

**Current behavior:**
- Template creates mindfolio with `starting_balance` and empty `modules: []`
- User must manually allocate modules after creation

**Future enhancement (TODO):**
```python
# In create_mindfolio endpoint
async def create_mindfolio(body: MindfolioCreate):
    mindfolio = Mindfolio(
        id=f"mf_{uuid.uuid4().hex[:12]}",
        name=body.name,
        cash_balance=body.starting_balance,
        starting_balance=body.starting_balance,
        modules=body.modules,  # Accept modules from template
        ...
    )
    # TODO: Validate module budgets don't exceed cash_balance
    await pf_put(mindfolio)
```

### Design Guidelines (Applied)

**Colors:**
- Background: `bg-slate-900`, `bg-slate-800/50`
- Borders: `border-slate-700`
- Text: `text-white` (primary), `text-gray-400` (secondary)
- Accents: `text-blue-400` (interactive), `text-green-400` (money)

**Fonts:**
- No custom fonts - system default
- Font sizes: `text-xs`, `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`
- Never use inline font-size styles

**Emoji:**
- Lucid unicode only: 📈 💰 🏦 📝 ✨ ✓ ✕
- No custom icon libraries (no react-icons, no FontAwesome)

**Spacing:**
- Gap: `gap-2`, `gap-3`, `gap-4`, `gap-6`
- Padding: `p-2`, `p-3`, `p-4`, `p-6`
- Margin: `mb-1`, `mb-2`, `mb-3`, `mb-4`

### Testing Checklist

- [x] Backend endpoint returns 4 templates
- [x] Frontend modal opens on button click
- [x] Template cards display correctly (icon, risk, balance, modules)
- [x] Customization form shows template data
- [x] Create button calls API with template data
- [ ] Modal closes after creation
- [ ] List refreshes with new mindfolio
- [ ] Modules are saved to mindfolio (currently not implemented)

### Known Limitations

1. **Modules not auto-allocated:** Template modules are shown but not saved yet
2. **No module validation:** Backend doesn't validate module budgets vs cash_balance
3. **No template persistence:** Templates are hardcoded (not in database)
4. **No custom templates:** User can't create their own templates

### Future Enhancements

- [ ] Save modules from template to mindfolio
- [ ] Validate module budgets don't exceed cash_balance
- [ ] Allow users to create custom templates
- [ ] Store templates in database
- [ ] Template versioning (update templates without breaking existing mindfolios)
- [ ] Template marketplace (share templates with community)

---

## TradeStation Import System

### Overview (Oct 27, 2025 - 19:35 UTC)
**Status:** ✅ Full import system operational  
**Files:** 
- `backend/mindfolio.py` (import-from-tradestation, import-ytd endpoints)
- `frontend/src/pages/MindfolioDetailNewV2.jsx` (YTD import UI)
- `frontend/src/services/mindfolioClient.js` (importYTD method)

**Purpose:** Import live positions AND complete YTD transaction history from TradeStation

### Import Types

#### 1. Initial Import (Current Positions)
**Endpoint:** `POST /api/mindfolio/import-from-tradestation`
**Purpose:** Create new mindfolio with current positions snapshot
**Flow:**
```
1. User → /mindfolio/import page
2. OAuth: https://{codespace}-8000.app.github.dev/api/ts/login
3. Callback → frontend_url/mindfolio/import (3s auto-redirect)
4. Select account → POST /api/mindfolio/import-from-tradestation
5. Backend:
   - Create Mindfolio (cash_balance from balances API)
   - Fetch positions (40+ positions for account 11775499)
   - Create BUY transactions for each position
   - Calculate FIFO positions
   - Backup to JSON
```

#### 2. YTD Transaction History Import (NEW - Oct 27, 2025)
**Endpoint:** `POST /api/mindfolio/{id}/import-ytd`
**Purpose:** Import ALL filled orders since 2025-01-01 for complete P&L tracking
**Flow:**
```
1. User clicks "Import YTD Data" in MindfolioDetailNewV2
2. POST /api/mindfolio/{id}/import-ytd with account_id
3. Backend:
   - Get TradeStation token (token_data.get("access_token"))
   - Fetch orders: GET /brokerage/accounts/{id}/orders?since=2025-01-01T00:00:00Z
   - Pagination: Loop while NextToken exists (5300+ orders support)
   - Filter: Only FILLED orders (Status: "FLL" or "FILLED")
   - Extract: Symbol, FilledQuantity, FilledPrice, TradeAction
   - Determine side: BUY (BUY/BUYTOOPEN/BUYTOCOVER) or SELL
   - Create Transaction for each order
   - Recalculate FIFO positions
   - Return: transactions_imported, date_range, symbols, positions_recalculated
4. Frontend:
   - Show success alert with statistics
   - Auto-reload mindfolio data
   - Switch to Transactions tab
```

**Code Implementation:**
```python
# backend/mindfolio.py - import-ytd endpoint
token_data = await get_valid_token(user_id)
token = token_data.get("access_token")  # CRITICAL: Extract from dict!

# Pagination support for 5300+ orders
while orders_data.get("NextToken"):
    params["pageToken"] = orders_data["NextToken"]
    orders_resp = requests.get(orders_url, headers=headers, params=params)
    all_orders.extend(orders_data.get("Orders", []))
```

### Known Issues (CRITICAL)

1. **Positions backup fixed (Oct 27):**
   - ✅ `backup_mindfolio_to_disk()` now async, fetches positions from Redis
   - ✅ Positions included in JSON backup
   - ✅ `restore_mindfolio_from_disk()` restores positions to Redis

2. **YTD Import Issues (Pending Fix):**
   - ⚠️ Orders imported with empty symbols (`symbol=""`, `qty=0`)
   - Cause: TradeStation order structure may differ
   - Debug: Added logging `logger.info(f"Sample order: {json.dumps(filled_orders[0])}")`
   - Fix: Need to inspect actual order structure and adjust field extraction

3. **Redis volatility:** Data lost on restart
   - Mitigation: Auto-restore from JSON backups on startup (TODO)
   - Config: 3600s/1key, 300s/100keys, 60s/10000keys

4. **Codespaces port reset:** Port 8000 reverts to private on reload
   - Fix: VS Code → PORTS tab → port 8000 → Public
   - Permanent solution: Deploy to Railway/VPS

5. **Token expiry:** TradeStation OAuth token expires (60 minutes)
   - Solution: Re-auth at https://{codespace}-8000.app.github.dev/api/ts/login
   - Token stored in Redis/fallback cache (60-day refresh token)

### Data Model
```python
# Mindfolio (backend/mindfolio.py line 94-116)
class Mindfolio(BaseModel):
    id: str
    name: str
    broker: str = "TradeStation"
    environment: str = "SIM"  # "SIM" | "LIVE"
    account_type: str = "Equity"
    account_id: Optional[str] = None
    cash_balance: float
    starting_balance: float = 10000.0
    status: str = "ACTIVE"
    modules: List[ModuleAllocation] = []
    created_at: str
    updated_at: str
    # NOTE: positions NOT in model - stored separately in Redis!

# Position (line 74-79)
class Position(BaseModel):
    symbol: str
    qty: float
    cost_basis: float
    avg_cost: float

# Transaction (line 81-92)
class Transaction(BaseModel):
    id: str
    mindfolio_id: str
    datetime: str
    symbol: str
    side: str  # "BUY" | "SELL"
    qty: float
    price: float
    fee: float = 0.0
    notes: str = ""
    created_at: str
```

### Redis Keys
```python
key_mindfolio(id) = f"mindfolio:{id}"
key_mindfolio_list() = "mindfolios"
key_transaction(tid) = f"tx:{tid}"
key_mindfolio_transactions(pid) = f"mf:{pid}:transactions"
key_mindfolio_positions(pid) = f"mf:{pid}:positions"
```

### JSON Backup System
```python
# backend/mindfolio.py line 163-195
BACKUP_DIR = Path("/workspaces/Flowmind/data/mindfolios")

def backup_mindfolio_to_disk(mindfolio: Mindfolio):
    """Auto-called by pf_put() after every mindfolio save"""
    backup_file = BACKUP_DIR / f"{mindfolio.id}.json"
    json_data = json.dumps(mindfolio.dict(), indent=2)  # Pydantic v2: use .dict(), not .json(indent=2)
    backup_file.write_text(json_data)
    # NOTE: Does NOT include positions! Positions stored separately in Redis.

def restore_mindfolio_from_disk(mindfolio_id: str):
    """Manual restore from backup JSON"""
    backup_file = BACKUP_DIR / f"{mindfolio_id}.json"
    if backup_file.exists():
        data = json.loads(backup_file.read_text())
        return Mindfolio(**data)
    return None

# Restore endpoint: POST /api/mindfolio/restore-from-backup
# Scans backup dir, restores all JSON files to Redis
```

### FIFO Position Calculation
```python
# backend/mindfolio.py line 221-270
async def calculate_positions_fifo(mindfolio_id: str) -> List[Position]:
    """Calculate current positions using FIFO method"""
    transactions = await get_mindfolio_transactions(mindfolio_id)
    lots: dict[str, list[dict]] = {}  # {symbol: [{"qty": float, "price": float}, ...]}
    
    for tx in transactions:
        if tx.side == "BUY":
            # Add to lots
            cost_per_share = tx.price + (tx.fee / tx.qty if tx.qty > 0 else 0)
            lots[symbol].append({"qty": tx.qty, "price": cost_per_share})
        elif tx.side == "SELL":
            # Consume lots FIFO
            qty_to_sell = tx.qty
            while qty_to_sell > 0 and lots[symbol]:
                lot = lots[symbol][0]
                if lot["qty"] <= qty_to_sell:
                    qty_to_sell -= lot["qty"]
                    lots[symbol].pop(0)  # Consume entire lot
                else:
                    lot["qty"] -= qty_to_sell
                    qty_to_sell = 0
    
    # Return remaining positions
    positions = []
    for symbol, remaining_lots in lots.items():
        if remaining_lots:
            total_qty = sum(lot["qty"] for lot in remaining_lots)
            total_cost = sum(lot["qty"] * lot["price"] for lot in remaining_lots)
            positions.append(Position(
                symbol=symbol,
                qty=round2(total_qty),
                cost_basis=round2(total_cost),
                avg_cost=round2(total_cost / total_qty)
            ))
    return sorted(positions, key=lambda x: x.symbol)
```

### Import Endpoint Implementation
```python
# backend/mindfolio.py line 608-760
@router.post("/import-from-tradestation")
async def import_full_tradestation_mindfolio(body: dict, ...):
    # 1. Get TradeStation token from cache
    token_data = await get_valid_token(user_id)
    
    # 2. Fetch balances
    balance_url = f"{TS_API_BASE}/brokerage/accounts/{account_id}/balances"
    balance_response = requests.get(balance_url, headers={"Authorization": f"Bearer {token}"})
    cash_balance = float(balances_list[0].get("CashBalance", 0))
    
    # 3. Fetch positions
    positions_url = f"{TS_API_BASE}/brokerage/accounts/{account_id}/positions"
    positions_response = requests.get(positions_url, headers=...)
    positions_list = positions_data.get("Positions", [])  # 40+ positions
    
    # 4. Create mindfolio
    new_mindfolio = Mindfolio(
        id=f"mf_{secrets.token_hex(6)}",
        name=f"TradeStation - {account_id}",
        broker="TradeStation",
        environment=os.getenv("TRADESTATION_MODE", "SIMULATION"),
        cash_balance=cash_balance,
        ...
    )
    await pf_put(new_mindfolio)  # Triggers backup (without positions!)
    
    # 5. Create BUY transactions for each position
    cli = await get_kv()
    for pos in positions_list:
        tx = Transaction(
            id=f"tx_{secrets.token_hex(6)}",
            mindfolio_id=new_mindfolio.id,
            symbol=pos.get("Symbol"),
            side="BUY",
            qty=float(pos.get("Quantity")),
            price=float(pos.get("AveragePrice")),
            ...
        )
        # Save transaction
        await cli.set(key_transaction(tx.id), tx.model_dump_json())
        
        # Update transaction list
        tx_list_raw = await cli.get(key_mindfolio_transactions(new_mindfolio.id)) or "[]"
        tx_ids = json.loads(tx_list_raw)
        tx_ids.append(tx.id)
        await cli.set(key_mindfolio_transactions(new_mindfolio.id), json.dumps(tx_ids))
    
    # 6. Calculate positions from transactions
    calculated_positions = await calculate_positions_fifo(new_mindfolio.id)
    
    # 7. Save positions to Redis
    positions_json = json.dumps([pos.dict() for pos in calculated_positions])
    await cli.set(key_mindfolio_positions(new_mindfolio.id), positions_json)
    
    # 8. Re-save mindfolio (triggers backup again, still without positions)
    refreshed_mindfolio = await pf_get(new_mindfolio.id)
    if refreshed_mindfolio:
        await pf_put(refreshed_mindfolio)
    
    return {
        "status": "success",
        "mindfolio": refreshed_mindfolio.dict(),
        "positions_imported": len(calculated_positions),
        ...
    }
```

### Debugging Commands
```bash
# Check mindfolios in Redis
curl -s http://localhost:8000/api/mindfolio -H "X-User-ID: default" | jq

# Check backup files
ls -lh /workspaces/Flowmind/data/mindfolios/
cat /workspaces/Flowmind/data/mindfolios/mf_*.json | jq

# Check Redis keys
docker exec flowmind-redis-1 redis-cli KEYS "*"
docker exec flowmind-redis-1 redis-cli GET "mf:{id}:positions"

# Check transactions
docker exec flowmind-redis-1 redis-cli GET "mf:{id}:transactions"
docker exec flowmind-redis-1 redis-cli GET "tx:{transaction_id}"

# Manual restore from backup
curl -X POST http://localhost:8000/api/mindfolio/restore-from-backup -H "X-User-ID: default"

# Delete mindfolio (also deletes backup)
curl -X DELETE http://localhost:8000/api/mindfolio/{id} -H "X-User-ID: default"
```

### TODO: Fix Positions in Backup
**Problem:** Backup JSON only contains Mindfolio fields, not positions (stored separately)  
**Solutions:**
1. **Option A:** Add positions to Mindfolio model (breaks separation of concerns)
2. **Option B:** Modify backup_mindfolio_to_disk() to fetch + include positions in JSON
3. **Option C:** Separate positions backup file: {id}_positions.json
4. **Option D:** Auto-restore from backup on backend startup (workaround for Redis volatility)

**Recommended:** Option B - Fetch positions in backup function:
```python
def backup_mindfolio_to_disk(mindfolio: Mindfolio) -> None:
    try:
        # Get positions from Redis
        cli = await get_kv()  # Need to make function async!
        positions_json = await cli.get(key_mindfolio_positions(mindfolio.id)) or "[]"
        positions = json.loads(positions_json)
        
        # Create backup dict with positions
        backup_data = mindfolio.dict()
        backup_data["positions"] = positions
        
        backup_file = BACKUP_DIR / f"{mindfolio.id}.json"
        backup_file.write_text(json.dumps(backup_data, indent=2))
    except Exception as e:
        logger.error(f"Failed to backup mindfolio {mindfolio.id}: {e}")
```

### Codespaces Port Visibility Issue
**Problem:** Port 8000 reverts to private on backend reload/suspend  
**Symptoms:** CORS errors, "Failed to fetch", 401 on public URL  
**Fix:** VS Code → PORTS tab → port 8000 → right click → Port Visibility → Public  
**Permanent solution:** Deploy to Railway/VPS/Windows Docker Desktop (stable URLs)

### OAuth Token Expiry
**Token lifetime:** 60 minutes (TradeStation limit)  
**Symptoms:** Import fails with 401, "Not authenticated"  
**Fix:** Re-authenticate: https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/ts/login  
**Storage:** Redis/fallback cache (key: `ts_token:{user_id}`, TTL: 60 days for refresh token)

---

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
// OAuth Credentials
TS_CLIENT_ID=YOUR_TRADESTATION_CLIENT_ID
TS_CLIENT_SECRET=YOUR_TRADESTATION_CLIENT_SECRET
TS_REDIRECT_URI=https://your-domain.com/api/oauth/tradestation/callback

// CRITICAL: Both variables required for mode switching
TS_MODE=LIVE
TRADESTATION_MODE=LIVE  # app/routers/tradestation.py checks this!

// API URLs (LIVE mode)
TS_BASE_URL=https://api.tradestation.com
TS_AUTH_URL=https://signin.tradestation.com/authorize
TS_TOKEN_URL=https://signin.tradestation.com/oauth/token

// Scopes (verified working)
TS_SCOPE=openid offline_access MarketData ReadAccount Trade OptionSpreads Matrix

// Token settings
TS_HTTP_TIMEOUT=15
TS_REFRESH_SKEW=60
```

#### CRITICAL: OAuth Requirements
1. **`audience` parameter REQUIRED** - Without this, API returns 401
   ```python
   // backend/app/services/tradestation.py - auth_url()
   params = {
       "response_type": "code",
       "client_id": TS_CLIENT_ID,
       "audience": "https://api.tradestation.com",  // MUST INCLUDE!
       "redirect_uri": redirect_uri,
       "scope": TS_SCOPE,
       "state": state,
   }
   ```

2. **Async token persistence** - Tokens stored in Redis/fallback cache
   ```python
   // All token functions are async:
   await set_token(user_id, token)
   token = await get_cached_token(user_id)
   token = await get_valid_token(user_id)  // Auto-refreshes if needed
   ```

3. **Mode switching** - `TRADESTATION_MODE` controls API base URL
   ```python
   // backend/app/routers/tradestation.py
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
// Accounts (returns LIVE or SIM based on TRADESTATION_MODE)
GET /api/tradestation/accounts
Response: {"Accounts": [{"AccountID": "11775499", "AccountType": "Margin", ...}]}

// Balances
GET /api/tradestation/accounts/{account_id}/balances
Response: {"Balances": [{"CashBalance": "...", "BuyingPower": "...", ...}]}

// Positions (real-time P&L)
GET /api/tradestation/accounts/{account_id}/positions
Response: {"Positions": [{"Symbol": "TSLA", "Quantity": 100, "UnrealizedProfitLoss": "11281.97", ...}]}

// Options Chain (NEW - Oct 24, 2025)
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
// backend/server.py
from app.routers.tradestation import router as ts_data_router
app.include_router(ts_data_router, prefix="/api")  // Mounts /api/tradestation/*
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

// Quality gates (CI/CD compliance):
pytest -q --maxfail=1 --disable-warnings
ruff check . && ruff format --check
mypy . --ignore-missing-imports
bandit -ll -r . -x tests
pip-audit --strict
```

### Frontend Development
```bash
cd frontend
npm start  // Uses Craco (craco.config.js)

// Quality gates:
npm run lint
npm run build
npm audit --audit-level=high
```

### Docker Compose
```bash
docker-compose up  // Backend :8000, Redis :6379
// Uses: python -m uvicorn server:app --reload (not app.main:app)
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
// Backend (backend/.env)
REDIS_URL=redis://localhost:6379/0
FM_FORCE_FALLBACK=1              // Force in-memory cache
FM_REDIS_REQUIRED=1              // Fail if Redis unavailable
TEST_MODE=1                      // Shared in-memory for tests
MONGO_URL=mongodb://...
TS_CLIENT_ID/TS_CLIENT_SECRET/TS_REDIRECT_URI
UW_API_TOKEN or UNUSUAL_WHALES_API_KEY

// Frontend (frontend/.env.local)
REACT_APP_BACKEND_URL=http://localhost:8000  // NEVER hardcode!
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
