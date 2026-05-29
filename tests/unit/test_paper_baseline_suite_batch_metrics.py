from __future__ import annotations

import unittest

from src.analysis.paper_baseline_suite_batch import build_paper_baseline_suite_batch_report


class PaperBaselineSuiteBatchMetricsTests(unittest.TestCase):
    def test_metrics_flags(self) -> None:
        payload = build_paper_baseline_suite_batch_report().to_dict()
        self.assertTrue(payload["legal_action_compliance_verified"])
        self.assertEqual(payload["baseline_count"], 6)


if __name__ == "__main__":
    unittest.main()

