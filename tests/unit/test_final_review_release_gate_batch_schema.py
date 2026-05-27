from __future__ import annotations

import unittest

from src.analysis.final_review_release_gate_batch import build_final_review_release_gate_batch_report
from src.analysis.final_review_release_gate_batch.config import FEATURE_ID, REQUIRED_TOP_LEVEL_FIELDS
from src.analysis.final_review_release_gate_batch.model import FinalReviewReleaseGateBatchReport


class FinalReviewReleaseGateBatchSchemaTests(unittest.TestCase):
    def test_report_has_required_fields_and_pass_verdict(self) -> None:
        payload = build_final_review_release_gate_batch_report().to_dict()
        for key in REQUIRED_TOP_LEVEL_FIELDS:
            self.assertIn(key, payload)
        self.assertEqual(payload["feature_id"], FEATURE_ID)
        self.assertEqual(payload["final_verdict"], "final_review_release_gate_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])

    def test_pass_with_blockers_is_rejected(self) -> None:
        payload = build_final_review_release_gate_batch_report().to_dict()
        payload["remaining_blockers"] = ["feature_063_prerequisite_blocked"]
        payload["final_verdict"] = "final_review_release_gate_batch_passed"
        with self.assertRaises(ValueError):
            FinalReviewReleaseGateBatchReport(**payload)


if __name__ == "__main__":
    unittest.main()
