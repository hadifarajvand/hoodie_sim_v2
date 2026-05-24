from __future__ import annotations

import unittest

from src.analysis.selected_action_family_per_action_outcome_evidence import build_selected_action_outcome_evidence_report


class SelectedActionOutcomeEvidenceSchemaTest(unittest.TestCase):
    def test_required_fields_exist(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        for key in [
            "selected_action_family_evidence_status",
            "selected_action_to_task_join_status",
            "per_action_outcome_evidence_status",
            "behavior_equivalence_passed",
            "feature_049_can_be_rerun",
            "feature_049_remaining_blockers",
            "feature_049_unblock_assessment",
        ]:
            self.assertIn(key, payload)

    def test_nested_assessment_matches_top_level(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        nested = payload["feature_049_unblock_assessment"]
        self.assertEqual(payload["selected_action_family_evidence_status"], nested["selected_action_family_evidence_status"])
        self.assertEqual(payload["selected_action_to_task_join_status"], nested["selected_action_to_task_join_status"])
        self.assertEqual(payload["per_action_outcome_evidence_status"], nested["per_action_outcome_evidence_status"])
        self.assertEqual(payload["behavior_equivalence_passed"], nested["behavior_equivalence_passed"])
        self.assertEqual(payload["feature_049_can_be_rerun"], nested["feature_049_can_be_rerun"])
        self.assertEqual(payload["feature_049_remaining_blockers"], nested["feature_049_remaining_blockers"])


if __name__ == "__main__":
    unittest.main()
