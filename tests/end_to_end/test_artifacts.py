import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ArtifactTests(unittest.TestCase):
    def test_committed_run_completed(self):
        summary = json.loads((ROOT / "reports/pipeline-summary.json").read_text())
        self.assertEqual(summary["status"], "passed")
        self.assertEqual(summary["records"]["orders"], 50000)
        self.assertEqual(summary["quality_failures"], 0)

    def test_dashboard_and_screenshot_are_nonempty(self):
        self.assertGreater((ROOT / "dashboard/metric-governance-dashboard.html").stat().st_size, 1000)
        self.assertGreater((ROOT / "screenshots/metric-governance-dashboard.png").stat().st_size, 50000)
