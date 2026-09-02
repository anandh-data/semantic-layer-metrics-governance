from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psycopg2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from metric_hub.config import Settings
from metric_hub.database import execute_sql_file, fetch_rows, ingest_parquet, reset_raw_tables
from metric_hub.drift import evaluate_rows, write_drift
from metric_hub.generator import generate_dataset
from metric_hub.logging_utils import build_logger, log_event
from metric_hub.profiling import profile_parquet
from metric_hub.reports import dashboard, evidence_charts, quality_report
from metric_hub.validation import require_pass, validate_raw, write_results


def git_sha() -> str:
    configured = os.getenv("GIT_SHA")
    if configured:
        return configured
    result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else "container-build"


def run_dbt(settings: Settings) -> None:
    environment = os.environ | {
        "POSTGRES_HOST": settings.pg_host, "POSTGRES_PORT": str(settings.pg_port),
        "POSTGRES_USER": settings.pg_user, "POSTGRES_PASSWORD": settings.pg_password,
        "POSTGRES_DB": settings.pg_database, "DBT_PROFILES_DIR": str(ROOT / "dbt"),
    }
    command = ["dbt", "build", "--project-dir", str(ROOT / "dbt"), "--profiles-dir", str(ROOT / "dbt")]
    result = subprocess.run(command, cwd=ROOT, env=environment, text=True, capture_output=True)
    clean_output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout + result.stderr)
    (ROOT / "logs/dbt-build.log").write_text(clean_output)
    if result.returncode:
        raise RuntimeError(f"dbt build failed; see {ROOT / 'logs/dbt-build.log'}")


def record_run(settings: Settings, run_id: str, started: datetime, status: str, records: int) -> None:
    with psycopg2.connect(settings.dsn) as connection, connection.cursor() as cursor:
        cursor.execute(
            """insert into governance.pipeline_run(run_id,git_sha,dataset_version,started_at,completed_at,status,records_processed)
            values(%s,%s,'1.0.0',%s,now(),%s,%s)
            on conflict(run_id) do update set completed_at=excluded.completed_at,status=excluded.status,records_processed=excluded.records_processed""",
            (run_id, git_sha(), started, status, records),
        )


def run(rows: int, seed: int) -> dict[str, object]:
    settings = Settings(dataset_rows=rows, dataset_seed=seed)
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    logger = build_logger("metric-governance", settings.log_dir / "end-to-end-pipeline.jsonl")
    run_id, started = str(uuid.uuid4()), datetime.now(timezone.utc)
    log_event(logger, "pipeline_started", run_id=run_id, git_sha=git_sha(), rows=rows, seed=seed)
    try:
        dataset = generate_dataset(settings.raw_dir, settings.manifest_dir, rows, seed, logger)
        checks = validate_raw(settings.raw_dir)
        profile_parquet([dataset.orders, dataset.escrow_events, dataset.finance_transactions], ROOT / "reports/data-profile.html")
        write_results(checks, ROOT / "reports/quality-results.json")
        quality_report(checks, ROOT / "reports/data-quality-report.html")
        require_pass(checks)
        for migration in sorted((ROOT / "db/migrations").glob("*.sql")):
            execute_sql_file(settings.dsn, migration)
            log_event(logger, "migration_applied", migration=migration.name)
        execute_sql_file(settings.dsn, ROOT / "db/ddl/create_indexes.sql")
        reset_raw_tables(settings.dsn)
        counts = {
            "orders": ingest_parquet(settings.dsn, "orders", dataset.orders, logger),
            "escrow_events": ingest_parquet(settings.dsn, "escrow_events", dataset.escrow_events, logger),
            "finance_transactions": ingest_parquet(settings.dsn, "finance_transactions", dataset.finance_transactions, logger),
        }
        quality_columns, quality_rows = fetch_rows(settings.dsn, (ROOT / "sql/validation/source_quality.sql").read_text())
        failed_sql_checks = [dict(zip(quality_columns, row)) for row in quality_rows if row[1] != 0]
        if failed_sql_checks:
            raise RuntimeError(f"warehouse source checks failed: {failed_sql_checks}")
        run_dbt(settings)
        _, comparison_rows = fetch_rows(settings.dsn, (ROOT / "sql/marts/team_metric_comparison.sql").read_text())
        drift = evaluate_rows(comparison_rows, ROOT / "configs/metric-thresholds.json")
        write_drift(drift, ROOT / "reports/metric-drift-results.json")
        columns, daily_rows = fetch_rows(settings.dsn, "select * from analytics.metric_daily_performance order by metric_date, region")
        daily = pd.DataFrame(daily_rows, columns=columns)
        settings.processed_dir.mkdir(parents=True, exist_ok=True)
        daily.to_parquet(settings.processed_dir / "daily-governed-metrics.parquet", index=False)
        order_columns, order_rows = fetch_rows(settings.dsn, "select * from analytics.fct_order_performance order by order_id")
        pd.DataFrame(order_rows, columns=order_columns).to_parquet(settings.processed_dir / "order-performance.parquet", index=False)
        dashboard(daily, drift, ROOT / "dashboard/metric-governance-dashboard.html", ROOT / "screenshots/metric-governance-dashboard.png")
        evidence_charts(daily, drift, checks, ROOT / "screenshots")
        summary = {
            "run_id": run_id, "status": "passed", "git_sha": git_sha(), "dataset_version": "1.0.0",
            "records": counts, "quality_checks": len(checks), "quality_failures": 0,
            "metric_evaluations": len(drift), "drifted_metrics": sum(result.status == "drifted" for result in drift),
            "started_at": started.isoformat(), "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        (ROOT / "reports/pipeline-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        record_run(settings, run_id, started, "passed", sum(counts.values()))
        log_event(logger, "pipeline_completed", **summary)
        return summary
    except Exception as error:
        log_event(logger, "pipeline_failed", run_id=run_id, error_type=type(error).__name__, error=str(error))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute the complete metric-governance pipeline")
    parser.add_argument("--rows", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=2026)
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.rows, arguments.seed), indent=2))
