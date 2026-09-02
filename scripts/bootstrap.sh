#!/usr/bin/env bash
set -euo pipefail
docker compose up -d --wait postgres
python3 -m pip install -r requirements-dev.txt
PYTHONPATH=src python3 pipelines/run_pipeline.py --rows "${DATASET_ROWS:-50000}" --seed "${DATASET_SEED:-2026}"
