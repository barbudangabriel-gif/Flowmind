# Flowmind – FIS UI Smoke (Codespaces/dev)

## Obiectiv
Validare rapidă că FIS UI pornește în Codespaces, randează cardul de scor și comunică cu mock API fără erori.

## Scope
**In:** pornire UI (Vite), mock API, fetch-uri cheie, verificări UI/Network.  
**Out:** performanță, auth real, date live, E2E.

## Setup
- `.env`
  - `VITE_FIS_API_BASE=http://localhost:5174`
  - `VITE_FIS_API_MODE=mock`
  - `VITE_FIS_DEFAULT_SYMBOL=TSLA`
- `package.json` (scripts)
  - `start = vite --host 0.0.0.0 --port 5173 --strictPort --open=false --clearScreen=false`
  - `dev:all = concurrently -k -n API,UI "yarn mock:api" "yarn start"`
  - `health = node scripts/health-check.js`
- Mock API: CORS activ (`app.use(cors({ origin: true }))`)

## Rulare
```bash
yarn dev:all        # pornește mock API + UI
yarn health         # verifică API + UI
```

Criterii PASS

UI accesibil pe 5173 (Public), fără erori roșii în Console.

Card FIS Score vizibil cu scor 0–100.

DevTools → Network: 200 la:

/fis/score, /analytics/ivx, /options/gex, /flow/bias.

Troubleshooting rapid
# port blocat / instanțe paralele
pkill -f vite || true; pkill -f mock-api.js || true
lsof -t -i :5173 | xargs -r kill -9
lsof -t -i :5174 | xargs -r kill -9

# repornire curată
nohup yarn mock:api >/tmp/mock-api.log 2>&1 & disown
yarn start

Audit

Screenshot Dashboard + Network (4×200).

yarn health output.

Commit hash.

Status curent

PASS (smoke-green dev) – UI 5173 Public, API 5174 Public, 4×200 OK, scor afișat TSLA.


### (Opțional) CI – health-check GitHub Actions
```yaml
name: FIS Smoke Health
on: [workflow_dispatch]
jobs:
  health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '18' }
      - run: corepack enable
      - run: yarn install --frozen-lockfile
      - run: nohup node ./scripts/mock-api.js >/tmp/mock.log 2>&1 & disown
      - run: node scripts/health-check.js
```
