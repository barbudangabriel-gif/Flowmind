# Quick Commands - Guard-Rails Cheat Sheet

## 🚀 Quick Start (One-Time Setup)

```bash
# Run automated installation
./INSTALL_GUARDRAILS.sh
```

---

## 📋 Daily Workflow

### Start Copilot Session
```
@workspace Read COPILOT_COMMIT_CONTRACT.md and follow strictly.
```

### Before Commit (Frontend)
```bash
cd frontend
pnpm format      # Auto-fix formatting
pnpm lint --fix  # Auto-fix linting
```

### Before Commit (Backend)
```bash
cd backend
black .          # Auto-fix formatting
isort .          # Auto-fix imports
```

### Verify Clean State
```bash
# Frontend
cd frontend
pnpm format:check
pnpm lint

# Backend
cd backend
black --check .
isort --check-only .
```

---

## 🧪 Test Guard-Rails

### Test Frontend Hooks
```bash
cd frontend
echo "const bad={a:1,b:2}" > test-bad.ts
git add test-bad.ts
git commit -m "test: bad formatting"
# Should FAIL with Prettier/ESLint errors

# Fix and retry
pnpm format
git add test-bad.ts
git commit -m "test: good formatting"
# Should PASS

# Cleanup
git reset HEAD~1
rm test-bad.ts
```

### Test Backend Hooks
```bash
cd backend
echo "def bad(x,y): return x+y" > test_bad.py
git add test_bad.py
git commit -m "test: bad formatting"
# Should FAIL with Black/isort errors

# Fix and retry
black test_bad.py
isort test_bad.py
git add test_bad.py
git commit -m "test: good formatting"
# Should PASS

# Cleanup
git reset HEAD~1
rm test_bad.py
```

---

## 🔧 Manual Checks

### Frontend
```bash
cd frontend

# Lint check
pnpm lint

# Format check
pnpm format:check

# Fix all issues
pnpm lint --fix
pnpm format
```

### Backend
```bash
cd backend

# Black check
black --check .

# Isort check
isort --check-only .

# Fix all issues
black .
isort .

# Run pre-commit on all files
pre-commit run --all-files
```

---

## 🆘 Emergency Bypass (NOT RECOMMENDED)

```bash
# Skip pre-commit hooks (emergency only)
git commit --no-verify -m "emergency fix"

# Note: CI will still catch formatting issues!
```

---

## 📊 Check CI Status

```bash
# View GitHub Actions workflow
https://github.com/barbudangabriel-gif/Flowmind/actions

# Local CI simulation (frontend)
cd frontend
pnpm install --frozen-lockfile
pnpm lint

# Local CI simulation (backend)
cd backend
pip install black isort
black --check .
isort --check-only .
```

---

## 🔄 Update Dependencies

### Frontend
```bash
cd frontend
pnpm update prettier eslint husky lint-staged
```

### Backend
```bash
cd backend
pip install --upgrade black isort pre-commit
pre-commit autoupdate
```

---

## 📁 Files Reference

| File | Purpose |
|------|---------|
| `.editorconfig` | IDE indentation rules |
| `.gitattributes` | Git EOL normalization |
| `.vscode/settings.json` | VS Code settings |
| `frontend/.prettierrc` | Prettier config |
| `frontend/.eslintrc.cjs` | ESLint config |
| `frontend/.husky/pre-commit` | Frontend git hook |
| `backend/pyproject.toml` | Black + isort config |
| `backend/.pre-commit-config.yaml` | Backend git hooks |
| `.github/workflows/ci.yml` | GitHub Actions CI |
| `COPILOT_COMMIT_CONTRACT.md` | AI session rules |
| `SETUP_GUARDRAILS.md` | Full setup guide |

---

## ✅ Pre-Commit Checklist

- [ ] Read COPILOT_COMMIT_CONTRACT.md
- [ ] Made minimal changes (1-3 files)
- [ ] Ran `pnpm format` (frontend) or `black .` (backend)
- [ ] Verified `pnpm lint` or `black --check .` passes
- [ ] Tested endpoints: `curl http://localhost:8000/health`
- [ ] Diff is <80 lines
- [ ] Commit message is clear and descriptive

---

**🎯 Remember: Small commits, clean formatting, tested code!**
