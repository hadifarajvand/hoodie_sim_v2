from __future__ import annotations

import unittest

from src.analysis.paper_baseline_suite_batch import build_paper_baseline_suite_batch_report


class PaperBaselineSuiteBatchSchemaTests(unittest.TestCase):
    def test_report_schema(self) -> None:
        payload = build_paper_baseline_suite_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "paper_baseline_suite_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertTrue(payload["deterministic_repeatability_proven"])


if __name__ == "__main__":
    unittest.main()

