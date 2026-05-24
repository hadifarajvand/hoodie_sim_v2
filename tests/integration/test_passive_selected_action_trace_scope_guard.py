from __future__ import annotations

import unittest

from src.analysis.passive_selected_action_trace_repair import build_passive_selected_action_trace_repair_report


class PassiveSelectedActionTraceScopeGuardIntegrationTest(unittest.TestCase):
    def test_readiness_fields_must_match_summary_copies(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        self.assertEqual(payload["selected_action_family_evidence_status"], payload["selected_action_family_trace_summary"]["selected_action_family_evidence_status"])
        self.assertEqual(payload["selected_action_to_task_join_status"], payload["selected_action_to_task_join_summary"]["selected_action_to_task_join_status"])
        self.assertEqual(payload["terminal_outcome_join_status"], payload["terminal_outcome_join_key_summary"]["terminal_outcome_join_status"])
        self.assertEqual(payload["per_action_outcome_join_readiness"], "unavailable")
        self.assertFalse(payload["evidence_readiness_for_feature_050_rerun"])
        self.assertTrue(payload["remaining_blockers"])

    def test_no_dirty_worktree_sensitive_prior_feature_test_is_needed(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        self.assertEqual(payload["selected_action_family_evidence_status"], "unavailable")
        self.assertEqual(payload["selected_action_to_task_join_status"], "unavailable")
        self.assertEqual(payload["terminal_outcome_join_status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
