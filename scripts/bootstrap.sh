#!/usr/bin/env bash
set -euo pipefail
python3 data_generator/generate.py --rows "${DATASET_ROWS:-10000}" --seed "${DATASET_SEED:-2026}"
docker compose up -d postgres
python3 -m pip install -r requirements-dev.txt
DBT_PROFILES_DIR=dbt dbt seed --project-dir dbt
DBT_PROFILES_DIR=dbt dbt build --project-dir dbt
