from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class CheckResult:
    dataset: str
    check: str
    status: str
    observed: int | float | str
    expectation: str


def validate_raw(raw_dir: Path) -> list[CheckResult]:
    orders = pd.read_parquet(raw_dir / "orders.parquet")
    events = pd.read_parquet(raw_dir / "escrow_events.parquet")
    finance = pd.read_parquet(raw_dir / "finance_transactions.parquet")
    results = [
        CheckResult("orders", "row_count", "pass" if len(orders) > 0 else "fail", len(orders), "> 0"),
        CheckResult("orders", "unique_order_id", "pass" if orders.order_id.is_unique else "fail", int(orders.order_id.nunique()), f"= {len(orders)}"),
        CheckResult("orders", "valid_status", "pass" if orders.status.isin(["open", "closed", "cancelled"]).all() else "fail", int((~orders.status.isin(["open", "closed", "cancelled"])).sum()), "0 invalid"),
        CheckResult("orders", "nonnegative_order_value", "pass" if orders.order_value.min() >= 0 else "fail", float(orders.order_value.min()), ">= 0"),
        CheckResult("escrow_events", "unique_event_id", "pass" if events.event_id.is_unique else "fail", int(events.event_id.nunique()), f"= {len(events)}"),
        CheckResult("escrow_events", "known_order", "pass" if events.order_id.isin(orders.order_id).all() else "fail", int((~events.order_id.isin(orders.order_id)).sum()), "0 orphaned"),
        CheckResult("finance_transactions", "unique_transaction_id", "pass" if finance.transaction_id.is_unique else "fail", int(finance.transaction_id.nunique()), f"= {len(finance)}"),
        CheckResult("finance_transactions", "known_order", "pass" if finance.order_id.isin(orders.order_id).all() else "fail", int((~finance.order_id.isin(orders.order_id)).sum()), "0 orphaned"),
        CheckResult("finance_transactions", "usd_only", "pass" if finance.currency.eq("USD").all() else "fail", int((~finance.currency.eq("USD")).sum()), "0 non-USD"),
    ]
    return results


def write_results(results: list[CheckResult], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"checks": [asdict(result) for result in results]}, indent=2) + "\n")


def require_pass(results: list[CheckResult]) -> None:
    failed = [result for result in results if result.status != "pass"]
    if failed:
        raise RuntimeError(f"quality gate failed: {[result.check for result in failed]}")
