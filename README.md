# Here are your Instructions

![FIS Smoke Health](https://github.com/barbudangabriel-gif/Flowmind/actions/workflows/fis-smoke.yml/badge.svg)

## Staging Quickstart
- `.env.staging`:

```
VITE_FIS_API_BASE=https://<staging-api>
VITE_FIS_API_MODE=live
VITE_FIS_DEFAULT_SYMBOL=TSLA
```

- Start:
```bash
VITE_FIS_API_BASE="https://<staging-api>" yarn start:staging
```

Criterii OK: UI 5173 (Public), răspuns 200 de la <staging-api> pe /fis/score, /analytics/ivx, /options/gex, /flow/bias.

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
