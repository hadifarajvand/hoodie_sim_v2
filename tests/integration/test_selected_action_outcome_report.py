from __future__ import annotations

import unittest

from src.analysis.selected_action_family_per_action_outcome_evidence import build_selected_action_outcome_evidence_report


class SelectedActionOutcomeReportIntegrationTest(unittest.TestCase):
    def test_top_level_contract(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        for key in [
            "feature_id",
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
            "selected_action_family_evidence_status",
            "selected_action_to_task_join_status",
            "per_action_outcome_evidence_status",
            "behavior_equivalence_passed",
            "feature_049_can_be_rerun",
            "feature_049_remaining_blockers",
            "feature_049_unblock_assessment",
            "final_verdict",
            "recommended_next_feature",
        ]:
            self.assertIn(key, payload)

    def test_rerun_requires_available_statuses(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        if payload["feature_049_can_be_rerun"]:
            self.assertEqual(payload["selected_action_family_evidence_status"], "available")
            self.assertEqual(payload["selected_action_to_task_join_status"], "available")
            self.assertEqual(payload["per_action_outcome_evidence_status"], "available")


if __name__ == "__main__":
    unittest.main()
