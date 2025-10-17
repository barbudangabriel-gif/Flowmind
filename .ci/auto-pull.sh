#!/usr/bin/env bash
# FlowMind Auto-Pull Script
# Automatically pulls latest changes from origin/main every 60 seconds
# Runs via systemd timer (flowmind-autopull.timer)

set -euo pipefail

# Navigate to repository root
cd "$(dirname "$0")/.."

echo "[autopull] Starting at $(date '+%Y-%m-%d %H:%M:%S')"

# Fetch latest changes from origin/main
git fetch origin main

# Get commit hashes
LOCAL=$(git rev-parse @ || echo "")
REMOTE=$(git rev-parse @{u} || echo "")

# Check if update needed
if [ "$LOCAL" != "$REMOTE" ]; then
  echo "[autopull] Changes detected on origin/main"
  echo "[autopull]   Local:  ${LOCAL:0:8}"
  echo "[autopull]   Remote: ${REMOTE:0:8}"
  echo "[autopull] Updating to origin/main..."
  
  # Hard reset to remote (DESTRUCTIVE - discards local changes)
  git reset --hard origin/main
  
  echo "[autopull] ✅ Code updated"
  
  # Check if frontend dependencies changed
  if git diff --name-only HEAD@{1}...HEAD 2>/dev/null | grep -q "frontend/pnpm-lock.yaml"; then
    echo "[autopull] Frontend lockfile changed -> reinstalling dependencies"
    (cd frontend && corepack enable && pnpm install --frozen-lockfile) || {
      echo "[autopull] ⚠️  Frontend install failed (non-fatal)"
    }
  fi
  
  # Check if backend dependencies changed
  if git diff --name-only HEAD@{1}...HEAD 2>/dev/null | grep -q "backend/requirements.txt"; then
    echo "[autopull] Backend requirements changed -> reinstalling dependencies"
    (cd backend && pip install -q -r requirements.txt) || {
      echo "[autopull] ⚠️  Backend install failed (non-fatal)"
    }
  fi
  
  # Optional: Rebuild frontend for production
  # Uncomment if running production build
  # if git diff --name-only HEAD@{1}...HEAD 2>/dev/null | grep -qE "^frontend/(src|public)/"; then
  #   echo "[autopull] Frontend code changed -> rebuilding"
  #   (cd frontend && pnpm build) || {
  #     echo "[autopull] ⚠️  Frontend build failed"
  #   }
  # fi
  
  # Note: uvicorn --reload will auto-restart backend
  # For gunicorn/production: systemctl --user restart flowmind-backend.service
  
  echo "[autopull] 🚀 Deployment complete"
else
  echo "[autopull] No changes detected (${LOCAL:0:8})"
fi

echo "[autopull] Done at $(date '+%Y-%m-%d %H:%M:%S')"
