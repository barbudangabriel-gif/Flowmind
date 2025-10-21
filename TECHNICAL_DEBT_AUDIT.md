# Technical Debt Audit Report
**Date:** October 21, 2025  
**Auditor:** GitHub Copilot  
**Scope:** Backend + Frontend codebase analysis

---

## 📊 Executive Summary

| Metric | Count | Priority |
|--------|-------|----------|
| TODO/FIXME Comments | 37 | MEDIUM |
| Hardcoded URLs | 18+ | HIGH |
| Files > 1000 lines | 11 | MEDIUM |
| Unused imports (after fix) | 2 | LOW |
| Ruff errors remaining | 103 | MEDIUM |

---

## 🔍 Detailed Findings

### 1. TODO/FIXME Comments (37 total)

#### HIGH Priority TODOs (8 items):
```python
# OPS-001 to OPS-008: Critical integrations needed
backend/mindfolio.py:724   - TODO[OPS-001]: Implement quote subscription (database service)
backend/mindfolio.py:759   - TODO[OPS-002]: Database integration for position tracking
backend/mindfolio.py:803   - TODO[OPS-003]: Database integration for buckets
backend/mindfolio.py:881   - TODO[OPS-004]: Calculate win_rate from trades
backend/mindfolio.py:882   - TODO[OPS-005]: Calculate sharpe_ratio from equity curve
backend/mindfolio.py:883   - TODO[OPS-006]: Calculate max_drawdown from equity curve
backend/mindfolio.py:886   - TODO[OPS-007]: Implement bucket-level analytics
backend/investment_scoring.py:147 - TODO[OPS-008]: TradeStation API integration for ticker list
```

#### MEDIUM Priority TODOs (12 items):
```python
# Integration with external services
backend/geopolitical_news_agent.py:48  - TODO: Integrate real data sources
backend/geopolitical_news_agent.py:334 - TODO: Integrate Investment Scoring Agent
backend/routers/geopolitical.py:99     - TODO: Fetch actual positions from mindfolio
backend/routers/geopolitical.py:223    - TODO: Integrate economic calendar API
backend/routers/term_structure.py:268  - TODO: Integrate TradeStation execution
backend/routers/dashboard.py:19        - TODO: Integrate real data sources

# WebSocket channel verification
backend/routers/stream.py:372  - TODO: Verify market_movers channel name
backend/routers/stream.py:421  - TODO: Verify dark_pool channel name
backend/routers/stream.py:468  - TODO: Verify congress_trades channel name

# Business logic improvements
backend/mindfolio.py:1187  - TODO: Add module field to Transaction model
backend/mindfolio.py:1200  - TODO: Sophisticated calculation for options
backend/mindfolio.py:1349  - TODO: Check daily loss limit per module
```

#### LOW Priority TODOs (17 items):
- Various code cleanup and optimization opportunities
- Frontend component improvements
- Documentation updates

---

### 2. Hardcoded URLs (18 instances)

#### 🔴 CRITICAL: Hardcoded API URLs (should use env vars)
```python
# TradeStation URLs
backend/tradestation_auth_service.py:30   - "http://localhost:8001/api/auth/tradestation/callback"
backend/tradestation_auth_service.py:37   - "https://api.tradestation.com/v3"
backend/tradestation_auth.py:34           - "https://api.tradestation.com/v3"
backend/tradestation_auth.py:58           - "http://localhost:8001/api/auth/tradestation/callback"
backend/app/routers/tradestation.py:16    - "https://api.tradestation.com/v3"

# Unusual Whales URLs
backend/unusual_whales_service_clean.py:83 - "https://api.unusualwhales.com/api" (HARDCODED!)
backend/services/uw_flow.py:11             - Uses env var with hardcoded fallback ✅

# Frontend redirects
backend/app/routers/oauth.py:158   - "http://localhost:3000/" (OAuth success redirect)
backend/app/routers/oauth.py:171   - "http://localhost:3000/" (Dashboard link)
```

#### ✅ ACCEPTABLE: Uses env vars with fallbacks
```python
backend/config.py:31  - ts_base_url with Field default
backend/config.py:35  - ts_redirect_uri with Field default
backend/app/main.py:18 - ALLOWED_ORIGINS with getenv
backend/services/providers/uw_provider.py:12 - Uses getenv with fallback
```

**Recommendation:** Move ALL hardcoded URLs to environment variables or config.py

---

### 3. Large Files (>1000 lines)

#### 🔴 CRITICAL: Files needing refactoring (>2000 lines)
```
frontend/src/pages/MindfolioDetailNew.jsx  - 3,339 lines ⚠️ HUGE!
backend/technical_analysis_agent.py        - 2,532 lines
backend/unusual_whales_service.py          - 1,674 lines
frontend/src/components/InvestmentScoring.js - 1,553 lines
backend/investment_scoring_agent.py        - 1,383 lines
```

**Impact:**
- Hard to maintain and test
- Difficult code reviews
- Higher bug risk
- Slow IDE performance

**Recommendation:** Split into smaller modules (<500 lines each)

#### 🟡 MEDIUM: Files approaching limit (1000-2000 lines)
```
backend/mindfolio.py              - 1,381 lines (FIFO logic, could split)
backend/investment_scoring.py     - 1,245 lines
backend/mindfolios.py             - 1,137 lines (duplicate of mindfolio.py?)
backend/smart_money_analysis.py   - 1,015 lines
```

**Action:** Monitor growth, consider splitting when adding features

---

### 4. Duplicate/Similar Files

#### Potential Duplicates Found:
```
backend/mindfolio.py (1,381 lines) vs backend/mindfolios.py (1,137 lines)
→ Need to verify if these serve different purposes or are duplicates

backend/unusual_whales_service.py (1,674 lines) vs unusual_whales_service_clean.py (739 lines)
→ Clean version is 56% smaller, consider deprecating old one

backend/tradestation_auth.py vs backend/tradestation_auth_service.py
→ Similar functionality, consolidate?
```

---

### 5. Environment Variables Audit

#### ✅ Well-documented variables:
- `UW_API_TOKEN` / `UNUSUAL_WHALES_API_KEY`
- `TS_CLIENT_ID`, `TS_CLIENT_SECRET`, `TS_REDIRECT_URI`
- `REDIS_URL`, `MONGO_URL`
- `REACT_APP_BACKEND_URL`

#### ⚠️ Missing from docs:
- `UW_BASE_URL` (default: https://api.unusualwhales.com)
- `TS_BASE_URL` (default: https://api.tradestation.com)
- `ALLOWED_ORIGINS` (CORS configuration)
- `FM_FORCE_FALLBACK`, `FM_REDIS_REQUIRED`, `TEST_MODE`

**Recommendation:** Create `.env.example` with all variables documented

---

### 6. Code Quality Metrics

#### Backend (Python):
- **Total files:** 128
- **Ruff errors:** 103 (down from 645, -84% ✅)
  - 49x F405 (import star usage) - SAFE
  - 18x E722 (bare except) - Should add exception types
  - 17x E402 (module import not at top) - Reorganize imports
  - 10x E741 (ambiguous variable name) - Rename variables
  - 4x F811 (redefined while unused) - Remove duplicates
  - 2x F401 (unused import) - Clean up
  - 2x F821 (undefined name) - Fix references

#### Frontend (JavaScript/JSX):
- **ESLint issues:** 1,054 (167 errors, 887 warnings)
  - Mostly `no-unused-vars` warnings (safe, can clean up)
  - Some `no-undef` errors for `process` and `module` (needs env config)

---

### 7. Architecture Issues

#### Routing Confusion:
- **Duplicate router patterns:**
  - `backend/routers/*.py` (mounted with `/api` prefix)
  - `backend/app/routers/*.py` (some pre-configured with `/api`)
  - Causes confusion about where to add new routes

#### Service Organization:
- **Mixed patterns:**
  - Some services in `backend/services/`
  - Some services at root `backend/*_service.py`
  - Some in `backend/app/services/`
  - **Recommendation:** Consolidate into single pattern

#### Test Organization:
- ✅ **FIXED:** 96 test files moved to `tests/archived_integration_tests/`
- 91 files still in root (documentation, scripts, etc.)
- **Recommendation:** Move all `.py` scripts to `scripts/` folder

---

## 🎯 Prioritized Action Plan

### Phase 1: Quick Wins (1-2 hours)
1. ✅ Fix duplicate key in App.js (DONE)
2. ✅ Archive old App.js versions (DONE)
3. ✅ Organize test files (DONE)
4. 🔲 Create `.env.example` with all variables
5. 🔲 Fix 2 unused imports in backend/server.py
6. 🔲 Add exception types to bare excepts (18 instances)

### Phase 2: Medium Impact (4-6 hours)
1. 🔲 Move hardcoded URLs to config (18 instances)
2. 🔲 Document all TODO comments in PROJECT_TASKS.md
3. 🔲 Consolidate router organization (pick one pattern)
4. 🔲 Remove deprecated unusual_whales_service.py (keep _clean.py)
5. 🔲 Split MindfolioDetailNew.jsx (3,339 lines → 5-6 smaller components)

### Phase 3: Refactoring (2-3 days)
1. 🔲 Refactor technical_analysis_agent.py (2,532 lines)
2. 🔲 Split InvestmentScoring.js component (1,553 lines)
3. 🔲 Consolidate mindfolio.py and mindfolios.py
4. 🔲 Implement OPS-001 to OPS-008 TODOs (critical features)
5. 🔲 WebSocket channel verification (stream.py TODOs)

### Phase 4: Architecture (1 week)
1. 🔲 Standardize service organization
2. 🔲 Implement multi-broker architecture (Task #1)
3. 🔲 Add comprehensive error handling
4. 🔲 Performance optimization (large files, queries)
5. 🔲 Security hardening (remove hardcoded secrets)

---

## 📈 Progress Tracking

### Completed (Today):
- ✅ Code cleanup: 645 → 103 errors (-84%)
- ✅ Fixed duplicate key in App.js
- ✅ Archived 4 old App.js versions
- ✅ Organized 96 test files
- ✅ Auto-formatted 18 Python files

### In Progress:
- 🟡 Technical debt documentation (this file)
- 🟡 Environment variables audit

### Blocked:
- ⏸️ Database integration (OPS-001 to OPS-007) - needs design decision
- ⏸️ TradeStation execution (needs production credentials)

---

## 💡 Recommendations

### Immediate (Do Today):
1. Create `.env.example` with all variables documented
2. Fix 2 unused imports in server.py
3. Move all hardcoded `localhost:3000` URLs to env vars

### Short-term (This Week):
1. Split MindfolioDetailNew.jsx into smaller components
2. Document all TODOs in PROJECT_TASKS.md
3. Consolidate router organization
4. Remove deprecated files (unusual_whales_service.py old version)

### Long-term (Next Sprint):
1. Implement multi-broker architecture
2. Refactor large files (>2000 lines)
3. Add comprehensive test coverage
4. Performance optimization

---

## 📝 Notes

- All git history preserved (used `git mv` for file moves)
- Pre-commit hooks passing (Python 3.12 validation)
- No breaking changes introduced in cleanup
- Backward compatibility maintained

**Last Updated:** October 21, 2025  
**Next Review:** October 28, 2025 (1 week)
