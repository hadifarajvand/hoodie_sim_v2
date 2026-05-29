from __future__ import annotations

import unittest

from src.analysis.paper_baseline_suite_batch import build_paper_baseline_suite_batch_report


class PaperBaselineSuiteBatchBehaviorEquivalenceTests(unittest.TestCase):
    def test_no_claim_inflation(self) -> None:
        payload = build_paper_baseline_suite_batch_report().to_dict()
        self.assertEqual(payload["implemented_baselines"], ["RO", "FLC", "VO", "HO", "BCO", "MLEO"])
        self.assertFalse(payload["remaining_blockers"])


if __name__ == "__main__":
    unittest.main()

