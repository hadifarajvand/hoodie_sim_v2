from __future__ import annotations

from src.analysis.completion_path_deadline_feasibility_repair.feasibility import (
    build_action_path_feasibility,
    build_completion_path_probe,
    build_evaluation_coverage_classification,
    build_task_feasibility_summary,
    estimate_task_action_feasibility,
)


def _task(task_id: int, selected_action: str = "vertical") -> dict[str, object]:
    return {
        "trace_id": "trace-a",
        "episode_id": 0,
        "task_id": task_id,
        "arrival_slot": 0,
        "absolute_deadline_slot": 4,
        "timeout_length": 4,
        "task_size": 12.0,
        "processing_density": 2.0,
        "selected_action": selected_action,
        "legal_action_mask": {"local": True, "horizontal": True, "vertical": True},
        "source_agent_id": 1,
        "queue_load": 2,
    }


def test_feasibility_estimation_and_summary_marks_all_actions_infeasible():
    estimate = estimate_task_action_feasibility(_task(1))
    assert estimate["local_feasible_before_deadline"] is False
    assert estimate["horizontal_feasible_before_deadline"] is False
    assert estimate["vertical_feasible_before_deadline"] is False

    summary = build_task_feasibility_summary({"trace-a:0:1": _task(1), "trace-a:0:2": _task(2, "local")})
    assert summary["total_task_count"] == 2
    assert summary["all_actions_infeasible"] is True
    assert summary["local_feasible_task_count"] == 0
    assert summary["horizontal_feasible_task_count"] == 0
    assert summary["vertical_feasible_task_count"] == 0

    action_path = build_action_path_feasibility(summary)
    assert action_path["all_actions_infeasible"] is True
    assert action_path["total_task_count"] == 2


def test_completion_probe_classifies_episode_sampled_evaluation():
    evaluation_result = {
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "evaluation_decision_count": 100,
        "task_records": {"trace-a:0:1": _task(1)},
    }
    probe = build_completion_path_probe(evaluation_result, max_task_decisions_to_analyze=100)
    classification = build_evaluation_coverage_classification(probe)
    assert classification["evaluation_mode"] == "full_episode_single_task_evaluation"
    assert classification["one_decision_per_episode_observed"] is True
    assert classification["full_step_decision_coverage_unavailable"] is True
