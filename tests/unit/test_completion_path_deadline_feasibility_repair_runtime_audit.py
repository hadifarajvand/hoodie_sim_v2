from __future__ import annotations

from src.analysis.completion_path_deadline_feasibility_repair.runtime_audit import build_runtime_event_path_audit


def _policy_result() -> dict[str, object]:
    task_records = {
        "trace-a:0:1": {
            "selected_action": "vertical",
            "terminal_outcome": "dropped",
            "lifecycle_event_types": ["deadline_reached", "deadline_expired", "task_dropped", "reward_emitted"],
            "latency_slots": 4,
        },
        "trace-a:0:2": {
            "selected_action": "vertical",
            "terminal_outcome": "dropped",
            "lifecycle_event_types": ["deadline_reached", "deadline_expired", "task_dropped", "reward_emitted"],
            "latency_slots": 5,
        },
    }
    return {
        "evaluation_decision_count": 2,
        "evaluation_action_distribution": {"local": 0, "horizontal": 0, "vertical": 2},
        "evaluation_reward_summary": {
            "evaluation_episode_count": 100,
            "mean_reward": -40.0,
            "completed_task_count": 0,
            "dropped_task_count": 2,
            "pending_at_horizon_count": 0,
            "terminal_transition_count": 2,
            "reward_bearing_transition_count": 2,
            "canonical_task_count": 2,
        },
        "raw_vs_canonical_terminal_reconciliation": {
            "raw_terminal_event_count": 4,
            "canonical_terminal_task_count": 2,
            "terminal_event_coverage_ratio": 2.0,
            "duplicate_terminal_event_count": 2,
            "raw_reward_event_count": 2,
            "canonical_reward_event_count": 2,
            "reward_event_coverage_ratio": 1.0,
            "raw_event_reward_total": -80.0,
            "canonical_task_reward_total": -80.0,
            "raw_vs_canonical_reward_delta": 0.0,
            "terminal_reconciled": True,
            "reward_reconciled": True,
            "raw_reward_event_recovery_blocked": False,
            "terminal_event_recovery_blocked": False,
        },
        "reward_reconciliation_after_terminal_repair": {
            "raw_event_reward_total": -80.0,
            "raw_event_reward_count": 2,
            "canonical_task_reward_total": -80.0,
            "canonical_task_reward_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_reconciled": True,
        },
        "task_records": task_records,
        "completion_path_audit": {
            "execution_started_event_count": 0,
            "execution_progress_event_count": 0,
            "execution_completed_event_count": 0,
            "task_completed_event_count": 0,
            "deadline_reached_event_count": 2,
            "deadline_expired_event_count": 2,
            "task_dropped_event_count": 2,
            "reward_emitted_event_count": 2,
            "pending_at_horizon_count": 0,
        },
        "terminal_event_classification": {
            "overall": {
                "event_type_counts": {
                    "deadline_reached": 2,
                    "deadline_expired": 2,
                    "task_dropped": 2,
                    "reward_emitted": 2,
                    "execution_started": 0,
                    "execution_progress": 0,
                    "execution_completed": 0,
                    "task_completed": 0,
                }
            }
        },
    }


def test_runtime_audit_counts_and_derived_metrics():
    audit = build_runtime_event_path_audit(
        {"candidate_policy_at_100": _policy_result()},
        {"records_by_task_key": {"trace-a:0:1": {"local_feasible_before_deadline": False, "horizontal_feasible_before_deadline": False, "vertical_feasible_before_deadline": False}, "trace-a:0:2": {"local_feasible_before_deadline": False, "horizontal_feasible_before_deadline": False, "vertical_feasible_before_deadline": False}}},
        checkpoint_results=[{"training_budget": 100, "evaluation_policy_result": _policy_result()}],
    )
    overall = audit["overall"]
    assert overall["execution_started_event_count"] == 0
    assert overall["execution_completed_event_count"] == 0
    assert overall["task_dropped_event_count"] == 2
    assert audit["by_checkpoint"][0]["training_budget"] == 100
    assert audit["by_policy"]["candidate_policy_at_100"]["tasks_with_positive_execution_progress_count"] == 0
