# 🔍 Sidebar Missing Pages - Complete Audit

**Date:** October 21, 2025  
**Auditor:** Copilot Agent  
**Source:** `frontend/src/lib/nav.simple.js` vs `frontend/src/App.js`

---

## 📊 Summary Statistics

- **Total Sidebar Items:** ~40 menu items
- **Existing Pages (Routes in App.js):** 18
- **Missing Pages (No Route):** 22
- **Homepage Broken Links:** 2
- **Coverage:** 45% (less than half functional!)

---

## ✅ EXISTING PAGES (18 total)

### Working Routes in App.js:
1. `/` → HomePage.jsx (Screensaver)
2. `/dashboard` → Dashboard.jsx
3. `/builder` → BuilderPage.jsx
4. `/simulator` → SimulatorPage.jsx
5. `/flow` → FlowPage.jsx
6. `/mindfolio` → MindfolioList.jsx
7. `/mindfolio/new` → MindfolioCreate.jsx
8. `/mindfolio/:id` → MindfolioDetailNew.jsx
9. `/account/balance` → AccountBalancePage.jsx
10. `/market-movers` → MarketMoversPage.jsx
11. `/congress-trades` → CongressTradesPage.jsx
12. `/dark-pool` → DarkPoolPage.jsx
13. `/institutional` → InstitutionalPage.jsx
14. `/settings/screensaver` → ScreensaverSettings.jsx
15. `/tradestation/login` → TradeStationLogin.jsx
16. `/logos` → LogosPage.jsx (hidden utility page)
17. `/mindfolio/page/:id` → MindfolioPage.jsx
18. `*` → ComingSoonPage (catch-all 404)

---

## ❌ MISSING PAGES (22 total)

### 🏠 Homepage Broken Links (2)
| # | Route | Link From | Status | Priority |
|---|-------|-----------|--------|----------|
| 1 | `/mindfolios` | HomePage Quick Action #3 | WRONG - should be `/mindfolio` | HIGH |
| 2 | `/optimize` | HomePage Quick Action #4 | MISSING PAGE | HIGH |

### 📊 Stocks Data (3)
| # | Route | Sidebar Label | Parent Section | Priority |
|---|-------|---------------|----------------|----------|
| 3 | `/stocks/scoring` | Investment Scoring | Stocks Data | MEDIUM |
| 4 | `/stocks/scanner` | Scoring Scanner | Stocks Data | MEDIUM |
| 5 | `/stocks/top-picks` | Top Picks | Stocks Data | LOW |

### 📈 Options Data - Algos Submenu (12)
| # | Route | Sidebar Label | Parent Section | Priority |
|---|-------|---------------|----------------|----------|
| 6 | `/screener/iv` | IV Setups (Auto) | Options Data > Algos | HIGH |
| 7 | `/screener/iv?strategy=IRON_CONDOR` | Iron Condor Scanner | Options Data > Algos | MEDIUM |
| 8 | `/screener/iv?strategy=CALENDAR` | Calendar Scanner | Options Data > Algos | MEDIUM |
| 9 | `/screener/iv?strategy=DIAGONAL` | Diagonal Scanner | Options Data > Algos | MEDIUM |
| 10 | `/screener/iv?strategy=DOUBLE_DIAGONAL` | Double Diagonal | Options Data > Algos | MEDIUM |
| 11 | `/screener/sell-puts` | Sell Puts (Auto) + Put Selling Engine | Options Data > Algos | HIGH |
| 12 | `/screener/covered-calls` | Covered Calls | Options Data > Algos | MEDIUM |
| 13 | `/screener/csp` | Cash-Secured Puts | Options Data > Algos | MEDIUM |
| 14 | `/trades/preview` | Preview Queue | Options Data > Algos | LOW |
| 15 | `/trades/orders/sim` | Orders (SIM) | Options Data > Algos | LOW |
| 16 | `/trades/orders/live` | Orders (LIVE) | Options Data > Algos | LOW |
| 17 | `/md/chain` | Option Chain (TS) | Options Data | MEDIUM |

### 📉 Analytics Submenu (2)
| # | Route | Sidebar Label | Parent Section | Priority |
|---|-------|---------------|----------------|----------|
| 18 | `/analytics/backtests` | Backtests | Options Data > Analytics | MEDIUM |
| 19 | `/analytics/verified` | Verified Chains | Options Data > Analytics | LOW |

### 💼 Mindfolio Manager (2)
| # | Route | Sidebar Label | Parent Section | Priority |
|---|-------|---------------|----------------|----------|
| 20 | `/mindfolio/analytics` | Mindfolio Analytics | Mindfolio Manager | MEDIUM |
| 21 | `/mindfolio/rebalancing` | Smart Rebalancing | Mindfolio Manager | LOW |

### ⚙️ Settings & System (5)
| # | Route | Sidebar Label | Parent Section | Priority |
|---|-------|---------------|----------------|----------|
| 22 | `/settings/gates` | Risk & Gates | Settings | LOW |
| 23 | `/settings/keys` | API Keys | Settings > Data & APIs | LOW |
| 24 | `/providers/ts` | TradeStation | Settings > Data & APIs | MEDIUM |
| 25 | `/providers/uw` | Unusual Whales | Settings > Data & APIs | LOW |
| 26 | `/ops/redis` | Redis Cache | Settings > System Diagnostics | LOW |
| 27 | `/ops/bt` | Backtest Ops | Settings > System Diagnostics | LOW |

### 📚 Help (1)
| # | Route | Sidebar Label | Parent Section | Priority |
|---|-------|---------------|----------------|----------|
| 28 | `/help/docs` | Docs | Help | LOW |

---

## 🎯 Priority Breakdown

### 🔴 HIGH Priority (4 pages)
**Must create before deploy - user-facing features**
1. Fix `/mindfolios` → `/mindfolio` (HomePage line 30)
2. `/optimize` - AI strategy optimizer (HomePage + Sidebar)
3. `/screener/iv` - IV scanner (core algo feature)
4. `/screener/sell-puts` - Put selling engine (core algo feature)

### 🟡 MEDIUM Priority (11 pages)
**Important features, can create iteratively**
5. `/stocks/scoring` - Investment scoring
6. `/stocks/scanner` - Stock scanner
7. `/screener/iv?strategy=IRON_CONDOR` - Iron condor scanner
8. `/screener/iv?strategy=CALENDAR` - Calendar scanner
9. `/screener/iv?strategy=DIAGONAL` - Diagonal scanner
10. `/screener/iv?strategy=DOUBLE_DIAGONAL` - Double diagonal scanner
11. `/screener/covered-calls` - Covered calls scanner
12. `/screener/csp` - Cash-secured puts
13. `/md/chain` - TradeStation option chain viewer
14. `/analytics/backtests` - Backtest history
15. `/mindfolio/analytics` - Mindfolio analytics
16. `/providers/ts` - TradeStation settings

### 🟢 LOW Priority (13 pages)
**Nice-to-have, can defer or remove from sidebar**
17-28. (Rest of the pages - settings, diagnostics, help docs, etc.)

---

## 🗂️ Archived Pages (Potential Restore)

Located in `/frontend/src/archive/` (24 files):
- `ChartPage.js` → Might restore for charting features
- `ChartProPage.js` → Advanced charting
- `OptionsWorkbench.jsx` → Could repurpose for `/screener/iv`
- `OptionsAnalytics.jsx` → Could use for `/analytics/backtests`

---

## 📋 Recommended Action Plan

### Phase 1: Quick Fixes (30 minutes)
1. ✅ Fix `/mindfolios` → `/mindfolio` in HomePage.jsx line 30
2. ✅ Update PROJECT_TASKS.md with individual tasks

### Phase 2: HIGH Priority Pages (2-3 days)
3. Create `/optimize` - OptimizePage.jsx (AI strategy optimizer)
4. Create `/screener/iv` - IVScannerPage.jsx (IV setups)
5. Create `/screener/sell-puts` - SellPutsPage.jsx (put selling engine)

### Phase 3: MEDIUM Priority (1-2 weeks)
6-16. Create remaining medium priority pages

### Phase 4: LOW Priority or Remove (optional)
17-28. Either create low priority pages OR remove from sidebar

---

## 🛠️ Individual Task Files to Create

Each missing page should have a task in PROJECT_TASKS.md:
- Task #3: Fix HomePage /mindfolios link
- Task #4: Create OptimizePage (/optimize)
- Task #5: Create IVScannerPage (/screener/iv)
- Task #6: Create SellPutsPage (/screener/sell-puts)
- Task #7: Create StockScoringPage (/stocks/scoring)
- Task #8: Create StockScannerPage (/stocks/scanner)
... (continue for all 28 items)

---

**Next Step:** Create individual granular tasks în PROJECT_TASKS.md pentru fiecare pagină lipsă, începând cu HIGH priority items.
