import tempfile
import unittest
from pathlib import Path

import pandas as pd

from metric_hub.validation import require_pass, validate_raw


class FailureInjectionTests(unittest.TestCase):
    def test_duplicate_order_blocks_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            orders = pd.DataFrame([
                {"order_id":"ORD-1","status":"closed","order_value":100},
                {"order_id":"ORD-1","status":"closed","order_value":100},
            ])
            events = pd.DataFrame([{"event_id":"E-1","order_id":"ORD-1"}])
            finance = pd.DataFrame([{"transaction_id":"T-1","order_id":"ORD-1","currency":"USD"}])
            orders.to_parquet(root / "orders.parquet")
            events.to_parquet(root / "escrow_events.parquet")
            finance.to_parquet(root / "finance_transactions.parquet")
            results = validate_raw(root)
            with self.assertRaises(RuntimeError):
                require_pass(results)
