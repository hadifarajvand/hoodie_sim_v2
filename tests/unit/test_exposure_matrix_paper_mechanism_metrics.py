from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_paper_mechanism_alignment import build_exposure_matrix_paper_mechanism_report


class ExposureMatrixPaperMechanismMetricsTests(unittest.TestCase):
    def test_selected_action_family_evidence_status_required(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        summary = payload["exposure_matrix_rerun_summary"]
        self.assertEqual(summary["decision_opportunity_count"], 1650)
        self.assertEqual(payload["selected_action_family_evidence_status"], "unavailable")
        self.assertFalse(payload["selected_action_count_consistency_verified"])
        self.assertFalse(payload["legal_but_unselected_consistency_verified"])
        self.assertFalse(payload["exposure_matrix_internal_consistency_verified"])
        self.assertIsNone(summary["selected_local_count"])
        self.assertIsNone(summary["selected_horizontal_count"])
        self.assertIsNone(summary["selected_vertical_count"])
        self.assertEqual(payload["selected_illegal_action_summary"]["selected_illegal_action_count"], 0)
        self.assertEqual(payload["selected_illegal_action_summary"]["selected_illegal_action_rate"], 0.0)

    def test_per_action_outcome_evidence_status_required(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        summary = payload["exposure_matrix_rerun_summary"]
        self.assertEqual(payload["per_action_outcome_evidence_status"], "unavailable")
        self.assertIsNone(summary["per_action_completion_rate"]["local"])
        self.assertIsNone(summary["per_action_completion_rate"]["horizontal"])
        self.assertIsNone(summary["per_action_completion_rate"]["vertical"])
        self.assertIsNone(summary["per_action_drop_rate"]["local"])
        self.assertIsNone(summary["per_action_drop_rate"]["horizontal"])
        self.assertIsNone(summary["per_action_drop_rate"]["vertical"])
        self.assertIsNone(summary["per_action_pending_rate"]["local"])
        self.assertIsNone(summary["per_action_pending_rate"]["horizontal"])
        self.assertIsNone(summary["per_action_pending_rate"]["vertical"])
        self.assertEqual(payload["training_readiness_decision"]["final_verdict"], "insufficient_legality_or_trace_evidence")
        self.assertEqual(payload["training_readiness_decision"]["recommended_next_feature"], "selected-action family evidence expansion before training")

    def test_unavailable_selected_family_does_not_fake_zero_counts(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        summary = report.to_dict()["exposure_matrix_rerun_summary"]
        for key in ("local", "horizontal", "vertical"):
            self.assertIsNone(summary["legal_but_unselected_by_action"][key])
            self.assertIsNone(summary["per_action_completion_rate"][key])
            self.assertIsNone(summary["per_action_drop_rate"][key])
            self.assertIsNone(summary["per_action_pending_rate"][key])

    def test_unavailable_per_action_outcomes_do_not_fake_zero_rates(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        summary = report.to_dict()["exposure_matrix_rerun_summary"]
        for rates in (summary["per_action_completion_rate"], summary["per_action_drop_rate"], summary["per_action_pending_rate"]):
            for key in ("local", "horizontal", "vertical"):
                self.assertIsNone(rates[key])

    def test_selected_count_consistency_blocks_feature_050(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        self.assertFalse(payload["selected_action_count_consistency_verified"])
        self.assertEqual(payload["training_readiness_decision"]["final_verdict"], "insufficient_legality_or_trace_evidence")
        self.assertNotEqual(payload["training_readiness_decision"]["recommended_next_feature"], "Feature 050 — DDQN Training Contract Bundle")

    def test_legal_but_unselected_consistency_blocks_feature_050(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        self.assertFalse(payload["legal_but_unselected_consistency_verified"])
        self.assertEqual(payload["training_readiness_decision"]["final_verdict"], "insufficient_legality_or_trace_evidence")
        self.assertNotEqual(payload["training_readiness_decision"]["recommended_next_feature"], "Feature 050 — DDQN Training Contract Bundle")

    def test_exposure_matrix_internal_consistency_required(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        self.assertFalse(payload["exposure_matrix_internal_consistency_verified"])
        self.assertEqual(payload["training_readiness_decision"]["final_verdict"], "insufficient_legality_or_trace_evidence")
        self.assertEqual(payload["training_readiness_decision"]["recommended_next_feature"], "selected-action family evidence expansion before training")

    def test_feature_050_not_recommended_from_placeholder_exposure_matrix(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        self.assertNotEqual(payload["training_readiness_decision"]["readiness_state"], "ready_for_feature_050")
        self.assertNotEqual(payload["training_readiness_decision"]["final_verdict"], "paper_mechanism_alignment_ready_for_training_contract")
        self.assertNotEqual(payload["training_readiness_decision"]["recommended_next_feature"], "Feature 050 — DDQN Training Contract Bundle")

    def test_report_final_verdict_blocks_training_when_exposure_evidence_unavailable(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        decision = payload["training_readiness_decision"]
        self.assertEqual(decision["readiness_state"], "blocked_by_insufficient_evidence")
        self.assertEqual(decision["final_verdict"], "insufficient_legality_or_trace_evidence")
        self.assertEqual(decision["recommended_next_feature"], "selected-action family evidence expansion before training")
        self.assertFalse(payload["selected_action_count_consistency_verified"])
        self.assertFalse(payload["legal_but_unselected_consistency_verified"])
        self.assertFalse(payload["exposure_matrix_internal_consistency_verified"])


if __name__ == "__main__":
    unittest.main()
