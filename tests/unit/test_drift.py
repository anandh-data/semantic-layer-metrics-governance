import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from metric_hub.drift import classify, evaluate_rows


class DriftTests(unittest.TestCase):
    def setUp(self):
        self.thresholds = {"default": {"absolute_tolerance": 1, "relative_tolerance": 0.01}}

    def test_exact_value_is_certified(self):
        result = classify("revenue", "finance", Decimal("100"), Decimal("100"), self.thresholds)
        self.assertEqual(result.status, "certified")

    def test_material_difference_is_drifted(self):
        result = classify("revenue", "sales", Decimal("100"), Decimal("120"), self.thresholds)
        self.assertEqual(result.status, "drifted")
        self.assertEqual(result.absolute_delta, 20.0)

    def test_zero_baseline_uses_absolute_tolerance(self):
        result = classify("revenue", "finance", Decimal("0"), Decimal("0.5"), self.thresholds)
        self.assertEqual(result.status, "certified")

    def test_threshold_file_drives_evaluation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "thresholds.json"
            path.write_text(json.dumps(self.thresholds))
            result = evaluate_rows([("revenue", "finance", Decimal("100"), Decimal("102"))], path)
            self.assertEqual(result[0].status, "drifted")
