from __future__ import annotations

import unittest

from src.analysis.passive_selected_action_trace_repair import build_passive_selected_action_trace_repair_report
from src.environment.gym_adapter import HoodieGymEnvironment


class PassiveSelectedActionTraceMetricsTests(unittest.TestCase):
    def test_report_exposes_canonical_readiness_fields(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        for key in [
            "decision_opportunity_count",
            "selected_action_trace_record_count",
            "selected_action_family_trace_record_count",
            "selected_action_to_task_join_key_count",
            "terminal_outcome_join_key_count",
            "selected_action_trace_coverage_ratio",
            "selected_action_family_coverage_ratio",
            "selected_action_to_task_join_coverage_ratio",
            "terminal_outcome_join_key_coverage_ratio",
            "missing_selected_action_trace_count",
            "missing_selected_action_family_count",
            "missing_selected_action_to_task_join_key_count",
            "missing_terminal_outcome_join_key_count",
            "selected_action_family_evidence_status",
            "selected_action_to_task_join_status",
            "terminal_outcome_join_status",
            "per_action_outcome_join_readiness",
            "evidence_readiness_for_feature_050_rerun",
            "remaining_blockers",
        ]:
            self.assertIn(key, payload)
        self.assertGreater(payload["decision_opportunity_count"], 0)
        self.assertEqual(payload["selected_action_trace_record_count"], payload["decision_opportunity_count"])
        self.assertEqual(payload["selected_action_family_trace_record_count"], payload["decision_opportunity_count"])
        self.assertEqual(payload["selected_action_to_task_join_key_count"], payload["decision_opportunity_count"])
        self.assertEqual(payload["terminal_outcome_join_key_count"], payload["decision_opportunity_count"])
        self.assertEqual(payload["selected_action_trace_coverage_ratio"], 1.0)
        self.assertEqual(payload["selected_action_family_coverage_ratio"], 1.0)
        self.assertEqual(payload["selected_action_to_task_join_coverage_ratio"], 1.0)
        self.assertEqual(payload["terminal_outcome_join_key_coverage_ratio"], 1.0)
        self.assertEqual(payload["missing_selected_action_trace_count"], 0)
        self.assertEqual(payload["missing_selected_action_family_count"], 0)
        self.assertEqual(payload["missing_selected_action_to_task_join_key_count"], 0)
        self.assertEqual(payload["missing_terminal_outcome_join_key_count"], 0)
        self.assertIn(payload["selected_action_family_evidence_status"], {"available", "partial", "unavailable"})
        self.assertIn(payload["selected_action_to_task_join_status"], {"available", "partial", "unavailable"})
        self.assertIn(payload["terminal_outcome_join_status"], {"available", "partial", "unavailable"})
        self.assertEqual(payload["selected_action_family_evidence_status"], "available")
        self.assertEqual(payload["selected_action_to_task_join_status"], "available")
        self.assertEqual(payload["terminal_outcome_join_status"], "available")
        self.assertEqual(payload["per_action_outcome_join_readiness"], "ready")
        self.assertEqual(payload["selected_action_family_evidence_status"], payload["selected_action_family_trace_summary"]["selected_action_family_evidence_status"])
        self.assertEqual(payload["selected_action_to_task_join_status"], payload["selected_action_to_task_join_summary"]["selected_action_to_task_join_status"])
        self.assertEqual(payload["terminal_outcome_join_status"], payload["terminal_outcome_join_key_summary"]["terminal_outcome_join_status"])

    def test_report_becomes_ready_when_runtime_trace_population_is_complete(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        self.assertTrue(payload["evidence_readiness_for_feature_050_rerun"])
        self.assertFalse(payload["remaining_blockers"])
        self.assertEqual(payload["final_verdict"], "passive_selected_action_trace_ready_for_feature_050_rerun")
        self.assertEqual(payload["recommended_next_feature"], "Feature 052 — Selected-Action Outcome Evidence Rerun")
        self.assertEqual(payload["selected_action_family_evidence_status"], "available")
        self.assertEqual(payload["selected_action_to_task_join_status"], "available")
        self.assertEqual(payload["terminal_outcome_join_status"], "available")
        self.assertEqual(payload["per_action_outcome_join_readiness"], "ready")

    def test_selected_action_family_mapping_returns_unknown_for_unrecognized_actions(self) -> None:
        self.assertEqual(HoodieGymEnvironment._selected_action_family("bogus"), "unknown")
        self.assertEqual(HoodieGymEnvironment._selected_action_family("compute_local"), "local")
        self.assertEqual(HoodieGymEnvironment._selected_action_family("offload_horizontal"), "horizontal")


if __name__ == "__main__":
    unittest.main()
