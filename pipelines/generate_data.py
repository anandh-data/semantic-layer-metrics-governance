from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from metric_hub.generator import generate_dataset
from metric_hub.logging_utils import build_logger


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate the authoritative project dataset")
    parser.add_argument("--rows", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    logger = build_logger("data-generation", ROOT / "logs/data-generation.jsonl")
    generate_dataset(ROOT / "data/raw", ROOT / "data/manifests", args.rows, args.seed, logger)
