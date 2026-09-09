import tempfile
import unittest
from pathlib import Path

import pandas as pd

from metric_hub.reconciliation import build_reconciliation_report


class ReconciliationTests(unittest.TestCase):
    def test_compares_all_measures_and_preserves_legacy_audit(self):
        values = {
            "denial_rate": 0.20, "denied_applications": 20, "applications_decided": 100,
            "hmda_records": 140, "net_revenue": 90, "closed_order_value": 10000,
            "close_rate": 0.60, "closed_orders": 60, "open_orders": 30,
        }
        frame = pd.DataFrame(values.items(), columns=["metric_name", "metric_value"])
        with tempfile.TemporaryDirectory() as directory:
            report = build_reconciliation_report(frame, Path(directory) / "result.json")
        self.assertEqual(report["measures_compared"], len(values))
        self.assertEqual(report["legacy_conflicts_resolved"], 3)
        self.assertEqual(report["matched_after_correction"], len(values))
