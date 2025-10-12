# Here are your Instructions

## Package Manager Policy
**Use only `yarn` for all Node.js/React/Frontend operations. Do NOT use `pnpm` or `npm` in this repository.**

If you see a `pnpm-lock.yaml`, delete it. Only `yarn.lock` is supported. All install/build/dev commands must use `yarn`.

## CI/QA Gates (GitLab)
- **FE (Node 20):** `eslint`, `build`, `npm audit --audit-level=high`
- **BE (Py 3.11):** `ruff`, `mypy`, `bandit`, `pip-audit --strict`, `pytest` → **JUnit** ca artifact
### Local:
```bash
# Frontend
cd frontend && npm ci && npm run lint && npm run build && npm audit --audit-level=high
# Backend
cd backend && pip install -r requirements.txt || true
pip install ruff mypy bandit pytest pip-audit
ruff check . && mypy . --ignore-missing-imports && bandit -ll -r . && pip-audit -r requirements.txt --strict
pytest -q --maxfail=1 --disable-warnings
```
