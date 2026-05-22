from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_review import build_exposure_matrix_report


class ExposureMatrixReviewIntegrationTests(unittest.TestCase):
    def test_matrix_completeness_and_routing_for_missing_legal_evidence(self) -> None:
        report = build_exposure_matrix_report()
        payload = report.to_dict()
        self.assertEqual(report.final_verdict, "exposure_matrix_incomplete_requires_legality_evidence")
        self.assertEqual(report.recommended_next_feature, "legality evidence expansion before Feature 048")
        self.assertEqual(payload["legal_action_evidence_source"], "unavailable_in_committed_artifacts")
        self.assertEqual(payload["legal_action_evidence_coverage_ratio"], 0.0)
        self.assertEqual(payload["matrix_completeness_summary"]["status"], "incomplete")
        self.assertTrue(payload["load_vs_exposure_summary"]["load_pressure_explains_completion_weakness"])
        self.assertEqual(payload["exposure_matrix_population"], "feature_045_full_reconstruction_summary_for_load_metrics_only")

    def test_prior_feature_gates_include_037_through_046(self) -> None:
        report = build_exposure_matrix_report()
        features = [entry["feature"] for entry in report.prior_feature_gates_verified]
        self.assertEqual(features, ["037", "038", "039", "040", "041", "042", "043", "044", "045", "046"])

    def test_per_strategy_seed_matrix_covers_required_grid_or_marks_unavailable(self) -> None:
        report = build_exposure_matrix_report()
        rows = report.per_strategy_seed_matrix
        self.assertEqual(len(rows), 15)
        pairs = {(row["strategy"], row["seed"]) for row in rows}
        self.assertEqual(
            pairs,
            {
                ("environment_default_policy_probe", 0),
                ("environment_default_policy_probe", 1),
                ("environment_default_policy_probe", 2),
                ("force_local_legal_probe", 0),
                ("force_local_legal_probe", 1),
                ("force_local_legal_probe", 2),
                ("force_horizontal_legal_probe", 0),
                ("force_horizontal_legal_probe", 1),
                ("force_horizontal_legal_probe", 2),
                ("force_vertical_legal_probe", 0),
                ("force_vertical_legal_probe", 1),
                ("force_vertical_legal_probe", 2),
                ("mixed_legal_round_robin_probe", 0),
                ("mixed_legal_round_robin_probe", 1),
                ("mixed_legal_round_robin_probe", 2),
            },
        )
        self.assertTrue(all(row["selected_illegal_action_count"] is None for row in rows))


if __name__ == "__main__":
    unittest.main()
