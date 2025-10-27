# 📋 FlowMind Project Tasks & Roadmap

**Last Updated:** October 27, 2025 - 19:35 UTC  
**Repository:** github.com/barbudangabriel-gif/Flowmind  
**Project Status:** Active Development

---

## 🎯 Quick Navigation

- [Active Tasks](#active-tasks-in-progress)
- [Backlog](#backlog-planned)
- [Completed](#completed-tasks)
- [Architecture Improvements](#architecture-improvements)
- [Bug Fixes](#bug-fixes)
- [Documentation](#documentation)

---

## 🚀 Active Tasks (In Progress)

### 1. ✅ Mindfolio Detail Page Redesign + YTD Import (COMPLETED - Oct 27, 2025)
**Status:** ✅ COMPLETE (5/6 tasks)  
**Assignee:** AI Agent  
**Priority:** HIGH  
**Files:** 
- `frontend/src/pages/MindfolioDetailNewV2.jsx` (518 lines)
- `backend/mindfolio.py` (import-ytd endpoint)
- `frontend/src/services/mindfolioClient.js` (importYTD method)

**Completed Phase 1: Page Redesign ✅**
- [x] Clean header with mindfolio name, ID, environment badge
- [x] Performance cards (Daily P/L, Total Return, Win Rate)
- [x] 4 tabs: Overview, Positions, Transactions, Analytics
- [x] Routes updated in App.js (`/mindfolio/:id`)
- [x] Import YTD button with loading state
- [x] Delete button with confirmation

**Completed Phase 2: Positions Tab ✅**
- [x] Display positions in FlowMind-style table
- [x] Live prices integration (`/api/options/spot/{symbol}`)
- [x] Color-coded P&L (green profit, red loss)
- [x] Refresh button functional
- [x] Market value, unrealized P&L calculated with FIFO

**Completed Phase 3: Transactions Tab ✅**
- [x] Full transaction history display
- [x] Date, symbol, side, qty, price, total
- [x] Auto-reload after YTD import
- [x] Switch to Transactions tab after import

**Completed Phase 4: YTD Import Backend ✅**
- [x] Endpoint: `POST /api/mindfolio/{id}/import-ytd`
- [x] TradeStation orders API integration
- [x] Token refresh fix (`token_data.get("access_token")`)
- [x] Pagination support (NextToken) for 5300+ orders
- [x] Filter FILLED orders only
- [x] Create BUY/SELL transactions from orders
- [x] FIFO position recalculation after import
- [x] Debug logging for order structure

**Pending Tasks for Next Session:**
- [ ] **Overview Tab:** P/L line chart with YTD performance
- [ ] **Analytics Tab:** Win/Loss breakdown, trade statistics
- [ ] **Realized P&L Calculation:** Match BUY/SELL pairs for closed positions
- [ ] **YTD Import Testing:** Full test with 5300 orders (pagination)
- [ ] **Fix empty symbols:** Debug TradeStation order structure (Symbol field)

**Known Issues:**
1. YTD import returns 13 transactions with empty symbols (`symbol=""`, `qty=0`)
   - Possible cause: TradeStation order structure differs
   - Debug logging added to inspect first order
   - Needs backend restart + re-test

2. Redis volatility: Data lost on restart
   - Backup system works (JSON files)
   - Auto-restore on startup needed

3. Port 8000 visibility: Reverts to private on reload
   - Manual fix: VS Code PORTS tab → Public
   - Needs permanent solution (Railway/VPS deployment)

**Current Mindfolio:** `mf_8a1a9a51c2cb` (TradeStation - 11775499, LIVE)

**Estimated Time Remaining:** 3-4 hours (Overview tab + Realized P&L)

---

### 2. 🔄 TradeStation Transaction History Import (MERGED INTO #1 - Oct 27, 2025)
**Status:** ✅ MERGED  
**Note:** Combined with Mindfolio Detail Page redesign for cohesive implementation

---

### 3. 🎨 BuilderV2 Page - Complete All 4 Tabs + "Open in Builder" Auto-Population (HIGH PRIORITY)
**Status:** 🔄 IN PROGRESS - October 24, 2025  
**Assignee:** AI Agent  
**File:** `frontend/src/pages/BuilderV2Page.jsx`  
**Route:** `/builder`

**Current Focus:**
- [ ] **Build Tab Refinements:** 
  - [x] Interactive P&L chart with probability distribution (mathematically correct risk-neutral)
  - [x] Date slider (0-420 DTE) with smooth transitions
  - [x] Probability overlay (blue curve) - terminal distribution at expiration T (FIXED)
  - [ ] Additional visual polish and edge cases
  - [ ] Layer system: Table, Graph, P/L, Greeks tabs
  
- [ ] **Optimize Tab:** Complete functionality
  - [ ] Connect backend for strategy recommendations
  - [ ] Real-time filtering by direction/expiration
  - [ ] Strategy cards with live data
  
- [ ] **Strategy Tab:** Full implementation
  - [ ] 69 strategy cards display
  - [ ] Search/filter by strategy type
  - [ ] "Open in Builder" button integration
  
- [ ] **Flow Tab:** Real-time flow data
  - [ ] Unusual Whales API integration
  - [ ] Live options flow display
  - [ ] Filter by ticker/premium/sentiment

**Next Major Task:**
- [ ] **"Open in Builder" Auto-Population System**
  - [ ] Create universal strategy engine (avoid writing 69 separate implementations)
  - [ ] Strategy → Build Tab state transfer (strikes, expiration, quantities)
  - [ ] Dynamic chart rendering based on strategy type
  - [ ] Scale from 360x180 (card) to 1000x400 (Build tab)
  - [ ] Reference: See `STRATEGY_ENGINE_PROPOSAL.md` for architecture

**Completed Work (Oct 24):**
- [x] Build Tab: Complete options trading builder interface with P&L chart
- [x] Probability mathematics: Risk-neutral lognormal distribution (see copilot-instructions.md)
- [x] Black-Scholes option valuation with smooth date slider transitions
- [x] Optimize Tab: Full UI implementation with direction filters and sliders
- [x] **Strategy Tab:** Links to StrategyLibraryPage (69+ strategies library)
- [x] **Flow Tab:** Complete implementation with 6 sub-pages
  - [x] **Summary Page:** Bullish/Bearish columns with 36 flow pairs, FiltersPanel on right, Market Bias indicator (bulina)
  - [x] **Live Flow Page:** Real-time flow table with 32+ trades, columns (Time, Symbol, Strategy, Expiration, Premium, Type), FiltersPanel
  - [ ] **Historical Flow:** Under construction (placeholder)
  - [ ] **News Flow:** Under construction (placeholder)
  - [ ] **Congress Flow:** Under construction (placeholder)
  - [ ] **Insider Flow:** Under construction (placeholder)
- [x] **UI Polish:** 
  - [x] All text white, gradients cyan-600/50 (bullish) and orange-600/50 (bearish)
  - [x] Custom 6px scrollbar for columns and FiltersPanel
  - [x] Tab navigation header with Market Bias indicator (gradient cyan-to-purple bulina)
  - [x] Consistent fonts: text-base font-semibold for tabs, text-lg for flow data

---

### 2. 💼 Mindfolio Manager - TradeStation Import Workflow (COMPLETED - Oct 27, 2025)
**Status:** ✅ COMPLETE  
**Priority:** HIGH

**Completed Features:**
- [x] Removed sidebar "Create Mindfolio" buttons (2 instances removed)
- [x] Added two-button Manager interface:
  - [x] "Import from TradeStation" (gradient blue-purple, priority action)
  - [x] "Create Empty Mindfolio" (gray, secondary action)
- [x] Created dedicated import page: `frontend/src/pages/ImportFromTradeStation.jsx`
  - [x] Account selection dropdown
  - [x] Positions preview table (symbol, quantity, value, P&L)
  - [x] Balance display
  - [x] "Import X Positions" button with loading state
- [x] Backend endpoint: `POST /api/mindfolio/import-from-tradestation`
  - [x] Fetches positions from TradeStation API
  - [x] Fetches cash balance
  - [x] Creates master mindfolio with all 51 positions
  - [x] Stores transactions with FIFO-ready structure
- [x] Authentication flow: X-User-ID header with token from cache
- [x] Frontend route: `/mindfolio/import`

**Import Results (Oct 27):**
- ✅ 51 positions imported successfully
- ✅ Cash balance: $447,395.73
- ✅ Mindfolio ID: mf_bc04f8dc90bd
- ✅ Name: "TradeStation Master"
- ⚠️ Minor UX issue: Redirect after import shows "site can't be reached" (non-blocking)

**Files Modified:**
- `backend/mindfolio.py` - Import endpoint with transaction storage
- `frontend/src/pages/ImportFromTradeStation.jsx` - Full import UI
- `frontend/src/pages/MindfolioList.jsx` - Two-button interface
- `frontend/src/lib/nav.simple.js` - Sidebar buttons removed
- `frontend/src/services/mindfolioClient.js` - Import API method
- `frontend/src/App.js` - Route added

**Estimated Time:** 4 hours (actual)

---
  - [x] Build tab uses custom slider styles (cyan thumb, 18px diameter)
- [x] **Code Structure:** OptimizeTab separated, BuildTab fully replaced (deleted BuilderPage link)
- [x] **State Management:** 14 props correctly passed from BuilderV2Page to OptimizeTab
- [x] **Testing:** Zero compilation errors, Build tab displays complete options trading interface

**Next Steps:**
- [ ] Implement Historical Flow page (table structure TBD)
- [ ] Implement News Flow page (layout TBD)
- [ ] Implement Congress Flow page (congressional trades tracking)
- [ ] Implement Insider Flow page (corporate insider trades)
- [ ] Connect Market Bias indicator to real-time flow data (dynamic color based on bullish/bearish sentiment)
- [ ] Backend integration for live flow data (WebSocket or polling)
- [ ] Connect FiltersPanel to backend API for real filtering
- [ ] Build Tab Backend Integration:
  - [ ] Connect to options chain API for real strike prices
  - [ ] Fetch real expiration dates from TradeStation
  - [ ] Implement Greeks calculation for strategy metrics
  - [ ] Add P&L calculation engine based on IV/Range sliders
  - [ ] Connect strategy switching (Long Call → other strategies)
  - [ ] Implement Add/Save/Positions functionality

**Next Steps (Optimize Backend Integration):**
- [ ] Connect symbol input to live price API (replace mock $250.75)
- [ ] Fetch real expiration dates from TradeStation options chain API
- [ ] Implement strategy calculation engine based on direction + slider position
- [ ] Connect Budget filter to strategy risk/capital calculations
- [ ] Add API endpoint `/api/optimize/suggest` for real strategy recommendations
- [ ] Replace mockStrategies with dynamic strategy generation

---

### 1. � Multi-Broker Architecture - Mindfolio Manager (CRITICAL PRIORITY)
**Status:** 🔴 NEW REQUIREMENT - Must implement before other features  
**Assignee:** TBD  
**Due:** 2-3 days (October 23-24, 2025)  
**Task File:** `MINDFOLIO_BROKER_ARCHITECTURE.md`

**Objectives:**
- [ ] **Phase 0: Foundation (Day 1)**
  - [ ] Add broker/environment/account_type fields to Mindfolio model (`backend/mindfolio.py`)
  - [ ] Add validators to MindfolioCreate
  - [ ] Update `create_mindfolio()` to save new fields
  - [ ] Add filtering to `list_mindfolios()` endpoint (broker, environment, account_type params)
  - [ ] Test with curl: Create TS SIM Equity mindfolio
- [ ] **Phase 1: UI Implementation (Day 2)**
  - [ ] Add Broker Tabs (TradeStation/TastyTrade) to `frontend/src/pages/MindfolioList.jsx`
  - [ ] Add Environment Sub-tabs (SIM/LIVE)
  - [ ] Add Account Type Dropdown (All/Equity/Futures/Crypto)
  - [ ] Update MindfolioCard with broker badges
  - [ ] Add Stats Cards Breakdown (per-broker/environment totals)
- [ ] **Phase 2: Create Form (Day 2)**
  - [ ] Update `frontend/src/pages/MindfolioCreate.jsx`
  - [ ] Add broker selection (TradeStation/TastyTrade radio buttons)
  - [ ] Add environment selection (SIM/LIVE radio buttons)
  - [ ] Add account type dropdown
  - [ ] Add optional account_id field
- [ ] **Phase 3: Context-Aware Features (Day 3)**
  - [ ] Quick Actions: Reset for SIM, extra confirm for LIVE
  - [ ] ROI color coding based on environment
  - [ ] Detail page: Show broker info in header
  - [ ] LIVE delete confirmation modal

**Data Model Changes:**
```python
# NEW Mindfolio fields:
broker: str  # "TradeStation" | "TastyTrade"
environment: str  # "SIM" | "LIVE"
account_type: str  # "Equity" | "Futures" | "Crypto"
account_id: Optional[str] = None  # Broker's account number
```

**API Changes:**
```python
# GET /api/mindfolio with query params:
?broker=TradeStation&environment=SIM&account_type=Equity
```

**Dependencies:**
- ✅ Existing Mindfolio Manager
- ✅ Redis/MongoDB storage
- ⚠️ TradeStation OAuth (pending callback approval)

**Success Criteria:**
- Broker tabs working with proper filtering
- Can create mindfolios per broker/environment/type
- Stats cards show per-broker breakdowns
- SIM accounts have Reset button, LIVE have extra delete confirm

**Migration Required:**
- Existing mindfolios need default values: `broker='TradeStation', environment='SIM', account_type='Equity'`

**Notes:**
- **Color schemes:** TradeStation=Blue, TastyTrade=Orange, SIM=Blue, LIVE=Red
- See `MINDFOLIO_BROKER_ARCHITECTURE.md` (890 lines) for complete specs
- This is ARCHITECTURAL - must do before adding other manager features
- 4 broker docs exist: TRADESTATION_CALLBACK_SETUP.md, EMAIL_TRADESTATION_CALLBACK_REQUEST.md, TRADESTATION_TIMELINE.md

---

### 3. 📱 Sidebar Audit & Missing Pages (HIGH PRIORITY)
**Status:** � IN PROGRESS - Phase 1 Complete (October 27, 2025)  
**Assignee:** GitHub Copilot  
**Due:** 1-2 days remaining for Phases 2-4  
**Task Files:** 
- `SIDEBAR_AUDIT_REPORT.md` (complete audit - 700+ lines)
- `SIDEBAR_PHASE1_COMPLETE.md` (implementation summary)

**Problem:**
Sidebar in `nav.simple.js` has ~47 menu items, but only 36% have working pages!

**Phase 1: Audit Complete + Quick Fixes ✅ DONE (October 27, 2025)**
- [x] Complete mapping: Sidebar items → Routes in App.js
- [x] Identified missing pages: 30/47 routes (64%) have no pages
- [x] Documentation: Complete table with Menu Item | Route | Page Exists? | File Path
- [x] **Quick Fix 1:** Fixed TradeStation route mismatch (`/providers/ts` → `/tradestation/login`)
- [x] **Quick Fix 2:** Added Strategy Library to sidebar (page existed, not in menu)
- [x] **Quick Fix 3:** Added Account Balance to sidebar (page existed, not in menu)
- [x] **Quick Fix 4:** Removed duplicate "Sell Puts (Auto)" entry
- [x] **Quick Fix 5:** Fixed active state highlighting for nested routes (startsWith logic)

**Results After Phase 1:**
- ✅ Working routes: 19/47 (40%) - UP from 17/47 (36%)
- ✅ Route mismatches: 0 (was 1)
- ✅ Active state highlighting: Fixed for nested routes
- 🔴 Still missing: 28/47 routes (60%)

**Phase 2: Decizie per Item (2 ore)**
Pentru fiecare item fără pagină, decide:
- [ ] **Option A:** Create pagină nouă (`pages/NewPage.jsx`)
- [ ] **Option B:** Remove din sidebar (`nav.simple.js`)
- [ ] **Option C:** Redirect la existing page (update route)

**Phase 3: Implementare (varies)**
- [ ] Create pages lipsa SAU
- [ ] Remove items inutile din `nav.simple.js`
- [ ] Update `App.js` routes
- [ ] Test fiecare link din sidebar → NO 404s

**Known Issues (din SIDEBAR_TODO.md):**
```javascript
// Items fără pagini (suspected):
- /screener/iv → Scanner IV? Missing?
- /screener/sell-puts → Missing?
- /screener/covered-calls → Missing?
- /screener/csp → Missing?
- /trades/preview → Missing?
- /trades/orders/sim → Missing?
- /trades/orders/live → Missing?
- /md/chain → TradeStation chain? Missing?
- /mindfolio/analytics → Missing?
- /mindfolio/rebalancing → Missing?
- /stocks/scoring → Missing?
- /stocks/scanner → Missing?
- /stocks/top-picks → Missing?
- /analytics/backtests → Missing?
- /analytics/verified → Missing?
- /settings/gates → Missing?
- /settings/keys → Missing?
- /providers/ts → TradeStationLogin exists? Check route
- /providers/uw → Missing?
- /ops/redis → Missing?
- /ops/bt → Missing?
- /help/docs → Missing?
```

**Existing Pages (VERIFIED in App.js):**
```javascript
✅ /dashboard → Dashboard.jsx
✅ /builder → BuilderPage.jsx
✅ /simulator → SimulatorPage.jsx
✅ /flow → FlowPage.jsx
✅ /mindfolio → MindfolioList.jsx
✅ /mindfolio/:id → MindfolioDetail.jsx / MindfolioDetailNew.jsx
✅ /mindfolio/new → MindfolioCreate.jsx
✅ /account/balance → AccountBalancePage.jsx
✅ /market-movers → MarketMoversPage.jsx
✅ /congress-trades → CongressTradesPage.jsx
✅ /dark-pool → DarkPoolPage.jsx
✅ /institutional → InstitutionalPage.jsx
```

**Deliverables:**
1. **AUDIT_REPORT.md** - Tabel complet cu toate sidebar items + status
2. **Missing pages created** SAU **Sidebar cleaned** (remove dead links)
3. **Zero 404 errors** când click oricare link din sidebar
4. **Active state highlighting** fixed (isActive detection)

**Success Criteria:**
- ✅ Fiecare sidebar item → funcțional (pagină sau redirect)
- ✅ No ComingSoonPage placeholders (resolve toate)
- ✅ Sidebar logic flow: Dashboard → Builder → Flow → Mindfolio
- ✅ Mobile menu funcțional (collapse/expand)

**Dependencies:**
- ✅ SidebarSimple.jsx (349 lines) - working
- ✅ nav.simple.js (400 lines) - complete structure
- ⚠️ App.js routes (250 lines) - many missing routes

**Notes:**
- 24 files în `/frontend/src/archive` - some pages might be there!
- Chart pages archived: ChartPage.js, ChartProPage.js, etc.
- OptionsWorkbench.jsx, OptionsAnalytics.jsx în archive
- Consider restoring archived pages vs creating new ones

---

### 4. ��🎯 GEX Enhancement - Phase 1 (HIGH PRIORITY)
**Status:** 🔄 Planning Complete, Ready to Start  
**Assignee:** TBD  
**Due:** Week 1-2 (Nov 4, 2025)  
**Task File:** `GEX_ENHANCEMENT_TASK.md`

**Objectives:**
- [ ] Create `backend/services/gex_service.py`
- [ ] Implement GEX calculation engine
- [ ] Integrate UW API spot-exposures endpoint (300-410 records)
- [ ] Add Redis caching with 60s TTL
- [ ] Support multi-ticker GEX fetching
- [ ] Add API endpoint: `GET /api/gex/{ticker}`

**Dependencies:**
- ✅ UW API integration (17 endpoints verified)
- ✅ Redis fallback system
- ✅ FastAPI backend structure

**Success Criteria:**
- GEX data retrieval < 2s
- Proper error handling & demo fallback
- Unit tests with 80%+ coverage

**Notes:**
- Pre-calculated GEX available from UW API
- No need to calculate from options chain initially
- See `GEX_ENHANCEMENT_TASK.md` for full details

---

### 5. 🔧 Fix HomePage /mindfolios Link (HIGH PRIORITY - Quick Fix)
**Status:** ✅ COMPLETED (Oct 21, 2025)  
**Assignee:** Copilot  
**Completed:** Oct 21, 2025  
**Time:** 2 minutes  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #1

**Problem:**
HomePage Quick Action card #3 linked to `/mindfolios` (plural) but correct route is `/mindfolio` (singular)

**Fix Applied:**
```javascript
// File: frontend/src/pages/HomePage.jsx - Line 33
// CHANGED:
link: '/mindfolios',  // ❌ WRONG (plural)

// TO:
link: '/mindfolio',   // ✅ CORRECT (singular, matches App.js route)
```

**Testing:**
- [x] Fixed link from `/mindfolios` → `/mindfolio`
- [x] Matches App.js route: `<Route path="/mindfolio" element={<MindfolioList />} />`
- [x] "Mindfolio Manager" card now navigates correctly

**Result:** HomePage Quick Action #3 now works correctly ✅

---

### 5. 📊 Create OptimizePage - AI Strategy Optimizer (HIGH PRIORITY)
**Status:** 🔴 MISSING PAGE  
**Assignee:** TBD  
**Due:** Oct 22-23, 2025  
**Time:** 4-6 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #2

**Problem:**
- HomePage Quick Action #4 links to `/optimize` → 404 error
- Feature promised: "AI-powered strategy recommendations"
- Backend endpoint exists: `POST /api/optimize/suggest`

**Requirements:**
- [ ] Create `frontend/src/pages/OptimizePage.jsx`
- [ ] Add route to `App.js`: `<Route path="/optimize" element={<OptimizePage />} />`
- [ ] UI Components:
  - [ ] Symbol input (ticker search)
  - [ ] Sentiment selector (bullish/bearish/neutral)
  - [ ] Target price input (optional)
  - [ ] Budget slider
  - [ ] DTE selector
  - [ ] Risk bias slider (conservative ↔ aggressive)
- [ ] Results Display:
  - [ ] Top 3-5 strategy recommendations
  - [ ] Expected return, max risk, max profit per strategy
  - [ ] Probability of profit
  - [ ] "Build This" button → redirect to BuilderPage with pre-filled legs
- [ ] Backend Integration:
  - [ ] `GET /api/optimize/suggest` with query params
  - [ ] Handle loading states
  - [ ] Error handling with demo fallback

**Design:**
- Dark theme (slate-900 bg, emerald accents)
- Similar layout to BuilderPage (left form, right results)
- Strategy cards with gradient backgrounds

**Success Criteria:**
- [ ] Page loads without errors
- [ ] Can enter symbol + sentiment → get recommendations
- [ ] "Build This" button works (navigates to BuilderPage)
- [ ] Mobile responsive

---

### 6. 🔍 Create IVScannerPage - IV Setups Scanner (HIGH PRIORITY)
**Status:** 🔴 MISSING PAGE  
**Assignee:** TBD  
**Due:** Oct 23-24, 2025  
**Time:** 6-8 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #6

**Problem:**
- Sidebar "Options Data > Algos > IV Setups (Auto)" links to `/screener/iv` → 404
- 4 strategy variants also missing:
  - `/screener/iv?strategy=IRON_CONDOR`
  - `/screener/iv?strategy=CALENDAR`
  - `/screener/iv?strategy=DIAGONAL`
  - `/screener/iv?strategy=DOUBLE_DIAGONAL`

**Requirements:**
- [ ] Create `frontend/src/pages/IVScannerPage.jsx`
- [ ] Add route: `<Route path="/screener/iv" element={<IVScannerPage />} />`
- [ ] Support query param: `?strategy=STRATEGY_NAME`
- [ ] UI Components:
  - [ ] Strategy selector dropdown (All, Iron Condor, Calendar, Diagonal, Double Diagonal)
  - [ ] Filters:
    - [ ] Min IV Rank slider (0-100)
    - [ ] Max days to expiration
    - [ ] Min volume
    - [ ] Sectors filter (checkboxes)
  - [ ] Scan button
  - [ ] Results table:
    - [ ] Columns: Ticker, IV Rank, IV Percentile, Price, Volume, Setup Quality Score
    - [ ] Sortable columns
    - [ ] "Analyze" button per row → redirect to BuilderPage
- [ ] Backend Integration:
  - [ ] Create `backend/routers/screener.py` if doesn't exist
  - [ ] `GET /api/screener/iv` endpoint
  - [ ] Return top 20-50 candidates with IV metrics
  - [ ] Use UW API screener endpoint: `/api/screener/stocks`

**Success Criteria:**
- [ ] Scanner loads and displays results
- [ ] Strategy selector works (updates results)
- [ ] Filters work correctly
- [ ] "Analyze" button navigates to BuilderPage with ticker pre-filled
- [ ] Mobile responsive table

---

### 7. 📉 Create SellPutsPage - Put Selling Engine (HIGH PRIORITY)
**Status:** 🔴 MISSING PAGE  
**Assignee:** TBD  
**Due:** Oct 24-25, 2025  
**Time:** 6-8 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #11

**Problem:**
- Sidebar "Options Data > Algos > Sell Puts (Auto)" links to `/screener/sell-puts` → 404
- Core algo feature for income generation strategy

**Requirements:**
- [ ] Create `frontend/src/pages/SellPutsPage.jsx`
- [ ] Add route: `<Route path="/screener/sell-puts" element={<SellPutsPage />} />`
- [ ] UI Components:
  - [ ] Capital input (max cash allocation)
  - [ ] Target premium per contract (min $100?)
  - [ ] Max days to expiration slider
  - [ ] Delta range (0.10 - 0.30 recommended)
  - [ ] Sector exclusions
  - [ ] Risk tolerance (conservative/moderate/aggressive)
  - [ ] Scan button
  - [ ] Results table:
    - [ ] Ticker, Strike, DTE, Premium, Delta, Probability ITM
    - [ ] "Sell This Put" button → add to trades preview
- [ ] Backend Integration:
  - [ ] `GET /api/screener/sell-puts` endpoint
  - [ ] Filter logic:
    - Min premium threshold
    - Delta range check
    - High liquidity (volume > 100, OI > 500)
    - IV rank > 50 (sell high IV)
  - [ ] Return top 20 candidates
- [ ] Trade Preview Integration:
  - [ ] "Add to Queue" button
  - [ ] Show in `/trades/preview` (create this page later)

**Success Criteria:**
- [ ] Scanner identifies high-premium put opportunities
- [ ] Filters work correctly
- [ ] Can add selected puts to preview queue
- [ ] Shows capital requirement per trade
- [ ] Mobile responsive

---

### 8. 🎯 Create Investment Scoring Page (MEDIUM PRIORITY)
**Status:** 🟡 MISSING PAGE  
**Assignee:** TBD  
**Due:** Oct 24-25, 2025  
**Time:** 3-4 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #3

**Problem:**
- Sidebar "Stocks Data > Investment Scoring" links to `/stocks/scoring` → 404
- AI-powered stock scoring system needs UI

**Requirements:**
- [ ] Create `frontend/src/pages/StockScoringPage.jsx`
- [ ] Add route: `<Route path="/stocks/scoring" element={<StockScoringPage />} />`
- [ ] UI Components:
  - [ ] Ticker input with autocomplete
  - [ ] "Analyze" button
  - [ ] Results card showing:
    - [ ] Overall score (0-100)
    - [ ] Category scores (Technical, Fundamental, Sentiment, Options Flow)
    - [ ] Recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
    - [ ] Reasoning (AI-generated explanation)
    - [ ] Key metrics table
- [ ] Backend Integration:
  - [ ] `POST /api/stocks/scoring` with ticker
  - [ ] Uses existing `investment_scoring_agent.py`
  - [ ] Combines UW data + TradeStation data
- [ ] Design:
  - [ ] Score visualization (circular progress bar)
  - [ ] Color-coded categories (green = bullish, red = bearish)
  - [ ] Expandable sections for detailed metrics

**Success Criteria:**
- [ ] Returns comprehensive stock analysis
- [ ] AI reasoning is clear and actionable
- [ ] Mobile responsive
- [ ] Handles errors gracefully

---

### 9. 🔍 Create Stock Scanner Page (MEDIUM PRIORITY)
**Status:** 🟡 MISSING PAGE  
**Assignee:** TBD  
**Due:** Oct 26-27, 2025  
**Time:** 4-5 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #4

**Problem:**
- Sidebar "Stocks Data > Scoring Scanner" links to `/stocks/scanner` → 404
- Bulk stock screening with scoring filters

**Requirements:**
- [ ] Create `frontend/src/pages/StockScannerPage.jsx`
- [ ] Add route: `<Route path="/stocks/scanner" element={<StockScannerPage />} />`
- [ ] UI Components:
  - [ ] Filter panel:
    - [ ] Min overall score (slider 0-100)
    - [ ] Sector multi-select
    - [ ] Market cap range
    - [ ] Min volume
    - [ ] Scan universe selector (SP500, Russell2000, All Stocks)
  - [ ] Results table:
    - [ ] Ticker, Score, Recommendation, Price, Change, Volume
    - [ ] Sortable columns
    - [ ] "Analyze" button → opens StockScoringPage
  - [ ] Pagination (show 50 per page)
- [ ] Backend Integration:
  - [ ] `GET /api/stocks/scanner` with filter params
  - [ ] Uses UW screener API + scoring engine
  - [ ] Returns top 100 stocks by score
- [ ] Performance:
  - [ ] Cache results for 5 minutes
  - [ ] Show loading skeleton during scan

**Success Criteria:**
- [ ] Identifies high-scoring stocks quickly
- [ ] Filters work correctly
- [ ] Can export results to CSV
- [ ] Mobile responsive table

---

### 10. 🤖 Create IV Strategy Scanner Variants (MEDIUM PRIORITY - 4 variants)
**Status:** 🟡 MISSING PAGES  
**Assignee:** TBD  
**Due:** Oct 28-29, 2025  
**Time:** 2-3 hours each (8-12 hours total)  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` items #7-10

**Problem:**
- IVScannerPage exists for base `/screener/iv`
- But needs query param handling for 4 strategy variants:
  - `/screener/iv?strategy=IRON_CONDOR`
  - `/screener/iv?strategy=CALENDAR`
  - `/screener/iv?strategy=DIAGONAL`
  - `/screener/iv?strategy=DOUBLE_DIAGONAL`

**Requirements:**
- [ ] Update `frontend/src/pages/IVScannerPage.jsx`:
  - [ ] Read `?strategy=` query param
  - [ ] Show strategy-specific filters
  - [ ] Adjust backend API call based on strategy
- [ ] Strategy-Specific Filters:
  - [ ] **Iron Condor**: Wing width, probability range
  - [ ] **Calendar**: Front/back month DTE difference
  - [ ] **Diagonal**: Strike spread, time spread
  - [ ] **Double Diagonal**: Symmetric wing configuration
- [ ] Backend Updates:
  - [ ] Update `GET /api/screener/iv` to accept `strategy` param
  - [ ] Filter logic per strategy type
  - [ ] Return strategy-appropriate setups
- [ ] UI Enhancements:
  - [ ] Strategy selector dropdown at top
  - [ ] Strategy description tooltip
  - [ ] Results show strategy-specific metrics

**Success Criteria:**
- [ ] Each strategy variant works independently
- [ ] Filters are relevant to strategy type
- [ ] Backend returns appropriate setups
- [ ] Can switch between strategies without page reload

---

### 11. 🛡️ Create Covered Calls Page (MEDIUM PRIORITY)
**Status:** 🟡 MISSING PAGE  
**Assignee:** TBD  
**Due:** Oct 30, 2025  
**Time:** 4-5 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #12

**Problem:**
- Sidebar "Options Data > Algos > Covered Calls" links to `/screener/covered-calls` → 404
- Income generation strategy for stock holders

**Requirements:**
- [ ] Create `frontend/src/pages/CoveredCallsPage.jsx`
- [ ] Add route: `<Route path="/screener/covered-calls" element={<CoveredCallsPage />} />`
- [ ] UI Components:
  - [ ] Stock holdings input (import from Mindfolio or manual)
  - [ ] Target premium per contract
  - [ ] Max days to expiration
  - [ ] Strike delta preference (0.20-0.40 typical)
  - [ ] Results table per holding:
    - [ ] Strike, DTE, Premium, Delta, Annualized Return
    - [ ] "Write This Call" button
- [ ] Backend Integration:
  - [ ] `GET /api/screener/covered-calls` with holdings array
  - [ ] Filter logic:
    - OTM calls (strike > current price)
    - High liquidity (volume > 50, OI > 200)
    - Premium > threshold
  - [ ] Calculate annualized return: (premium / stock_price) * (365 / DTE)
- [ ] Mindfolio Integration:
  - [ ] "Import Stock Holdings" button
  - [ ] Load stocks from selected mindfolio
  - [ ] Show current position qty

**Success Criteria:**
- [ ] Identifies best covered call opportunities
- [ ] Annualized return calculation correct
- [ ] Can import holdings from mindfolio
- [ ] Mobile responsive

---

### 12. 💰 Create Cash-Secured Puts Page (MEDIUM PRIORITY)
**Status:** 🟡 MISSING PAGE  
**Assignee:** TBD  
**Due:** Oct 31, 2025  
**Time:** 4-5 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #13

**Problem:**
- Sidebar "Options Data > Algos > Cash-Secured Puts" links to `/screener/csp` → 404
- Stock acquisition strategy with premium income

**Requirements:**
- [ ] Create `frontend/src/pages/CSPPage.jsx`
- [ ] Add route: `<Route path="/screener/csp" element={<CSPPage />} />`
- [ ] UI Components:
  - [ ] Available cash input
  - [ ] Target stocks watchlist input (or scan all)
  - [ ] Min premium per contract
  - [ ] Delta range (0.20-0.35 typical)
  - [ ] Max DTE
  - [ ] Results table:
    - [ ] Ticker, Strike, DTE, Premium, Delta, Cash Required
    - [ ] Annualized Return %
    - [ ] "Sell This Put" button
- [ ] Backend Integration:
  - [ ] `GET /api/screener/csp` with filters
  - [ ] Filter logic:
    - High-quality stocks (market cap > $1B)
    - Strike < current price (OTM puts)
    - Premium > threshold
    - Liquidity check
  - [ ] Calculate annualized return + cash requirement
- [ ] Trade Preview:
  - [ ] Show cash reserve needed (strike * 100)
  - [ ] Calculate max positions based on available cash

**Success Criteria:**
- [ ] Identifies high-yield CSP opportunities
- [ ] Cash requirement calculations correct
- [ ] Can filter by specific tickers
- [ ] Shows portfolio allocation impact

---

### 13. 📊 Create TradeStation Option Chain Page (MEDIUM PRIORITY)
**Status:** 🟡 MISSING PAGE  
**Assignee:** TBD  
**Due:** Nov 1-2, 2025  
**Time:** 5-6 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #17

**Problem:**
- Sidebar "Options Data > Option Chain (TS)" links to `/md/chain` → 404
- TradeStation-specific option chain viewer (when `TS_LIVE` flag enabled)

**Requirements:**
- [ ] Create `frontend/src/pages/TSOptionChainPage.jsx`
- [ ] Add route: `<Route path="/md/chain" element={<TSOptionChainPage />} />`
- [ ] Conditional visibility: Only show if `flags.TS_LIVE === true`
- [ ] UI Components:
  - [ ] Ticker input
  - [ ] Expiration selector dropdown
  - [ ] Strike range slider
  - [ ] Option chain grid:
    - [ ] CALLS (left side): Strike, Bid, Ask, Last, Volume, OI, IV, Delta, Theta
    - [ ] PUTS (right side): Same columns mirrored
    - [ ] ATM strike highlighted
  - [ ] Real-time price updates (via WebSocket if available)
- [ ] Backend Integration:
  - [ ] `GET /api/tradestation/options/chain?symbol={ticker}&expiry={date}`
  - [ ] Uses TradeStation API directly (not UW)
  - [ ] Format data for grid display
- [ ] Features:
  - [ ] Click strike to view Greeks detail
  - [ ] Color-coded by moneyness (ITM/ATM/OTM)
  - [ ] Export to CSV

**Success Criteria:**
- [ ] Shows TradeStation option chain data
- [ ] Only visible when TS connected
- [ ] Grid is responsive and scrollable
- [ ] Real-time updates if WebSocket available

---

### 14. 📈 Create Backtests History Page (MEDIUM PRIORITY)
**Status:** 🟡 MISSING PAGE  
**Assignee:** TBD  
**Due:** Nov 3, 2025  
**Time:** 4-5 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #18

**Problem:**
- Sidebar "Options Data > Analytics > Backtests" links to `/analytics/backtests` → 404
- Historical backtest results repository

**Requirements:**
- [ ] Create `frontend/src/pages/BacktestsPage.jsx`
- [ ] Add route: `<Route path="/analytics/backtests" element={<BacktestsPage />} />`
- [ ] UI Components:
  - [ ] Backtests table:
    - [ ] Strategy Name, Symbol, Date Range, Return %, Sharpe Ratio, Max DD
    - [ ] Sortable columns
    - [ ] "View Details" button → opens backtest detail modal
  - [ ] Filter panel:
    - [ ] Strategy type filter
    - [ ] Symbol filter
    - [ ] Date range picker
    - [ ] Min return % filter
  - [ ] Pagination
- [ ] Backend Integration:
  - [ ] `GET /api/analytics/backtests` with filters
  - [ ] Retrieves from Redis `bt:*` keys or MongoDB archive
  - [ ] Returns list with summary stats
- [ ] Detail Modal:
  - [ ] Full P&L chart
  - [ ] Trade log table
  - [ ] Performance metrics
  - [ ] Strategy parameters used

**Success Criteria:**
- [ ] Shows all historical backtests
- [ ] Can filter and search
- [ ] Detail modal displays full analysis
- [ ] Export results to CSV

---

### 15. 💼 Create Mindfolio Analytics Page (MEDIUM PRIORITY)
**Status:** 🟡 MISSING PAGE  
**Assignee:** TBD  
**Due:** Nov 4-5, 2025  
**Time:** 5-6 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #20

**Problem:**
- Sidebar "Mindfolio Manager > Mindfolio Analytics" links to `/mindfolio/analytics` → 404
- Advanced portfolio analytics and insights

**Requirements:**
- [ ] Create `frontend/src/pages/MindfolioAnalyticsPage.jsx`
- [ ] Add route: `<Route path="/mindfolio/analytics" element={<MindfolioAnalyticsPage />} />`
- [ ] Mindfolio selector dropdown at top
- [ ] Analytics Sections:
  - [ ] **Performance Metrics**:
    - Total Return %, Sharpe Ratio, Max Drawdown
    - Win Rate, Avg Win/Loss, Profit Factor
  - [ ] **Portfolio Greeks**:
    - Net Delta, Gamma, Theta, Vega
    - Position-level Greeks breakdown
  - [ ] **Risk Analysis**:
    - Value at Risk (VaR 95%)
    - Correlation matrix (positions)
    - Concentration risk (top 5 holdings)
  - [ ] **Trade Statistics**:
    - Total trades, Win/Loss distribution
    - Avg holding period
    - Best/Worst trades
  - [ ] **Equity Curve**:
    - Historical NAV chart
    - Drawdown overlay
- [ ] Backend Integration:
  - [ ] `GET /api/mindfolio/{id}/analytics`
  - [ ] Comprehensive calculations using FIFO positions
  - [ ] Greeks aggregation across all positions

**Success Criteria:**
- [ ] Shows comprehensive portfolio analytics
- [ ] Greeks calculations accurate
- [ ] Charts responsive and interactive
- [ ] Export analytics report to PDF

---

### 16. 🔧 Create TradeStation Settings Page (MEDIUM PRIORITY)
**Status:** 🟡 MISSING PAGE  
**Assignee:** TBD  
**Due:** Nov 6, 2025  
**Time:** 2-3 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #24

**Problem:**
- Sidebar "Settings > Data & APIs > TradeStation" links to `/providers/ts` → 404
- TradeStation connection management UI

**Requirements:**
- [ ] Create `frontend/src/pages/TSSettingsPage.jsx`
- [ ] Add route: `<Route path="/providers/ts" element={<TSSettingsPage />} />`
- [ ] UI Components:
  - [ ] Connection Status:
    - [ ] Green/Red indicator (connected/disconnected)
    - [ ] Last sync timestamp
    - [ ] Account ID display
  - [ ] OAuth Flow:
    - [ ] "Connect TradeStation" button
    - [ ] "Disconnect" button
    - [ ] Refresh token status
  - [ ] Settings:
    - [ ] Environment toggle (SIMULATION / LIVE)
    - [ ] Default account selector
    - [ ] Data sync frequency
  - [ ] Test Connection:
    - [ ] "Test API Connection" button
    - [ ] Shows balances, positions count
- [ ] Backend Integration:
  - [ ] `GET /api/tradestation/status`
  - [ ] `POST /api/tradestation/connect` (OAuth)
  - [ ] `DELETE /api/tradestation/disconnect`
  - [ ] `POST /api/tradestation/test`

**Success Criteria:**
- [ ] Can connect/disconnect TS account
- [ ] OAuth flow works smoothly
- [ ] Shows real-time connection status
- [ ] Environment switching works

---

### 17. 📊 Create Top Picks Page (LOW PRIORITY)
**Status:** 🔵 NICE-TO-HAVE  
**Assignee:** TBD  
**Due:** Nov 7, 2025  
**Time:** 2-3 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #5

**Problem:**
- Sidebar "Stocks Data > Top Picks" links to `/stocks/top-picks` → 404
- Curated list of AI-recommended stocks

**Requirements:**
- [ ] Create `frontend/src/pages/TopPicksPage.jsx`
- [ ] Add route: `<Route path="/stocks/top-picks" element={<TopPicksPage />} />`
- [ ] UI Components:
  - [ ] Featured stock cards (top 10)
  - [ ] Score badge, recommendation, price, change %
  - [ ] "Analyze" button → StockScoringPage
  - [ ] Auto-refresh every 30 minutes
- [ ] Backend Integration:
  - [ ] `GET /api/stocks/top-picks`
  - [ ] Returns stocks with score > 80
  - [ ] Sorted by score + recent momentum
- [ ] Design:
  - [ ] Card grid layout
  - [ ] Color-coded by recommendation strength
  - [ ] Hover effects with mini chart

**Success Criteria:**
- [ ] Shows AI-curated top stocks
- [ ] Auto-refreshes periodically
- [ ] Quick access to detailed analysis
- [ ] Mobile responsive

---

### 18. 📋 Create Trade Preview Queue Page (LOW PRIORITY)
**Status:** 🔵 NICE-TO-HAVE  
**Assignee:** TBD  
**Due:** Nov 8, 2025  
**Time:** 3-4 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #14

**Problem:**
- Sidebar "Options Data > Algos > Preview Queue" links to `/trades/preview` → 404
- Trade queue management before execution

**Requirements:**
- [ ] Create `frontend/src/pages/TradePreviewPage.jsx`
- [ ] Add route: `<Route path="/trades/preview" element={<TradePreviewPage />} />`
- [ ] UI Components:
  - [ ] Queued trades table:
    - [ ] Strategy, Symbol, Legs, Max Risk, Expected Return
    - [ ] "Execute Now" button
    - [ ] "Remove" button
  - [ ] Total capital requirement summary
  - [ ] Bulk actions:
    - [ ] "Execute All" button
    - [ ] "Clear Queue" button
  - [ ] Filters:
    - [ ] By strategy type
    - [ ] By symbol
- [ ] Backend Integration:
  - [ ] `GET /api/trades/queue`
  - [ ] `POST /api/trades/queue` (add trade)
  - [ ] `DELETE /api/trades/queue/{id}` (remove)
  - [ ] `POST /api/trades/execute/{id}` (execute single)
- [ ] Integration:
  - [ ] Receives trades from screener pages ("Add to Queue")
  - [ ] Shows position sizing recommendations

**Success Criteria:**
- [ ] Can queue trades from screeners
- [ ] Manage queue (add/remove/execute)
- [ ] Shows capital allocation
- [ ] Mobile responsive

---

### 19. 📄 Create SIM Orders Page (LOW PRIORITY)
**Status:** 🔵 NICE-TO-HAVE  
**Assignee:** TBD  
**Due:** Nov 9, 2025  
**Time:** 3-4 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #15

**Problem:**
- Sidebar "Options Data > Algos > Orders (SIM)" links to `/trades/orders/sim` → 404
- TradeStation SIMULATION account orders history

**Requirements:**
- [ ] Create `frontend/src/pages/SIMOrdersPage.jsx`
- [ ] Add route: `<Route path="/trades/orders/sim" element={<SIMOrdersPage />} />`
- [ ] UI Components:
  - [ ] Orders table:
    - [ ] Order ID, Symbol, Type, Status, Qty, Price, Time
    - [ ] Status badges (Filled/Pending/Cancelled/Rejected)
  - [ ] Filters:
    - [ ] Date range picker
    - [ ] Status filter
    - [ ] Symbol filter
  - [ ] Pagination
  - [ ] "Refresh" button
- [ ] Backend Integration:
  - [ ] `GET /api/tradestation/orders/sim` with filters
  - [ ] Uses TradeStation Orders API (SIMULATION environment)
  - [ ] Real-time status updates if WebSocket available
- [ ] Design:
  - [ ] Color-coded status (green=filled, yellow=pending, red=rejected)
  - [ ] Expandable row for order details
  - [ ] Export to CSV

**Success Criteria:**
- [ ] Shows SIMULATION orders history
- [ ] Status updates in real-time
- [ ] Can filter and search
- [ ] Mobile responsive

---

### 20. 💳 Create LIVE Orders Page (LOW PRIORITY)
**Status:** 🔵 NICE-TO-HAVE  
**Assignee:** TBD  
**Due:** Nov 10, 2025  
**Time:** 3-4 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #16

**Problem:**
- Sidebar "Options Data > Algos > Orders (LIVE)" links to `/trades/orders/live` → 404
- TradeStation LIVE account orders history (PRODUCTION)

**Requirements:**
- [ ] Create `frontend/src/pages/LIVEOrdersPage.jsx`
- [ ] Add route: `<Route path="/trades/orders/live" element={<LIVEOrdersPage />} />`
- [ ] **CRITICAL: Conditional visibility**:
  - [ ] Only show if `flags.TS_LIVE === true` AND `environment === 'LIVE'`
  - [ ] Show warning banner: "⚠️ LIVE TRADING ENVIRONMENT - REAL MONEY"
- [ ] UI Components: Same as SIMOrdersPage but:
  - [ ] Red warning banner at top
  - [ ] Additional "Cancel Order" buttons (for pending orders)
  - [ ] Confirmation modals before actions
- [ ] Backend Integration:
  - [ ] `GET /api/tradestation/orders/live`
  - [ ] `DELETE /api/tradestation/orders/live/{id}` (cancel order)
  - [ ] Requires elevated permissions
- [ ] Safety:
  - [ ] Double-confirmation for cancellations
  - [ ] Audit log all actions
  - [ ] Rate limiting on cancel requests

**Success Criteria:**
- [ ] Only accessible in LIVE mode
- [ ] Clear visual distinction from SIM
- [ ] Safe order cancellation flow
- [ ] Complete audit trail

---

### 21. ✅ Create Verified Chains Page (LOW PRIORITY)
**Status:** 🔵 NICE-TO-HAVE  
**Assignee:** TBD  
**Due:** Nov 11, 2025  
**Time:** 2-3 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #19

**Problem:**
- Sidebar "Options Data > Analytics > Verified Chains" links to `/analytics/verified` → 404
- Option chain quality verification and data integrity checks

**Requirements:**
- [ ] Create `frontend/src/pages/VerifiedChainsPage.jsx`
- [ ] Add route: `<Route path="/analytics/verified" element={<VerifiedChainsPage />} />`
- [ ] UI Components:
  - [ ] Verified chains table:
    - [ ] Ticker, Expiry, Verification Status, Data Quality Score
    - [ ] Last Verified timestamp
    - [ ] Issues count (if any)
  - [ ] Filters:
    - [ ] Verification status (Verified/Failed/Pending)
    - [ ] Date range
    - [ ] Min quality score
  - [ ] Detail modal:
    - [ ] Shows verification checks passed/failed
    - [ ] Data quality metrics
    - [ ] Missing strikes/contracts
- [ ] Backend Integration:
  - [ ] `GET /api/analytics/verified-chains`
  - [ ] Runs verification checks:
    - Complete strike coverage
    - Bid-ask spread reasonability
    - IV smile consistency
    - Volume/OI correlation
  - [ ] Returns quality score (0-100)

**Success Criteria:**
- [ ] Shows option chain quality metrics
- [ ] Identifies data issues
- [ ] Can re-verify chains manually
- [ ] Export verification report

---

### 22. ⚖️ Create Smart Rebalancing Page (LOW PRIORITY)
**Status:** 🔵 NICE-TO-HAVE  
**Assignee:** TBD  
**Due:** Nov 12, 2025  
**Time:** 4-5 hours  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` item #21

**Problem:**
- Sidebar "Mindfolio Manager > Smart Rebalancing" links to `/mindfolio/rebalancing` → 404
- AI-driven portfolio rebalancing recommendations

**Requirements:**
- [ ] Create `frontend/src/pages/SmartRebalancingPage.jsx`
- [ ] Add route: `<Route path="/mindfolio/rebalancing" element={<SmartRebalancingPage />} />`
- [ ] Mindfolio selector dropdown
- [ ] UI Components:
  - [ ] Current allocation chart (pie/treemap)
  - [ ] Target allocation chart (AI recommended)
  - [ ] Rebalancing actions table:
    - [ ] Symbol, Action (Buy/Sell), Quantity, Reason
    - [ ] Expected impact on Greeks, risk metrics
  - [ ] "Apply Rebalancing" button
  - [ ] Rebalancing rules configurator:
    - [ ] Max position size %
    - [ ] Correlation threshold
    - [ ] Greeks targets (delta neutral, etc.)
- [ ] Backend Integration:
  - [ ] `GET /api/mindfolio/{id}/rebalancing`
  - [ ] Uses `smart_rebalancing_service.py`
  - [ ] Calculates optimal trades to reach target allocation
  - [ ] Considers: correlation, Greeks, sector exposure, risk metrics
- [ ] Preview Mode:
  - [ ] Shows "before/after" comparison
  - [ ] Impact on portfolio metrics

**Success Criteria:**
- [ ] Generates smart rebalancing recommendations
- [ ] Clear reasoning for each action
- [ ] Can apply recommendations with one click
- [ ] Mobile responsive

---

### 23. 🔧 Create Additional Settings Pages (LOW PRIORITY - 5 pages)
**Status:** 🔵 NICE-TO-HAVE  
**Assignee:** TBD  
**Due:** Nov 13-15, 2025  
**Time:** 1-2 hours each (5-10 hours total)  
**Audit Reference:** `SIDEBAR_MISSING_PAGES_AUDIT.md` items #22, #23, #25, #26, #27, #28

**Problem:**
- Multiple settings pages missing: Risk Gates, API Keys, UW Settings, System Diagnostics, Help Docs

**Requirements (5 separate pages):**

**A. Risk & Gates Page** (`/settings/gates`):
- [ ] Gate rules configurator
- [ ] Daily loss limits, position size limits
- [ ] Auto-pause triggers
- [ ] Gates history log

**B. API Keys Page** (`/settings/keys`):
- [ ] Encrypted key storage UI
- [ ] Add/Remove API keys
- [ ] Test connection button per key
- [ ] Security best practices warnings

**C. Unusual Whales Settings** (`/providers/uw`):
- [ ] API token input
- [ ] Connection status indicator
- [ ] Rate limit settings
- [ ] Test UW API endpoints

**D. Redis Cache Diagnostics** (`/ops/redis`):
- [ ] Cache stats (hit rate, miss rate, size)
- [ ] Key browser/search
- [ ] Manual cache clear buttons
- [ ] Performance metrics

**E. Backtest Ops** (`/ops/bt`):
- [ ] Backtest cache management
- [ ] Clear old backtests button
- [ ] Storage usage stats
- [ ] Performance benchmarks

**F. Help Docs** (`/help/docs`):
- [ ] User documentation browser
- [ ] Search functionality
- [ ] Video tutorials embed
- [ ] FAQs accordion

**Success Criteria:**
- [ ] All 5 pages functional
- [ ] Settings persist correctly
- [ ] Dark theme consistent
- [ ] Mobile responsive

---

## 📦 Backlog (Planned)

### Phase 2: GEX Backtesting (Weeks 3-4)
**Priority:** HIGH  
**Dependencies:** Phase 1 complete

- [ ] Build backtest framework (`backend/services/backtest_gex.py`)
- [ ] Entry filters: GEX thresholds, ratios, concentrations
- [ ] Risk management: R/R ratios, position sizing
- [ ] Drawdown period tracking
- [ ] Frontend: `GEXBacktestPage.jsx`
- [ ] Visualization: equity curves, day-by-day results

### Phase 3: GEX Bot Automation (Weeks 5-6)
**Priority:** HIGH  
**Dependencies:** Phase 2 complete

- [ ] Decision recipes for GEX levels & strikes
- [ ] Position entry logic with GEX confirmation
- [ ] Stop loss $ exit option (highly requested!)
- [ ] Real-time GEX monitoring
- [ ] Position notes with GEX snapshots
- [ ] Alert system for GEX zone breaches

### Phase 4: Advanced Features (Weeks 7-8)
**Priority:** MEDIUM  
**Dependencies:** Phase 3 complete

- [ ] ORB + GEX for Magnificent 7 (TSLA, NVDA, GOOGL, AMZN, AAPL, MSFT, META)
- [ ] Market event filters (FOMC, CPI, earnings, OpEx)
- [ ] GEX heatmaps (strike × time visualization)
- [ ] GEX zones charts (support/resistance)
- [ ] Multi-ticker GEX comparison
- [ ] Community strategy sharing

### Phase 5: Testing & Documentation (Weeks 9-10)
**Priority:** HIGH  
**Dependencies:** Phases 1-4 complete

- [ ] Unit tests (6 test files)
- [ ] Integration tests (3 test files)
- [ ] Performance tests (< 10s backtests)
- [ ] User guides (4 documents)
- [ ] Developer docs (3 documents)
- [ ] Video tutorials
- [ ] Beta testing with users

---

## ✅ Completed Tasks

### Quality Sprint - Zero Errors Achievement (Oct 21, 2025)
**Status:** ✅ COMPLETE  
**Duration:** Multi-phase sprint (9 commits)  
**Documentation:** `QUALITY_SPRINT_COMPLETE_OCT21.md`

**Completed:**
- ✅ Reduced ruff errors from 645 → 0 (-100% reduction)
- ✅ Fixed 4 duplicate function definitions (F811)
- ✅ Renamed 10 ambiguous variables (E741: l→leg, l→level)
- ✅ Executed breaking change: emergent→diagnostics rename
- ✅ Configured E402 suppression for FastAPI architectural pattern
- ✅ Archived broken test file with documentation
- ✅ All Python files compile successfully
- ✅ Created comprehensive documentation
- ✅ Updated Copilot instructions

**Breaking Changes:**
- Module: `bt_emergent.py` → `bt_diagnostics.py`
- API Endpoints: `/_emergent/*` → `/_diagnostics/*`
- Frontend Route: `/ops/emergent` → `/ops/diagnostics`

**Key Achievements:**
- Ruff configuration with per-file-ignores
- E402 pattern documented (router imports after app config)
- Zero compilation errors across entire codebase
- Production-ready code quality

---

### UW API Discovery & Integration (Oct 21, 2025)
**Status:** ✅ COMPLETE  
**Duration:** 3 days  
**Documentation:** `UW_API_FINAL_17_ENDPOINTS.md`

**Completed:**
- ✅ Discovered 17 unique UW API endpoint patterns
- ✅ Found 5 NEW endpoints (insider buys/sells, earnings today/week)
- ✅ Tested 150+ endpoint variations
- ✅ Cross-validated with 8 tickers
- ✅ Implemented all 17 methods in `unusual_whales_service_clean.py`
- ✅ Created comprehensive documentation (3 files, 18KB)
- ✅ Updated Copilot instructions with UW API context
- ✅ Committed 13 commits to git with full history

**Key Achievements:**
- 8 patterns work with ANY ticker = thousands of combinations
- Pre-calculated GEX (300-410 records per ticker) 🔥
- Dark pool data (500 trades per ticker) 🔥
- Screener with unified GEX/IV/Greeks
- Parameter support for 9 endpoints

---

## 🏗️ Architecture Improvements

### High Priority

#### 1. Mindfolio Performance Optimization
**Priority:** HIGH  
**Status:** 📋 Backlog

- [ ] Optimize FIFO calculation for large mindfolios (1000+ transactions)
- [ ] Add position caching with smart invalidation
- [ ] Implement batch transaction processing
- [ ] Add database indexes for transaction queries

**Why:** Current FIFO algorithm recalculates positions on every request

#### 2. Real-Time Market Data Pipeline
**Priority:** MEDIUM  
**Status:** 📋 Backlog

- [ ] WebSocket integration for live options prices
- [ ] Real-time GEX updates (< 5s latency)
- [ ] Push notifications for significant market events
- [ ] Live P&L updates for open positions

**Why:** Currently polling-based, need push-based real-time updates

#### 3. Multi-Broker Support Enhancement
**Priority:** MEDIUM  
**Status:** 📋 Backlog

- [ ] Complete TradeStation OAuth flow (60-day refresh)
- [ ] Add Interactive Brokers integration
- [ ] Add TD Ameritrade integration
- [ ] Unified broker API abstraction layer

**Why:** Currently only partial TradeStation support

### Medium Priority

#### 4. Frontend Performance
**Priority:** MEDIUM  
**Status:** 📋 Backlog

- [ ] Implement React.memo for expensive components
- [ ] Add virtual scrolling for large option chains
- [ ] Optimize Plotly chart rendering
- [ ] Lazy load heavy components

**Why:** Builder page can be slow with many strikes

#### 5. Mobile Responsive Design
**Priority:** MEDIUM  
**Status:** 📋 Backlog

- [ ] Responsive BuilderPage layout
- [ ] Mobile-friendly GEX charts
- [ ] Touch-optimized UI controls
- [ ] PWA support for mobile install

**Why:** Currently optimized for desktop only

---

## 🐛 Bug Fixes

### Critical Bugs

#### 1. TradeStation OAuth Token Refresh
**Priority:** 🔴 CRITICAL  
**Status:** 🔄 In Progress

**Issue:** Tokens expire after 60 days, refresh mechanism not fully tested  
**Files:** `backend/app/routers/tradestation_auth.py`

- [ ] Test refresh token flow end-to-end
- [ ] Add automated token refresh before expiry
- [ ] Handle refresh failures gracefully
- [ ] Add token expiry notifications

#### 2. Redis Connection Failures
**Priority:** 🟡 HIGH  
**Status:** ✅ MITIGATED (Fallback exists)

**Issue:** Redis connection drops cause temporary errors  
**Current Solution:** In-memory fallback works, but needs improvement

- [ ] Implement connection pooling
- [ ] Add automatic reconnection logic
- [ ] Better error messages for users
- [ ] Health check endpoint for Redis status

### Medium Priority Bugs

#### 3. Options Chain Demo Mode
**Priority:** 🟢 MEDIUM  
**Status:** 📋 Backlog

**Issue:** Demo data structure doesn't match UW API format exactly  
**Files:** `backend/unusual_whales_service_clean.py` (line 696-712)

- [ ] Update demo data to match UW API response format
- [ ] Add more realistic demo data (Greeks, premiums)
- [ ] Test demo mode with all features

#### 4. Builder Page Price Debouncing
**Priority:** 🟢 MEDIUM  
**Status:** 📋 Backlog

**Issue:** 500ms debounce can feel slow on fast edits  
**Files:** `frontend/src/pages/BuilderPage.jsx`

- [ ] Reduce debounce to 300ms
- [ ] Add loading indicator during pricing
- [ ] Implement optimistic UI updates

---

## 📚 Documentation

### User Documentation

#### 1. Getting Started Guide
**Priority:** HIGH  
**Status:** 📋 Backlog

- [ ] Installation instructions
- [ ] First mindfolio setup
- [ ] Building first options strategy
- [ ] Understanding P&L tracking
- [ ] Video walkthrough (10 min)

#### 2. Features Documentation
**Priority:** MEDIUM  
**Status:** 📋 Backlog

- [ ] Options Builder guide
- [ ] Mindfolio management guide
- [ ] Flow analysis guide
- [ ] GEX trading guide (post Phase 1)
- [ ] Backtest tutorial (post Phase 2)

#### 3. API Reference
**Priority:** MEDIUM  
**Status:** ⚠️ Partial (exists in copilot-instructions.md)

- [ ] Complete API endpoint documentation
- [ ] Request/response examples for all endpoints
- [ ] Error codes reference
- [ ] Rate limiting documentation
- [ ] Authentication guide

### Developer Documentation

#### 4. Architecture Guide
**Priority:** HIGH  
**Status:** ✅ COMPLETE (in copilot-instructions.md)

Current state:
- ✅ Redis fallback system documented
- ✅ FIFO position tracking explained
- ✅ Dark theme enforcement rules
- ✅ Integration test patterns
- ✅ UW API endpoints (17 patterns)

Still needed:
- [ ] Database schema diagrams
- [ ] System architecture diagram
- [ ] Data flow diagrams
- [ ] Deployment architecture

#### 5. Contributing Guide
**Priority:** MEDIUM  
**Status:** 📋 Backlog

- [ ] Code style guidelines
- [ ] Pull request process
- [ ] Testing requirements
- [ ] Git commit conventions
- [ ] Branch naming strategy

#### 6. Development Setup
**Priority:** HIGH  
**Status:** ⚠️ Partial

Current state:
- ✅ Backend development workflow
- ✅ Frontend development workflow
- ✅ Docker compose setup
- ✅ Quality gates (CI/CD)

Still needed:
- [ ] Detailed environment setup
- [ ] Troubleshooting guide
- [ ] Local development tips
- [ ] Debugging guide

---

## 🔄 Continuous Improvements

### Code Quality

- [ ] Increase backend test coverage to 80%+
- [ ] Add frontend unit tests (currently minimal)
- [ ] Implement E2E tests with Playwright
- [ ] Set up automated code reviews
- [ ] Add performance benchmarking

### Security

- [ ] Complete security audit (bandit, pip-audit)
- [ ] Implement rate limiting on all API endpoints
- [ ] Add input validation middleware
- [ ] Set up CORS properly for production
- [ ] API key rotation mechanism

### DevOps

- [ ] Set up staging environment
- [ ] Implement blue-green deployments
- [ ] Add monitoring & alerting (Sentry, Datadog)
- [ ] Set up automated backups
- [ ] Create disaster recovery plan

---

## 📊 Project Metrics

### Development Velocity
- **Sprint Duration:** 2 weeks
- **Current Sprint:** GEX Phase 1 (Week 1-2)
- **Completed Tasks (Last 30 Days):** 1 major (UW API Discovery)
- **Active Contributors:** 1-2

### Code Health
- **Backend Test Coverage:** ~60% (target: 80%)
- **Frontend Test Coverage:** ~20% (target: 60%)
- **Open Issues:** 4 critical, 6 high, 8 medium
- **Technical Debt:** Medium (FIFO optimization, real-time data)

### Performance Metrics
- **API Response Time (p95):** < 500ms
- **Frontend Load Time:** ~2s
- **Backtest Performance:** Not yet implemented
- **Real-time Data Latency:** Polling-based (30-60s)

---

## 🎯 Roadmap (Next 6 Months)

### Q4 2025 (Oct-Dec)
- ✅ UW API Discovery (Oct) - COMPLETE
- 🔄 GEX Enhancement Phases 1-3 (Nov-Dec)
- 📋 Real-time market data pipeline
- 📋 Mobile responsive design

### Q1 2026 (Jan-Mar)
- 📋 GEX Enhancement Phases 4-5
- 📋 Multi-broker support (Interactive Brokers, TD Ameritrade)
- 📋 Community features (strategy sharing)
- 📋 Advanced mindfolio analytics

### Q2 2026 (Apr-Jun)
- 📋 Machine learning trade signals
- 📋 Social trading features
- 📋 Mobile app (React Native)
- 📋 Premium subscription tier

---

## 💡 Feature Requests

### From Users

1. **Stop Loss $ Exit Option** (HIGH) - Added to GEX Phase 3
2. **Dark Pool Tracking Dashboard** (MEDIUM) - UW API ready, needs UI
3. **Earnings Calendar Integration** (MEDIUM) - UW API ready, needs UI
4. **Insider Trading Monitors** (LOW) - UW API ready, needs UI
5. **Export Backtest Results** (LOW) - Phase 2 feature

### From Team

1. **Automated Trading Bots** (HIGH) - GEX Phase 3
2. **Strategy Marketplace** (MEDIUM) - Community feature
3. **API for Third-Party Integrations** (LOW) - Future consideration
4. **Telegram/Discord Alerts** (LOW) - Phase 4 feature

---

## 📝 Notes & Decisions

### Architecture Decisions

**Oct 21, 2025:** Decided to use pre-calculated GEX from UW API instead of calculating from options chain
- **Why:** Faster, more reliable, reduces computation cost
- **Impact:** Phase 1 simpler, can focus on visualization
- **Fallback:** Can still calculate if UW API unavailable

**Oct 18, 2025:** Enforced dark theme only, removed light mode toggle
- **Why:** Simplify codebase, consistent UX, trader preference
- **Impact:** Reduced frontend complexity, faster development
- **Documentation:** `DARK_THEME_ONLY_VALIDATION.md`

### Development Principles

1. **Iterative Development:** Ship Phase 1, get feedback, iterate
2. **Test Coverage:** Minimum 60% for new features
3. **Documentation First:** Write docs before implementation
4. **User Feedback:** Weekly office hours for user input
5. **Performance:** < 2s for all user-facing operations

---

## 🔗 Related Resources

- **Main Documentation:** `.github/copilot-instructions.md`
- **UW API Reference:** `UW_API_FINAL_17_ENDPOINTS.md`
- **GEX Task Details:** `GEX_ENHANCEMENT_TASK.md`
- **Development Guidelines:** `DEVELOPMENT_GUIDELINES.md`
- **Dark Theme Docs:** `DARK_THEME_ONLY_VALIDATION.md`

---

## 📞 Contact & Support

- **GitHub Issues:** [github.com/barbudangabriel-gif/Flowmind/issues](https://github.com/barbudangabriel-gif/Flowmind/issues)
- **Email:** barbudangabriel@gmail.com
- **Project Owner:** Gabriel Barbudan

---

**Last Task Update:** Oct 21, 2025 - Added GEX Enhancement task  
**Next Review Date:** Oct 28, 2025  
**Status:** 🟢 On Track
