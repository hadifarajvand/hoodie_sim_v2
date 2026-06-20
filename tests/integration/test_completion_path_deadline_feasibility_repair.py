from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import src.analysis.completion_path_deadline_feasibility_repair.config as config_module
from src.analysis.completion_path_deadline_feasibility_repair import runner as feature_runner


def _task_record(task_id: int, selected_action: str, trace_prefix: str) -> dict[str, object]:
    return {
        "trace_id": trace_prefix,
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
        "queue_load": 1,
        "terminal_outcome": "dropped",
        "latency_slots": 4,
        "lifecycle_event_types": ["deadline_reached", "deadline_expired", "task_dropped", "reward_emitted"],
        "terminal_outcome_event_types": ["task_dropped"],
        "canonical_reward": -40.0,
        "canonical_reward_count": 1,
        "raw_reward_total": -40.0,
        "raw_reward_event_count": 1,
        "raw_terminal_event_count": 1,
    }


def _task_records(selected_actions: list[str], trace_prefix: str) -> dict[str, dict[str, object]]:
    return {
        f"{trace_prefix}:0:{index + 1}": _task_record(index + 1, action, trace_prefix)
        for index, action in enumerate(selected_actions)
    }


def _policy_summary(action_distribution: dict[str, int], *, vertical_collapse: bool = False) -> dict[str, object]:
    total = sum(action_distribution.values())
    return {
        "policy_name": "synthetic",
        "decision_count": total,
        "action_distribution": action_distribution,
        "canonical_task_count": total,
        "completed_count": 0,
        "dropped_count": total,
        "pending_count": 0,
        "completion_ratio": 0.0,
        "drop_ratio": 1.0,
        "deadline_violation_ratio": 1.0,
        "mean_reward": -40.0,
        "reward_per_task": -40.0,
        "reward_per_decision": -40.0,
        "mean_terminal_latency_slots": 4.0,
        "mean_completion_latency_slots": None,
        "mean_drop_latency_slots": 4.0,
        "terminal_event_coverage_ratio": 1.0,
        "reward_event_coverage_ratio": 1.0,
        "reward_reconciled": True,
        "terminal_reconciled": True,
        "feasible_task_count_by_action": {"local": 0, "horizontal": 0, "vertical": 0},
        "infeasible_task_count_by_action": dict(action_distribution),
        "completed_feasible_task_count": 0,
        "dropped_feasible_task_count": 0,
        "dropped_infeasible_task_count": total,
        "runtime_event_audit": {
            "policy_name": "synthetic",
            "decision_count": total,
            "transmission_started_event_count": 0,
            "transmission_completed_event_count": 0,
            "execution_started_event_count": 0,
            "execution_progress_event_count": 0,
            "execution_completed_event_count": 0,
            "task_completed_event_count": 0,
            "deadline_reached_event_count": total,
            "deadline_expired_event_count": total,
            "task_dropped_event_count": total,
            "reward_emitted_event_count": total,
            "pending_at_horizon_count": 0,
            "execution_progress_without_completion_count": 0,
            "transmission_completed_without_execution_count": 0,
            "execution_started_without_progress_count": 0,
            "deadline_before_execution_completion_count": total,
            "deadline_before_transmission_completion_count": total,
            "tasks_with_positive_execution_progress_count": 0,
            "tasks_with_zero_execution_progress_count": total,
            "tasks_with_remaining_cycles_at_drop_count": total,
            "canonical_task_count": total,
        },
        "sample_task_records": [],
        "candidate_policy_vertical_collapse_in_evaluation": vertical_collapse,
    }


def _fake_policy_effect(checkpoint_results: list[dict[str, object]], **_: object) -> dict[str, object]:
    policy_feasibility_summary = {
        "candidate_policy_at_50": _policy_summary({"local": 50, "vertical": 50}, vertical_collapse=False),
        "candidate_policy_at_100": _policy_summary({"vertical": 100}, vertical_collapse=True),
        "fixed_local_policy": _policy_summary({"local": 100}, vertical_collapse=False),
        "fixed_horizontal_policy": _policy_summary({"horizontal": 100}, vertical_collapse=False),
        "fixed_vertical_policy": _policy_summary({"vertical": 100}, vertical_collapse=True),
        "random_legal_policy": _policy_summary({"local": 34, "horizontal": 33, "vertical": 33}, vertical_collapse=False),
    }
    policy_results = {
        name: {
            "evaluation_reward_summary": {
                "completed_task_count": summary["completed_count"],
                "dropped_task_count": summary["dropped_count"],
                "pending_at_horizon_count": summary["pending_count"],
                "mean_reward": summary["mean_reward"],
            },
            "evaluation_action_distribution": summary["action_distribution"],
            "reward_reconciliation_after_terminal_repair": {
                "raw_event_reward_total": -40.0 * summary["canonical_task_count"],
                "raw_event_reward_count": summary["canonical_task_count"],
                "canonical_task_reward_total": -40.0 * summary["canonical_task_count"],
                "canonical_task_reward_count": summary["canonical_task_count"],
                "raw_vs_canonical_reward_delta": 0.0,
                "reward_reconciled": True,
            },
            "raw_vs_canonical_terminal_reconciliation": {
                "raw_terminal_event_count": summary["canonical_task_count"],
                "canonical_terminal_task_count": summary["canonical_task_count"],
                "terminal_event_coverage_ratio": 1.0,
                "duplicate_terminal_event_count": 0,
                "raw_reward_event_count": summary["canonical_task_count"],
                "canonical_reward_event_count": summary["canonical_task_count"],
                "reward_event_coverage_ratio": 1.0,
                "raw_event_reward_total": -40.0 * summary["canonical_task_count"],
                "canonical_task_reward_total": -40.0 * summary["canonical_task_count"],
                "raw_vs_canonical_reward_delta": 0.0,
                "terminal_reconciled": True,
                "reward_reconciled": True,
                "raw_reward_event_recovery_blocked": False,
                "terminal_event_recovery_blocked": False,
            },
            "completion_path_audit": summary["runtime_event_audit"],
        }
        for name, summary in policy_feasibility_summary.items()
    }
    by_checkpoint = [
        {"training_budget": int(checkpoint["training_budget"]), **policy_feasibility_summary[f"candidate_policy_at_{int(checkpoint['training_budget'])}"]["runtime_event_audit"]}
        for checkpoint in checkpoint_results
    ]
    return {
        "evaluation_trace_bank_id": "synthetic-trace-bank",
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "candidate_policy_vertical_collapse_in_evaluation": True,
        "candidate_policy_vertical_collapse_in_training_replay_window": True,
        "policy_affects_reward": "false",
        "policy_affects_terminal_outcomes": "false",
        "evaluation_reward_static_after_terminal_repair": True,
        "evaluation_action_distribution_static_across_budget": False,
        "raw_event_reward_static_across_budget": True,
        "canonical_task_reward_static_across_budget": True,
        "canonical_completion_rate_static_across_budget": True,
        "canonical_drop_rate_static_across_budget": True,
        "policy_results": policy_results,
        "policy_feasibility_summary": policy_feasibility_summary,
        "runtime_event_path_audit": {"overall_policy_name": "candidate_policy_at_100", "overall": policy_feasibility_summary["candidate_policy_at_100"]["runtime_event_audit"], "by_policy": {name: summary["runtime_event_audit"] for name, summary in policy_feasibility_summary.items()}, "by_checkpoint": by_checkpoint},
        "candidate_reward_variation": 0.0,
        "candidate_action_distribution_changed_by_budget": True,
        "candidate_terminal_outcomes_changed_by_budget": False,
        "canonical_policy_effect_summary": {},
    }


class FakeSession:
    def __init__(self, config: object) -> None:
        self.config = config
        self.campaign_config = SimpleNamespace(seed_bundle=SimpleNamespace(evaluation_trace_generation_seed=17), evaluation_trace_bank_id="synthetic-trace-bank")
        self.trainer = SimpleNamespace()
        self.calls: list[int] = []

    def train_to_budget(self, target_budget: int) -> dict[str, object]:
        self.calls.append(target_budget)
        return {
            "training_budget": target_budget,
            "cumulative_training_episode_count": target_budget,
            "optimizer_step_count": target_budget * 2,
            "replay_size": 10000,
            "loss_count": target_budget,
            "last_loss": 0.1,
            "loss_finite": True,
            "reward_summary": {"reward_count": target_budget, "total_reward": -40.0 * target_budget, "mean_reward": -40.0, "pending_at_horizon_count": 0},
            "replay_window_action_distribution": {"local": 0, "horizontal": 0, "vertical": target_budget},
            "replay_window_is_full_training_history": False,
            "replay_window_capacity": 10000,
            "replay_window_interpretation_warning": True,
            "cumulative_training_action_distribution": {"local": 0, "horizontal": 0, "vertical": target_budget},
        }

    def candidate_policy_result(self, *, checkpoint_budget: int) -> dict[str, object]:
        actions = ["local"] * 50 + ["vertical"] * 50 if checkpoint_budget == 50 else ["vertical"] * 100
        task_records = _task_records(actions, f"trace-{checkpoint_budget}")
        action_distribution = {"local": actions.count("local"), "horizontal": actions.count("horizontal"), "vertical": actions.count("vertical")}
        total = len(actions)
        return {
            "policy_name": f"candidate_policy_at_{checkpoint_budget}",
            "policy_kind": "candidate",
            "checkpoint_budget": checkpoint_budget,
            "evaluation_episode_count": 100,
            "episode_length": 110,
            "evaluation_trace_bank_id": "synthetic-trace-bank",
            "same_evaluation_trace_bank": True,
            "evaluation_action_distribution_source": "evaluation_episodes",
            "evaluation_action_distribution": action_distribution,
            "evaluation_decision_count": total,
            "evaluation_action_sequence_sample": [],
            "evaluation_legal_action_mask_distribution": {},
            "evaluation_action_by_trace_id": {},
            "evaluation_action_by_episode_id": {},
            "decision_records_summary": {"decision_count": total, "evaluation_action_distribution_source": "evaluation_episodes", "sample_records": []},
            "terminal_event_records": {"record_count": total, "sample_records": [], "recovered_from_finalized_tasks": True},
            "reward_event_records": {"record_count": total, "sample_records": [], "reward_available_count": total, "raw_reward_event_recovery_blocked": False},
            "task_records": task_records,
            "episode_summaries": [],
            "reward_reconciliation_tolerance": 1e-9,
            "raw_reward_event_recovery_blocked": False,
            "terminal_event_recovery_blocked": False,
            "raw_reward_event_count": total,
            "raw_reward_total": -40.0 * total,
            "raw_terminal_event_count": total,
            "episode_reward_totals": [-40.0] * 100,
            "candidate_policy_vertical_share": 1.0 if checkpoint_budget == 100 else 0.5,
            "evaluation_reward_summary": {
                "evaluation_episode_count": 100,
                "mean_reward": -40.0,
                "completed_task_count": 0,
                "dropped_task_count": total,
                "pending_at_horizon_count": 0,
                "unknown_task_count": 0,
                "terminal_transition_count": total,
                "reward_bearing_transition_count": total,
                "canonical_task_count": total,
                "canonical_task_reward_total": -40.0 * total,
                "canonical_task_reward_count": total,
                "raw_terminal_event_count": total,
                "raw_reward_emission_count": total,
                "raw_event_reward_total": -40.0 * total,
                "raw_event_reward_count": total,
                "raw_vs_canonical_reward_delta": 0.0,
                "reward_available_count": total,
                "raw_reward_event_recovery_blocked": False,
                "terminal_event_recovery_blocked": False,
                "trace_bank_disjoint": True,
                "trace_bank_ids": {"training": "training", "evaluation": "synthetic-trace-bank"},
                "trace_ids": [f"trace-{checkpoint_budget}"],
                "evaluation_on_training_traces": False,
                "same_evaluation_trace_bank": True,
                "candidate_reproduction_supported": True,
            },
            "terminal_event_classification": {"overall": {"terminal_outcome_event_count": total, "lifecycle_only_event_count": total * 2, "reward_event_count": total, "pending_event_count": 0, "event_type_counts": {"task_dropped": total, "deadline_reached": total, "deadline_expired": total, "reward_emitted": total, "execution_started": 0, "execution_progress": 0, "execution_completed": 0, "task_completed": 0}, "sample_events": []}},
            "canonical_terminal_task_summary": {"checkpoint_budget": checkpoint_budget, "overall": {"canonical_task_count": total, "canonical_terminal_task_count": total, "canonical_completion_count": 0, "canonical_drop_count": total, "canonical_pending_count": 0, "canonical_unknown_count": 0, "raw_terminal_event_count": total, "raw_reward_emission_count": total, "raw_event_reward_total": -40.0 * total, "raw_event_reward_count": total, "canonical_task_reward_total": -40.0 * total, "canonical_task_reward_count": total, "raw_vs_canonical_reward_delta": 0.0, "duplicate_terminal_event_count": 0, "duplicate_reward_event_count": 0, "double_count_detected": False, "canonical_completion_ratio": 0.0, "canonical_drop_ratio": 1.0, "canonical_deadline_violation_ratio": 1.0, "canonical_pending_ratio": 0.0, "canonical_mean_completion_latency_slots": None, "canonical_mean_drop_latency_slots": 4.0, "canonical_mean_terminal_latency_slots": 4.0, "canonical_reward_per_task": -40.0, "canonical_reward_per_decision": -40.0, "canonical_tasks_per_decision": 1.0}, "sample_task_outcomes": list(task_records.values())[:25]},
            "raw_vs_canonical_terminal_reconciliation": {"raw_terminal_event_count": total, "canonical_terminal_task_count": total, "terminal_event_coverage_ratio": 1.0, "duplicate_terminal_event_count": 0, "raw_reward_event_count": total, "canonical_reward_event_count": total, "reward_event_coverage_ratio": 1.0, "raw_event_reward_total": -40.0 * total, "canonical_task_reward_total": -40.0 * total, "raw_vs_canonical_reward_delta": 0.0, "terminal_reconciled": True, "reward_reconciled": True, "raw_reward_event_recovery_blocked": False, "terminal_event_recovery_blocked": False},
            "reward_reconciliation_after_terminal_repair": {"raw_event_reward_total": -40.0 * total, "raw_event_reward_count": total, "canonical_task_reward_total": -40.0 * total, "canonical_task_reward_count": total, "raw_vs_canonical_reward_delta": 0.0, "reward_reconciled": True, "reward_reconciliation_tolerance": 1e-9, "raw_reward_event_recovery_blocked": False, "terminal_event_recovery_blocked": False},
            "completion_path_audit": {"execution_started_event_count": 0, "execution_progress_event_count": 0, "execution_completed_event_count": 0, "task_completed_event_count": 0, "deadline_reached_event_count": total, "deadline_expired_event_count": total, "task_dropped_event_count": total, "reward_emitted_event_count": total, "pending_at_horizon_count": 0, "completed_canonical_task_count": 0, "execution_completed_but_no_task_completed_detected": False, "task_completed_but_no_reward_detected": False, "deadline_reached_then_task_dropped_duplicate_detected": False, "reward_emitted_without_terminal_outcome_detected": False, "terminal_outcome_without_reward_detected": False},
            "paper_aligned_diagnostic_metrics": {"checkpoint_budget": checkpoint_budget, "canonical_completion_ratio": 0.0, "canonical_drop_ratio": 1.0, "canonical_deadline_violation_ratio": 1.0, "canonical_pending_ratio": 0.0, "canonical_mean_completion_latency_slots": None, "canonical_mean_drop_latency_slots": 4.0, "canonical_mean_terminal_latency_slots": 4.0, "canonical_reward_per_task": -40.0, "canonical_reward_per_decision": -40.0, "canonical_tasks_per_decision": 1.0, "reward_reconciliation_status": "passed", "raw_reward_event_coverage_ratio": 1.0, "terminal_event_coverage_ratio": 1.0},
        }


def _fake_config(tmp_path: Path) -> SimpleNamespace:
    return SimpleNamespace(
        feature_id="068-completion-path-deadline-feasibility-repair",
        base_branch_name="067-terminal-lifecycle-accounting-50-100-comparison",
        branch_name="068-completion-path-deadline-feasibility-repair",
        output_dir=tmp_path,
        figures_dir=tmp_path / "figures",
        training_budgets=(50, 100),
        max_training_budget=100,
        evaluation_episode_count_per_checkpoint=100,
        episode_length=110,
        sampled_completion_path_max_task_decisions=100,
        expected_max_decision_slots=11000,
        training_mode="cumulative_staged_50_100_completion_feasibility",
        training_rerun_from_scratch=False,
        training_5000_run=False,
        reward_reconciliation_tolerance=1e-9,
        record_sample_limit=25,
        recommended_next_feature="Deadline / timeout repair",
    )


def test_runner_generates_artifacts_with_fake_session(monkeypatch, tmp_path):
    output_dir = tmp_path / "artifacts"
    fake_config = _fake_config(output_dir)
    monkeypatch.setattr(config_module, "CompletionPathFeasibilityConfig", lambda: fake_config)
    monkeypatch.setattr(feature_runner, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(feature_runner, "build_prerequisite_artifacts", lambda: {"feature_067_report": {"verified": True, "exists": True, "details": "ok"}})
    monkeypatch.setattr(feature_runner, "build_prerequisite_tags", lambda *args: [{"name": "feature_067_report_valid", "verified": True, "details": "ok"}])
    monkeypatch.setattr(feature_runner, "build_claim_safety_status", lambda: {"paper_reproduction_claim_made": False, "performance_superiority_claim_made": False, "baseline_superiority_claim_made": False, "claim_safety_passed": True})
    monkeypatch.setattr(feature_runner, "build_scope_guard_summary", lambda *args, **kwargs: {"working_tree_paths_approved": True, "staged_paths_approved": True, "base_branch_head_diff_approved": True, "forbidden_paths_detected": [], "approved_paths_detected": [], "status_classification": {}, "staged_classification": {}, "diff_classification": {}})
    monkeypatch.setattr(feature_runner, "TerminalLifecycleTrainingSession", FakeSession)
    monkeypatch.setattr(feature_runner, "build_policy_effect_completion_feasibility", _fake_policy_effect)

    payload = feature_runner.run_completion_path_feasibility()
    feature_runner.write_artifacts(payload)

    assert payload["checkpoint_budgets"] == [50, 100]
    assert payload["max_training_budget"] == 100
    assert payload["training_5000_run"] is False
    assert payload["diagnostic_decision"]["recommended_next_action"] == "fix_deadline_timeout_configuration_next"
    assert payload["completion_failure_classification"]["root_cause"] == "all_tasks_infeasible_under_current_deadlines"
    assert payload["evaluation_coverage_classification"]["one_decision_per_episode_observed"] is True
    assert payload["checkpoint_50_100_feasibility_comparison"]["comparison_classification"] == "action_changed_but_outcome_static"
    assert payload["final_verdict"] == "completion_path_feasibility_repair_ready"

    required_files = [
        "completion-path-feasibility-report.json",
        "completion-path-feasibility-report.md",
        "task-feasibility-summary.json",
        "action-path-feasibility.json",
        "runtime-event-path-audit.json",
        "completion-failure-classification.json",
        "policy-effect-completion-feasibility.json",
        "checkpoint-50-100-feasibility-comparison.json",
        "evaluation-coverage-classification.json",
        "diagnostic-decision.json",
        "final-completion-path-summary.md",
        "figure-manifest.json",
    ]
    for filename in required_files:
        assert (output_dir / filename).exists()
    assert (output_dir / "figures" / "figure_01_action_path_feasibility_50_vs_100.png").exists()
    assert (output_dir / "figures" / "figure_02_completion_drop_by_policy.png").exists()
    assert (output_dir / "figures" / "figure_03_runtime_event_path_counts.png").exists()
    assert (output_dir / "figures" / "figure_04_deadline_slack_distribution.png").exists()
    assert (output_dir / "figures" / "figure_05_feasible_vs_completed_tasks.png").exists()
