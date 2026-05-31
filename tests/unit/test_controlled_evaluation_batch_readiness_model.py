from __future__ import annotations

from dataclasses import replace
import unittest

from src.analysis.controlled_evaluation_batch_readiness.model import (
    ControlledEvaluationBatchReport,
    ControlledEvaluationMetrics,
    ControlledEvaluationRegressionEvidence,
    ControlledEvaluationScenario,
    ControlledEvaluationTaskRecord,
)


class ControlledEvaluationBatchReadinessModelTests(unittest.TestCase):
    def test_task_record_validates_explicit_terminal_status(self) -> None:
        record = ControlledEvaluationTaskRecord(
            task_id="task-1",
            source_agent_id="1",
            action_type="local",
            destination_agent_id="private",
            arrival_slot=2,
            phi=4,
            completion_slot=4,
            terminal_status="completed_private",
            reward_value=-3.0,
            delay=3,
            illegal_action_rejected=False,
            compatibility_mode_used=False,
        )
        self.assertEqual(record.terminal_status, "completed_private")
        self.assertTrue(record.is_completed)

        with self.assertRaises(ValueError):
            ControlledEvaluationTaskRecord(
                task_id="task-2",
                source_agent_id="1",
                action_type="local",
                destination_agent_id="private",
                arrival_slot=2,
                phi=4,
                completion_slot=4,
                terminal_status="",
                reward_value=-3.0,
                delay=3,
                illegal_action_rejected=False,
                compatibility_mode_used=False,
            )

    def test_scenario_requires_tasks(self) -> None:
        metrics = ControlledEvaluationMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0, False)
        with self.assertRaises(ValueError):
            ControlledEvaluationScenario(
                scenario_id="scenario-1",
                name="Empty",
                description="should fail",
                tasks=(),
                expected_metrics=metrics,
                actual_metrics=replace(metrics),
                paper_mode_only=True,
                passed=False,
            )

    def test_metrics_reject_negative_counts(self) -> None:
        with self.assertRaises(ValueError):
            ControlledEvaluationMetrics(-1, 0, 0, 0, 0, 0.0, 0.0, 0, False)

    def test_scenario_fails_when_expected_and_actual_metrics_diverge(self) -> None:
        task = ControlledEvaluationTaskRecord(
            task_id="task-3",
            source_agent_id="1",
            action_type="local",
            destination_agent_id="private",
            arrival_slot=2,
            phi=4,
            completion_slot=4,
            terminal_status="completed_private",
            reward_value=-3.0,
            delay=3,
            illegal_action_rejected=False,
            compatibility_mode_used=False,
        )
        expected = ControlledEvaluationMetrics(1, 0, 0, 0, 0, 3.0, -3.0, 1, False)
        actual = ControlledEvaluationMetrics(0, 1, 0, 1, 0, 4.0, -40.0, 0, False)
        scenario = ControlledEvaluationScenario(
            scenario_id="scenario-2",
            name="Divergent",
            description="expected and actual differ",
            tasks=(task,),
            expected_metrics=expected,
            actual_metrics=actual,
            paper_mode_only=True,
            passed=False,
        )
        self.assertFalse(scenario.passed)

    def test_expected_and_actual_metrics_must_be_distinct_objects(self) -> None:
        metrics = ControlledEvaluationMetrics(1, 0, 0, 0, 0, 3.0, -3.0, 1, False)
        task = ControlledEvaluationTaskRecord(
            task_id="task-4",
            source_agent_id="1",
            action_type="local",
            destination_agent_id="private",
            arrival_slot=2,
            phi=4,
            completion_slot=4,
            terminal_status="completed_private",
            reward_value=-3.0,
            delay=3,
            illegal_action_rejected=False,
            compatibility_mode_used=False,
        )
        with self.assertRaises(ValueError):
            ControlledEvaluationScenario(
                scenario_id="scenario-3",
                name="Shared metrics",
                description="must reject shared metric objects",
                tasks=(task,),
                expected_metrics=metrics,
                actual_metrics=metrics,
                paper_mode_only=True,
                passed=True,
            )

    def test_batch_report_passes_only_when_all_gates_pass(self) -> None:
        task = ControlledEvaluationTaskRecord(
            task_id="task-5",
            source_agent_id="1",
            action_type="local",
            destination_agent_id="private",
            arrival_slot=2,
            phi=4,
            completion_slot=4,
            terminal_status="completed_private",
            reward_value=-3.0,
            delay=3,
            illegal_action_rejected=False,
            compatibility_mode_used=False,
        )
        metrics = ControlledEvaluationMetrics(1, 0, 0, 0, 0, 3.0, -3.0, 1, False)
        scenario = ControlledEvaluationScenario(
            scenario_id="scenario-4",
            name="Passing",
            description="valid scenario",
            tasks=(task,),
            expected_metrics=replace(metrics),
            actual_metrics=metrics,
            paper_mode_only=True,
            passed=True,
        )
        regression = ControlledEvaluationRegressionEvidence(
            name="regression",
            passed=True,
            summary="ok",
            validation_commands=("echo ok",),
        )
        report = ControlledEvaluationBatchReport(
            feature_name="Feature 073 - Controlled Evaluation Batch Readiness",
            status="controlled_evaluation_batch_readiness_ready",
            passed=True,
            changed_files=("src/analysis/controlled_evaluation_batch_readiness/model.py",),
            scenarios=(scenario,),
            aggregate_metrics=metrics,
            feature_068r_regression_status=regression,
            feature_069_regression_status=replace(regression, name="069"),
            feature_070_regression_status=replace(regression, name="070"),
            feature_071_regression_status=replace(regression, name="071"),
            feature_072_regression_status=replace(regression, name="072"),
            paper_claim_boundary="No final evaluation claim is made.",
            recommended_next_feature="Feature 074 - Baseline Policy Comparative Evaluation Readiness",
        )
        self.assertTrue(report.passed)
        self.assertEqual(report.status, "controlled_evaluation_batch_readiness_ready")

        bad_regression = replace(regression, passed=False)
        with self.assertRaises(ValueError):
            ControlledEvaluationBatchReport(
                feature_name="Feature 073 - Controlled Evaluation Batch Readiness",
                status="controlled_evaluation_batch_readiness_ready",
                passed=True,
                changed_files=("src/analysis/controlled_evaluation_batch_readiness/model.py",),
                scenarios=(scenario,),
                aggregate_metrics=metrics,
                feature_068r_regression_status=bad_regression,
                feature_069_regression_status=replace(regression, name="069"),
                feature_070_regression_status=replace(regression, name="070"),
                feature_071_regression_status=replace(regression, name="071"),
                feature_072_regression_status=replace(regression, name="072"),
                paper_claim_boundary="No final evaluation claim is made.",
                recommended_next_feature="Feature 074 - Baseline Policy Comparative Evaluation Readiness",
            )
