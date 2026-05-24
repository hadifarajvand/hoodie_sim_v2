from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.passive_selected_action_trace_repair import build_passive_selected_action_trace_repair_report, run_passive_selected_action_trace_repair


class PassiveSelectedActionTraceReportIntegrationTest(unittest.TestCase):
    def test_report_top_level_contract(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        for key in [
            "feature_id",
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
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
            "behavior_equivalence_passed",
            "selected_action_family_evidence_status",
            "selected_action_to_task_join_status",
            "terminal_outcome_join_status",
            "per_action_outcome_join_readiness",
            "selected_action_trace_schema",
            "selected_action_trace_emission_summary",
            "selected_action_family_trace_summary",
            "selected_action_to_task_join_summary",
            "terminal_outcome_join_key_summary",
            "behavior_equivalence_summary",
            "evidence_readiness_for_feature_050_rerun",
            "remaining_blockers",
            "recommended_next_feature",
            "final_verdict",
        ]:
            self.assertIn(key, payload)
        self.assertEqual(payload["decision_opportunity_count"], payload["selected_action_trace_record_count"])
        self.assertEqual(payload["selected_action_family_trace_record_count"], payload["decision_opportunity_count"])
        self.assertEqual(payload["selected_action_to_task_join_key_count"], payload["decision_opportunity_count"])
        self.assertEqual(payload["terminal_outcome_join_key_count"], payload["decision_opportunity_count"])
        self.assertEqual(payload["selected_action_trace_coverage_ratio"], 1.0)
        self.assertEqual(payload["selected_action_family_coverage_ratio"], 1.0)
        self.assertEqual(payload["selected_action_to_task_join_coverage_ratio"], 1.0)
        self.assertEqual(payload["terminal_outcome_join_key_coverage_ratio"], 1.0)
        self.assertEqual(payload["selected_action_family_evidence_status"], "available")
        self.assertEqual(payload["selected_action_to_task_join_status"], "available")
        self.assertEqual(payload["terminal_outcome_join_status"], "available")
        self.assertEqual(payload["per_action_outcome_join_readiness"], "ready")
        self.assertTrue(payload["behavior_equivalence_passed"])
        self.assertTrue(payload["evidence_readiness_for_feature_050_rerun"])
        self.assertEqual(payload["recommended_next_feature"], "Feature 052 — Selected-Action Outcome Evidence Rerun")
        self.assertEqual(payload["final_verdict"], "passive_selected_action_trace_ready_for_feature_050_rerun")

    def test_report_written_to_artifacts(self) -> None:
        report = run_passive_selected_action_trace_repair()
        json_path = Path("artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.json")
        md_path = Path("artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.md")
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], report.feature_id)

    def test_current_report_remains_blocked_on_committed_artifacts(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        self.assertTrue(payload["evidence_readiness_for_feature_050_rerun"])
        self.assertFalse(payload["remaining_blockers"])


if __name__ == "__main__":
    unittest.main()
