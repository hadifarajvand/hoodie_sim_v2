from __future__ import annotations

import unittest

from src.analysis.paper_baseline_suite_batch import build_paper_baseline_suite_batch_report


class PaperBaselineSuiteBatchIntegrationTests(unittest.TestCase):
    def test_passes(self) -> None:
        payload = build_paper_baseline_suite_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "paper_baseline_suite_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])


if __name__ == "__main__":
    unittest.main()

