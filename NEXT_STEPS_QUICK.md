# Next Steps Rapide - FlowMind Setup Complete
**Data:** 17 octombrie 2025  
**Status:** Backend funcțional, next steps pentru integrare completă

---

## ✅ Status Curent

### Backend (Port 8000):
```bash
✅ FastAPI running: http://0.0.0.0:8000
✅ Health check: {"ok": true}
✅ Flow endpoints: /api/flow/health, /api/flow/snapshot/{symbol}
✅ TS OAuth endpoints: /api/ts/login, /api/ts/callback, /api/ts/status
✅ CORS configured: ALLOWED_ORIGINS din .env
```

### Frontend (Port 3000):
```bash
✅ React app: http://localhost:3000
✅ Backend URL: REACT_APP_BACKEND_URL în .env.local
⚠️  Codespaces URL: Verifică dacă e actualizat
```

---

## 🎯 Next Steps - Copy/Paste Ready

### 1. **Frontend → Backend Connection**

#### Local (Windows - C:\Users\gamebox\Documents\Flowmind):

**Frontend `.env.local`:**
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

**Backend `.env`:**
```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Teste rapide:**
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend  
cd frontend
npm start

# Terminal 3 - Tests
curl http://localhost:8000/health
curl http://localhost:8000/api/flow/health
curl http://localhost:8000/api/flow/snapshot/TSLA
```

---

#### Codespaces (Current Environment):

**Frontend `.env.local`:**
```bash
REACT_APP_BACKEND_URL=https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev
```

**Backend `.env`:**
```bash
ALLOWED_ORIGINS=https://sturdy-system-wvrqjjp49wg29qxx-3000.app.github.dev,https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev
```

**Teste în browser:**
```
https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/health
https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/flow/health
https://sturdy-system-wvrqjjp49wg29qxx-3000.app.github.dev (frontend)
```

---

### 2. **Smoke Tests - Copy/Paste Commands**

#### WSL/Linux/Codespaces:
```bash
# Activate venv (dacă folosești)
cd /workspaces/Flowmind/backend
source .venv/bin/activate 2>/dev/null || echo "No venv, using system Python"

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# Wait for startup
sleep 5

# Test endpoints
echo "🔍 SMOKE TESTS:"
echo ""
echo "1️⃣ Health:"
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "2️⃣ Flow health:"
curl -s http://localhost:8000/api/flow/health | python3 -m json.tool

echo ""
echo "3️⃣ Flow snapshot TSLA:"
curl -s http://localhost:8000/api/flow/snapshot/TSLA | python3 -m json.tool

echo ""
echo "4️⃣ TS status:"
curl -s http://localhost:8000/api/ts/status | python3 -m json.tool

echo ""
echo "✅ All smoke tests complete!"
```

#### Windows PowerShell:
```powershell
# Navigate to backend
cd C:\Users\gamebox\Documents\Flowmind\backend

# Activate venv
.\\.venv\Scripts\Activate.ps1

# Start backend
Start-Process powershell -ArgumentList "uvicorn app.main:app --reload --port 8000"

# Wait
Start-Sleep -Seconds 5

# Test endpoints
Write-Host "🔍 SMOKE TESTS:" -ForegroundColor Cyan
curl http://localhost:8000/health
curl http://localhost:8000/api/flow/health
curl http://localhost:8000/api/flow/snapshot/TSLA
curl http://localhost:8000/api/ts/status
```

---

### 3. **Guard-Rails - Prevent Future Issues**

#### A. Git Branch Protection (GitHub Settings):

1. Go to: `https://github.com/barbudangabriel-gif/Flowmind/settings/branches`
2. Add rule for `main` branch:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators (optional)

#### B. Pre-commit Hooks (Husky + lint-staged):

**Install dependencies:**
```bash
cd /workspaces/Flowmind/backend

# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
EOF

# Install git hooks
pre-commit install

# Test
pre-commit run --all-files
```

#### C. CI/CD Pipeline (GitLab CI):

**Already exists:** `.gitlab-ci.yml` with:
- ✅ Frontend: ESLint, build, npm audit
- ✅ Backend: ruff, mypy, bandit, pip-audit, pytest
- ✅ SAST: dependency scanning, container scanning

**Enable in GitLab:**
1. Settings → CI/CD → Runners → Enable shared runners
2. Settings → CI/CD → Variables → Add secrets
3. Pipelines will run on every push

---

### 4. **Copilot Session Prompt - Prevent Issues**

**Save this as `COPILOT_SESSION_RULES.md` and reference at start of each session:**

```markdown
# Copilot Session Rules - FlowMind

## ROLE
You are a minimal-change code fixer. Your goal is surgical precision, not wholesale rewrites.

## DO (Allowed Actions)
- ✅ Fix ONLY these files:
  - `backend/app/main.py` (imports, CORS, router registration)
  - `backend/app/routers/flow.py` (flow endpoints)
  - `backend/app/services/tradestation.py` (TS OAuth service)
  - `frontend/.env.local` (backend URL)
  - `backend/.env` (CORS origins, TS credentials)

- ✅ Minimal edits:
  - Fix indentation errors with `black`
  - Add missing imports
  - Update environment variables
  - Fix type annotations

## DON'T (Forbidden Actions)
- ❌ DO NOT modify:
  - `requirements.txt` / `package.json` (unless explicitly requested)
  - `package-lock.json` / `yarn.lock` (never touch)
  - Other routers in `backend/app/routers/*` (except flow.py)
  - Database models, migrations
  - Git history, branches

- ❌ DO NOT reindent entire files (only fix syntax errors)
- ❌ DO NOT add new dependencies without approval
- ❌ DO NOT rewrite working code ("refactoring")

## CHECK (Before Committing)
```bash
# Backend
cd backend
black --check app/main.py app/routers/flow.py app/services/tradestation.py
mypy app/main.py --ignore-missing-imports
python -m py_compile app/routers/flow.py

# Frontend (if TypeScript)
cd frontend
npm run typecheck 2>/dev/null || echo "No typecheck script"

# Smoke test
curl http://localhost:8000/health
curl http://localhost:8000/api/flow/health
```

## CONFIRM (After Changes)
- ✅ Backend starts without errors
- ✅ All smoke tests pass
- ✅ No new dependencies added
- ✅ Git diff shows ONLY intended changes
```

**Usage:**
```bash
# At start of each Copilot session, paste:
@workspace Read COPILOT_SESSION_RULES.md and follow strictly.
```

---

### 5. **TradeStation OAuth Complete Setup**

#### Local (Will Actually Work):

**Backend `.env`:**
```bash
# TradeStation Credentials
TS_CLIENT_ID=XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj
TS_CLIENT_SECRET=NsAIybzKV6GbYGqQZwF0cHypdXfwiDYL5-EY4nRXEbIy748Zp-FdeuDXJIu6Jhwk
TS_REDIRECT_URI=http://localhost:8000/api/ts/callback

# TradeStation SIMULATION URLs
TS_BASE_URL=https://sim-api.tradestation.com
TS_AUTH_URL=https://sim-signin.tradestation.com/authorize
TS_TOKEN_URL=https://sim-signin.tradestation.com/oauth/token
TS_SCOPE=openid offline_access MarketData ReadAccount Trade Crypto
```

**Test OAuth Flow:**
```bash
# 1. Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# 2. Open browser
http://localhost:8000/api/ts/login

# 3. Login with TradeStation SIMULATION credentials
# (Use your TradeStation Paper Trading account)

# 4. After successful callback:
curl http://localhost:8000/api/ts/status
# Should show: {"authenticated": true, "user_id": "demo", ...}
```

#### Codespaces (Requires Approved Redirect URI):

**Steps:**
1. **TradeStation Developer Portal:**
   - Login: https://developer.tradestation.com
   - Your App → Redirect URIs
   - Add: `https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/ts/callback`
   - Save & wait for approval (24-48 hours)

2. **Update `.env`:**
```bash
TS_REDIRECT_URI=https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/ts/callback
```

3. **Mark port 8000 as Public:**
   - VS Code Ports tab
   - Port 8000 → Right click → Port Visibility → Public

4. **Test:**
```bash
https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/ts/login
```

---

## 📋 Quick Reference Commands

### Backend Development:
```bash
# Start
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Format
black app/main.py app/routers/ app/services/

# Type check
mypy app/main.py --ignore-missing-imports

# Security scan
bandit -ll -r app/

# Tests
pytest -q --maxfail=1
```

### Frontend Development:
```bash
# Start
cd frontend && npm start

# Lint
npm run lint

# Build
npm run build

# Audit
npm audit --audit-level=high
```

### Full Stack:
```bash
# Docker Compose (if configured)
docker-compose up

# Or manual:
# Terminal 1:
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2:
cd frontend && npm start
```

---

## 🎯 Success Criteria

### ✅ Local Setup Complete When:
- [ ] Backend starts on port 8000 without errors
- [ ] Frontend starts on port 3000 and connects to backend
- [ ] `/health` returns `{"ok": true}`
- [ ] `/api/flow/health` returns `{"ok": true, "scope": "flow"}`
- [ ] `/api/ts/login` redirects to TradeStation
- [ ] After TS login, `/api/ts/status` shows authenticated
- [ ] Frontend can call backend APIs (check Network tab)

### ✅ Codespaces Setup Complete When:
- [ ] Backend runs on public port 8000
- [ ] Frontend runs on public port 3000
- [ ] CORS allows Codespaces origins
- [ ] All smoke tests pass from browser
- [ ] TradeStation redirect URI approved (for OAuth)

---

## 🚨 Common Issues & Fixes

### Issue: CORS Error in Browser
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS
```

**Fix:**
```bash
# In backend/.env, add:
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Restart backend
```

---

### Issue: Backend Won't Start (IndentationError)
```
IndentationError: expected an indented block after 'try' statement
```

**Fix:**
```bash
cd backend

# Run black on problematic file
black app/routers/flow.py

# If still broken, restore from git
git checkout HEAD -- app/routers/flow.py

# Restart backend
uvicorn app.main:app --reload --port 8000
```

---

### Issue: TradeStation OAuth Fails in Codespaces
```
Something Went Wrong - The redirect URI is not approved
```

**Fix:**
- TradeStation only approves `localhost` by default
- Must request approval for Codespaces URL at TradeStation Developer Portal
- Use local Windows setup instead (C:\Users\gamebox\Documents\Flowmind)

---

### Issue: Frontend Can't Connect to Backend
```
Network Error: Request failed with status code undefined
```

**Fix:**
```bash
# Check REACT_APP_BACKEND_URL in frontend/.env.local
# Should be:
# Local: http://localhost:8000
# Codespaces: https://<id>-8000.app.github.dev

# Restart frontend after changing .env.local
```

---

## 📖 Documentație Completă

- **BACKEND_FIXED_2025-10-17.md** - Backend absolute imports, CORS fix
- **TRADESTATION_SERVICE_COMPLETE.md** - TS OAuth implementation details
- **SETUP_INSTRUCTIONS_LOCAL.md** - Local Windows setup guide
- **PLATFORM_GUIDE.md** - Full architecture overview
- **DEVELOPMENT_GUIDELINES.md** - Development workflows (Romanian)

---

## 🔗 Useful Links

- **Backend:** http://localhost:8000/docs (Swagger UI)
- **Backend Health:** http://localhost:8000/health
- **Frontend:** http://localhost:3000
- **GitHub Repo:** https://github.com/barbudangabriel-gif/Flowmind
- **TradeStation Dev Portal:** https://developer.tradestation.com

---

**Next Steps Document - 17 octombrie 2025**  
**Status:** Ready for local testing and production deployment
