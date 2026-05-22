from __future__ import annotations

import unittest

from src.analysis.completion_root_cause_diagnosis import RootCauseClassifier, RootCauseEvaluation, TaskLifecycleReconstruction
from src.analysis.completion_root_cause_diagnosis.config import ROOT_CAUSE_CLASSES


def make_task(
    task_id: int,
    *,
    run_id: str = "run-1",
    strategy: str = "environment_default_policy_probe",
    seed: int = 0,
    queue_type: str = "private",
    selected_action: str = "local",
    terminal_outcome: str | None = "dropped",
    queue_wait_time_slots: int | None = 3,
    execution_progress_slots: list[int] | None = None,
    task_completed_at: int | None = None,
    task_dropped_at: int | None = 4,
    deadline_expired_at: int | None = 4,
    reward_emitted_at: int | None = 4,
    completed_before_deadline: bool | None = False,
    reward_after_terminal_outcome: bool | None = True,
    transmission_started_at: int | None = None,
    transmission_completed_at: int | None = None,
    execution_started_at: int | None = None,
) -> TaskLifecycleReconstruction:
    return TaskLifecycleReconstruction(
        run_id=run_id,
        strategy=strategy,
        seed=seed,
        task_id=task_id,
        arrival_slot=0,
        absolute_deadline_slot=20,
        size_mbits=2.0,
        processing_density_gcycles_per_mbit=0.297,
        cycles_required_gcycles=0.594,
        generated_slot=0,
        admitted_slot=0,
        selected_action=selected_action,
        destination="self" if queue_type == "private" else "cloud",
        queue_type=queue_type,
        host_node_id="3",
        transmission_started_at=transmission_started_at,
        transmission_completed_at=transmission_completed_at,
        execution_started_at=execution_started_at,
        execution_progress_slots=execution_progress_slots or [1],
        execution_completed_at=task_completed_at,
        deadline_reached_at=task_dropped_at,
        deadline_expired_at=deadline_expired_at,
        task_completed_at=task_completed_at,
        task_dropped_at=task_dropped_at,
        pending_at_horizon_at=None,
        reward_emitted_at=reward_emitted_at,
        terminal_outcome=terminal_outcome,
        reward=-4.0 if terminal_outcome == "dropped" else -2.0,
        remaining_cycles_by_slot={0: 0.594, 1: 0.094},
        task_age_by_slot={0: 0, 1: 1, 2: 2},
        queue_wait_time_slots=queue_wait_time_slots,
        completed_before_deadline=completed_before_deadline,
        deadline_or_drop_before_completion=True,
        reward_after_terminal_outcome=reward_after_terminal_outcome,
        trace_event_types=["task_generated", "task_admitted", "execution_started", "execution_progress", "deadline_reached", "deadline_expired", "task_dropped", "reward_emitted"],
        trace_source_components=["traffic_generator", "environment"],
        evidence_notes=["terminal:dropped@4"] if terminal_outcome == "dropped" else ["terminal:completed@2"],
        source_event_count=8,
    )


def base_summary() -> dict[str, object]:
    return {
        "run_count": 3,
        "strategy_counts": {"environment_default_policy_probe": 3},
        "seed_counts": {0: 1, 1: 1, 2: 1},
        "total_tasks": 3,
        "completed_count": 1,
        "dropped_count": 2,
        "pending_at_horizon_count": 1,
        "action_counts": {"local": 3},
        "queue_counts": {"private": 2, "public": 1},
        "terminal_counts": {"completed": 1, "dropped": 2},
        "median_queue_wait_time": 2,
        "queue_pressure_task_ids": ["run-1:1", "run-1:2"],
        "task_generation_admission_overload_task_ids": ["run-1:1", "run-1:2"],
        "action_exposure_bias_task_ids": ["run-1:1"],
        "local_private_queue_blockage_task_ids": ["run-1:1"],
        "public_cloud_queue_blockage_task_ids": ["run-1:2"],
        "transmission_delay_admission_mismatch_task_ids": ["run-1:2"],
        "execution_progress_deadline_expires_first_task_ids": ["run-1:1"],
        "completion_reward_counter_mismatch_task_ids": [],
        "deadline_drop_ordering_issue_task_ids": [],
        "formula_mismatch_task_ids": [],
        "no_completion_problem_task_ids": ["run-1:3"],
        "deadline_ordering_ok": True,
        "reward_after_terminal_ok": True,
        "formula_consistency_ok": True,
        "trace_depth_ok": True,
        "runtime_bug_detected": False,
    }


class CompletionRootCauseClassifierTests(unittest.TestCase):
    def test_all_root_cause_classes_are_evaluated(self) -> None:
        lifecycles = [
            make_task(1, queue_type="private", selected_action="local", terminal_outcome="dropped"),
            make_task(2, queue_type="public", selected_action="horizontal", terminal_outcome="dropped", transmission_started_at=0, transmission_completed_at=2),
            make_task(3, queue_type="private", selected_action="local", terminal_outcome="completed", task_completed_at=2, reward_emitted_at=2, completed_before_deadline=True, queue_wait_time_slots=0),
        ]
        evaluations = RootCauseClassifier.evaluate_all(lifecycles, base_summary())
        self.assertEqual({evaluation.root_cause_class for evaluation in evaluations}, set(ROOT_CAUSE_CLASSES))
        self.assertEqual(len(evaluations), len(ROOT_CAUSE_CLASSES))

    def test_queue_pressure_classifier(self) -> None:
        lifecycles = [make_task(1, queue_type="private", queue_wait_time_slots=3), make_task(2, queue_type="private", queue_wait_time_slots=2)]
        evaluation = RootCauseClassifier.classify_queue_pressure(lifecycles, base_summary())
        self.assertTrue(evaluation.detected)
        self.assertGreater(evaluation.evidence_count, 0)
        self.assertIn("task_dropped", evaluation.supporting_event_types)

    def test_action_exposure_bias_classifier(self) -> None:
        summary = base_summary()
        summary["action_counts"] = {"local": 8, "horizontal": 1, "vertical": 1}
        lifecycles = [make_task(1, selected_action="local"), make_task(2, selected_action="horizontal")]
        evaluation = RootCauseClassifier.classify_action_exposure_bias(lifecycles, summary)
        self.assertTrue(evaluation.detected)
        self.assertEqual(evaluation.confidence, "medium")

    def test_execution_progress_deadline_expires_first_classifier(self) -> None:
        lifecycles = [make_task(1, execution_progress_slots=[1, 2], task_dropped_at=4, deadline_expired_at=4, completed_before_deadline=False)]
        evaluation = RootCauseClassifier.classify_execution_progress_deadline_expires_first(lifecycles, base_summary())
        self.assertTrue(evaluation.detected)
        self.assertIn("deadline_expired", evaluation.supporting_event_types)

    def test_completion_reward_counter_mismatch_classifier(self) -> None:
        lifecycles = [make_task(1, terminal_outcome="completed", task_completed_at=2, reward_emitted_at=None, reward_after_terminal_outcome=False, completed_before_deadline=True)]
        evaluation = RootCauseClassifier.classify_completion_emitted_but_reward_or_counter_path_wrong(lifecycles, base_summary())
        self.assertTrue(evaluation.detected)
        self.assertIn("task_completed", evaluation.supporting_event_types)

    def test_deadline_drop_ordering_issue_classifier(self) -> None:
        lifecycles = [make_task(1, task_dropped_at=3, deadline_expired_at=4)]
        evaluation = RootCauseClassifier.classify_deadline_drop_ordering_issue(lifecycles, base_summary())
        self.assertTrue(evaluation.detected)
        self.assertIn("reward_emitted", evaluation.supporting_event_types)

    def test_formula_unit_mismatch_classifier(self) -> None:
        summary = base_summary()
        summary["formula_consistency_ok"] = False
        lifecycles = [make_task(1)]
        evaluation = RootCauseClassifier.classify_formula_unit_mismatch(lifecycles, summary)
        self.assertTrue(evaluation.detected)
        self.assertEqual(evaluation.root_cause_class, "formula_unit_mismatch")

    def test_dominant_root_causes_are_ranked(self) -> None:
        evaluations = [
            RootCauseEvaluation("queue_pressure", True, True, 6, ["task_dropped"], ["a"], "queue pressure", "high", "audit"),
            RootCauseEvaluation("action_exposure_bias", True, True, 3, ["task_admitted"], ["b"], "action bias", "medium", "audit"),
            RootCauseEvaluation("formula_unit_mismatch", True, True, 1, ["execution_progress"], ["c"], "formula", "low", "audit"),
        ]
        ranked = RootCauseClassifier.rank(evaluations)
        self.assertEqual([item.root_cause_class for item in ranked], ["queue_pressure", "action_exposure_bias", "formula_unit_mismatch"])


if __name__ == "__main__":
    unittest.main()
