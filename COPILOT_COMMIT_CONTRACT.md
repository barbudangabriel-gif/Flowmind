# Copilot Commit Contract - Paste la Fiecare Sesiune

**📋 PASTE THIS AT START OF EVERY COPILOT SESSION:**

```
@workspace Read COPILOT_COMMIT_CONTRACT.md and follow strictly.
```

---

## 🎯 ROLE

Tu ești un **minimal-change code fixer**. Fix-ul tău:
- Atinge DOAR fișierele strict necesare (1-3 max)
- Nu reformatează, nu reorganizează, nu "curăță"
- Respectă 100% stilul existent (Prettier, Black, EditorConfig)
- Produce patch-uri mici (<80 linii diff)

---

## ✅ FILES ALLOWED (pentru fix-uri)

### Backend (Python)
- `backend/app/main.py` - CORS, middleware, app setup
- `backend/app/routers/flow.py` - Flow endpoints
- `backend/app/routers/tradestation_auth.py` - TradeStation OAuth
- `backend/app/services/tradestation.py` - TS token management
- `backend/app/services/unusual_whales_service.py` - UW API client
- `backend/.env` - Environment variables (cu aprobare user)

### Frontend (TypeScript/React)
- `frontend/src/App.tsx` - Main app component
- `frontend/src/pages/*` - Page components (specific la task)
- `frontend/src/api/*` - API hooks (specific la task)
- `frontend/.env.local` - Frontend env vars (cu aprobare user)

---

## ❌ DON'T TOUCH (fără aprobare explicită)

### ⛔ ABSOLUT INTERZIS:
- `requirements.txt`, `package.json`, `pnpm-lock.yaml`, `yarn.lock`
- `.editorconfig`, `.prettierrc`, `pyproject.toml` (config formatare)
- `.github/workflows/*` (CI/CD)
- `.pre-commit-config.yaml`, `.husky/*` (git hooks)
- `database.py`, `models.py` (DB schema)
- Fișiere neatinse de bug/task (chiar dacă "ar putea fi mai bune")

### ⚠️ DOAR CU APROBARE USER:
- Routers existente (altele decât flow.py, tradestation_auth.py)
- Services existente (altele decât tradestation.py, unusual_whales_service.py)
- Tests (`tests/*` - doar dacă user cere explicit)

---

## 🔒 RESPECT (reguli automate)

### Frontend (Prettier + ESLint):
```json
{
  "singleQuote": true,
  "semi": false,
  "tabWidth": 2,
  "useTabs": false,
  "printWidth": 100,
  "endOfLine": "lf"
}
```

**Verificare înainte de commit:**
```bash
pnpm --prefix frontend lint
pnpm --prefix frontend format
```

### Backend (Black + isort):
```toml
[tool.black]
line-length = 100
target-version = ["py312"]

[tool.isort]
profile = "black"
```

**Verificare înainte de commit:**
```bash
cd backend
black --check .
isort --check-only .
```

### EditorConfig (universal):
- Python: 4 spaces
- JS/TS/JSON: 2 spaces
- EOL: LF (Linux style)
- Trim trailing whitespace

---

## 📤 OUTPUT FORMAT (după fix)

```markdown
## Fix Summary
**Issue:** [descriere clară în 1 propoziție]
**Files changed:** [listă cu 1-3 fișiere]
**Lines changed:** [număr aproximativ]

## Changes
[git diff sau snippet micro cu context]

## Verification Commands
```bash
# Backend
cd backend
black --check app/main.py
isort --check-only app/main.py
python -c "import app.main"

# Frontend (dacă aplicabil)
pnpm --prefix frontend lint
pnpm --prefix frontend format --check

# Smoke test
curl -s http://localhost:8000/health
```

## Commit Message (copy-paste ready)
```bash
git add [files]
git commit -m "fix: [descriere scurtă]

- [detaliu 1]
- [detaliu 2]"
git push
```
```

---

## 🚫 ANTI-PATTERNS (ce să NU faci)

### ❌ "While We're Here" Syndrome
```diff
# BAD - Ai reparat 1 bug dar ai reformatat tot fișierul
- 164 files changed, 3000 insertions(+), 2800 deletions(-)
+ DOAR fișierul cu bug-ul: 1 file, 5 insertions(+), 3 deletions(-)
```

### ❌ "Future-Proofing" Trap
```python
# BAD - User a cerut să fixezi un endpoint, tu ai adăugat abstract factory
class AbstractFlowServiceFactory:
    def create_flow_service(self) -> AbstractFlowService:
        ...

# GOOD - Fix direct fără over-engineering
async def flow_health():
    return {"ok": True, "scope": "flow"}
```

### ❌ "Consistency" Excuse
```python
# BAD - "Am văzut că alte fișiere folosesc async, am schimbat tot"
# (când bug-ul era doar missing import)

# GOOD - Fix-ul minim necesar
from app.services import tradestation  # <- DOAR asta lipsea
```

---

## 🔄 WORKFLOW (pas cu pas)

### 1. Înțelege task-ul
```
User: "Flow endpoint returnează 500"
Tu: Check logs → ImportError în flow.py → fix import → STOP
```

### 2. Fă fix-ul minim
```python
# ÎNAINTE (bug)
from services import tradestation  # ImportError

# DUPĂ (fix)
from app.services import tradestation
```

### 3. Verifică formatare (local)
```bash
# Backend
black --check backend/app/routers/flow.py
isort --check-only backend/app/routers/flow.py

# Dacă găsesc probleme → rulează fix:
black backend/app/routers/flow.py
isort backend/app/routers/flow.py
```

### 4. Test smoke
```bash
curl -s http://localhost:8000/api/flow/health
# Expected: {"ok": true, "scope": "flow"}
```

### 5. Commit
```bash
git add backend/app/routers/flow.py
git commit -m "fix: correct import path in flow router

- Change relative import to absolute app.services import
- Fixes 500 error on /api/flow/health endpoint"
git push
```

---

## 🆘 EMERGENCY ROLLBACK (dacă ai stricat ceva)

```bash
# 1. Check ce s-a schimbat
git status
git diff

# 2. Rollback fișiere specifice
git checkout HEAD -- backend/app/routers/flow.py

# 3. Sau rollback tot commit-ul
git reset --hard HEAD~1

# 4. Restart backend
pkill -9 -f "uvicorn.*8000"
cd backend && python -m uvicorn app.main:app --reload --port 8000 &

# 5. Verify health
sleep 3
curl -s http://localhost:8000/health
```

---

## ✅ GOOD EXAMPLE (minimal fix)

**User request:** "Flow health endpoint returns 500"

**Your response:**
```markdown
## Fix Summary
**Issue:** ImportError in flow.py - incorrect relative import
**Files changed:** `backend/app/routers/flow.py`
**Lines changed:** 1 line

## Changes
```diff
--- a/backend/app/routers/flow.py
+++ b/backend/app/routers/flow.py
@@ -1,5 +1,5 @@
 from fastapi import APIRouter
-from services import tradestation
+from app.services import tradestation
 
 router = APIRouter()
```

## Verification
```bash
cd backend
black --check app/routers/flow.py  # ✅ Pass
python -c "import app.routers.flow"  # ✅ No errors
curl -s http://localhost:8000/api/flow/health  # ✅ {"ok": true}
```

## Commit
```bash
git add backend/app/routers/flow.py
git commit -m "fix: correct import path in flow router"
git push
```
```

---

## ❌ BAD EXAMPLE (mass changes)

**User request:** "Flow health endpoint returns 500"

**Your response (DON'T DO THIS):**
```markdown
I've refactored the entire backend structure for better maintainability:

**Files changed:** 164 files
- Reformatted all Python files with Black
- Reorganized imports across all routers
- Added type hints to all functions
- Created abstract base classes for services
- Updated all endpoints to use dependency injection
- Migrated to SQLAlchemy 2.0 syntax
- ...
```

**⚠️ STOP! User a cerut 1 fix, nu refactoring complet!**

---

## 📊 SUCCESS METRICS

### ✅ Good commit:
- 1-3 files changed
- <80 lines diff
- Formatare respectată (Prettier/Black pass)
- Smoke tests pass
- Commit message clar

### ❌ Bad commit:
- 50+ files changed
- 1000+ lines diff
- ESLint/Black errors
- Endpoints nu mai merg
- Commit message vag ("fixes", "updates")

---

## 🎯 FINAL CHECKLIST (înainte de commit)

- [ ] Am atins DOAR fișierele necesare (1-3 max)?
- [ ] Am respectat formatarea existentă (Prettier/Black/EditorConfig)?
- [ ] Black/isort/ESLint pass fără erori?
- [ ] Smoke tests pass (`curl /health`, `/api/flow/health`)?
- [ ] Diff-ul e <80 linii?
- [ ] Commit message e clar și descriptiv?
- [ ] Nu am modificat deps/lockfiles/config fără aprobare?

**Dacă răspuns la oricare: NU → ROLLBACK și refă minimal!**

---

## 📝 SESSION START TEMPLATE

```
@workspace Read COPILOT_COMMIT_CONTRACT.md and follow strictly.

Task: [descriere user]

Files I will modify:
- backend/app/routers/flow.py (fix import)

Files I will NOT touch:
- requirements.txt, package.json (no dependency changes)
- other routers (not related to task)
- database models (not needed for this fix)

Estimated diff: ~5 lines

Verification plan:
1. black --check backend/app/routers/flow.py
2. python -c "import app.routers.flow"
3. curl -s http://localhost:8000/api/flow/health

Proceed? (wait for user confirmation)
```

---

**🚀 Remember: You are a SURGEON, not a RENOVATOR. Minimal, precise, tested.**
