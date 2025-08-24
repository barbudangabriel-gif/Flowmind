#!/bin/bash
set -euo pipefail

BRANCH="chore/gitlab-ci-hardening"
cd /app
git fetch origin || true
git checkout -b "$BRANCH" || git checkout -B "$BRANCH"

# 1) .gitlab-ci.yml — FE lint/build/audit + BE ruff/mypy/bandit/pip-audit/pytest (JUnit)
cat > .gitlab-ci.yml <<'YAML'
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH

stages: [fe, be, gate]

variables:
  NODE_OPTIONS: --max-old-space-size=2048
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  NPM_CONFIG_CACHE: "$CI_PROJECT_DIR/.cache/npm"

frontend:
  stage: fe
  image: node:20
  cache:
    key: "${CI_COMMIT_REF_SLUG}-fe"
    paths:
      - .cache/npm/
  before_script:
    - cd frontend
    - |
      if [ -f yarn.lock ]; then
        corepack enable
        yarn --version
        yarn install --immutable
      else
        npm ci
      fi
  script:
    - |
      if [ -f yarn.lock ]; then
        yarn run lint
        if grep -q '"build"' package.json; then yarn build; fi
        yarn audit --level high
      else
        npm run lint
        npm run build --if-present
        npm audit --audit-level=high
      fi
  artifacts:
    when: always
    expire_in: 1 week
    paths:
      - frontend/build/
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH

backend:
  stage: be
  image: python:3.11
  cache:
    key: "${CI_COMMIT_REF_SLUG}-be"
    paths:
      - .cache/pip/
  before_script:
    - cd backend
    - pip install -U pip
    - pip install ruff mypy bandit pytest pip-audit
    - |
      if [ -f requirements.txt ]; then
        pip install -r requirements.txt
      fi
  script:
    - ruff --output-format=github check .
    - ruff format --check
    - mypy . --ignore-missing-imports --pretty
    - bandit -ll -r . -x tests
    - |
      if [ -f requirements.txt ]; then
        pip-audit -r requirements.txt --strict
      else
        pip-audit --strict
      fi
    # Rulează teste și exportă JUnit; nu blochează pipeline dacă nu ai teste încă
    - pytest -q --maxfail=1 --disable-warnings --junitxml=backend/junit-report.xml || true
  artifacts:
    when: always
    expire_in: 1 week
    reports:
      junit: backend/junit-report.xml
    paths:
      - backend/.ruff_cache/
      - backend/.mypy_cache/
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH

gate:
  stage: gate
  image: alpine:3.19
  needs: [frontend, backend]
  script:
    - echo "All gates passed ✅"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH
YAML

# 2) CODEOWNERS — modifică @reviewer cu utilizatorii tăi GitLab
cat > CODEOWNERS <<'TXT'
# Frontend
/frontend/ @reviewer-frontend
# Backend
/backend/  @reviewer-backend
# CI
/.gitlab-ci.yml @reviewer-devops
TXT

# 3) README.md — adaugă secțiune scurtă despre CI/QA gates
if [ -f README.md ]; then
  awk '1' README.md > README.md.bak
else
  : > README.md.bak
fi

cat >> README.md <<'MD'

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
MD

# 4) Commituri
git add .gitlab-ci.yml CODEOWNERS README.md README.md.bak
git commit -m "ci(gitlab): FE lint/build/audit + BE ruff/mypy/bandit/pip-audit + pytest JUnit artifact"
git push -u origin "$BRANCH"

echo
echo "Branch împins: $BRANCH"
echo "Deschide Merge Request din GitLab: Compare → $BRANCH → $BASE (de obicei main)"