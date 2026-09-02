import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect the latest executed metric-governance result")
    parser.add_argument("--allow-drift", action="store_true", help="return success even when team definitions drift")
    args = parser.parse_args()
    summary = json.loads((ROOT / "reports/pipeline-summary.json").read_text())
    drift = json.loads((ROOT / "reports/metric-drift-results.json").read_text())
    print(json.dumps({"pipeline": summary, "metric_drift": drift["evaluations"]}, indent=2))
    has_drift = any(item["status"] == "drifted" for item in drift["evaluations"])
    return 0 if args.allow_drift or not has_drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
