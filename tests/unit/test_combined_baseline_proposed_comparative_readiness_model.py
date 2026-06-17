from __future__ import annotations

import unittest
from dataclasses import replace

from src.analysis.combined_baseline_proposed_comparative_readiness.model import (
    CombinedComparativeReadinessReport,
    CombinedPolicyAggregate,
    CombinedPolicyRow,
    CombinedRegressionEvidence,
)
from src.analysis.combined_baseline_proposed_comparative_readiness.report import build_feature_076_report
from src.analysis.proposed_method_integration_readiness.model import PROPOSED_METHOD_POLICY_ID


class CombinedBaselineProposedComparativeReadinessModelTests(unittest.TestCase):
    def _row(self, **overrides) -> CombinedPolicyRow:
        row = CombinedPolicyRow(
            policy_id="FLC",
            policy_family="fixed-local / local-first family",
            scenario_id="light_load_no_deadline_pressure",
            selected_action_id="local",
            selected_action_family="local",
            action_legality="legal",
            action_bound_terminal_status="completed_private",
            action_bound_reward_value=-3.0,
            action_bound_metrics_derived=True,
            compatibility_mode_used=False,
            decision_trace_present=True,
            completed_count=1,
            dropped_timeout_count=0,
            dropped_unavailable_count=0,
            deadline_violation_count=0,
            illegal_action_rejection_count=0,
            average_delay=3.0,
            average_reward=-3.0,
            source_feature="074",
            source_report_status="baseline_policy_comparative_evaluation_readiness_ready",
        )
        return replace(row, **overrides) if overrides else row

    def _aggregate(self, **overrides) -> CombinedPolicyAggregate:
        aggregate = CombinedPolicyAggregate(
            policy_id="FLC",
            policy_family="fixed-local / local-first family",
            scenario_count=7,
            completed_count=1,
            dropped_timeout_count=0,
            dropped_unavailable_count=0,
            deadline_violation_count=0,
            illegal_action_rejection_count=0,
            mean_delay=3.0,
            mean_reward=-3.0,
            all_rows_action_bound=True,
            compatibility_mode_used=False,
            decision_trace_present=True,
        )
        return replace(aggregate, **overrides) if overrides else aggregate

    def _valid_report(self) -> CombinedComparativeReadinessReport:
        policies = ("FLC", "VO", "HO", "RO", "BCO", "MLEO", PROPOSED_METHOD_POLICY_ID)
        scenarios = (
            "light_load_no_deadline_pressure",
            "tight_deadline_pressure",
            "legal_horizontal_offload",
            "illegal_horizontal_destination_attempt",
            "cloud_vertical_fallback",
            "timeout_drop_case",
            "mixed_local_horizontal_cloud_candidates",
        )
        rows = tuple(
            replace(
                self._row(policy_id=policy_id, scenario_id=scenario_id),
                policy_family=f"family-{policy_id}",
                source_feature="075" if policy_id == PROPOSED_METHOD_POLICY_ID else "074",
            )
            for policy_id in policies
            for scenario_id in scenarios
        )
        aggregates = tuple(
            CombinedPolicyAggregate(
                policy_id=policy_id,
                policy_family=f"family-{policy_id}",
                scenario_count=7,
                completed_count=7,
                dropped_timeout_count=0,
                dropped_unavailable_count=0,
                deadline_violation_count=0,
                illegal_action_rejection_count=0,
                mean_delay=3.0,
                mean_reward=-3.0,
                all_rows_action_bound=True,
                compatibility_mode_used=False,
                decision_trace_present=True,
            )
            for policy_id in policies
        )
        regression_evidence = tuple(
            CombinedRegressionEvidence(
                feature_id=feature_id,
                status="ok",
                passed=True,
                command_hint=f"check-{feature_id}",
                scope="synthetic validation scope",
            )
            for feature_id in ("068R", "069", "070", "071", "072", "073", "074", "075")
        )
        return CombinedComparativeReadinessReport(
            feature_name="Feature 076 - Combined Baseline + Proposed Comparative Readiness",
            status="combined_baseline_proposed_comparative_readiness_ready",
            passed=True,
            rows=rows,
            aggregates=aggregates,
            regression_evidence=regression_evidence,
            required_policy_ids=("FLC", "VO", "HO", "RO", "BCO", "MLEO", PROPOSED_METHOD_POLICY_ID),
            required_scenario_ids=scenarios,
            claim_boundary=(
                "No training claim is made.",
                "No superiority claim is made.",
                "No final evaluation claim is made.",
                "No statistical significance claim is made.",
                "No full paper reproduction claim is made.",
            ),
            scope_evidence=("synthetic scope",),
            source_features=("074", "075"),
        )

    def test_combined_policy_row_rejects_invalid_readiness_evidence(self) -> None:
        with self.assertRaises(ValueError):
            self._row(selected_action_id="")

        with self.assertRaises(ValueError):
            self._row(compatibility_mode_used=True)

        with self.assertRaises(ValueError):
            self._row(action_bound_metrics_derived=False)

    def test_combined_policy_aggregate_validates_scenario_count(self) -> None:
        with self.assertRaises(ValueError):
            self._aggregate(scenario_count=6)

    def test_combined_comparative_report_rejects_missing_policy_scenario_and_duplicate_coverage(self) -> None:
        report = self._valid_report()
        rows = list(report.rows)
        aggregates = list(report.aggregates)
        evidence = list(report.regression_evidence)

        missing_policy_rows = tuple(row for row in rows if row.policy_id != PROPOSED_METHOD_POLICY_ID)
        with self.assertRaises(ValueError):
            CombinedComparativeReadinessReport(
                feature_name=report.feature_name,
                status=report.status,
                passed=True,
                rows=missing_policy_rows,
                aggregates=tuple(aggregates),
                regression_evidence=tuple(evidence),
                required_policy_ids=report.required_policy_ids,
                required_scenario_ids=report.required_scenario_ids,
                claim_boundary=report.claim_boundary,
                scope_evidence=report.scope_evidence,
                source_features=report.source_features,
            )

        missing_scenario_rows = tuple(row for row in rows if row.scenario_id != "timeout_drop_case")
        with self.assertRaises(ValueError):
            CombinedComparativeReadinessReport(
                feature_name=report.feature_name,
                status=report.status,
                passed=True,
                rows=missing_scenario_rows,
                aggregates=tuple(aggregates),
                regression_evidence=tuple(evidence),
                required_policy_ids=report.required_policy_ids,
                required_scenario_ids=report.required_scenario_ids,
                claim_boundary=report.claim_boundary,
                scope_evidence=report.scope_evidence,
                source_features=report.source_features,
            )

        duplicate_rows = tuple(rows + [rows[0]])
        with self.assertRaises(ValueError):
            CombinedComparativeReadinessReport(
                feature_name=report.feature_name,
                status=report.status,
                passed=True,
                rows=duplicate_rows,
                aggregates=tuple(aggregates),
                regression_evidence=tuple(evidence),
                required_policy_ids=report.required_policy_ids,
                required_scenario_ids=report.required_scenario_ids,
                claim_boundary=report.claim_boundary,
                scope_evidence=report.scope_evidence,
                source_features=report.source_features,
            )

    def test_combined_comparative_report_rejects_missing_claim_boundary_and_failed_regression(self) -> None:
        report = self._valid_report()
        with self.assertRaises(ValueError):
            CombinedComparativeReadinessReport(
                feature_name=report.feature_name,
                status=report.status,
                passed=True,
                rows=report.rows,
                aggregates=report.aggregates,
                regression_evidence=report.regression_evidence,
                required_policy_ids=report.required_policy_ids,
                required_scenario_ids=report.required_scenario_ids,
                claim_boundary=(),
                scope_evidence=report.scope_evidence,
                source_features=report.source_features,
            )

        failed_evidence = list(report.regression_evidence)
        failed_evidence[0] = CombinedRegressionEvidence(
            feature_id=failed_evidence[0].feature_id,
            status=failed_evidence[0].status,
            passed=False,
            command_hint=failed_evidence[0].command_hint,
            scope=failed_evidence[0].scope,
        )
        with self.assertRaises(ValueError):
            CombinedComparativeReadinessReport(
                feature_name=report.feature_name,
                status=report.status,
                passed=True,
                rows=report.rows,
                aggregates=report.aggregates,
                regression_evidence=tuple(failed_evidence),
                required_policy_ids=report.required_policy_ids,
                required_scenario_ids=report.required_scenario_ids,
                claim_boundary=report.claim_boundary,
                scope_evidence=report.scope_evidence,
                source_features=report.source_features,
            )


if __name__ == "__main__":
    unittest.main()
