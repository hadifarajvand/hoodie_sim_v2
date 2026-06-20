from __future__ import annotations

from src.analysis.deadline_timeout_feasible_workload_calibration.policy_probe import build_calibrated_policy_effect_comparison


def test_policy_probe_compacts_fixed_policy_summary(monkeypatch):
    candidate_50 = {
        "policy_name": "candidate_policy_at_50",
        "checkpoint_budget": 50,
        "evaluation_action_distribution": {"local": 1},
        "evaluation_reward_summary": {
            "mean_reward": -1.0,
            "canonical_task_count": 1,
            "completed_task_count": 0,
            "dropped_task_count": 1,
            "pending_at_horizon_count": 0,
            "canonical_task_reward_total": -1.0,
            "raw_event_reward_total": -1.0,
            "evaluation_episode_count": 1,
        },
        "evaluation_action_distribution_source": "evaluation_episodes",
        "evaluation_decision_count": 1,
        "task_records": {"trace:0:1": {"terminal_outcome": "dropped", "selected_action": "local", "latency_slots": 2, "canonical_reward": -1.0}},
        "completion_path_audit": {},
        "paper_aligned_diagnostic_metrics": {},
    }
    candidate_100 = {
        "policy_name": "candidate_policy_at_100",
        "checkpoint_budget": 100,
        "evaluation_action_distribution": {"local": 2},
        "evaluation_reward_summary": {
            "mean_reward": -2.0,
            "canonical_task_count": 1,
            "completed_task_count": 0,
            "dropped_task_count": 1,
            "pending_at_horizon_count": 0,
            "canonical_task_reward_total": -2.0,
            "raw_event_reward_total": -2.0,
            "evaluation_episode_count": 1,
        },
        "evaluation_action_distribution_source": "evaluation_episodes",
        "evaluation_decision_count": 1,
        "task_records": {"trace:0:1": {"terminal_outcome": "dropped", "selected_action": "local", "latency_slots": 2, "canonical_reward": -2.0}},
        "completion_path_audit": {},
        "paper_aligned_diagnostic_metrics": {},
    }

    monkeypatch.setattr(
        "src.analysis.deadline_timeout_feasible_workload_calibration.policy_probe.build_fixed_policy_suite",
        lambda seed: {"fixed_local_policy": object(), "fixed_horizontal_policy": object(), "fixed_vertical_policy": object(), "random_legal_policy": object()},
    )

    def _evaluate_policy_on_trace_bank_terminal_repaired(**kwargs):
        name = kwargs["policy_name"]
        if name == "fixed_local_policy":
            return {
                "policy_name": name,
                "checkpoint_budget": 100,
                "evaluation_action_distribution": {"local": 3},
                "evaluation_reward_summary": {
                    "mean_reward": 4.0,
                    "canonical_task_count": 1,
                    "completed_task_count": 1,
                    "dropped_task_count": 0,
                    "pending_at_horizon_count": 0,
                    "canonical_task_reward_total": 4.0,
                    "raw_event_reward_total": 4.0,
                    "evaluation_episode_count": 1,
                },
                "evaluation_action_distribution_source": "evaluation_episodes",
                "task_records": {"trace:0:1": {"terminal_outcome": "completed", "selected_action": "local", "latency_slots": 1, "canonical_reward": 4.0}},
                "completion_path_audit": {},
                "paper_aligned_diagnostic_metrics": {},
                "reward_reconciliation_after_terminal_repair": {},
                "raw_vs_canonical_terminal_reconciliation": {},
            }
        return {
            "policy_name": name,
            "checkpoint_budget": 100,
            "evaluation_action_distribution": {"horizontal": 3 if name == "fixed_horizontal_policy" else 0, "vertical": 3 if name == "fixed_vertical_policy" else 0, "random": 3 if name == "random_legal_policy" else 0},
            "evaluation_reward_summary": {
                "mean_reward": 0.0,
                "canonical_task_count": 1,
                "completed_task_count": 0,
                "dropped_task_count": 1,
                "pending_at_horizon_count": 0,
                "canonical_task_reward_total": 0.0,
                "raw_event_reward_total": 0.0,
                "evaluation_episode_count": 1,
            },
            "evaluation_action_distribution_source": "evaluation_episodes",
            "task_records": {"trace:0:1": {"terminal_outcome": "dropped", "selected_action": "horizontal", "latency_slots": 2, "canonical_reward": 0.0}},
            "completion_path_audit": {},
            "paper_aligned_diagnostic_metrics": {},
            "reward_reconciliation_after_terminal_repair": {},
            "raw_vs_canonical_terminal_reconciliation": {},
        }

    monkeypatch.setattr("src.analysis.deadline_timeout_feasible_workload_calibration.policy_probe.evaluate_policy_on_trace_bank_terminal_repaired", _evaluate_policy_on_trace_bank_terminal_repaired)

    result = build_calibrated_policy_effect_comparison(
        trainer=object(),
        checkpoint_results=[{"evaluation_policy_result": candidate_50, "training_state": {"replay_window_action_distribution": {"local": 0}}}, {"evaluation_policy_result": candidate_100, "training_state": {"replay_window_action_distribution": {"local": 0}}}],
        fixed_policy_seed=0,
        evaluation_episode_count=100,
        episode_length=110,
        evaluation_trace_bank_id="trace-bank",
        record_sample_limit=3,
    )

    assert result["candidate_policy_at_50"]["decision_count"] == 1
    assert result["fixed_policy_summaries"]["fixed_local_policy"]["mean_reward"] == 4.0
    assert result["any_fixed_policy_completes"] is True
    assert set(result["fixed_policy_summaries"]) == {"fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy"}
