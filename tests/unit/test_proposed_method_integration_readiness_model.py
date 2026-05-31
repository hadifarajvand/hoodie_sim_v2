from __future__ import annotations

import unittest
from dataclasses import replace

from src.analysis.controlled_evaluation_batch_readiness.model import ControlledEvaluationMetrics
from src.analysis.proposed_method_integration_readiness.model import (
    PROPOSED_METHOD_POLICY_FAMILY,
    PROPOSED_METHOD_POLICY_ID,
    ProposedMethodAggregateComparison,
    ProposedMethodCandidate,
    ProposedMethodDescriptor,
    ProposedMethodIntegrationReadinessReport,
    ProposedMethodRegressionEvidence,
    ProposedMethodScenarioEvaluation,
    aggregate_proposed_method_rows,
)
from src.analysis.proposed_method_integration_readiness.report import build_feature_075_report


class ProposedMethodIntegrationReadinessModelTests(unittest.TestCase):
    def _metrics(self, *, compatibility: bool = False) -> ControlledEvaluationMetrics:
        return ControlledEvaluationMetrics(
            completed_count=1,
            dropped_timeout_count=0,
            dropped_unavailable_count=0,
            deadline_violation_count=0,
            illegal_action_rejection_count=0,
            average_delay=3.0,
            average_reward=-3.0,
            paper_mode_success_count=1,
            compatibility_mode_used=compatibility,
        )

    def _descriptor(self) -> ProposedMethodDescriptor:
        return ProposedMethodDescriptor(
            policy_id=PROPOSED_METHOD_POLICY_ID,
            policy_family=PROPOSED_METHOD_POLICY_FAMILY,
            registry_key=PROPOSED_METHOD_POLICY_ID,
            available=True,
            decision_trace_supported=True,
        )

    def _candidate(self, action_id: str, family: str, *, legal: bool = True, selected: bool = True) -> ProposedMethodCandidate:
        return ProposedMethodCandidate(
            action_id=action_id,
            action_family=family,
            legal=legal,
            estimated_delay=3.0,
            deadline_slack=1.0,
            queue_or_load_value=0.2,
            reward_risk_value=0.1,
            ranking_score=3.3,
            selected=selected,
        )

    def _evaluation(
        self,
        *,
        selected_action_id: str,
        selected_action_family: str,
        action_legality: str = "legal",
        action_bound_terminal_status: str = "completed_private",
        action_bound_reward_value: float | None = -3.0,
        action_bound_metrics_derived: bool = True,
        passed: bool = True,
        compatibility_mode_used: bool = False,
        metrics: ControlledEvaluationMetrics | None = None,
    ) -> ProposedMethodScenarioEvaluation:
        metrics = metrics or self._metrics(compatibility=compatibility_mode_used)
        candidate = self._candidate(
            action_id=selected_action_id or "local",
            family=selected_action_family or "local",
            legal=action_legality != "unmapped",
            selected=True,
        )
        return ProposedMethodScenarioEvaluation(
            scenario_id="light_load_no_deadline_pressure",
            candidate_evidence=(candidate,),
            candidate_ranking_trace=("rank=1 action_id=local family=local score=3.3 selected=True",),
            candidate_ranking_trace_present=True,
            deadline_slack_evidence_present=True,
            queue_or_load_evidence_present=True,
            topology_legality_enforced=True,
            action_legality=action_legality,
            selected_action_id=selected_action_id,
            selected_action_family=selected_action_family,
            action_bound_terminal_status=action_bound_terminal_status,
            action_bound_reward_value=action_bound_reward_value,
            action_bound_metrics_derived=action_bound_metrics_derived,
            metrics=metrics,
            compatibility_mode_used=compatibility_mode_used,
            passed=passed,
        )

    def test_descriptor_exposes_required_identity(self) -> None:
        descriptor = self._descriptor()
        self.assertEqual(descriptor.policy_id, PROPOSED_METHOD_POLICY_ID)
        self.assertEqual(descriptor.policy_family, PROPOSED_METHOD_POLICY_FAMILY)
        self.assertTrue(descriptor.available)
        self.assertTrue(descriptor.decision_trace_supported)

    def test_scenario_evaluation_rejects_passed_rows_without_selected_action_or_action_bound_metrics(self) -> None:
        with self.assertRaises(ValueError):
            self._evaluation(
                selected_action_id="",
                selected_action_family="local",
                action_bound_metrics_derived=True,
            )

        with self.assertRaises(ValueError):
            self._evaluation(
                selected_action_id="local",
                selected_action_family="",
                action_bound_metrics_derived=True,
            )

        with self.assertRaises(ValueError):
            self._evaluation(
                selected_action_id="local",
                selected_action_family="local",
                action_bound_metrics_derived=False,
            )

        with self.assertRaises(ValueError):
            self._evaluation(
                selected_action_id="local",
                selected_action_family="local",
                action_legality="unmapped",
            )

    def test_policy_aggregate_includes_distinct_selected_action_families(self) -> None:
        rows = (
            self._evaluation(selected_action_id="local", selected_action_family="local"),
            replace(
                self._evaluation(
                    selected_action_id="6",
                    selected_action_family="horizontal",
                    action_bound_terminal_status="completed_public",
                    action_bound_reward_value=-5.0,
                ),
                metrics=self._metrics(),
            ),
        )
        aggregate = aggregate_proposed_method_rows(rows)
        self.assertIsInstance(aggregate, ProposedMethodAggregateComparison)
        self.assertEqual(aggregate.policy_id, PROPOSED_METHOD_POLICY_ID)
        self.assertEqual(aggregate.policy_family, PROPOSED_METHOD_POLICY_FAMILY)
        self.assertEqual(aggregate.scenario_count, 2)
        self.assertEqual(aggregate.distinct_selected_action_families, ("horizontal", "local"))
        self.assertTrue(aggregate.action_bound_metrics_derived)
        self.assertFalse(aggregate.compatibility_mode_used)

    def test_report_rejects_passed_true_if_any_row_is_not_action_bound(self) -> None:
        report = build_feature_075_report()
        mutated_rows = list(report.scenario_evaluations)
        mutated_rows[0] = replace(mutated_rows[0], action_bound_metrics_derived=False, passed=False)
        mutated_aggregate = aggregate_proposed_method_rows(tuple(mutated_rows))
        with self.assertRaises(ValueError):
            ProposedMethodIntegrationReadinessReport(
                feature_name=report.feature_name,
                status="proposed_method_integration_readiness_ready",
                passed=True,
                changed_files=report.changed_files,
                proposed_method_descriptor=report.proposed_method_descriptor,
                scenario_evaluations=tuple(mutated_rows),
                policy_aggregate_metrics=(mutated_aggregate,),
                feature_068r_regression_status=ProposedMethodRegressionEvidence("068R", True, "ok"),
                feature_069_regression_status=ProposedMethodRegressionEvidence("069", True, "ok"),
                feature_070_regression_status=ProposedMethodRegressionEvidence("070", True, "ok"),
                feature_071_regression_status=ProposedMethodRegressionEvidence("071", True, "ok"),
                feature_072_regression_status=ProposedMethodRegressionEvidence("072", True, "ok"),
                feature_073_regression_status=ProposedMethodRegressionEvidence("073", True, "ok"),
                feature_074_regression_status=ProposedMethodRegressionEvidence("074", True, "ok"),
                paper_claim_boundary=report.paper_claim_boundary,
                recommended_next_feature=report.recommended_next_feature,
            )


if __name__ == "__main__":
    unittest.main()
