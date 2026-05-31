from __future__ import annotations

import unittest

from src.analysis.controlled_evaluation_batch_readiness.report import build_feature_073_report, build_controlled_evaluation_scenarios


class ControlledEvaluationBatchReadinessReportTests(unittest.TestCase):
    def test_feature_073_report_passes_only_when_all_gates_pass(self) -> None:
        report = build_feature_073_report()
        self.assertTrue(report.passed)
        self.assertEqual(report.status, "controlled_evaluation_batch_readiness_ready")
        self.assertEqual(report.feature_name, "Feature 073 - Controlled Evaluation Batch Readiness")
        self.assertEqual(report.recommended_next_feature, "Feature 074 - Baseline Policy Comparative Evaluation Readiness")
        self.assertIn("controlled evaluation batch readiness", report.paper_claim_boundary.lower())
        self.assertIn("No final evaluation claim is made.", report.paper_claim_boundary)
        self.assertIn("No performance superiority claim is made.", report.paper_claim_boundary)
        self.assertIn("No full paper reproduction claim is made.", report.paper_claim_boundary)

    def test_feature_073_report_includes_prior_regression_evidence(self) -> None:
        report = build_feature_073_report()
        self.assertTrue(report.feature_068r_regression_status.passed)
        self.assertTrue(report.feature_069_regression_status.passed)
        self.assertTrue(report.feature_070_regression_status.passed)
        self.assertTrue(report.feature_071_regression_status.passed)
        self.assertTrue(report.feature_072_regression_status.passed)
        self.assertIn("Feature 072", report.feature_072_regression_status.summary)

    def test_report_uses_distinct_expected_and_actual_metric_objects(self) -> None:
        scenarios = build_controlled_evaluation_scenarios()
        for scenario in scenarios:
            self.assertIsNot(scenario.expected_metrics, scenario.actual_metrics)
            self.assertTrue(scenario.passed)
