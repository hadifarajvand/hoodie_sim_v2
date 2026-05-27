from __future__ import annotations

import unittest

from src.analysis.final_review_release_gate_batch import build_final_review_release_gate_batch_report


class FinalReviewReleaseGateBatchBehaviorEquivalenceTests(unittest.TestCase):
    def test_source_mappings_and_prerequisite_names_are_unique(self) -> None:
        payload = build_final_review_release_gate_batch_report().to_dict()
        self.assertTrue(payload["repository_state_audit_summary"]["release_evidence_mapped_to_source"])
        names = [entry["name"] for entry in payload["prerequisite_tags_verified"]]
        self.assertEqual(len(names), len(set(names)))

    def test_non_claims_are_preserved_in_handoff(self) -> None:
        payload = build_final_review_release_gate_batch_report().to_dict()
        self.assertIn("thesis/paper writing workflow", payload["handoff_summary"]["next_work_recommendation"])


if __name__ == "__main__":
    unittest.main()
