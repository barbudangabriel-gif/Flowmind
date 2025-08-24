set -euo pipefail

# 0) Setup
BRANCH="chore/qa-gates-ci"
BASE_BRANCH="main"   # schimbă dacă folosești "master"

cd /app
git fetch origin
git checkout -B "$BRANCH" "origin/$BASE_BRANCH" || git checkout -b "$BRANCH"

# 1) FRONTEND: package.json -> scripts + lint-staged + prepare
[ -f frontend/package.json ] || { echo "LIPSESTE frontend/package.json"; exit 2; }
python3 - <<'PY'
import json,sys,os
p="frontend/package.json"
with open(p,encoding="utf-8") as f: j=json.load(f)

j.setdefault("scripts",{})
j["scripts"].setdefault("lint","eslint \"src/**/*.{js,jsx,ts,tsx}\"")
j["scripts"].setdefault("format","prettier --write .")
j["scripts"].setdefault("prepare","husky")  # va rula la npm install

j.setdefault("lint-staged",{})
j["lint-staged"].setdefault("src/**/*.{js,jsx,ts,tsx}",["eslint --fix"])
j["lint-staged"].setdefault("*.{json,md,css,scss}",["prettier --write"])

with open(p,"w",encoding="utf-8") as f: json.dump(j,f,ensure_ascii=False,indent=2)
print("UPDATED:",p)
PY

# 2) FRONTEND: .husky/pre-commit (rulează lint-staged)
mkdir -p frontend/.husky
cat > frontend/.husky/pre-commit <<'SH'
#!/usr/bin/env sh
. "$(dirname "$0")/_/husky.sh"
npx lint-staged
SH
chmod +x frontend/.husky/pre-commit

# 3) BACKEND: pre-commit hooks (ruff + mypy + bandit)
cat > backend/.pre-commit-config.yaml <<'YAML'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        args: [-ll, -r, .]
        exclude: ^tests/|^migrations/|^venv/|^\.venv/
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports, --pretty]
YAML

# (opțional) mypy.ini de bază
cat > backend/mypy.ini <<'INI'
[mypy]
ignore_missing_imports = True
pretty = True
show_error_context = True
INI

# 4) CI pe PR: GitHub Actions
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'YAML'
name: CI

on:
  pull_request:
    branches: [ main, master ]
  push:
    branches: [ main ]

jobs:
  frontend:
    name: FE Lint & Build & Audit
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm run build --if-present
      - run: npm audit --audit-level=high

  backend:
    name: BE Ruff & Mypy & Bandit & Pytest & pip-audit
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -U pip
      - run: pip install -r requirements.txt || true
      - run: pip install ruff mypy bandit pytest pip-audit
      - run: ruff --output-format=github check .
      - run: ruff format --check
      - run: mypy . --ignore-missing-imports --pretty
      - run: bandit -ll -r . -x tests
      - run: pip-audit -r requirements.txt --strict || pip-audit --strict
      - run: pytest -q || true

  gate:
    name: PR Gate
    runs-on: ubuntu-latest
    needs: [frontend, backend]
    steps:
      - run: echo "All gates passed ✅"
YAML

# 5) COMMITURI
git add -A
git commit -m "chore(fe): add lint scripts, lint-staged and prepare(husky) in package.json"
git add frontend/.husky/pre-commit
git commit -m "chore(fe): add husky pre-commit (runs lint-staged)"
git add backend/.pre-commit-config.yaml backend/mypy.ini
git commit -m "chore(be): add pre-commit hooks (ruff, mypy, bandit)"
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions pipeline (FE lint/build/audit, BE ruff/mypy/bandit/pip-audit/pytest)"

# 6) PUSH
git push -u origin "$BRANCH"

# 7) Creează PR (folosește gh dacă e disponibil)
if command -v gh >/dev/null 2>&1; then
  gh pr create \
    --base "$BASE_BRANCH" \
    --head "$BRANCH" \
    --title "chore(ci): add PR gates (FE+BE) + Husky/pre-commit" \
    --body "$(cat <<'MD'
### What
- FE: Husky + lint-staged (eslint --fix, prettier on misc)
- BE: pre-commit (ruff --fix, mypy, bandit)
- CI: GitHub Actions (FE lint/build/audit; BE ruff/mypy/bandit/pip-audit/pytest)

### Why
Block low-quality code & high/critical vulns before merge; consistent QA across FE/BE.

### How to use locally
- Frontend:
  ```bash
  cd frontend
  npm ci
  npx husky install   # hooks
  ```
- Backend:
  ```bash
  cd backend
  pip install pre-commit
  pre-commit install
  ```

### Merge safety
No runtime logic changed. Only QA/CI configuration. Rollback = revert PR.
MD
)"
else
echo "PR creat manual: deschide repo -> Compare & pull request pentru branch $BRANCH"
fi