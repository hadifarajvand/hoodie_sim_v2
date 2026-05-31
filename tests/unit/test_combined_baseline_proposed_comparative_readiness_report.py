from __future__ import annotations

import unittest

from src.analysis.combined_baseline_proposed_comparative_readiness.report import (
    build_combined_aggregates,
    build_combined_rows,
    build_feature_076_report,
    build_regression_evidence,
    normalize_feature_074_rows,
    normalize_feature_075_rows,
    render_feature_076_report,
)
from src.analysis.baseline_policy_comparative_evaluation_readiness.report import build_feature_074_report
from src.analysis.proposed_method_integration_readiness.model import PROPOSED_METHOD_POLICY_ID
from src.analysis.proposed_method_integration_readiness.report import build_feature_075_report


class CombinedBaselineProposedComparativeReadinessReportTests(unittest.TestCase):
    def test_build_feature_076_report_is_ready_and_preserves_action_bound_matrix(self) -> None:
        report = build_feature_076_report()
        self.assertTrue(report.passed)
        self.assertEqual(report.status, "combined_baseline_proposed_comparative_readiness_ready")
        self.assertEqual(len(report.rows), 49)
        self.assertEqual(len(report.aggregates), 7)
        self.assertEqual(set(report.required_policy_ids), {"FLC", "VO", "HO", "RO", "BCO", "MLEO", PROPOSED_METHOD_POLICY_ID})
        self.assertEqual(
            set(report.required_scenario_ids),
            {
                "light_load_no_deadline_pressure",
                "tight_deadline_pressure",
                "legal_horizontal_offload",
                "illegal_horizontal_destination_attempt",
                "cloud_vertical_fallback",
                "timeout_drop_case",
                "mixed_local_horizontal_cloud_candidates",
            },
        )
        self.assertTrue(all(row.action_bound_metrics_derived for row in report.rows))
        self.assertTrue(all(not row.compatibility_mode_used for row in report.rows))
        self.assertTrue(all(row.decision_trace_present for row in report.rows))
        self.assertEqual(sum(1 for row in report.rows if row.source_feature == "074"), 42)
        self.assertEqual(sum(1 for row in report.rows if row.source_feature == "075"), 7)
        self.assertEqual(sum(1 for row in report.rows if row.policy_id == PROPOSED_METHOD_POLICY_ID), 7)
        self.assertEqual(sum(1 for row in report.rows if row.policy_id in {"FLC", "VO", "HO", "RO", "BCO", "MLEO"}), 42)
        self.assertEqual(len(build_combined_rows()), 49)
        self.assertEqual(len(build_combined_aggregates(report.rows)), 7)
        self.assertEqual(len(build_regression_evidence()), 8)

    def test_report_uses_feature_074_and_075_rows_and_aggregate_counts_match_row_sums(self) -> None:
        report_074 = build_feature_074_report()
        report_075 = build_feature_075_report()
        baseline_rows = normalize_feature_074_rows(report_074)
        proposed_rows = normalize_feature_075_rows(report_075)
        self.assertEqual(len(baseline_rows), 42)
        self.assertEqual(len(proposed_rows), 7)
        self.assertTrue(all(row.source_feature == "074" for row in baseline_rows))
        self.assertTrue(all(row.source_feature == "075" for row in proposed_rows))
        self.assertEqual(all(row.source_report_status == report_074.status for row in baseline_rows), True)
        self.assertEqual(all(row.source_report_status == report_075.status for row in proposed_rows), True)

        report = build_feature_076_report()
        for aggregate in report.aggregates:
            rows = [row for row in report.rows if row.policy_id == aggregate.policy_id]
            self.assertEqual(aggregate.scenario_count, 7)
            self.assertEqual(aggregate.completed_count, sum(row.completed_count for row in rows))
            self.assertEqual(aggregate.dropped_timeout_count, sum(row.dropped_timeout_count for row in rows))
            self.assertEqual(aggregate.dropped_unavailable_count, sum(row.dropped_unavailable_count for row in rows))
            self.assertEqual(aggregate.deadline_violation_count, sum(row.deadline_violation_count for row in rows))
            self.assertEqual(aggregate.illegal_action_rejection_count, sum(row.illegal_action_rejection_count for row in rows))
            self.assertEqual(aggregate.all_rows_action_bound, True)
            self.assertEqual(aggregate.compatibility_mode_used, False)
            self.assertEqual(aggregate.decision_trace_present, True)

    def test_rendered_report_contains_claim_boundary_and_no_overclaim_language(self) -> None:
        report = build_feature_076_report()
        rendered = render_feature_076_report(report)
        self.assertIn("Feature 076 Combined Baseline + Proposed Comparative Readiness Report", rendered)
        self.assertIn("combined_baseline_proposed_comparative_readiness_ready", rendered)
        self.assertIn("Feature 074 source report status", rendered)
        self.assertIn("Feature 075 source report status", rendered)
        self.assertIn("Feature 074 rows are consumed.", rendered)
        self.assertIn("Feature 075 rows are consumed.", rendered)
        self.assertIn("Action-bound evidence is preserved.", rendered)
        self.assertIn("Compatibility mode is not used.", rendered)
        self.assertIn("No training claim is made.", rendered)
        self.assertIn("No superiority claim is made.", rendered)
        self.assertIn("No final evaluation claim is made.", rendered)
        self.assertIn("No statistical significance claim is made.", rendered)
        self.assertIn("No full paper reproduction claim is made.", rendered)


if __name__ == "__main__":
    unittest.main()
