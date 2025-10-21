# 🎯 FlowMind - UW API Integration Task List

**Date:** October 21, 2025  
**Status:** Ready for implementation  
**Priority:** HIGH - Unblocks TradeStation OAuth dependency

---

## ✅ Discovery Phase (COMPLETE)

- [x] Tested UW API token authentication
- [x] Discovered 5 working endpoints
- [x] Verified data quality (500+ options contracts, 345+ GEX records)
- [x] Documented all endpoint structures
- [x] Created comprehensive endpoint documentation

---

## 🚀 Phase 1: Backend Integration (IMMEDIATE)

### Task 1.1: Update `backend/unusual_whales_service.py`
**Priority:** 🔴 CRITICAL  
**Estimated time:** 30 minutes

**Actions:**
- [ ] Remove hallucinated endpoints (`/api/options-flow`, `/api/stock/{ticker}/quote`, etc.)
- [ ] Add `get_option_contracts(ticker)` method
- [ ] Add `get_spot_exposures(ticker)` method  
- [ ] Add `get_stock_info(ticker)` method
- [ ] Add `get_alerts(noti_type=None)` method
- [ ] Test each method with TSLA

**Files:**
- `backend/unusual_whales_service.py`
- `backend/integrations/uw_client.py` (if exists)

---

### Task 1.2: Add Options Chain Fallback
**Priority:** 🔴 CRITICAL  
**Estimated time:** 20 minutes

**Actions:**
- [ ] Update `backend/routers/options.py` → `/api/options/chain` endpoint
- [ ] Add try/except for TradeStation → fallback to UW
- [ ] Transform UW option-contracts format to match current response
- [ ] Add `source` field to response ("TradeStation" or "UnusualWhales")
- [ ] Test with frontend BuilderPage

**Files:**
- `backend/routers/options.py`

**Response format:**
```python
{
    "status": "success",
    "source": "UnusualWhales",  # or "TradeStation"
    "data": {
        "symbol": "TSLA",
        "spot": 444.5,  # Extract from option contracts
        "strikes": [
            {
                "strike": 450,
                "calls": {
                    "bid": 14.60,
                    "ask": 14.70,
                    "mid": 14.65,
                    "iv": 0.984,
                    "oi": 24061,
                    "volume": 23546,
                    "premium": 33892043
                },
                "puts": {...}
            }
        ]
    }
}
```

---

### Task 1.3: Add GEX Endpoint
**Priority:** 🟡 HIGH  
**Estimated time:** 15 minutes

**Actions:**
- [ ] Create new endpoint: `GET /api/options/gex?symbol=TSLA`
- [ ] Use `uw_service.get_spot_exposures(ticker)`
- [ ] Return gamma data in chart-friendly format
- [ ] Test with Plotly visualization

**Files:**
- `backend/routers/options.py` (add new route)

**Response format:**
```python
{
    "status": "success",
    "data": {
        "symbol": "TSLA",
        "timestamps": ["2025-10-21T10:30:00Z", ...],
        "prices": [444.5, 445.3, ...],
        "gamma_oi": [-415456.99, 823882513.69, ...],
        "charm_oi": [6932976.64, -87618802532.18, ...],
        "vanna_oi": [-52879.60, 211337523.26, ...]
    }
}
```

---

### Task 1.4: Update Flow Endpoints
**Priority:** 🟢 MEDIUM  
**Estimated time:** 20 minutes

**Actions:**
- [ ] Update `backend/routers/flow.py` → `/api/flow/summary`
- [ ] Use `uw_service.get_alerts(noti_type="market_tide")`
- [ ] Transform alerts format to match current flow response
- [ ] Add fallback to demo data if alerts empty
- [ ] Test with FlowPage frontend

**Files:**
- `backend/routers/flow.py`

---

## 🎨 Phase 2: Frontend Updates (OPTIONAL)

### Task 2.1: Add Data Source Indicator
**Priority:** 🟢 MEDIUM  
**Estimated time:** 10 minutes

**Actions:**
- [ ] Update `BuilderPage.jsx` to show data source badge
- [ ] Display "TradeStation" or "Unusual Whales" based on API response
- [ ] Add tooltip explaining source

**Files:**
- `frontend/src/pages/BuilderPage.jsx`

---

### Task 2.2: Add GEX Chart Component
**Priority:** 🟡 HIGH  
**Estimated time:** 45 minutes

**Actions:**
- [ ] Create `GammaExposureChart.jsx` component
- [ ] Fetch data from `/api/options/gex?symbol={ticker}`
- [ ] Render Plotly chart with gamma/charm/vanna lines
- [ ] Add to BuilderPage or create dedicated GEX page

**Files:**
- `frontend/src/components/charts/GammaExposureChart.jsx` (new)
- `frontend/src/pages/BuilderPage.jsx` (integrate)

---

### Task 2.3: Update Flow Page
**Priority:** 🟢 MEDIUM  
**Estimated time:** 15 minutes

**Actions:**
- [ ] Update `FlowPage.jsx` to handle new alerts format
- [ ] Display market tide events prominently
- [ ] Add filtering by alert type

**Files:**
- `frontend/src/pages/FlowPage.jsx`

---

## ✅ Phase 3: Testing & Validation

### Task 3.1: Backend Tests
**Priority:** 🔴 CRITICAL  
**Estimated time:** 20 minutes

**Actions:**
- [ ] Test `test_uw_advanced_plan.py` with new methods
- [ ] Create `test_options_uw_fallback.py` for fallback logic
- [ ] Verify all 5 endpoints still working
- [ ] Check response times (< 1 second)

**Files:**
- `test_uw_integration.py` (new)
- `test_options_uw_fallback.py` (new)

---

### Task 3.2: Frontend E2E Tests
**Priority:** 🟡 HIGH  
**Estimated time:** 15 minutes

**Actions:**
- [ ] Test BuilderPage with UW data source
- [ ] Verify options chain displays correctly
- [ ] Test strategy builder with UW-sourced prices
- [ ] Check GEX chart rendering (if implemented)

**Manual testing checklist:**
```
[ ] Open /builder?symbol=TSLA
[ ] Verify options chain loads (from UW if TS fails)
[ ] Check data source badge shows "Unusual Whales"
[ ] Build a simple call spread
[ ] Verify pricing calculation works
[ ] Check P&L chart renders
```

---

### Task 3.3: Documentation Updates
**Priority:** 🟢 MEDIUM  
**Estimated time:** 10 minutes

**Actions:**
- [ ] Update `README.md` with UW integration details
- [ ] Add UW API status to health check endpoint
- [ ] Update `.github/copilot-instructions.md` with correct endpoints
- [ ] Create `UW_API_INTEGRATION_COMPLETE.md` summary

**Files:**
- `README.md`
- `.github/copilot-instructions.md`
- `UW_API_INTEGRATION_COMPLETE.md` (new)

---

## 📊 Success Metrics

### Definition of Done:
- [x] ✅ UW API token verified working
- [x] ✅ 5 endpoints discovered and documented
- [ ] 🔄 Backend service updated with correct endpoints
- [ ] 🔄 Options chain accessible via UW (fallback working)
- [ ] 🔄 GEX data accessible and chartable
- [ ] 🔄 Flow alerts displaying market tide events
- [ ] 🔄 All tests passing
- [ ] 🔄 Frontend displaying UW data correctly
- [ ] 🔄 Documentation complete

### Performance Targets:
- Options chain load time: < 1 second
- GEX data load time: < 1 second
- Data freshness: Real-time (< 5 minutes)
- Fallback activation: < 2 seconds (if TradeStation fails)

---

## 🚦 Current Blockers

### RESOLVED:
- ✅ ~~TradeStation OAuth callback approval~~ (bypassed with UW)
- ✅ ~~UW API token validity~~ (confirmed working)
- ✅ ~~Unknown endpoint structure~~ (discovered via testing)

### ACTIVE:
- None! Ready to implement! 🎉

---

## 📝 Notes

**Why this is important:**
1. **Unblocks TradeStation dependency** - No need to wait for OAuth callback approval
2. **Better data quality** - UW provides sweep volume, multi-leg data, premiums
3. **Direct GEX access** - No need to calculate, UW provides it
4. **Real-time alerts** - Market tide events for flow analysis
5. **Future-proof** - Can use TradeStation as fallback when OAuth working

**Risk mitigation:**
- Keep TradeStation integration as primary (when OAuth working)
- Use UW as fallback/backup
- Both sources provide similar data formats
- Easy to switch between sources

---

**Ready to start?** Begin with Task 1.1 (Update `unusual_whales_service.py`)! 🚀
