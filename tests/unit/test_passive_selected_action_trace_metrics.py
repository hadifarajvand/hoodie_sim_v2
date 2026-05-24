from __future__ import annotations

import unittest

from src.analysis.passive_selected_action_trace_repair import build_passive_selected_action_trace_repair_report
from src.environment.gym_adapter import HoodieGymEnvironment


class PassiveSelectedActionTraceMetricsTests(unittest.TestCase):
    def test_report_exposes_canonical_readiness_fields(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        for key in [
            "selected_action_family_evidence_status",
            "selected_action_to_task_join_status",
            "terminal_outcome_join_status",
            "per_action_outcome_join_readiness",
            "evidence_readiness_for_feature_050_rerun",
            "remaining_blockers",
        ]:
            self.assertIn(key, payload)
        self.assertIn(payload["selected_action_family_evidence_status"], {"available", "partial", "unavailable"})
        self.assertIn(payload["selected_action_to_task_join_status"], {"available", "partial", "unavailable"})
        self.assertIn(payload["terminal_outcome_join_status"], {"available", "partial", "unavailable"})
        self.assertIn(payload["per_action_outcome_join_readiness"], {"ready", "partial", "unavailable"})
        self.assertEqual(payload["selected_action_family_evidence_status"], payload["selected_action_family_trace_summary"]["selected_action_family_evidence_status"])
        self.assertEqual(payload["selected_action_to_task_join_status"], payload["selected_action_to_task_join_summary"]["selected_action_to_task_join_status"])
        self.assertEqual(payload["terminal_outcome_join_status"], payload["terminal_outcome_join_key_summary"]["terminal_outcome_join_status"])

    def test_report_remains_blocked_when_current_committed_evidence_is_unavailable(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        self.assertFalse(payload["evidence_readiness_for_feature_050_rerun"])
        self.assertTrue(payload["remaining_blockers"])
        self.assertEqual(payload["final_verdict"], "selected_action_family_trace_incomplete")
        self.assertEqual(payload["recommended_next_feature"], "selected-action family trace repair continuation")

    def test_selected_action_family_mapping_returns_unknown_for_unrecognized_actions(self) -> None:
        self.assertEqual(HoodieGymEnvironment._selected_action_family("bogus"), "unknown")
        self.assertEqual(HoodieGymEnvironment._selected_action_family("compute_local"), "local")
        self.assertEqual(HoodieGymEnvironment._selected_action_family("offload_horizontal"), "horizontal")


if __name__ == "__main__":
    unittest.main()
