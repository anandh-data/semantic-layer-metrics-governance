#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PG_DATA="$REPO_ROOT/.local/postgres"
if [[ -f "$PG_DATA/PG_VERSION" ]] && pg_ctl -D "$PG_DATA" status >/dev/null 2>&1; then
  pg_ctl -D "$PG_DATA" stop -m fast >/dev/null
fi
echo "Local PostgreSQL stopped"
