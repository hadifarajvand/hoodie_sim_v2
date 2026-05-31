from __future__ import annotations

import unittest
from dataclasses import replace

from src.analysis.baseline_policy_comparative_evaluation_readiness.model import (
    BaselineComparativeReadinessReport,
    BaselinePolicyComparativeRegressionEvidence,
    BaselinePolicyDescriptor,
    PolicyAggregateComparison,
    PolicyScenarioComparison,
)
from src.analysis.baseline_policy_comparative_evaluation_readiness.report import (
    build_feature_074_report,
    build_policy_scenario_comparisons,
    build_required_policy_descriptors,
    compute_policy_aggregate_metrics,
)
from src.analysis.controlled_evaluation_batch_readiness.model import ControlledEvaluationMetrics


class BaselinePolicyComparativeEvaluationReadinessModelTests(unittest.TestCase):
    def _metrics(
        self,
        *,
        completed: int,
        timeout: int,
        unavailable: int,
        violations: int,
        illegal: int,
        delay: float,
        reward: float,
        paper_success: int,
        compatibility: bool,
    ) -> ControlledEvaluationMetrics:
        return ControlledEvaluationMetrics(
            completed_count=completed,
            dropped_timeout_count=timeout,
            dropped_unavailable_count=unavailable,
            deadline_violation_count=violations,
            illegal_action_rejection_count=illegal,
            average_delay=delay,
            average_reward=reward,
            paper_mode_success_count=paper_success,
            compatibility_mode_used=compatibility,
        )

    def _descriptor(
        self,
        policy_id: str,
        available: bool = True,
        decision_trace_supported: bool = True,
    ) -> BaselinePolicyDescriptor:
        families = {
            "FLC": "fixed-local / local-first family",
            "VO": "vertical-offload family",
            "HO": "horizontal-offload family",
            "RO": "random-offload family",
            "BCO": "balanced-cloud-offload family",
            "MLEO": "minimum-latency-estimation-offload family",
        }
        return BaselinePolicyDescriptor(
            policy_id=policy_id,
            policy_family=families[policy_id],
            registry_key=policy_id,
            available=available,
            decision_trace_supported=decision_trace_supported,
        )

    def _comparison(
        self,
        *,
        policy_id: str,
        scenario_id: str,
        policy_action_family: str,
        selected_action_id: str,
        selected_action_family: str,
        action_legality: str,
        action_bound_terminal_status: str,
        action_bound_reward_value: float | None,
        action_bound_metrics_derived: bool,
        passed: bool,
        compatibility_mode_used: bool = False,
        metrics_compatibility_mode_used: bool | None = None,
        decision_trace: tuple[str, ...] = ("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
        metrics: ControlledEvaluationMetrics | None = None,
    ) -> PolicyScenarioComparison:
        metrics_compatibility_mode_used = compatibility_mode_used if metrics_compatibility_mode_used is None else metrics_compatibility_mode_used
        if metrics is None:
            metrics = self._metrics(
                completed=1,
                timeout=0,
                unavailable=0,
                violations=0,
                illegal=0,
                delay=3.0,
                reward=-3.0,
                paper_success=1,
                compatibility=metrics_compatibility_mode_used,
            )
        return PolicyScenarioComparison(
            policy_id=policy_id,
            scenario_id=scenario_id,
            policy_action_family=policy_action_family,
            policy_decision_trace_present=bool(decision_trace),
            decision_trace=decision_trace,
            selected_action_id=selected_action_id,
            selected_action_family=selected_action_family,
            action_legality=action_legality,
            action_bound_terminal_status=action_bound_terminal_status,
            action_bound_reward_value=action_bound_reward_value,
            action_bound_metrics_derived=action_bound_metrics_derived,
            metrics=metrics,
            compatibility_mode_used=compatibility_mode_used,
            passed=passed,
        )

    def test_descriptor_validates_policy_identity_and_decision_trace_support(self) -> None:
        descriptor = self._descriptor("FLC")
        self.assertEqual(descriptor.policy_id, "FLC")
        self.assertEqual(descriptor.registry_key, "FLC")
        self.assertTrue(descriptor.available)
        self.assertTrue(descriptor.decision_trace_supported)

        with self.assertRaises(ValueError):
            BaselinePolicyDescriptor(
                policy_id="",
                policy_family="fixed-local / local-first family",
                registry_key="FLC",
                available=True,
                decision_trace_supported=True,
            )

    def test_policy_scenario_comparison_rejects_passed_rows_without_selected_action_evidence(self) -> None:
        metrics = self._metrics(
            completed=1,
            timeout=0,
            unavailable=0,
            violations=0,
            illegal=0,
            delay=3.0,
            reward=-3.0,
            paper_success=1,
            compatibility=False,
        )
        with self.assertRaises(ValueError):
            self._comparison(
                policy_id="FLC",
                scenario_id="light_load_no_deadline_pressure",
                policy_action_family="fixed-local / local-first family",
                selected_action_id="",
                selected_action_family="local",
                action_legality="legal",
                action_bound_terminal_status="completed_private",
                action_bound_reward_value=-3.0,
                action_bound_metrics_derived=True,
                passed=True,
                decision_trace=("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
                metrics=metrics,
            )

        with self.assertRaises(ValueError):
            self._comparison(
                policy_id="FLC",
                scenario_id="light_load_no_deadline_pressure",
                policy_action_family="fixed-local / local-first family",
                selected_action_id="local",
                selected_action_family="",
                action_legality="legal",
                action_bound_terminal_status="completed_private",
                action_bound_reward_value=-3.0,
                action_bound_metrics_derived=True,
                passed=True,
                decision_trace=("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
                metrics=metrics,
            )

        with self.assertRaises(ValueError):
            self._comparison(
                policy_id="FLC",
                scenario_id="light_load_no_deadline_pressure",
                policy_action_family="fixed-local / local-first family",
                selected_action_id="local",
                selected_action_family="local",
                action_legality="unmapped",
                action_bound_terminal_status="",
                action_bound_reward_value=None,
                action_bound_metrics_derived=False,
                passed=True,
                decision_trace=("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
                metrics=metrics,
            )

    def test_policy_aggregate_comparison_includes_selected_action_families(self) -> None:
        rows = (
            self._comparison(
                policy_id="FLC",
                scenario_id="light_load_no_deadline_pressure",
                policy_action_family="fixed-local / local-first family",
                selected_action_id="local",
                selected_action_family="local",
                action_legality="legal",
                action_bound_terminal_status="completed_private",
                action_bound_reward_value=-3.0,
                action_bound_metrics_derived=True,
                passed=True,
                decision_trace=("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
            ),
            replace(
                self._comparison(
                    policy_id="FLC",
                    scenario_id="legal_horizontal_offload",
                    policy_action_family="fixed-local / local-first family",
                    selected_action_id="6",
                    selected_action_family="horizontal",
                    action_legality="legal",
                    action_bound_terminal_status="completed_public",
                    action_bound_reward_value=-5.0,
                    action_bound_metrics_derived=True,
                    passed=True,
                    decision_trace=("policy=FLC", "scenario=legal_horizontal_offload", "action=6"),
                ),
                metrics=self._metrics(
                    completed=1,
                    timeout=0,
                    unavailable=0,
                    violations=0,
                    illegal=0,
                    delay=4.0,
                    reward=-5.0,
                    paper_success=1,
                    compatibility=False,
                ),
            ),
        )
        aggregate = compute_policy_aggregate_metrics("FLC", rows)
        self.assertIsInstance(aggregate, PolicyAggregateComparison)
        self.assertEqual(aggregate.policy_id, "FLC")
        self.assertEqual(aggregate.scenario_count, 2)
        self.assertEqual(aggregate.completed_count, 2)
        self.assertEqual(aggregate.dropped_timeout_count, 0)
        self.assertEqual(aggregate.dropped_unavailable_count, 0)
        self.assertEqual(aggregate.deadline_violation_count, 0)
        self.assertEqual(aggregate.illegal_action_rejection_count, 0)
        self.assertEqual(aggregate.mean_delay, 3.5)
        self.assertEqual(aggregate.mean_reward, -4.0)
        self.assertEqual(aggregate.distinct_selected_action_families, ("horizontal", "local"))
        self.assertTrue(aggregate.action_bound_metrics_derived)
        self.assertFalse(aggregate.compatibility_mode_used)

    def test_report_rejects_passed_true_if_any_row_is_not_action_bound(self) -> None:
        report = build_feature_074_report()
        broken_rows = list(report.scenario_comparisons)
        broken_rows[0] = replace(
            broken_rows[0],
            action_bound_metrics_derived=False,
            passed=False,
        )
        broken_aggregate = tuple(
            compute_policy_aggregate_metrics(policy_id, tuple(row for row in broken_rows if row.policy_id == policy_id))
            for policy_id in {"FLC", "VO", "HO", "RO", "BCO", "MLEO"}
        )
        with self.assertRaises(ValueError):
            BaselineComparativeReadinessReport(
                feature_name=report.feature_name,
                status="baseline_policy_comparative_evaluation_readiness_ready",
                passed=True,
                changed_files=report.changed_files,
                policy_descriptors=report.policy_descriptors,
                scenario_comparisons=tuple(broken_rows),
                policy_aggregate_metrics=broken_aggregate,
                feature_068r_regression_status=report.feature_068r_regression_status,
                feature_069_regression_status=report.feature_069_regression_status,
                feature_070_regression_status=report.feature_070_regression_status,
                feature_071_regression_status=report.feature_071_regression_status,
                feature_072_regression_status=report.feature_072_regression_status,
                feature_073_regression_status=report.feature_073_regression_status,
                paper_claim_boundary=report.paper_claim_boundary,
                recommended_next_feature=report.recommended_next_feature,
            )

    def test_report_fails_when_compatibility_mode_is_used_in_default_comparison(self) -> None:
        report = build_feature_074_report()
        comparison = self._comparison(
            policy_id="FLC",
            scenario_id="light_load_no_deadline_pressure",
            policy_action_family="fixed-local / local-first family",
            selected_action_id="local",
            selected_action_family="local",
            action_legality="legal",
            action_bound_terminal_status="completed_private",
            action_bound_reward_value=-3.0,
            action_bound_metrics_derived=True,
            passed=False,
            compatibility_mode_used=True,
            metrics_compatibility_mode_used=True,
            decision_trace=("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
        )
        self.assertTrue(comparison.compatibility_mode_used)
        self.assertTrue(comparison.metrics.compatibility_mode_used)
        self.assertFalse(report.policy_aggregate_metrics[0].compatibility_mode_used)


if __name__ == "__main__":
    unittest.main()
