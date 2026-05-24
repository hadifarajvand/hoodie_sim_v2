from __future__ import annotations

import unittest

from src.analysis.selected_action_outcome_evidence_rerun import build_selected_action_outcome_evidence_rerun_report


class SelectedActionOutcomeEvidenceRerunSchemaTests(unittest.TestCase):
    def test_top_level_contract(self) -> None:
        payload = build_selected_action_outcome_evidence_rerun_report().to_dict()
        for key in [
            "feature_id",
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
            "feature_051_trace_readiness_verified",
            "selected_action_family_evidence_summary",
            "selected_action_to_task_join_summary",
            "per_action_outcome_join_summary",
            "per_action_outcome_matrix",
            "legal_but_unselected_consistency_summary",
            "exposure_matrix_internal_consistency_summary",
            "feature_049_unblock_assessment",
            "behavior_equivalence_summary",
            "evidence_population_summary",
            "selected_action_family_evidence_status",
            "selected_action_to_task_join_status",
            "per_action_outcome_evidence_status",
            "behavior_equivalence_passed",
            "feature_049_can_be_rerun",
            "feature_049_remaining_blockers",
            "recommended_next_feature",
            "no_runtime_repair_performed",
            "final_verdict",
        ]:
            self.assertIn(key, payload)
        self.assertEqual(payload["per_action_outcome_evidence_status"], payload["per_action_outcome_join_summary"]["per_action_outcome_evidence_status"])
        self.assertEqual(payload["feature_049_unblock_assessment"]["per_action_outcome_evidence_status"], payload["per_action_outcome_evidence_status"])


if __name__ == "__main__":
    unittest.main()
