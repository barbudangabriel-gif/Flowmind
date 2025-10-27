# 📊 FlowMind Sidebar Audit Report

**Generated:** October 27, 2025  
**Auditor:** GitHub Copilot  
**Files Analyzed:**
- `frontend/src/lib/nav.simple.js` (sidebar configuration)
- `frontend/src/App.js` (route definitions)
- `frontend/src/pages/*` (existing page components)

---

## 📋 Executive Summary

**Total Sidebar Items:** 47 menu items across 8 sections  
**Existing Routes:** 17 routes defined in App.js  
**Missing Pages:** 30 routes (64% of sidebar items have no pages!)  
**Status:** 🔴 CRITICAL - Majority of sidebar links lead to "Coming Soon" page

---

## 🗺️ Complete Sidebar-to-Route Mapping

### ✅ SECTION 1: Overview (2/2 Complete)

| Menu Item | Route | Page Exists? | File Path | Status |
|-----------|-------|--------------|-----------|--------|
| Home (Dev) | `/` | ✅ YES | `pages/HomePage.jsx` | Working |
| Dashboard | `/dashboard` | ✅ YES | `pages/Dashboard.jsx` | Working |

**Section Status:** ✅ 100% Complete

---

### 🔴 SECTION 2: Accounts (0/6 Missing)

| Menu Item | Route | Page Exists? | File Path | Status |
|-----------|-------|--------------|-----------|--------|
| TradeStation | `/account/tradestation` | ❌ NO | N/A | **MISSING** |
| ├─ Equity | `/account/tradestation/equity` | ❌ NO | N/A | **MISSING** |
| ├─ Futures | `/account/tradestation/futures` | ❌ NO | N/A | **MISSING** |
| Tastytrade | `/account/tastytrade` | ❌ NO | N/A | **MISSING** |
| ├─ Equity | `/account/tastytrade/equity` | ❌ NO | N/A | **MISSING** |
| ├─ Futures | `/account/tastytrade/futures` | ❌ NO | N/A | **MISSING** |
| ├─ Crypto | `/account/tastytrade/crypto` | ❌ NO | N/A | **MISSING** |

**Section Status:** 🔴 0/6 pages exist  
**Impact:** HIGH - Core account management inaccessible

**Note:** Only `/account/balance` exists (`AccountBalancePage.jsx`), which is NOT in sidebar

---

### 🟡 SECTION 3: Mindfolio Manager (2/4 + Dynamic)

| Menu Item | Route | Page Exists? | File Path | Status |
|-----------|-------|--------------|-----------|--------|
| View All Mindfolios | `/mindfolio` | ✅ YES | `pages/MindfolioList.jsx` | Working |
| ├─ Dynamic: {name} | `/mindfolio/:id` | ✅ YES | `pages/MindfolioDetailNew.jsx` | Working |
| + Create Mindfolio | `/mindfolio/new` | ✅ YES | `pages/MindfolioCreate.jsx` | Working |
| Mindfolio Analytics | `/mindfolio/analytics` | ❌ NO | N/A | **MISSING** |
| Smart Rebalancing | `/mindfolio/rebalancing` | ❌ NO | N/A | **MISSING** |

**Section Status:** 🟡 3/5 pages exist (60%)  
**Impact:** MEDIUM - Core CRUD works, advanced features missing

---

### 🔴 SECTION 4: Stocks Data (0/3 Missing)

| Menu Item | Route | Page Exists? | File Path | Status |
|-----------|-------|--------------|-----------|--------|
| Investment Scoring | `/stocks/scoring` | ❌ NO | N/A | **MISSING** |
| Scoring Scanner | `/stocks/scanner` | ❌ NO | N/A | **MISSING** |
| Top Picks | `/stocks/top-picks` | ❌ NO | N/A | **MISSING** |

**Section Status:** 🔴 0/3 pages exist  
**Impact:** HIGH - Entire stock analysis section non-functional

---

### 🟡 SECTION 5: Options Data (4/18 Partial)

| Menu Item | Route | Page Exists? | File Path | Status |
|-----------|-------|--------------|-----------|--------|
| Builder | `/builder` | ✅ YES | `pages/BuilderV2Page.jsx` | Working |
| Analytics | `/options/analytics` | ❌ NO | N/A | **MISSING** |
| ├─ Backtests | `/analytics/backtests` | ❌ NO | N/A | **MISSING** |
| ├─ Verified Chains | `/analytics/verified` | ❌ NO | N/A | **MISSING** |
| Algos | `/screener/iv` | ❌ NO | N/A | **MISSING** |
| ├─ Trade Simulator | `/simulator` | ✅ YES | `pages/SimulatorPage.jsx` | Working |
| ├─ IV Setups (Auto) | `/screener/iv` | ❌ NO | N/A | **MISSING** |
| ├─ Iron Condor Scanner | `/screener/iv?strategy=IRON_CONDOR` | ❌ NO | N/A | **MISSING** |
| ├─ Calendar Scanner | `/screener/iv?strategy=CALENDAR` | ❌ NO | N/A | **MISSING** |
| ├─ Diagonal Scanner | `/screener/iv?strategy=DIAGONAL` | ❌ NO | N/A | **MISSING** |
| ├─ Double Diagonal | `/screener/iv?strategy=DOUBLE_DIAGONAL` | ❌ NO | N/A | **MISSING** |
| ├─ Sell Puts (Auto) | `/screener/sell-puts` | ❌ NO | N/A | **MISSING** |
| ├─ Put Selling Engine | `/screener/sell-puts` | ❌ NO | N/A | **MISSING** |
| ├─ Covered Calls | `/screener/covered-calls` | ❌ NO | N/A | **MISSING** |
| ├─ Cash-Secured Puts | `/screener/csp` | ❌ NO | N/A | **MISSING** |
| ├─ Preview Queue | `/trades/preview` | ❌ NO | N/A | **MISSING** |
| ├─ Orders (SIM) | `/trades/orders/sim` | ❌ NO | N/A | **MISSING** |
| ├─ Orders (LIVE) | `/trades/orders/live` | ❌ NO | N/A | **MISSING** |
| Option Chain (TS) | `/md/chain` | ❌ NO | N/A | **MISSING** |

**Section Status:** 🔴 2/18 pages exist (11%)  
**Impact:** CRITICAL - Most options tools unavailable

**Notes:**
- `/screener/iv` appears 7 times with different query params (should be 1 page with filtering)
- `/screener/sell-puts` is duplicated (should be 1 page)
- Strategy Library exists at `/strategies` but NOT in sidebar!

---

### ✅ SECTION 6: Market Intelligence (5/5 Complete)

| Menu Item | Route | Page Exists? | File Path | Status |
|-----------|-------|--------------|-----------|--------|
| Flow Summary | `/flow` | ✅ YES | `pages/FlowPage.jsx` | Working |
| Dark Pool | `/dark-pool` | ✅ YES | `pages/DarkPoolPage.jsx` | Working |
| Market Movers | `/market-movers` | ✅ YES | `pages/MarketMoversPage.jsx` | Working |
| Congress Trades | `/congress-trades` | ✅ YES | `pages/CongressTradesPage.jsx` | Working |
| Institutional | `/institutional` | ✅ YES | `pages/InstitutionalPage.jsx` | Working |

**Section Status:** ✅ 100% Complete  
**Impact:** NONE - All working!

---

### 🔴 SECTION 7: Settings (1/8 Partial)

| Menu Item | Route | Page Exists? | File Path | Status |
|-----------|-------|--------------|-----------|--------|
| Risk & Gates | `/settings/gates` | ❌ NO | N/A | **MISSING** |
| Screensaver | `/settings/screensaver` | ✅ YES | `pages/ScreensaverSettings.jsx` | Working |
| Data & APIs | `/settings/keys` | ❌ NO | N/A | **MISSING** |
| ├─ TradeStation | `/providers/ts` | ⚠️ PARTIAL | `pages/TradeStationLogin.jsx` | Route mismatch! |
| ├─ Unusual Whales | `/providers/uw` | ❌ NO | N/A | **MISSING** |
| ├─ API Keys | `/settings/keys` | ❌ NO | N/A | **MISSING** |
| System Diagnostics | `/ops/redis` | ❌ NO | N/A | **MISSING** |
| ├─ Redis Cache | `/ops/redis` | ❌ NO | N/A | **MISSING** |
| ├─ Backtest Ops | `/ops/bt` | ❌ NO | N/A | **MISSING** |

**Section Status:** 🔴 1/8 pages exist (12.5%)  
**Impact:** HIGH - System configuration mostly inaccessible

**Route Mismatch:**
- Sidebar: `/providers/ts`
- App.js: `/tradestation/login`
- **ACTION REQUIRED:** Fix route or sidebar config

---

### 🔴 SECTION 8: Help (0/1 Missing)

| Menu Item | Route | Page Exists? | File Path | Status |
|-----------|-------|--------------|-----------|--------|
| Docs | `/help/docs` | ❌ NO | N/A | **MISSING** |

**Section Status:** 🔴 0/1 pages exist  
**Impact:** LOW - Documentation can be external

---

## 🚨 Critical Issues Summary

### 1. Route Mismatches (Immediate Fix Required)

| Sidebar Link | Expected Route | Actual Route in App.js | Fix Action |
|--------------|----------------|------------------------|------------|
| TradeStation (Settings) | `/providers/ts` | `/tradestation/login` | Update sidebar to `/tradestation/login` |

### 2. Pages That Exist But NOT in Sidebar

| Page File | Route in App.js | Should Add to Sidebar? |
|-----------|-----------------|------------------------|
| `StrategyLibraryPage.jsx` | `/strategies` | ✅ YES - Add to Options Data section |
| `AccountBalancePage.jsx` | `/account/balance` | ✅ YES - Add to Accounts section |
| `TradeStationLogin.jsx` | `/tradestation/login` | ✅ Already in sidebar (wrong path) |
| `LogosPage.jsx` | `/logos` | ❌ NO - Dev tool |
| `CardTestPage.jsx` | `/card-test` | ❌ NO - Test page |
| `StrategyChartTestPage.jsx` | `/strategy-chart-test` | ❌ NO - Test page |
| `UniversalStrategyCardTestPage.jsx` | `/strategy-card-test` | ❌ NO - Test page |
| `LongPutTestPage.jsx` | `/long-put-test` | ❌ NO - Test page |
| `LiveFlowPage.jsx` | `/flow/live` | ⚠️ MAYBE - Sub-route of Flow |
| `MindfolioPage.jsx` | `/mindfolio/page/:id` | ❓ Check if duplicate |

### 3. Duplicate/Redundant Sidebar Items

| Item | Issue | Fix Action |
|------|-------|------------|
| "Sell Puts (Auto)" + "Put Selling Engine" | Both point to `/screener/sell-puts` | Remove duplicate |
| 7 IV Scanner entries | All point to `/screener/iv` with query params | Create 1 page with tabs/filters |

---

## 📊 Statistics by Priority

### High Priority (Core Features - 22 missing pages)
1. **Accounts Section:** 6 pages needed
2. **Stocks Section:** 3 pages needed
3. **Options Screeners:** 10 pages needed
4. **Settings:** 6 pages needed

### Medium Priority (Advanced Features - 5 missing pages)
1. **Mindfolio Analytics:** 2 pages needed
2. **Options Analytics:** 2 pages needed
3. **Option Chain (TS):** 1 page needed

### Low Priority (Nice-to-Have - 3 missing pages)
1. **Help/Docs:** 1 page needed
2. **Orders/Preview:** 2 pages needed (may not be implemented yet)

---

## ✅ Recommended Action Plan

### Phase 1: Fix Critical Mismatches (30 minutes)

**Task 1.1: Fix TradeStation Route Mismatch**
```javascript
// In nav.simple.js, change:
{ label: "TradeStation", to: "/providers/ts", icon: "Building2" }
// To:
{ label: "TradeStation", to: "/tradestation/login", icon: "Building2" }
```

**Task 1.2: Add Existing Pages to Sidebar**
```javascript
// In "Options Data" section, add after "Builder":
{ label: "Strategy Library", to: "/strategies", icon: "Library" },

// In "Accounts" section, add:
{ label: "Account Balance", to: "/account/balance", icon: "DollarSign" },
```

**Task 1.3: Remove Duplicate "Sell Puts"**
```javascript
// Keep only one:
{ label: "Put Selling Engine", to: "/screener/sell-puts", icon: "ArrowDown" },
// Delete:
{ label: "Sell Puts (Auto)", to: "/screener/sell-puts", icon: "ArrowDownCircle" },
```

### Phase 2: Create Missing High-Priority Pages (2-3 days)

**Priority 1: Accounts (6 pages)**
1. Create `/account/tradestation` - TradeStation account overview
2. Create `/account/tradestation/equity` - Equity account details
3. Create `/account/tradestation/futures` - Futures account details
4. Create `/account/tastytrade` - Tastytrade account overview
5. Create `/account/tastytrade/equity` - Equity account
6. Create `/account/tastytrade/futures` - Futures account
7. Create `/account/tastytrade/crypto` - Crypto account

**Priority 2: Options Screeners (Consolidate into 1 page with tabs)**
1. Create `/screener/iv` - IV Scanner with strategy tabs:
   - Iron Condor
   - Calendar
   - Diagonal
   - Double Diagonal
   - Default IV setups
2. Create `/screener/sell-puts` - Put Selling Engine (already in sidebar)
3. Create `/screener/covered-calls` - Covered Calls scanner
4. Create `/screener/csp` - Cash-Secured Puts scanner

**Priority 3: Settings (4 pages)**
1. Create `/settings/gates` - Risk management gates
2. Create `/settings/keys` - API keys management
3. Create `/providers/uw` - Unusual Whales API settings
4. Create `/ops/redis` - Redis cache diagnostics
5. Create `/ops/bt` - Backtest operations

### Phase 3: Create Missing Medium-Priority Pages (1-2 days)

**Mindfolio Enhancements:**
1. Create `/mindfolio/analytics` - Mindfolio analytics dashboard
2. Create `/mindfolio/rebalancing` - Smart rebalancing tool

**Options Analytics:**
1. Create `/analytics/backtests` - Backtest results viewer
2. Create `/analytics/verified` - Verified options chains
3. Create `/md/chain` - TradeStation options chain viewer

**Stocks Data:**
1. Create `/stocks/scoring` - Investment scoring tool
2. Create `/stocks/scanner` - Stock scanner
3. Create `/stocks/top-picks` - Top stock picks

### Phase 4: Low Priority & Cleanup (1 day)

1. Create `/help/docs` - Documentation page (or link to external docs)
2. Create `/trades/preview` - Preview queue (if trading feature exists)
3. Create `/trades/orders/sim` - SIM orders (if trading feature exists)
4. Create `/trades/orders/live` - LIVE orders (if trading feature exists)
5. Remove test pages from production sidebar

---

## 🎯 Quick Wins (Do First!)

These fixes take < 1 hour and improve UX immediately:

1. ✅ Fix TradeStation route mismatch
2. ✅ Add Strategy Library to sidebar (page exists!)
3. ✅ Add Account Balance to sidebar (page exists!)
4. ✅ Remove duplicate "Sell Puts" entry
5. ✅ Update sidebar to highlight active routes correctly

---

## 📝 Implementation Checklist

### Immediate Fixes (Phase 1)
- [ ] Update TradeStation route in `nav.simple.js`
- [ ] Add Strategy Library to sidebar under Options Data
- [ ] Add Account Balance to sidebar under Accounts
- [ ] Remove duplicate "Sell Puts (Auto)" entry
- [ ] Test all existing routes work correctly

### High Priority Pages (Phase 2)
- [ ] Create Account pages (7 total)
- [ ] Create Screener pages (4 total)
- [ ] Create Settings pages (5 total)

### Medium Priority Pages (Phase 3)
- [ ] Create Mindfolio Analytics pages (2 total)
- [ ] Create Options Analytics pages (3 total)
- [ ] Create Stocks Data pages (3 total)

### Low Priority (Phase 4)
- [ ] Create Help/Docs page (1 total)
- [ ] Create Trading pages if applicable (3 total)

---

## 🔍 Active State Highlighting Issue

**Problem:** Sidebar may not highlight active routes correctly for nested paths.

**Root Cause Analysis Required:**
1. Check `SidebarSimple.jsx` for `isActive` detection logic
2. Verify it handles nested routes like `/account/tradestation/equity`
3. Test with current routes to see if highlighting works

**Expected Behavior:**
- When on `/mindfolio/123`, "View All Mindfolios" should be highlighted
- When on `/screener/iv?strategy=IRON_CONDOR`, "IV Setups (Auto)" should be highlighted
- When on `/account/tradestation/equity`, "TradeStation" parent should be highlighted

**Investigation Needed:**
```javascript
// Check SidebarSimple.jsx for active detection:
const isActive = location.pathname === item.to; // Too simple?
// Should be:
const isActive = location.pathname.startsWith(item.to); // Better for nested routes
```

---

## 📈 Progress Tracking

**Current Status:**
- ✅ Complete: 17/47 routes (36%)
- 🔴 Missing: 30/47 routes (64%)

**After Phase 1 (Quick Fixes):**
- ✅ Complete: 19/47 routes (40%)
- 🔴 Missing: 28/47 routes (60%)

**After Phase 2 (High Priority):**
- ✅ Complete: 35/47 routes (74%)
- 🔴 Missing: 12/47 routes (26%)

**After Phase 3 (Medium Priority):**
- ✅ Complete: 43/47 routes (91%)
- 🔴 Missing: 4/47 routes (9%)

**After Phase 4 (Complete):**
- ✅ Complete: 47/47 routes (100%)
- 🔴 Missing: 0/47 routes (0%)

---

## 🎉 Summary

FlowMind has a comprehensive sidebar navigation with 47 menu items, but **only 36% have working pages**. The good news: Market Intelligence section is 100% complete, and core Mindfolio CRUD operations work.

**Top 3 Action Items:**
1. **Fix route mismatches** (TradeStation link) - 5 minutes
2. **Add existing pages to sidebar** (Strategy Library, Account Balance) - 10 minutes
3. **Create Account pages** (7 pages for broker accounts) - 1-2 days

**Estimated Time to 100% Completion:**
- Phase 1 (Quick Fixes): 30 minutes
- Phase 2 (High Priority): 2-3 days
- Phase 3 (Medium Priority): 1-2 days
- Phase 4 (Low Priority): 1 day
- **Total: 4-6 days of focused work**

---

**Next Steps:** Review this audit with the team and prioritize which sections to implement first based on business needs and user requests.
