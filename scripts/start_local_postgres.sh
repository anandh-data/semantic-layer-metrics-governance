#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PG_DATA="$REPO_ROOT/.local/postgres"
PG_LOG="$REPO_ROOT/.local/postgres.log"
PG_PORT="${POSTGRES_PORT:-55432}"

mkdir -p "$REPO_ROOT/.local"
if [[ ! -f "$PG_DATA/PG_VERSION" ]]; then
  initdb -D "$PG_DATA" --auth=trust --encoding=UTF8 >/dev/null
fi
if ! pg_ctl -D "$PG_DATA" status >/dev/null 2>&1; then
  pg_ctl -D "$PG_DATA" -l "$PG_LOG" -o "-p $PG_PORT -h 127.0.0.1" start >/dev/null
fi
if ! psql -h 127.0.0.1 -p "$PG_PORT" -d postgres -tAc "select 1 from pg_roles where rolname='metrics'" | grep -q 1; then
  psql -h 127.0.0.1 -p "$PG_PORT" -d postgres -c "create role metrics login password 'metrics_local_only'" >/dev/null
fi
if ! psql -h 127.0.0.1 -p "$PG_PORT" -d postgres -tAc "select 1 from pg_database where datname='metrics'" | grep -q 1; then
  createdb -h 127.0.0.1 -p "$PG_PORT" -O metrics metrics
fi
echo "PostgreSQL ready on 127.0.0.1:$PG_PORT"
