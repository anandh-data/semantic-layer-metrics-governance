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


def _present_id(values: pd.Series) -> pd.Series:
    return values.notna() & values.fillna("").astype(str).str.strip().ne("")


def validate_raw(raw_dir: Path) -> list[CheckResult]:
    orders = pd.read_parquet(raw_dir / "orders.parquet")
    events = pd.read_parquet(raw_dir / "escrow_events.parquet")
    finance = pd.read_parquet(raw_dir / "finance_transactions.parquet")
    valid_order_ids = orders.order_id[_present_id(orders.order_id)]
    valid_event_orders = _present_id(events.order_id) & events.order_id.isin(valid_order_ids)
    valid_finance_orders = _present_id(finance.order_id) & finance.order_id.isin(valid_order_ids)
    results = [
        CheckResult("orders", "row_count", "pass" if len(orders) > 0 else "fail", len(orders), "> 0"),
        CheckResult("orders", "unique_order_id", "pass" if orders.order_id.is_unique and _present_id(orders.order_id).all() else "fail", int(orders.order_id.nunique()), f"= {len(orders)} nonblank IDs"),
        CheckResult("orders", "valid_status", "pass" if orders.status.isin(["open", "closed", "cancelled"]).all() else "fail", int((~orders.status.isin(["open", "closed", "cancelled"])).sum()), "0 invalid"),
        CheckResult("orders", "nonnegative_order_value", "pass" if orders.order_value.min() >= 0 else "fail", float(orders.order_value.min()), ">= 0"),
        CheckResult("escrow_events", "unique_event_id", "pass" if events.event_id.is_unique and _present_id(events.event_id).all() else "fail", int(events.event_id.nunique()), f"= {len(events)} nonblank IDs"),
        CheckResult("escrow_events", "known_order", "pass" if valid_event_orders.all() else "fail", int((~valid_event_orders).sum()), "0 missing or orphaned"),
        CheckResult("finance_transactions", "unique_transaction_id", "pass" if finance.transaction_id.is_unique and _present_id(finance.transaction_id).all() else "fail", int(finance.transaction_id.nunique()), f"= {len(finance)} nonblank IDs"),
        CheckResult("finance_transactions", "known_order", "pass" if valid_finance_orders.all() else "fail", int((~valid_finance_orders).sum()), "0 missing or orphaned"),
        CheckResult("finance_transactions", "usd_only", "pass" if finance.currency.eq("USD").all() else "fail", int((~finance.currency.eq("USD")).sum()), "0 non-USD"),
    ]
    hmda_path = raw_dir / "hmda_applications.parquet"
    if hmda_path.exists():
        manifest = json.loads((raw_dir.parent / "manifests/hmda-data-manifest.json").read_text())
        expected_hmda_rows = int(manifest["records_selected"])
        hmda = pd.read_parquet(hmda_path, columns=["action_taken", "loan_type", "respondent_id", "state_code"])
        results.extend([
            CheckResult("hmda_applications", "row_count", "pass" if len(hmda) == expected_hmda_rows else "fail", len(hmda), f"= {expected_hmda_rows}"),
            CheckResult("hmda_applications", "valid_action_taken", "pass" if hmda.action_taken.isin(range(1, 9)).all() else "fail", int((~hmda.action_taken.isin(range(1, 9))).sum()), "0 invalid"),
            CheckResult("hmda_applications", "decided_population", "pass" if hmda.action_taken.isin([1, 2, 3]).any() else "fail", int(hmda.action_taken.isin([1, 2, 3]).sum()), "> 0"),
            CheckResult("hmda_applications", "valid_loan_type", "pass" if hmda.loan_type.isin([1, 2, 3, 4]).all() else "fail", int((~hmda.loan_type.isin([1, 2, 3, 4])).sum()), "0 invalid"),
            CheckResult("hmda_applications", "respondent_present", "pass" if hmda.respondent_id.ne("").all() else "fail", int(hmda.respondent_id.eq("").sum()), "0 missing"),
            CheckResult("hmda_applications", "geographic_coverage", "pass" if hmda.state_code.nunique() >= 50 else "fail", int(hmda.state_code.nunique()), ">= 50 state/territory codes"),
        ])
    return results


def write_results(results: list[CheckResult], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"checks": [asdict(result) for result in results]}, indent=2) + "\n")


def require_pass(results: list[CheckResult]) -> None:
    failed = [result for result in results if result.status != "pass"]
    if failed:
        raise RuntimeError(f"quality gate failed: {[result.check for result in failed]}")
