from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.paper_baseline_suite_batch import build_paper_baseline_suite_batch_report


class PaperBaselineSuiteBatchScopeGuardTests(unittest.TestCase):
    def test_feature_067_prerequisite_gate(self) -> None:
        import src.analysis.paper_baseline_suite_batch.runner as runner

        with mock.patch.object(runner, "_feature_067_verified", return_value=False):
            payload = build_paper_baseline_suite_batch_report().to_dict()
        self.assertIn("feature_067_prerequisite_blocked", payload["remaining_blockers"])
        self.assertNotEqual(payload["final_verdict"], "paper_baseline_suite_batch_passed")


if __name__ == "__main__":
    unittest.main()

