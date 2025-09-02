#!/usr/bin/env bash
set -euo pipefail
echo "=== ENV ==="
node -v || true; npm -v || true; python3 -V || true; pip -V || true

echo; echo "=== GIT HYGIENE ==="
git status -s || true
git log --oneline -n 5 || true
echo; echo "TODO in main (NU e voie):"
git grep -nE 'TODO|FIXME' -- ':!**/node_modules/**' ':!**/dist/**' ':!**/build/**' || true

echo; echo "=== FRONTEND ==="
if [ -f package.json ]; then
  npx -y eslint . --ext .ts,.tsx,.js,.jsx || true
  npx -y tsc --noEmit || true
  npx -y npm-run-all -p "npm:build --if-present" || true
  echo; echo "Dependency vulns (prod):"
  npm audit --production || true
fi

echo; echo "=== BACKEND (Python) ==="
if [ -f requirements.txt ] || [ -f pyproject.toml ]; then
  python3 -m pip install --quiet --upgrade pip || true
  python3 -m pip install --quiet bandit safety || true
  echo; echo "[bandit] Security scan (src/app, app, backend*)"
  bandit -q -r src app backend || true
  echo; echo "[safety] Vulnerable packages"
  safety check --full-report || true
fi

echo; echo "=== FASTAPI SMOKE (static) ==="
git grep -nE 'uvicorn.run|app = FastAPI' backend app src || true
git grep -nE 'add_middleware\\(CORSMiddleware' backend app src || true
git grep -nE 'IncludeRouter|APIRouter|@app\\.get|@router\\.' backend app src || true

echo; echo "=== SECRET LEAKS (grep) ==="
git grep -nE '(AWS_|API[_-]?KEY|SECRET|TOKEN|PASSWORD|PRIVATE KEY|BEGIN RSA)' -- ':!**/node_modules/**' ':!**/dist/**' || true

echo; echo "=== MONGO HOT PATHS ==="
git grep -nE 'db\\.|pymongo|motor' backend app src || true

echo; echo "=== FRONTEND BUNDLE RED FLAGS ==="
git grep -nE 'console\\.log|debugger;' src || true
git grep -nE 'process\\.env\\.' src || true

echo; echo "=== SUMMARY DONE ==="