from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path


@dataclass(frozen=True)
class DriftResult:
    metric_name: str
    team_name: str
    governed_value: float
    reported_value: float
    absolute_delta: float
    relative_delta: float | None
    status: str


def classify(metric_name: str, team_name: str, governed: Decimal, reported: Decimal, thresholds: dict) -> DriftResult:
    rule = thresholds.get(metric_name, thresholds["default"])
    absolute = abs(reported - governed)
    relative = None if governed == 0 else absolute / abs(governed)
    within_absolute = absolute <= Decimal(str(rule["absolute_tolerance"]))
    within_relative = relative is not None and relative <= Decimal(str(rule["relative_tolerance"]))
    status = "certified" if within_absolute or within_relative else "drifted"
    return DriftResult(metric_name, team_name, float(governed), float(reported), float(absolute), None if relative is None else float(relative), status)


def evaluate_rows(rows: list[tuple], threshold_path: Path) -> list[DriftResult]:
    thresholds = json.loads(threshold_path.read_text())
    return [classify(str(metric), str(team), Decimal(governed), Decimal(reported), thresholds) for metric, team, governed, reported in rows]


def write_drift(results: list[DriftResult], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"evaluations": [asdict(result) for result in results]}, indent=2) + "\n")
