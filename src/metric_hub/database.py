from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import psycopg2

from .logging_utils import log_event


TABLE_COLUMNS = {
    "orders": ["order_id", "opened_date", "closed_date", "status", "region", "product", "channel", "order_value", "source_updated_at"],
    "escrow_events": ["event_id", "order_id", "event_type", "event_date", "sequence"],
    "finance_transactions": ["transaction_id", "order_id", "transaction_date", "transaction_type", "amount", "currency"],
}


def execute_sql_file(dsn: str, path: Path) -> None:
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute(path.read_text())


def reset_raw_tables(dsn: str) -> None:
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute("truncate table raw.escrow_events, raw.finance_transactions, raw.orders")


def ingest_parquet(dsn: str, table: str, path: Path, logger) -> int:
    if table not in TABLE_COLUMNS:
        raise ValueError(f"unsupported table: {table}")
    frame = pd.read_parquet(path)[TABLE_COLUMNS[table]]
    buffer = io.StringIO()
    frame.to_csv(buffer, index=False, header=False, na_rep="\\N")
    buffer.seek(0)
    columns = ",".join(TABLE_COLUMNS[table])
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.copy_expert(f"copy raw.{table} ({columns}) from stdin with (format csv, null '\\N')", buffer)
    log_event(logger, "table_ingested", table=f"raw.{table}", rows=len(frame), source=f"data/raw/{path.name}")
    return len(frame)


def fetch_rows(dsn: str, query: str) -> tuple[list[str], list[tuple]]:
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute(query)
        columns = [item.name for item in cursor.description]
        return columns, cursor.fetchall()
