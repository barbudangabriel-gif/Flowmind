#!/usr/bin/env bash
set -euo pipefail

: "${GITLAB_BASE_URL:?ex: https://gitlab.com}"
: "${PROJECT_ID:?numeric}"
: "${GITLAB_TOKEN:?PAT with api scope}"

api() {
  curl -sS --fail -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_BASE_URL/api/v4/projects/$PROJECT_ID/labels" \
    -H 'Content-Type: application/json' -d "$1" || true
}

mk() { api "{\"name\":\"$1\",\"color\":\"$2\"}"; }

echo "Creating FlowMind GitLab labels..."

# Type labels
mk "type:feature" "#1f77b4"
mk "type:bug" "#d62728"
mk "type:chore" "#7f7f7f"

# Priority labels
mk "prio:P0" "#ff0000"
mk "prio:P1" "#ff7f0e"
mk "prio:P2" "#ffbb78"

# Area labels
mk "area:frontend" "#2ca02c"
mk "area:backend" "#17becf"
mk "area:iv" "#9467bd"
mk "area:ts" "#8c564b"
mk "area:infra" "#bcbd22"

# Status labels
mk "status:blocked" "#e377c2"
mk "needs-info" "#aec7e8"
mk "security" "#c5b0d5"
mk "performance" "#98df8a"

echo "Done. Verifică Project → Labels în GitLab."