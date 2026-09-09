import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ArtifactTests(unittest.TestCase):
    def test_committed_run_completed(self):
        summary = json.loads((ROOT / "reports/pipeline-summary.json").read_text())
        self.assertEqual(summary["status"], "passed")
        self.assertEqual(summary["records"]["orders"], 50000)
        self.assertEqual(summary["records"]["hmda_applications"], 2800000)
        self.assertEqual(summary["governed_metrics"], 25)
        self.assertEqual(summary["dax_measures_compared"], 25)
        self.assertEqual(summary["legacy_conflicts_resolved"], 3)
        self.assertEqual(summary["quality_failures"], 0)

    def test_dashboard_and_screenshot_are_nonempty(self):
        self.assertGreater((ROOT / "dashboard/metric-governance-dashboard.html").stat().st_size, 1000)
        self.assertGreater((ROOT / "screenshots/metric-governance-dashboard.png").stat().st_size, 50000)

    def test_registry_and_dax_are_complete(self):
        registry = json.loads((ROOT / "registry/metrics.json").read_text())
        measures = [line for line in (ROOT / "bi/powerbi-measures.dax").read_text().splitlines() if " = " in line]
        self.assertEqual(len(registry["metrics"]), 25)
        self.assertEqual(len(measures), 25)
        self.assertEqual(len({metric["owner"] for metric in registry["metrics"]}), 4)
