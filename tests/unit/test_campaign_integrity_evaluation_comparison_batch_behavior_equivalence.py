from __future__ import annotations

import unittest

from src.analysis.campaign_integrity_evaluation_comparison_batch import build_campaign_integrity_evaluation_comparison_batch_report


class CampaignIntegrityEvaluationComparisonBatchBehaviorEquivalenceTests(unittest.TestCase):
    def test_prerequisite_tag_names_are_unique(self) -> None:
        payload = build_campaign_integrity_evaluation_comparison_batch_report().to_dict()
        names = [entry["name"] for entry in payload["prerequisite_tags_verified"]]
        self.assertEqual(len(names), len(set(names)))

    def test_forbidden_claims_remain_false(self) -> None:
        safety = build_campaign_integrity_evaluation_comparison_batch_report().to_dict()["safety_summary"]
        self.assertTrue(safety["no_paper_reproduction_claim"])
        self.assertTrue(safety["no_unsupported_superiority_claim"])
        self.assertTrue(safety["no_uncontrolled_campaign_loop"])


if __name__ == "__main__":
    unittest.main()
