"""Generate a deterministic, multi-team business dataset for local and CI use."""
from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def generate(output: Path, rows: int, seed: int) -> None:
    rng = random.Random(seed)
    start = date(2025, 1, 1)
    orders, escrow_events, finance_transactions = [], [], []
    for index in range(1, rows + 1):
        order_id = f"ORD-{index:08d}"
        opened = start + timedelta(days=rng.randrange(365))
        amount = round(rng.uniform(2_500, 850_000), 2)
        status = rng.choices(["closed", "cancelled", "open"], [0.72, 0.08, 0.20])[0]
        closed = opened + timedelta(days=rng.randrange(2, 61)) if status == "closed" else None
        region = rng.choice(["NORTHEAST", "SOUTHEAST", "MIDWEST", "WEST"])
        orders.append({"order_id": order_id, "opened_date": opened, "closed_date": closed or "", "status": status, "region": region, "order_amount": amount})
        escrow_events.extend([
            {"event_id": f"EVT-{index:08d}-1", "order_id": order_id, "event_type": "escrow_opened", "event_date": opened},
            *([{"event_id": f"EVT-{index:08d}-2", "order_id": order_id, "event_type": "escrow_closed", "event_date": closed}] if closed else []),
        ])
        finance_transactions.append({"transaction_id": f"TXN-{index:08d}", "order_id": order_id, "transaction_date": closed or opened, "transaction_type": "recognized_revenue" if status == "closed" else "pending", "amount": round(amount * 0.0065, 2) if status == "closed" else 0})
    write_csv(output / "orders.csv", list(orders[0]), orders)
    write_csv(output / "escrow_events.csv", list(escrow_events[0]), escrow_events)
    write_csv(output / "finance_transactions.csv", list(finance_transactions[0]), finance_transactions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("dbt/seeds"))
    parser.add_argument("--rows", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    generate(args.output, args.rows, args.seed)
