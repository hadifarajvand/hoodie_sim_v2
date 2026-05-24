from __future__ import annotations

import unittest

from src.analysis.selected_action_outcome_evidence_rerun import build_selected_action_outcome_evidence_rerun_report


class SelectedActionOutcomeEvidenceRerunIntegrationTest(unittest.TestCase):
    def test_committed_prior_artifact_gates_and_feature_049_ready_path(self) -> None:
        payload = build_selected_action_outcome_evidence_rerun_report().to_dict()
        self.assertTrue(all(item["verified"] for item in payload["prior_feature_gates_verified"]))
        self.assertTrue(payload["feature_049_can_be_rerun"])
        self.assertEqual(payload["final_verdict"], "selected_action_outcome_evidence_ready_for_feature_049_rerun")


if __name__ == "__main__":
    unittest.main()
