from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import psycopg2

from .logging_utils import log_event


TABLE_COLUMNS = {
    "orders": ["order_id", "opened_date", "closed_date", "status", "region", "product", "channel", "order_value", "source_updated_at"],
    "escrow_events": ["event_id", "order_id", "event_type", "event_date", "sequence"],
    "finance_transactions": ["transaction_id", "order_id", "transaction_date", "transaction_type", "amount", "currency"],
    "hmda_applications": ["as_of_year", "respondent_id", "agency_code", "loan_type", "loan_purpose", "loan_amount_000s", "preapproval", "action_taken", "state_code", "county_code", "applicant_ethnicity", "applicant_race_1", "applicant_sex", "applicant_income_000s", "purchaser_type"],
}


def execute_sql_file(dsn: str, path: Path) -> None:
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute(path.read_text())


def reset_raw_tables(dsn: str) -> None:
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute("truncate table raw.escrow_events, raw.finance_transactions, raw.hmda_applications, raw.orders")


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


def ingest_parquet_batches(dsn: str, table: str, path: Path, logger, batch_size: int = 100_000) -> int:
    if table not in TABLE_COLUMNS:
        raise ValueError(f"unsupported table: {table}")
    columns = TABLE_COLUMNS[table]
    total = 0
    parquet = pq.ParquetFile(path)
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        for batch in parquet.iter_batches(batch_size=batch_size, columns=columns):
            frame = batch.to_pandas()
            buffer = io.StringIO()
            frame.to_csv(buffer, index=False, header=False, na_rep="\\N")
            buffer.seek(0)
            cursor.copy_expert(
                f"copy raw.{table} ({','.join(columns)}) from stdin with (format csv, null '\\N')",
                buffer,
            )
            total += len(frame)
    log_event(logger, "table_ingested", table=f"raw.{table}", rows=total, source=f"data/raw/{path.name}")
    return total


def fetch_rows(dsn: str, query: str) -> tuple[list[str], list[tuple]]:
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute(query)
        columns = [item.name for item in cursor.description]
        return columns, cursor.fetchall()
