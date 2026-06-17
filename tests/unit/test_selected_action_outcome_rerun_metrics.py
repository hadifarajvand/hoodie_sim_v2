from __future__ import annotations

import unittest

from src.analysis.selected_action_outcome_evidence_rerun import build_selected_action_outcome_evidence_rerun_report


class SelectedActionOutcomeEvidenceRerunMetricsTests(unittest.TestCase):
    def test_feature_051_readiness_gate_and_population_counts(self) -> None:
        payload = build_selected_action_outcome_evidence_rerun_report().to_dict()
        self.assertTrue(payload["feature_051_trace_readiness_verified"])
        self.assertGreater(payload["selected_action_family_evidence_summary"]["selected_action_count"], 0)
        self.assertEqual(
            payload["selected_action_family_evidence_summary"]["selected_action_count"],
            payload["selected_action_family_evidence_summary"]["selected_local_count"]
            + payload["selected_action_family_evidence_summary"]["selected_horizontal_count"]
            + payload["selected_action_family_evidence_summary"]["selected_vertical_count"],
        )
        self.assertEqual(payload["selected_action_family_evidence_status"], "available")
        self.assertEqual(payload["selected_action_to_task_join_status"], "available")
        self.assertEqual(payload["per_action_outcome_evidence_status"], "partial")
        self.assertFalse(payload["feature_049_can_be_rerun"])
        self.assertEqual(payload["recommended_next_feature"], "terminal outcome join repair continuation")

    def test_denominator_and_zero_handling(self) -> None:
        payload = build_selected_action_outcome_evidence_rerun_report().to_dict()
        matrix = payload["per_action_outcome_join_summary"]
        rows = {row["action_family"]: row for row in payload["per_action_outcome_matrix"]["per_strategy_seed_selected_action_family_matrix"]}
        local = rows["local"]
        self.assertEqual(local["selected_action_completion_rate"], local["selected_action_completed_count"] / local["selected_action_count"])
        self.assertEqual(local["selected_action_drop_rate"], local["selected_action_dropped_count"] / local["selected_action_count"])
        self.assertEqual(local["selected_action_pending_rate"], local["selected_action_pending_count"] / local["selected_action_count"])
        for family in ("horizontal", "vertical"):
            row = rows[family]
            self.assertEqual(row["selected_action_count"], 0)
            self.assertIsNone(row["selected_action_completion_rate"])
            self.assertIsNone(row["selected_action_drop_rate"])
            self.assertIsNone(row["selected_action_pending_rate"])
            self.assertEqual(row["selected_action_completed_count"] + row["selected_action_dropped_count"] + row["selected_action_pending_count"], row["selected_action_count"])

    def test_legal_but_unselected_consistency(self) -> None:
        payload = build_selected_action_outcome_evidence_rerun_report().to_dict()
        summary = payload["legal_but_unselected_consistency_summary"]
        self.assertTrue(summary["legal_but_unselected_consistency_verified"])
        self.assertGreaterEqual(summary["legal_but_unselected_local_count"], 0)
        self.assertGreaterEqual(summary["legal_but_unselected_horizontal_count"], 0)
        self.assertGreaterEqual(summary["legal_but_unselected_vertical_count"], 0)


if __name__ == "__main__":
    unittest.main()
