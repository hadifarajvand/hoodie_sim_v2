from __future__ import annotations

import unittest

from src.analysis.baseline_policy_comparative_evaluation_readiness.model import (
    BaselineComparativeReadinessReport,
    BaselinePolicyComparativeRegressionEvidence,
    PolicyAggregateComparison,
)
from src.analysis.baseline_policy_comparative_evaluation_readiness.report import build_feature_074_report


class BaselinePolicyComparativeEvaluationReadinessReportTests(unittest.TestCase):
    def test_feature_074_report_passes_only_when_all_gates_pass(self) -> None:
        report = build_feature_074_report()
        self.assertTrue(report.passed)
        self.assertEqual(report.status, "baseline_policy_comparative_evaluation_readiness_ready")
        self.assertEqual(report.feature_name, "Feature 074 - Baseline Policy Comparative Evaluation Readiness")
        self.assertEqual(report.recommended_next_feature, "Feature 075 - Proposed Deadline-Aware Method Integration Readiness")
        self.assertIn("no final evaluation claim is made", report.paper_claim_boundary.lower())
        self.assertIn("no performance superiority claim is made", report.paper_claim_boundary.lower())
        self.assertIn("no statistical significance claim is made", report.paper_claim_boundary.lower())
        self.assertIn("no full paper reproduction claim is made", report.paper_claim_boundary.lower())
        self.assertIn("feature 073 controlled scenarios are consumed", report.paper_claim_boundary.lower())
        self.assertIn("baseline policies are not rewritten", report.paper_claim_boundary.lower())

    def test_report_includes_policy_descriptors_and_regression_evidence(self) -> None:
        report = build_feature_074_report()
        self.assertEqual({descriptor.policy_id for descriptor in report.policy_descriptors}, {"FLC", "VO", "HO", "RO", "BCO", "MLEO"})
        self.assertEqual(len(report.scenario_comparisons), 42)
        self.assertEqual(len(report.policy_aggregate_metrics), 6)
        self.assertTrue(report.feature_068r_regression_status.passed)
        self.assertTrue(report.feature_069_regression_status.passed)
        self.assertTrue(report.feature_070_regression_status.passed)
        self.assertTrue(report.feature_071_regression_status.passed)
        self.assertTrue(report.feature_072_regression_status.passed)
        self.assertTrue(report.feature_073_regression_status.passed)

    def test_report_fails_when_compatibility_mode_is_used_in_default_comparison(self) -> None:
        report = build_feature_074_report()
        self.assertFalse(any(comparison.compatibility_mode_used for comparison in report.scenario_comparisons))
        self.assertFalse(any(aggregate.compatibility_mode_used for aggregate in report.policy_aggregate_metrics))

    def test_report_raises_when_policy_aggregate_is_inconsistent(self) -> None:
        report = build_feature_074_report()
        broken_aggregate = tuple(
            aggregate if aggregate.policy_id != "FLC" else PolicyAggregateComparison(
                policy_id=aggregate.policy_id,
                scenario_count=aggregate.scenario_count,
                completed_count=aggregate.completed_count + 1,
                dropped_timeout_count=aggregate.dropped_timeout_count,
                dropped_unavailable_count=aggregate.dropped_unavailable_count,
                deadline_violation_count=aggregate.deadline_violation_count,
                illegal_action_rejection_count=aggregate.illegal_action_rejection_count,
                mean_delay=aggregate.mean_delay,
                mean_reward=aggregate.mean_reward,
                compatibility_mode_used=aggregate.compatibility_mode_used,
            )
            for aggregate in report.policy_aggregate_metrics
        )
        with self.assertRaises(ValueError):
            BaselineComparativeReadinessReport(
                feature_name=report.feature_name,
                status=report.status,
                passed=True,
                changed_files=report.changed_files,
                policy_descriptors=report.policy_descriptors,
                scenario_comparisons=report.scenario_comparisons,
                policy_aggregate_metrics=broken_aggregate,
                feature_068r_regression_status=BaselinePolicyComparativeRegressionEvidence("068R", True, "ok"),
                feature_069_regression_status=BaselinePolicyComparativeRegressionEvidence("069", True, "ok"),
                feature_070_regression_status=BaselinePolicyComparativeRegressionEvidence("070", True, "ok"),
                feature_071_regression_status=BaselinePolicyComparativeRegressionEvidence("071", True, "ok"),
                feature_072_regression_status=BaselinePolicyComparativeRegressionEvidence("072", True, "ok"),
                feature_073_regression_status=BaselinePolicyComparativeRegressionEvidence("073", True, "ok"),
                paper_claim_boundary=report.paper_claim_boundary,
                recommended_next_feature=report.recommended_next_feature,
            )


if __name__ == "__main__":
    unittest.main()
