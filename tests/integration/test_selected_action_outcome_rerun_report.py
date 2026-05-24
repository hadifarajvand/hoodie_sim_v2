from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.selected_action_outcome_evidence_rerun import build_selected_action_outcome_evidence_rerun_report, run_selected_action_outcome_evidence_rerun


class SelectedActionOutcomeEvidenceRerunReportIntegrationTest(unittest.TestCase):
    def test_report_written_to_artifacts(self) -> None:
        report = run_selected_action_outcome_evidence_rerun()
        json_path = Path("artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.json")
        md_path = Path("artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.md")
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], report.feature_id)

    def test_report_contract_ready_state(self) -> None:
        payload = build_selected_action_outcome_evidence_rerun_report().to_dict()
        self.assertTrue(payload["feature_049_can_be_rerun"])
        self.assertFalse(payload["feature_049_remaining_blockers"])
        self.assertEqual(payload["recommended_next_feature"], "Feature 053 — Exposure Matrix Paper Mechanism Rerun with Outcome Evidence")
        self.assertEqual(payload["feature_049_unblock_assessment"]["recommended_next_feature"], payload["recommended_next_feature"])


if __name__ == "__main__":
    unittest.main()
