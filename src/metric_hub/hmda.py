from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


HMDA_SOURCE_URL = (
    "https://files.consumerfinance.gov/hmda-historic-loan-data/"
    "hmda_2017_nationwide_all-records_codes.zip"
)
HMDA_SOURCE_ROWS = 14_285_496
HMDA_COLUMNS = [
    "as_of_year", "respondent_id", "agency_code", "loan_type", "loan_purpose",
    "loan_amount_000s", "preapproval", "action_taken", "state_code",
    "county_code", "applicant_ethnicity", "applicant_race_1", "applicant_sex",
    "applicant_income_000s", "purchaser_type",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def prepare_hmda(zip_path: Path, destination: Path, manifest_path: Path, rows: int = 2_800_000) -> dict:
    """Create a deterministic analytical Parquet slice without extracting the 4.6 GB CSV."""
    if rows < 1 or rows > HMDA_SOURCE_ROWS:
        raise ValueError(f"rows must be between 1 and {HMDA_SOURCE_ROWS:,}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    written = 0
    source_offset = 0
    selected_positions = np.floor(np.arange(rows, dtype=np.float64) * HMDA_SOURCE_ROWS / rows).astype(np.int64)
    with zipfile.ZipFile(zip_path) as archive:
        member = archive.namelist()[0]
        with archive.open(member) as source:
            for chunk in pd.read_csv(source, usecols=HMDA_COLUMNS, dtype=str, chunksize=100_000):
                end = source_offset + len(chunk)
                left = np.searchsorted(selected_positions, source_offset, side="left")
                right = np.searchsorted(selected_positions, end, side="left")
                local_positions = selected_positions[left:right] - source_offset
                source_offset = end
                if len(local_positions) == 0:
                    continue
                chunk = chunk.iloc[local_positions].copy()
                for column in ["as_of_year", "agency_code", "loan_type", "loan_purpose", "preapproval", "action_taken", "applicant_ethnicity", "applicant_race_1", "applicant_sex", "purchaser_type"]:
                    chunk[column] = pd.to_numeric(chunk[column], errors="coerce").astype("Int16")
                for column in ["respondent_id", "state_code", "county_code"]:
                    chunk[column] = chunk[column].fillna("").astype(str)
                chunk["loan_amount_000s"] = pd.to_numeric(chunk["loan_amount_000s"], errors="coerce").astype("float64")
                chunk["applicant_income_000s"] = pd.to_numeric(chunk["applicant_income_000s"], errors="coerce").astype("float64")
                table = pa.Table.from_pandas(chunk, preserve_index=False)
                writer = writer or pq.ParquetWriter(destination, table.schema, compression="snappy")
                writer.write_table(table)
                written += len(chunk)
    if writer:
        writer.close()
    payload = {
        "dataset": "CFPB HMDA 2017 nationwide all-records coded file",
        "source_url": HMDA_SOURCE_URL,
        "source_records": HMDA_SOURCE_ROWS,
        "records_selected": written,
        "selection": "2,800,000-row deterministic systematic sample across all published rows",
        "source_sha256": sha256(zip_path),
        "parquet_sha256": sha256(destination),
        "columns": HMDA_COLUMNS,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n")
    return payload
