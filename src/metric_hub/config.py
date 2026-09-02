from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    root: Path = ROOT
    dataset_rows: int = int(os.getenv("DATASET_ROWS", "50000"))
    dataset_seed: int = int(os.getenv("DATASET_SEED", "2026"))
    pg_host: str = os.getenv("POSTGRES_HOST", "127.0.0.1")
    pg_port: int = int(os.getenv("POSTGRES_PORT", "55432"))
    pg_user: str = os.getenv("POSTGRES_USER", "metrics")
    pg_password: str = os.getenv("POSTGRES_PASSWORD", "metrics_local_only")
    pg_database: str = os.getenv("POSTGRES_DB", "metrics")

    @property
    def raw_dir(self) -> Path:
        return self.root / "data/raw"

    @property
    def processed_dir(self) -> Path:
        return self.root / "data/processed"

    @property
    def manifest_dir(self) -> Path:
        return self.root / "data/manifests"

    @property
    def log_dir(self) -> Path:
        return self.root / "logs"

    @property
    def dsn(self) -> str:
        return f"host={self.pg_host} port={self.pg_port} user={self.pg_user} password={self.pg_password} dbname={self.pg_database}"
