from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from .logging_utils import log_event


REGIONS = ("NORTHEAST", "SOUTHEAST", "MIDWEST", "WEST")
CHANNELS = ("partner", "direct", "enterprise", "referral")
PRODUCTS = ("purchase", "refinance", "commercial", "escrow_only")


@dataclass(frozen=True)
class GeneratedDataset:
    orders: Path
    escrow_events: Path
    finance_transactions: Path
    manifest: Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False, compression="snappy")


def generate_dataset(raw_dir: Path, manifest_dir: Path, rows: int, seed: int, logger) -> GeneratedDataset:
    if rows < 1000:
        raise ValueError("production dataset requires at least 1,000 orders")
    rng = random.Random(seed)
    start = date(2024, 1, 1)
    orders: list[dict[str, object]] = []
    events: list[dict[str, object]] = []
    transactions: list[dict[str, object]] = []
    for number in range(1, rows + 1):
        order_id = f"ORD-{number:09d}"
        opened = start + timedelta(days=rng.randrange(730))
        region = rng.choices(REGIONS, weights=(28, 25, 21, 26))[0]
        product = rng.choices(PRODUCTS, weights=(48, 29, 12, 11))[0]
        channel = rng.choice(CHANNELS)
        order_value = round(rng.triangular(25_000, 1_250_000, 330_000), 2)
        status = rng.choices(("closed", "open", "cancelled"), weights=(76, 17, 7))[0]
        close_days = rng.randint(3, 75)
        closed = opened + timedelta(days=close_days) if status == "closed" else None
        orders.append({
            "order_id": order_id, "opened_date": opened, "closed_date": closed,
            "status": status, "region": region, "product": product,
            "channel": channel, "order_value": order_value,
            "source_updated_at": (closed or opened) + timedelta(days=rng.randint(0, 2)),
        })
        events.append({"event_id": f"EVT-{number:09d}-01", "order_id": order_id, "event_type": "escrow_opened", "event_date": opened, "sequence": 1})
        if status == "closed":
            events.append({"event_id": f"EVT-{number:09d}-02", "order_id": order_id, "event_type": "documents_received", "event_date": opened + timedelta(days=max(1, close_days // 3)), "sequence": 2})
            events.append({"event_id": f"EVT-{number:09d}-03", "order_id": order_id, "event_type": "escrow_closed", "event_date": closed, "sequence": 3})
            fee_rate = {"purchase": 0.0065, "refinance": 0.0048, "commercial": 0.0075, "escrow_only": 0.0025}[product]
            revenue = round(order_value * fee_rate, 2)
            transactions.append({"transaction_id": f"TXN-{number:09d}-01", "order_id": order_id, "transaction_date": closed, "transaction_type": "recognized_revenue", "amount": revenue, "currency": "USD"})
            if rng.random() < 0.045:
                transactions.append({"transaction_id": f"TXN-{number:09d}-02", "order_id": order_id, "transaction_date": closed + timedelta(days=rng.randint(1, 20)), "transaction_type": "refund", "amount": round(-revenue * rng.uniform(0.05, 0.45), 2), "currency": "USD"})
        elif status == "cancelled":
            events.append({"event_id": f"EVT-{number:09d}-02", "order_id": order_id, "event_type": "escrow_cancelled", "event_date": opened + timedelta(days=close_days), "sequence": 2})

    paths = GeneratedDataset(
        raw_dir / "orders.parquet", raw_dir / "escrow_events.parquet",
        raw_dir / "finance_transactions.parquet", manifest_dir / "raw-data-manifest.json",
    )
    frames = {
        "orders": pd.DataFrame(orders), "escrow_events": pd.DataFrame(events),
        "finance_transactions": pd.DataFrame(transactions),
    }
    for name, frame in frames.items():
        _write(frame, getattr(paths, name))
        log_event(logger, "dataset_written", dataset=name, rows=len(frame), columns=len(frame.columns), path=f"data/raw/{getattr(paths, name).name}")
    manifest = {
        "dataset": "governed-metrics-domain", "version": "1.0.0", "seed": seed,
        "order_rows": rows,
        "files": {name: {"path": path.name, "rows": len(frames[name]), "bytes": path.stat().st_size, "sha256": sha256(path)} for name, path in (("orders", paths.orders), ("escrow_events", paths.escrow_events), ("finance_transactions", paths.finance_transactions))},
    }
    paths.manifest.parent.mkdir(parents=True, exist_ok=True)
    paths.manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    log_event(logger, "generation_completed", seed=seed, orders=rows, manifest="data/manifests/raw-data-manifest.json")
    return paths
