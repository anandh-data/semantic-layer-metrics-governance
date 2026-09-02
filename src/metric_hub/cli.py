import argparse
import json
from pathlib import Path

from .core import aggregate_csv, drift_report, evaluate, load_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare BI outputs with governed metrics")
    parser.add_argument("--registry", default="registry/metrics.json")
    parser.add_argument("--facts", default="sample_data/daily_sales.csv")
    parser.add_argument("--reported", default="sample_data/bi_reported.json")
    args = parser.parse_args()
    registry = load_registry(args.registry)
    inputs = aggregate_csv(args.facts)
    governed = {name: evaluate(metric.expression, inputs) for name, metric in registry.items()}
    reported = json.loads(Path(args.reported).read_text())
    report = drift_report(governed, reported)
    print(json.dumps({"inputs": inputs, "results": report}, indent=2))
    return 1 if any(item["drifted"] for item in report) else 0


if __name__ == "__main__":
    raise SystemExit(main())
