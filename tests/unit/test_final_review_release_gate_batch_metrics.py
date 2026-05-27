from __future__ import annotations

import unittest

from src.analysis.final_review_release_gate_batch import build_final_review_release_gate_batch_report


class FinalReviewReleaseGateBatchMetricsTests(unittest.TestCase):
    def test_feature_063_artifacts_are_verified_and_no_release_tag_is_created(self) -> None:
        payload = build_final_review_release_gate_batch_report().to_dict()
        self.assertTrue(payload["feature_063_verified"])
        self.assertTrue(payload["artifact_completeness_summary"]["feature_063_final_exports_exist"])
        self.assertTrue(payload["safety_summary"]["no_release_tag_created"])

    def test_claim_boundary_and_recommendation_are_explicit(self) -> None:
        payload = build_final_review_release_gate_batch_report().to_dict()
        self.assertTrue(payload["claim_boundary_review_summary"]["no_paper_reproduction_claim"])
        self.assertEqual(payload["recommended_next_feature"], "Release tag creation or thesis/paper writing workflow")


if __name__ == "__main__":
    unittest.main()
