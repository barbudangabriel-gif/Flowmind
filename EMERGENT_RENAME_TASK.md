# Task: Rename "emergent" → Alternative Name

**Created:** October 21, 2025  
**Status:** PLANNING  
**Estimated Time:** 30-45 minutes  
**Priority:** LOW (cosmetic, not functional)

---

## 📋 Current State Analysis

**Total occurrences:** ~50+ across backend, frontend, tests, docs

### **Files to modify:**

#### Backend (15 references)
1. `backend/bt_emergent.py` - **Main file** (rename to `bt_diagnostics.py`?)
   - Line 2: Module docstring
   - Line 15: `emergent_router` variable (3x)
   - Line 79-82: Comments and function names
   - Line 201-202: `emergent_status` function
   - Line 210: Docstring

2. `backend/server.py` - Import and router registration
   - Line 676: Comment
   - Line 677: `from bt_emergent import emergent_router` (2x)
   - Line 692: `app.include_router(emergent_router)`

#### Frontend (7 references)
3. `frontend/src/hooks/useNavContext.js`
   - Line 23: `emergentRes` variable
   - Line 25: URL `/_emergent/status`
   - Line 37-41: Variable names and logic (5x)

4. `frontend/src/lib/nav.js`
   - Line 3: Comment
   - Line 157: Menu label "Emergent Status"
   - Line 158: Route `/ops/emergent`

#### Tests (11 references)
5. `tests/archived_integration_tests/redis_iv_caching_test.py`
   - Line 120: Function name `test_emergent_status`
   - Line 121-122: Comments
   - Line 126: Test description
   - Line 128, 261, 283: URL `/_emergent/status`
   - Line 134, 137: Print messages
   - Line 321, 331-332, 435, 437: Various references

#### Documentation (7 references)
6. `REMAINING_ERRORS_ANALYSIS.md` - Line 72
7. `PYTHON312_CHECKPOINT_2025-10-18.md` - Line 94
8. `PROJECT_STATUS.md` - Lines 11, 104
9. `WORK_LOG_2025-10-14.md` - Lines 6, 50, 65, 73, 77

---

## 🎯 Proposed Renaming

### **Option 1: "diagnostics"** (Recommended)
**Rationale:** Clear, professional, describes functionality accurately

**Changes:**
- `bt_emergent.py` → `bt_diagnostics.py`
- `emergent_router` → `diagnostics_router`
- `/_emergent/status` → `/_diagnostics/status`
- `emergent_status()` → `diagnostics_status()`
- Menu: "Emergent Status" → "Diagnostics"
- Route: `/ops/emergent` → `/ops/diagnostics`

**Impact:**
- ✅ Professional terminology
- ✅ Clear purpose
- ✅ Aligns with industry standards
- ⚠️ API breaking change (need to update all clients)

### **Option 2: "monitor"**
**Changes:**
- `bt_monitor.py`, `monitor_router`, `/_monitor/status`
- Shorter, simpler
- Less descriptive

### **Option 3: "status"** 
**Changes:**
- `bt_status.py`, `status_router`, `/_status/info`
- Very generic
- May conflict with other status endpoints

---

## 📝 Implementation Plan

### **Phase 1: Backend Refactor** (15 min)
1. Rename `bt_emergent.py` → `bt_diagnostics.py`
2. Update all variable names:
   - `emergent_router` → `diagnostics_router`
   - `emergent_status` → `diagnostics_status`
   - `emergent_redis_diag` → `diagnostics_redis_diag`
3. Update router prefix: `/_emergent` → `/_diagnostics`
4. Update `server.py` imports and router registration
5. Test: `python -m py_compile backend/bt_diagnostics.py backend/server.py`

### **Phase 2: Frontend Update** (10 min)
1. `useNavContext.js`:
   - `emergentRes` → `diagnosticsRes`
   - `/_emergent/status` → `/_diagnostics/status`
   - Update comments
2. `nav.js`:
   - Label: "Emergent Status" → "Diagnostics"
   - Route: `/ops/emergent` → `/ops/diagnostics`
3. Test: `npm run build` (verify no errors)

### **Phase 3: Tests Update** (5 min)
1. `redis_iv_caching_test.py`:
   - `test_emergent_status` → `test_diagnostics_status`
   - URL updates: `/_emergent/` → `/_diagnostics/`
   - Print message updates
2. Test: Run archived tests (optional, they're archived)

### **Phase 4: Documentation** (5 min)
1. Update all .md files with new terminology
2. Add migration note for API consumers

### **Phase 5: Git Commit** (5 min)
```bash
git mv backend/bt_emergent.py backend/bt_diagnostics.py
git add -A
git commit -m "♻️ Rename emergent → diagnostics (better terminology)

BREAKING CHANGE: API endpoint /_emergent/* moved to /_diagnostics/*

- Renamed bt_emergent.py → bt_diagnostics.py
- Updated all router names, function names, URLs
- Frontend: useNavContext.js, nav.js updated
- Tests: redis_iv_caching_test.py updated
- Docs: All .md files updated

Migration: Update any clients calling /_emergent/status to /_diagnostics/status"
git push
```

---

## ⚠️ Breaking Changes

**API Endpoints:**
- ❌ `GET /_emergent/status` 
- ✅ `GET /_diagnostics/status`

- ❌ `GET /_emergent/redis/diag`
- ✅ `GET /_diagnostics/redis/diag`

**Frontend Routes:**
- ❌ `/ops/emergent`
- ✅ `/ops/diagnostics`

**Impact Assessment:**
- **Backend:** FastAPI router prefix change
- **Frontend:** Navigation menu + API calls
- **Tests:** URL updates in archived tests (low priority)
- **External clients:** Unknown (check logs for `/_emergent/*` usage)

---

## 🧪 Testing Checklist

- [ ] Backend compiles: `python -m py_compile backend/bt_diagnostics.py`
- [ ] Server starts: `python -m uvicorn server:app --reload`
- [ ] Endpoint works: `curl http://localhost:8000/_diagnostics/status`
- [ ] Redis diag works: `curl http://localhost:8000/_diagnostics/redis/diag`
- [ ] Frontend builds: `cd frontend && npm run build`
- [ ] Navigation menu shows "Diagnostics"
- [ ] Route `/ops/diagnostics` works
- [ ] useNavContext fetches from `/_diagnostics/status`
- [ ] No console errors in browser

---

## 🚦 Decision

**Recommendation:** **Option 1 - "diagnostics"**

**Pros:**
- Professional terminology
- Clear, descriptive purpose
- Industry-standard naming
- Better than vague "emergent"

**Cons:**
- Breaking change (but clean)
- 30-45 min work
- Need to communicate to any external consumers

**Alternative:** Keep "emergent" if no strong reason to change (it works, just unclear naming)

---

## 🎯 Execute?

**YES:** Run implementation plan above (30-45 min)  
**NO:** Mark as technical debt, fix later  
**DEFER:** Wait for feedback from team/users on current naming

---

**Final Estimate:** 30-45 minutes (all phases)  
**Risk:** LOW (simple rename, no logic changes)  
**Value:** MEDIUM (better code clarity, professional naming)
