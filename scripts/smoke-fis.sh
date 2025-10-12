#!/usr/bin/env bash
set -euo pipefail
corepack enable || true
yarn install --frozen-lockfile
cp -n .env.example .env || true
export FIS_API_MODE=mock
export FIS_API_BASE=${FIS_API_BASE:-http://localhost:5174}
(yarn mock:api &) >/dev/null 2>&1 || true
yarn start --smoke=fis
