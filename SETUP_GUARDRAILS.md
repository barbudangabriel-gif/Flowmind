# Setup Guard-Rails - One-Time Installation
**Date:** October 17, 2025  
**Purpose:** Prevent code chaos, enforce formatting, block bad commits

---

## 🎯 Overview

This guide sets up **automated guard-rails** to prevent:
- ❌ Mass reformatting (164 files changed)
- ❌ Indentation errors (manual spaces/tabs mixing)
- ❌ Import errors (relative vs absolute)
- ❌ CORS misconfigurations
- ❌ Bad commits reaching `main` branch

**Strategy:**
1. **EditorConfig** - IDE rules (spaces, EOL, encoding)
2. **Prettier + ESLint** - Frontend formatting (auto-fix on save)
3. **Black + isort** - Backend formatting (Python PEP8)
4. **Husky + lint-staged** - Pre-commit hooks (block bad commits)
5. **GitHub Actions CI** - PR checks (block bad merges)
6. **Branch Protection** - Require CI pass before merge

---

## 📦 1. Root Configuration (Universal Rules)

### A. EditorConfig (all files)

**Already created:** `.editorconfig`

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{js,jsx,ts,tsx,json,css,md}]
indent_style = space
indent_size = 2

[*.py]
indent_style = space
indent_size = 4
```

**Effect:** VS Code/IntelliJ/Vim will automatically use correct indentation.

---

### B. Git Attributes (EOL normalization)

**Already created:** `.gitattributes`

```
* text=auto eol=lf
```

**Effect:** All files use Linux line endings (LF), even on Windows.

---

### C. VS Code Settings (workspace)

**Already created:** `.vscode/settings.json`

```json
{
  "editor.detectIndentation": false,
  "files.eol": "\n",
  "editor.formatOnSave": true,
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "[python]": {
    "editor.tabSize": 4,
    "editor.insertSpaces": true
  }
}
```

**Effect:** Format-on-save enabled, correct indentation enforced.

---

## 🎨 2. Frontend Guard-Rails (TypeScript/React)

### A. Install Dependencies

```bash
cd /workspaces/Flowmind/frontend

# Install formatting tools
pnpm add -D prettier eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-config-prettier husky lint-staged

# Initialize Husky (git hooks)
pnpm dlx husky init
```

---

### B. Prettier Configuration

**Already created:** `frontend/.prettierrc`

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

---

### C. ESLint Configuration

**Already created:** `frontend/.eslintrc.cjs`

```javascript
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended', 'prettier']
}
```

---

### D. Package.json Scripts

**Add to `frontend/package.json`:**

```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx",
    "format": "prettier -w .",
    "format:check": "prettier --check ."
  },
  "lint-staged": {
    "*.{ts,tsx,js,css,md,json}": ["prettier -w", "eslint --fix"]
  }
}
```

---

### E. Husky Pre-Commit Hook

**Create/edit `frontend/.husky/pre-commit`:**

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

pnpm lint-staged
```

Make executable:
```bash
chmod +x frontend/.husky/pre-commit
```

**Effect:** Every commit runs Prettier + ESLint. Bad formatting = blocked commit.

---

### F. One-Time Cleanup

```bash
cd /workspaces/Flowmind/frontend

# Format all files
pnpm format

# Fix all linting errors
pnpm lint --fix

# Verify clean state
pnpm format:check
pnpm lint
```

---

## 🐍 3. Backend Guard-Rails (Python)

### A. Install Dependencies

```bash
cd /workspaces/Flowmind/backend

# Install formatting tools
pip install pre-commit black isort
```

---

### B. Black Configuration

**Already created:** `backend/pyproject.toml`

```toml
[tool.black]
line-length = 100
target-version = ["py312"]

[tool.isort]
profile = "black"
```

---

### C. Pre-Commit Configuration

**Already created:** `backend/.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
        args: [--check, --diff]
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--check-only, --diff]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

---

### D. Install Pre-Commit Hooks

```bash
cd /workspaces/Flowmind/backend

# Install git hooks
pre-commit install

# Test hooks (run on all files)
pre-commit run --all-files
```

**Effect:** Every commit runs Black + isort. Bad formatting = blocked commit with diff.

---

### E. One-Time Cleanup

```bash
cd /workspaces/Flowmind/backend

# Format all Python files
black .

# Sort all imports
isort .

# Verify clean state
black --check .
isort --check-only .
```

---

## 🚦 4. GitHub Actions CI (Automated PR Checks)

### A. CI Workflow

**Already created:** `.github/workflows/ci.yml`

```yaml
name: ci
on: [push, pull_request]
jobs:
  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'pnpm'
          cache-dependency-path: frontend/pnpm-lock.yaml
      - run: corepack enable
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint

  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install black isort
      - run: black --check .
      - run: isort --check-only .
```

**Effect:** Every push/PR triggers CI. Bad formatting = failed CI check.

---

### B. Enable Branch Protection

**In GitHub UI:**

1. Go to: `Settings` → `Branches` → `Branch protection rules`
2. Add rule for `main` branch:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select status checks: `frontend`, `backend`
   - ✅ Require conversation resolution before merging
   - ✅ Do not allow bypassing the above settings

**Effect:** Cannot merge PR if CI fails. No direct pushes to `main`.

---

## 🧪 5. Verification (Test Guard-Rails)

### A. Test Frontend Guard-Rails

```bash
cd /workspaces/Flowmind/frontend

# Create badly formatted file
cat > test-bad.ts << 'EOF'
const x={a:1,b:2}
function bad(){return "no formatting"}
EOF

# Try to commit (should FAIL)
git add test-bad.ts
git commit -m "test: bad formatting"

# Expected output:
# ❌ Prettier found issues
# ❌ ESLint found issues
# Commit blocked!

# Fix formatting
pnpm format
pnpm lint --fix

# Now commit should work
git add test-bad.ts
git commit -m "test: good formatting"
# ✅ Success

# Cleanup
git reset HEAD~1
rm test-bad.ts
```

---

### B. Test Backend Guard-Rails

```bash
cd /workspaces/Flowmind/backend

# Create badly formatted file
cat > test_bad.py << 'EOF'
def bad(x,y,z):
  return x+y+z
EOF

# Try to commit (should FAIL)
git add test_bad.py
git commit -m "test: bad formatting"

# Expected output:
# [INFO] black.......Failed
# [INFO] isort.......Failed
# Diff shows what needs fixing

# Fix formatting
black test_bad.py
isort test_bad.py

# Now commit should work
git add test_bad.py
git commit -m "test: good formatting"
# ✅ Success

# Cleanup
git reset HEAD~1
rm test_bad.py
```

---

### C. Test CI Workflow

```bash
# Create a branch with bad formatting
git checkout -b test-ci-guardrails

# Add badly formatted code
echo "bad_code={  'key':   'value'  }" >> backend/test_ci.py
git add backend/test_ci.py

# Bypass pre-commit (to test CI)
git commit --no-verify -m "test: CI should catch this"
git push origin test-ci-guardrails

# Create PR on GitHub
# Expected: CI fails with formatting errors
# ❌ backend job: black --check . FAILED

# Fix and push
black backend/test_ci.py
git add backend/test_ci.py
git commit -m "fix: formatting"
git push

# Expected: CI passes
# ✅ All checks passed
```

---

## 📋 6. Daily Workflow (With Guard-Rails)

### Before Starting Work

```bash
# Start Copilot session with contract
@workspace Read COPILOT_COMMIT_CONTRACT.md and follow strictly.
```

---

### Making Changes

```bash
# 1. Make minimal changes (1-3 files max)
# Edit backend/app/routers/flow.py

# 2. Format automatically (pre-commit will catch issues)
cd backend
black app/routers/flow.py
isort app/routers/flow.py

# 3. Verify
black --check app/routers/flow.py
python -c "import app.routers.flow"

# 4. Test
curl -s http://localhost:8000/api/flow/health
```

---

### Committing

```bash
# 1. Stage specific files
git add backend/app/routers/flow.py

# 2. Commit (pre-commit hooks will run)
git commit -m "fix: correct import in flow router"

# If pre-commit fails:
# - Read the diff
# - Run suggested fix (black ., isort .)
# - Re-stage and commit

# 3. Push
git push
```

---

### Creating PR

```bash
# 1. Create feature branch
git checkout -b fix/flow-import-error

# 2. Make changes + commit
# (with guard-rails enabled)

# 3. Push
git push origin fix/flow-import-error

# 4. Create PR on GitHub
# CI will run automatically

# 5. Wait for CI ✅ green checks
# 6. Request review
# 7. Merge when approved + CI passing
```

---

## 🆘 7. Troubleshooting

### Issue: Pre-commit hooks not running

```bash
# Reinstall hooks
cd backend && pre-commit install
cd frontend && pnpm dlx husky init
```

---

### Issue: Black/Prettier conflicts

```bash
# Black always wins for Python
cd backend && black .

# Prettier always wins for TS/JS
cd frontend && pnpm format
```

---

### Issue: CI fails but local passes

```bash
# Ensure same versions
cd backend
pip install black==24.8.0 isort==5.13.2

cd frontend
pnpm install  # Uses lockfile versions
```

---

### Issue: Want to bypass hooks (emergency)

```bash
# Skip pre-commit hooks (NOT RECOMMENDED)
git commit --no-verify -m "emergency fix"

# But CI will still catch formatting issues!
```

---

## ✅ 8. Success Criteria

After setup complete, verify:

- [ ] EditorConfig working (VS Code shows correct indentation)
- [ ] Frontend pre-commit blocks bad formatting
- [ ] Backend pre-commit blocks bad formatting
- [ ] `pnpm format` + `pnpm lint` pass in frontend
- [ ] `black --check .` + `isort --check-only .` pass in backend
- [ ] GitHub Actions CI workflow enabled
- [ ] Branch protection enabled on `main`
- [ ] Test commit with bad formatting gets blocked
- [ ] COPILOT_COMMIT_CONTRACT.md pasted at session start

---

## 📊 9. Files Created/Modified

### Created:
- `.editorconfig` - Universal IDE rules
- `.gitattributes` - Git EOL normalization
- `.vscode/settings.json` - VS Code workspace settings
- `frontend/.prettierrc` - Prettier config
- `frontend/.eslintrc.cjs` - ESLint config
- `frontend/.husky/pre-commit` - Git hook (frontend)
- `backend/pyproject.toml` - Black + isort config
- `backend/.pre-commit-config.yaml` - Pre-commit hooks config
- `.github/workflows/ci.yml` - GitHub Actions CI
- `COPILOT_COMMIT_CONTRACT.md` - AI session rules

### Modified:
- `frontend/package.json` - Add lint/format scripts + lint-staged config
- `backend/requirements.txt` - Add black, isort, pre-commit (if not present)

---

## 🚀 10. Next Steps

1. **Run one-time cleanup:**
   ```bash
   # Frontend
   cd frontend && pnpm format && pnpm lint --fix
   
   # Backend
   cd backend && black . && isort .
   ```

2. **Commit guard-rails setup:**
   ```bash
   git add .editorconfig .gitattributes .vscode/ frontend/ backend/ .github/
   git commit -m "feat: add formatting guard-rails and CI

   - Add EditorConfig, Prettier, ESLint, Black, isort
   - Setup Husky pre-commit hooks (frontend)
   - Setup pre-commit hooks (backend)
   - Add GitHub Actions CI workflow
   - Create Copilot commit contract
   - One-time formatting cleanup"
   git push
   ```

3. **Enable branch protection** (GitHub UI)

4. **Test guard-rails** (section 5 above)

5. **Start using COPILOT_COMMIT_CONTRACT.md** at every session

---

**🎉 Guard-rails complete! Code chaos prevention activated.**
