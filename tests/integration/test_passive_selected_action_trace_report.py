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
        self.assertFalse(payload["evidence_readiness_for_feature_050_rerun"])
        self.assertTrue(payload["remaining_blockers"])


if __name__ == "__main__":
    unittest.main()
