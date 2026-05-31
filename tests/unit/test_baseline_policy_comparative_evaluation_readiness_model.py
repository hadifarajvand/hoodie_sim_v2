from __future__ import annotations

import unittest
from dataclasses import replace

from src.analysis.baseline_policy_comparative_evaluation_readiness.model import (
    BaselineComparativeReadinessReport,
    BaselinePolicyDescriptor,
    BaselinePolicyComparativeRegressionEvidence,
    PolicyAggregateComparison,
    PolicyScenarioComparison,
)
from src.analysis.baseline_policy_comparative_evaluation_readiness.report import (
    build_feature_074_report,
    compute_policy_aggregate_metrics,
)
from src.analysis.controlled_evaluation_batch_readiness.model import ControlledEvaluationMetrics


class BaselinePolicyComparativeEvaluationReadinessModelTests(unittest.TestCase):
    def _metrics(self, *, completed: int, timeout: int, unavailable: int, violations: int, illegal: int, delay: float, reward: float, paper_success: int, compatibility: bool) -> ControlledEvaluationMetrics:
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

    def _descriptor(self, policy_id: str, available: bool = True, decision_trace_supported: bool = True) -> BaselinePolicyDescriptor:
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
        passed: bool,
        compatibility_mode_used: bool = False,
        metrics_compatibility_mode_used: bool | None = None,
        decision_trace: tuple[str, ...] = ("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
    ) -> PolicyScenarioComparison:
        metrics_compatibility_mode_used = compatibility_mode_used if metrics_compatibility_mode_used is None else metrics_compatibility_mode_used
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

    def test_policy_scenario_comparison_requires_policy_and_scenario_ids(self) -> None:
        comparison = self._comparison(
            policy_id="FLC",
            scenario_id="light_load_no_deadline_pressure",
            policy_action_family="fixed-local / local-first family",
            passed=True,
            decision_trace=("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
        )
        self.assertEqual(comparison.policy_id, "FLC")
        self.assertEqual(comparison.scenario_id, "light_load_no_deadline_pressure")
        self.assertTrue(comparison.policy_decision_trace_present)
        self.assertTrue(comparison.decision_trace)
        self.assertTrue(comparison.passed)

        with self.assertRaises(ValueError):
            PolicyScenarioComparison(
                policy_id="",
                scenario_id="light_load_no_deadline_pressure",
                policy_action_family="fixed-local / local-first family",
                policy_decision_trace_present=True,
                decision_trace=("policy=FLC",),
                metrics=comparison.metrics,
                compatibility_mode_used=False,
                passed=True,
            )

        with self.assertRaises(ValueError):
            PolicyScenarioComparison(
                policy_id="FLC",
                scenario_id="",
                policy_action_family="fixed-local / local-first family",
                policy_decision_trace_present=True,
                decision_trace=("policy=FLC",),
                metrics=comparison.metrics,
                compatibility_mode_used=False,
                passed=True,
            )

    def test_policy_aggregate_comparison_aggregates_from_scenario_rows(self) -> None:
        rows = (
            self._comparison(
                policy_id="FLC",
                scenario_id="light_load_no_deadline_pressure",
                policy_action_family="fixed-local / local-first family",
                passed=True,
                decision_trace=("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
            ),
            replace(
                self._comparison(
                    policy_id="FLC",
                    scenario_id="tight_deadline_pressure",
                    policy_action_family="fixed-local / local-first family",
                    passed=True,
                    decision_trace=("policy=FLC", "scenario=tight_deadline_pressure", "action=local"),
                ),
                metrics=self._metrics(
                    completed=0,
                    timeout=1,
                    unavailable=0,
                    violations=1,
                    illegal=0,
                    delay=4.0,
                    reward=-40.0,
                    paper_success=0,
                    compatibility=False,
                ),
            ),
        )
        aggregate = compute_policy_aggregate_metrics("FLC", rows)
        self.assertIsInstance(aggregate, PolicyAggregateComparison)
        self.assertEqual(aggregate.policy_id, "FLC")
        self.assertEqual(aggregate.scenario_count, 2)
        self.assertEqual(aggregate.completed_count, 1)
        self.assertEqual(aggregate.dropped_timeout_count, 1)
        self.assertEqual(aggregate.dropped_unavailable_count, 0)
        self.assertEqual(aggregate.deadline_violation_count, 1)
        self.assertEqual(aggregate.illegal_action_rejection_count, 0)
        self.assertEqual(aggregate.mean_delay, 3.5)
        self.assertEqual(aggregate.mean_reward, -21.5)
        self.assertFalse(aggregate.compatibility_mode_used)

    def test_report_passes_only_when_all_gates_pass(self) -> None:
        report = build_feature_074_report()
        self.assertTrue(report.passed)
        self.assertEqual(report.status, "baseline_policy_comparative_evaluation_readiness_ready")
        self.assertEqual(report.feature_name, "Feature 074 - Baseline Policy Comparative Evaluation Readiness")

    def test_report_fails_when_required_policy_is_missing(self) -> None:
        descriptor = self._descriptor("FLC")
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
        comparison = self._comparison(
            policy_id="FLC",
            scenario_id="light_load_no_deadline_pressure",
            policy_action_family="fixed-local / local-first family",
            passed=False,
            decision_trace=(),
        )
        aggregate = PolicyAggregateComparison(
            policy_id="FLC",
            scenario_count=1,
            completed_count=1,
            dropped_timeout_count=0,
            dropped_unavailable_count=0,
            deadline_violation_count=0,
            illegal_action_rejection_count=0,
            mean_delay=3.0,
            mean_reward=-3.0,
            compatibility_mode_used=False,
        )
        with self.assertRaises(ValueError):
            BaselineComparativeReadinessReport(
                feature_name="Feature 074 - Baseline Policy Comparative Evaluation Readiness",
                status="baseline_policy_comparative_evaluation_readiness_with_blockers",
                passed=False,
                changed_files=("src/analysis/baseline_policy_comparative_evaluation_readiness/report.py",),
                policy_descriptors=(
                    descriptor,
                    self._descriptor("VO", available=False, decision_trace_supported=False),
                    self._descriptor("HO"),
                    self._descriptor("RO"),
                    self._descriptor("BCO"),
                    self._descriptor("MLEO"),
                ),
                scenario_comparisons=(comparison,),
                policy_aggregate_metrics=(aggregate,),
                feature_068r_regression_status=BaselinePolicyComparativeRegressionEvidence("068R", True, "ok"),
                feature_069_regression_status=BaselinePolicyComparativeRegressionEvidence("069", True, "ok"),
                feature_070_regression_status=BaselinePolicyComparativeRegressionEvidence("070", True, "ok"),
                feature_071_regression_status=BaselinePolicyComparativeRegressionEvidence("071", True, "ok"),
                feature_072_regression_status=BaselinePolicyComparativeRegressionEvidence("072", True, "ok"),
                feature_073_regression_status=BaselinePolicyComparativeRegressionEvidence("073", True, "ok"),
                paper_claim_boundary="No final evaluation claim is made.",
                recommended_next_feature="Feature 075 - Proposed Deadline-Aware Method Integration Readiness",
            )

    def test_report_fails_when_compatibility_mode_is_used_in_default_comparison(self) -> None:
        descriptor = self._descriptor("FLC")
        comparison = self._comparison(
            policy_id="FLC",
            scenario_id="light_load_no_deadline_pressure",
            policy_action_family="fixed-local / local-first family",
            passed=False,
            compatibility_mode_used=True,
            metrics_compatibility_mode_used=True,
            decision_trace=("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
        )
        aggregate = PolicyAggregateComparison(
            policy_id="FLC",
            scenario_count=1,
            completed_count=1,
            dropped_timeout_count=0,
            dropped_unavailable_count=0,
            deadline_violation_count=0,
            illegal_action_rejection_count=0,
            mean_delay=3.0,
            mean_reward=-3.0,
            compatibility_mode_used=True,
        )
        with self.assertRaises(ValueError):
            BaselineComparativeReadinessReport(
                feature_name="Feature 074 - Baseline Policy Comparative Evaluation Readiness",
                status="baseline_policy_comparative_evaluation_readiness_with_blockers",
                passed=False,
                changed_files=("src/analysis/baseline_policy_comparative_evaluation_readiness/report.py",),
                policy_descriptors=(
                    descriptor,
                    self._descriptor("VO"),
                    self._descriptor("HO"),
                    self._descriptor("RO"),
                    self._descriptor("BCO"),
                    self._descriptor("MLEO"),
                ),
                scenario_comparisons=(comparison,),
                policy_aggregate_metrics=(aggregate,),
                feature_068r_regression_status=BaselinePolicyComparativeRegressionEvidence("068R", True, "ok"),
                feature_069_regression_status=BaselinePolicyComparativeRegressionEvidence("069", True, "ok"),
                feature_070_regression_status=BaselinePolicyComparativeRegressionEvidence("070", True, "ok"),
                feature_071_regression_status=BaselinePolicyComparativeRegressionEvidence("071", True, "ok"),
                feature_072_regression_status=BaselinePolicyComparativeRegressionEvidence("072", True, "ok"),
                feature_073_regression_status=BaselinePolicyComparativeRegressionEvidence("073", True, "ok"),
                paper_claim_boundary="No final evaluation claim is made.",
                recommended_next_feature="Feature 075 - Proposed Deadline-Aware Method Integration Readiness",
            )

    def test_report_fails_when_policy_aggregate_does_not_match_scenario_rows(self) -> None:
        descriptor = self._descriptor("FLC")
        comparison = self._comparison(
            policy_id="FLC",
            scenario_id="light_load_no_deadline_pressure",
            policy_action_family="fixed-local / local-first family",
            passed=True,
            decision_trace=("policy=FLC", "scenario=light_load_no_deadline_pressure", "action=local"),
        )
        with self.assertRaises(ValueError):
            BaselineComparativeReadinessReport(
                feature_name="Feature 074 - Baseline Policy Comparative Evaluation Readiness",
                status="baseline_policy_comparative_evaluation_readiness_ready",
                passed=True,
                changed_files=("src/analysis/baseline_policy_comparative_evaluation_readiness/report.py",),
                policy_descriptors=(
                    descriptor,
                    self._descriptor("VO"),
                    self._descriptor("HO"),
                    self._descriptor("RO"),
                    self._descriptor("BCO"),
                    self._descriptor("MLEO"),
                ),
                scenario_comparisons=(comparison,),
                policy_aggregate_metrics=(
                    PolicyAggregateComparison(
                        policy_id="FLC",
                        scenario_count=1,
                        completed_count=0,
                        dropped_timeout_count=1,
                        dropped_unavailable_count=0,
                        deadline_violation_count=1,
                        illegal_action_rejection_count=0,
                        mean_delay=4.0,
                        mean_reward=-40.0,
                        compatibility_mode_used=False,
                    ),
                ),
                feature_068r_regression_status=BaselinePolicyComparativeRegressionEvidence("068R", True, "ok"),
                feature_069_regression_status=BaselinePolicyComparativeRegressionEvidence("069", True, "ok"),
                feature_070_regression_status=BaselinePolicyComparativeRegressionEvidence("070", True, "ok"),
                feature_071_regression_status=BaselinePolicyComparativeRegressionEvidence("071", True, "ok"),
                feature_072_regression_status=BaselinePolicyComparativeRegressionEvidence("072", True, "ok"),
                feature_073_regression_status=BaselinePolicyComparativeRegressionEvidence("073", True, "ok"),
                paper_claim_boundary="No final evaluation claim is made.",
                recommended_next_feature="Feature 075 - Proposed Deadline-Aware Method Integration Readiness",
            )


if __name__ == "__main__":
    unittest.main()
