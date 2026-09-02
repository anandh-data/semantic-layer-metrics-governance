import json
import logging
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from metric_hub.generator import generate_dataset, sha256


class GeneratorTests(unittest.TestCase):
    def test_generator_is_deterministic_and_relational(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            logger = logging.getLogger("generator-test")
            one = generate_dataset(Path(first) / "raw", Path(first) / "manifest", 1000, 7, logger)
            two = generate_dataset(Path(second) / "raw", Path(second) / "manifest", 1000, 7, logger)
            self.assertEqual(sha256(one.orders), sha256(two.orders))
            orders = pd.read_parquet(one.orders)
            events = pd.read_parquet(one.escrow_events)
            finance = pd.read_parquet(one.finance_transactions)
            self.assertEqual(len(orders), 1000)
            self.assertTrue(events.order_id.isin(orders.order_id).all())
            self.assertTrue(finance.order_id.isin(orders.order_id).all())
            self.assertEqual(json.loads(one.manifest.read_text())["seed"], 7)

    def test_tiny_dataset_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                generate_dataset(Path(directory), Path(directory), 10, 1, logging.getLogger("test"))
