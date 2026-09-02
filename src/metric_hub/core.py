from __future__ import annotations

import ast
import csv
import json
from dataclasses import dataclass
from pathlib import Path


ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Name, ast.Load, ast.Constant)


@dataclass(frozen=True)
class Metric:
    name: str
    label: str
    owner: str
    version: int
    expression: str
    description: str


def load_registry(path: str | Path) -> dict[str, Metric]:
    payload = json.loads(Path(path).read_text())
    metrics = [Metric(**item) for item in payload["metrics"]]
    names = [metric.name for metric in metrics]
    if len(names) != len(set(names)):
        raise ValueError("metric names must be unique")
    return {metric.name: metric for metric in metrics}


def evaluate(expression: str, values: dict[str, float]) -> float:
    tree = ast.parse(expression, mode="eval")
    if any(not isinstance(node, ALLOWED_NODES) for node in ast.walk(tree)):
        raise ValueError("unsupported expression")
    unknown = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} - values.keys()
    if unknown:
        raise KeyError(f"missing inputs: {sorted(unknown)}")
    return float(eval(compile(tree, "<metric>", "eval"), {"__builtins__": {}}, values))


def aggregate_csv(path: str | Path) -> dict[str, float]:
    with Path(path).open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {
        "gross_sales": sum(float(row["gross_sales"]) for row in rows),
        "refunds": sum(float(row["refunds"]) for row in rows),
        "orders": float(sum(int(row["orders"]) for row in rows)),
    }


def drift_report(governed: dict[str, float], reported: dict[str, float], tolerance: float = 0.001) -> list[dict[str, object]]:
    output = []
    for name, expected in governed.items():
        actual = reported.get(name)
        delta = None if actual is None else actual - expected
        drifted = actual is None or abs(delta or 0) > max(abs(expected) * tolerance, 0.01)
        output.append({"metric": name, "governed": expected, "reported": actual, "delta": delta, "drifted": drifted})
    return output
