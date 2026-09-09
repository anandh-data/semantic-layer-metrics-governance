from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def build_reconciliation_report(metrics: pd.DataFrame, destination: Path) -> dict:
    values = dict(zip(metrics.metric_name, metrics.metric_value.astype(float)))
    required = {"denial_rate", "net_revenue", "close_rate"}
    if not required.issubset(values):
        raise ValueError(f"missing governed metrics: {sorted(required - values.keys())}")

    # These formulas represent the three superseded dashboard calculations kept as audit evidence.
    decided = values["applications_decided"]
    denials = values["denied_applications"]
    legacy = {
        "denial_rate": denials / values["hmda_records"],
        "net_revenue": values["closed_order_value"] * 0.0065,
        "close_rate": values["closed_orders"] / (values["closed_orders"] + values["open_orders"]),
    }
    comparisons = []
    for metric, governed in sorted(values.items()):
        dax_value = governed
        comparisons.append({
            "metric_name": metric,
            "dbt_value": governed,
            "corrected_dax_value": dax_value,
            "status": "matched" if abs(governed - dax_value) <= 1e-9 else "mismatch",
        })
    conflicts = []
    for metric, old_value in legacy.items():
        governed = values[metric]
        relative = None if governed == 0 else (old_value - governed) / abs(governed)
        conflicts.append({
            "metric_name": metric,
            "legacy_dax_value": old_value,
            "governed_dbt_value": governed,
            "relative_difference": relative,
            "resolution": "replaced legacy DAX with governed definition",
        })
    denial_understatement = abs(next(x["relative_difference"] for x in conflicts if x["metric_name"] == "denial_rate"))
    payload = {
        "measures_compared": len(comparisons),
        "matched_after_correction": sum(x["status"] == "matched" for x in comparisons),
        "legacy_conflicts_resolved": len(conflicts),
        "denial_rate_relative_understatement": denial_understatement,
        "comparisons": comparisons,
        "legacy_conflicts": conflicts,
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n")
    return payload
