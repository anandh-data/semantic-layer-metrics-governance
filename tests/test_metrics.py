import unittest
from metric_hub.core import drift_report, evaluate


class MetricTests(unittest.TestCase):
    def test_evaluates_governed_expression(self):
        self.assertEqual(evaluate("gross - refunds", {"gross": 100, "refunds": 4}), 96)

    def test_rejects_function_calls(self):
        with self.assertRaises(ValueError):
            evaluate("round(gross)", {"gross": 100})

    def test_flags_divergence(self):
        report = drift_report({"revenue": 100}, {"revenue": 90})
        self.assertTrue(report[0]["drifted"])

    def test_accepts_value_within_tolerance(self):
        report = drift_report({"revenue": 100}, {"revenue": 100.01})
        self.assertFalse(report[0]["drifted"])


if __name__ == "__main__":
    unittest.main()
