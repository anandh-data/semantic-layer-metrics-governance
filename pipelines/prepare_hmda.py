from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from metric_hub.hmda import prepare_hmda


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare the fixed CFPB HMDA analytical dataset")
    parser.add_argument("--zip", type=Path, default=ROOT / "data/external/hmda_2017_nationwide_all_records_codes.zip")
    parser.add_argument("--rows", type=int, default=2_800_000)
    args = parser.parse_args()
    result = prepare_hmda(
        args.zip,
        ROOT / "data/raw/hmda_applications.parquet",
        ROOT / "data/manifests/hmda-data-manifest.json",
        args.rows,
    )
    print(json.dumps(result, indent=2))
