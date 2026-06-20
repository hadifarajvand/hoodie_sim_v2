from __future__ import annotations

from typing import Any

from src.analysis.completion_path_deadline_feasibility_repair.feasibility import build_task_feasibility_summary
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.repaired_terminal_evaluator import (
    build_fixed_policy_suite,
    evaluate_policy_on_trace_bank_terminal_repaired,
)


def _policy_outcome_summary(policy_result: dict[str, Any], *, record_sample_limit: int) -> dict[str, Any]:
    task_records = policy_result.get("task_records", {})
    feasibility = build_task_feasibility_summary(task_records, record_sample_limit=record_sample_limit)
    reward_summary = policy_result.get("evaluation_reward_summary", {})
    completion_audit = policy_result.get("completion_path_audit", {})
    paper_metrics = policy_result.get("paper_aligned_diagnostic_metrics", {})
    decision_count = int(policy_result.get("evaluation_decision_count", 0))
    canonical_task_count = int(reward_summary.get("canonical_task_count", len(task_records)))
    feasible_task_count = canonical_task_count - int(feasibility.get("all_actions_infeasible_task_count", 0))
    total_reward = float(reward_summary.get("canonical_task_reward_total", 0.0))
    terminal_latencies = [float(record.get("latency_slots")) for record in task_records.values() if record.get("latency_slots") is not None]
    completion_latencies = [
        float(record.get("latency_slots")) for record in task_records.values() if record.get("terminal_outcome") == "completed" and record.get("latency_slots") is not None
    ]
    drop_latencies = [
        float(record.get("latency_slots")) for record in task_records.values() if record.get("terminal_outcome") == "dropped" and record.get("latency_slots") is not None
    ]
    completed_count = int(reward_summary.get("completed_task_count", 0))
    dropped_count = int(reward_summary.get("dropped_task_count", 0))
    pending_count = int(reward_summary.get("pending_at_horizon_count", 0))
    return {
        "policy_name": policy_result.get("policy_name"),
        "checkpoint_budget": policy_result.get("checkpoint_budget"),
        "decision_count": decision_count,
        "action_distribution": dict(policy_result.get("evaluation_action_distribution", {})),
        "feasible_task_count": feasible_task_count,
        "infeasible_task_count": int(feasibility.get("all_actions_infeasible_task_count", 0)),
        "feasible_task_count_by_action": dict(feasibility.get("feasible_task_count_by_action", {})),
        "infeasible_task_count_by_action": dict(feasibility.get("infeasible_task_count_by_action", {})),
        "completed_count": completed_count,
        "dropped_count": dropped_count,
        "pending_count": pending_count,
        "completion_ratio": completed_count / canonical_task_count if canonical_task_count else 0.0,
        "drop_ratio": dropped_count / canonical_task_count if canonical_task_count else 0.0,
        "deadline_violation_ratio": dropped_count / canonical_task_count if canonical_task_count else 0.0,
        "mean_reward": float(reward_summary.get("mean_reward", 0.0)),
        "reward_per_task": total_reward / canonical_task_count if canonical_task_count else 0.0,
        "reward_per_decision": total_reward / decision_count if decision_count else 0.0,
        "mean_completion_latency_slots": (sum(completion_latencies) / len(completion_latencies)) if completion_latencies else None,
        "mean_drop_latency_slots": (sum(drop_latencies) / len(drop_latencies)) if drop_latencies else None,
        "mean_terminal_latency_slots": (sum(terminal_latencies) / len(terminal_latencies)) if terminal_latencies else None,
        "completed_feasible_task_count": sum(1 for record in task_records.values() if record.get("terminal_outcome") == "completed" and record.get("selected_action") and record.get("selected_action") in {"local", "horizontal", "vertical"} and bool(record.get("canonical_reward"))),
        "dropped_feasible_task_count": sum(1 for record in task_records.values() if record.get("terminal_outcome") == "dropped" and not record.get("canonical_outcome") == "pending_at_horizon"),
        "dropped_infeasible_task_count": int(feasibility.get("all_actions_infeasible_task_count", 0)),
        "completion_path_audit": dict(completion_audit),
        "paper_aligned_diagnostic_metrics": dict(paper_metrics),
        "reward_reconciliation_after_terminal_repair": dict(policy_result.get("reward_reconciliation_after_terminal_repair", {})),
        "raw_vs_canonical_terminal_reconciliation": dict(policy_result.get("raw_vs_canonical_terminal_reconciliation", {})),
        "evaluation_action_distribution_source": policy_result.get("evaluation_action_distribution_source"),
        "evaluation_trace_bank_id": policy_result.get("evaluation_trace_bank_id"),
        "same_evaluation_trace_bank": bool(policy_result.get("same_evaluation_trace_bank", True)),
        "reward_event_records": {"record_count": len(policy_result.get("reward_event_records", [])) if isinstance(policy_result.get("reward_event_records"), list) else int(policy_result.get("reward_event_records", {}).get("record_count", 0))},
        "terminal_event_records": {"record_count": len(policy_result.get("terminal_event_records", [])) if isinstance(policy_result.get("terminal_event_records"), list) else int(policy_result.get("terminal_event_records", {}).get("record_count", 0))},
    }


def _canonical_policy_result(result: dict[str, Any], *, policy_name: str, checkpoint_budget: int) -> dict[str, Any]:
    canonical = dict(result)
    canonical["policy_name"] = policy_name
    canonical["checkpoint_budget"] = checkpoint_budget
    return canonical


def build_calibrated_policy_effect_comparison(
    *,
    trainer,
    checkpoint_results: list[dict[str, Any]],
    fixed_policy_seed: int,
    evaluation_episode_count: int,
    episode_length: int,
    evaluation_trace_bank_id: str,
    record_sample_limit: int,
) -> dict[str, Any]:
    candidate_50 = _canonical_policy_result(checkpoint_results[0]["evaluation_policy_result"], policy_name="candidate_policy_at_50", checkpoint_budget=50)
    candidate_100 = _canonical_policy_result(checkpoint_results[1]["evaluation_policy_result"], policy_name="candidate_policy_at_100", checkpoint_budget=100)

    fixed_suite = build_fixed_policy_suite(fixed_policy_seed)
    fixed_results: dict[str, dict[str, Any]] = {}
    for name in fixed_suite:
        fixed_results[name] = evaluate_policy_on_trace_bank_terminal_repaired(
            trainer=trainer,
            policy_name=name,
            policy_fn=fixed_suite[name],
            evaluation_episode_count=evaluation_episode_count,
            episode_length=episode_length,
            seed_base=fixed_policy_seed,
            checkpoint_budget=100,
            policy_kind="fixed",
            evaluation_trace_bank_id=evaluation_trace_bank_id,
            record_sample_limit=record_sample_limit,
        )

    policy_results = {
        "candidate_policy_at_50": candidate_50,
        "candidate_policy_at_100": candidate_100,
        **fixed_results,
    }
    policy_summaries = {name: _policy_outcome_summary(result, record_sample_limit=record_sample_limit) for name, result in policy_results.items()}
    candidate_50_summary = policy_summaries["candidate_policy_at_50"]
    candidate_100_summary = policy_summaries["candidate_policy_at_100"]
    fixed_policy_summaries = {name: policy_summaries[name] for name in ("fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy")}
    any_fixed_policy_completes = any(summary.get("completed_count", 0) > 0 for summary in fixed_policy_summaries.values())
    mean_rewards = {name: float(summary.get("mean_reward", 0.0)) for name, summary in policy_summaries.items()}
    completion_counts = {name: int(summary.get("completed_count", 0)) for name, summary in policy_summaries.items()}
    dropped_counts = {name: int(summary.get("dropped_count", 0)) for name, summary in policy_summaries.items()}
    candidate_100_action_distribution = candidate_100_summary.get("action_distribution", {})
    candidate_50_action_distribution = candidate_50_summary.get("action_distribution", {})
    candidate_100_replay = checkpoint_results[-1]["training_state"]["replay_window_action_distribution"] if checkpoint_results else {}
    return {
        "evaluation_trace_bank_id": evaluation_trace_bank_id,
        "evaluation_episode_count": evaluation_episode_count,
        "episode_length": episode_length,
        "raw_event_reward_static_across_budget": float(candidate_50_summary.get("reward_per_task", 0.0)) == float(candidate_100_summary.get("reward_per_task", 0.0)),
        "canonical_task_reward_static_across_budget": float(candidate_50_summary.get("reward_per_task", 0.0)) == float(candidate_100_summary.get("reward_per_task", 0.0)),
        "canonical_completion_rate_static_across_budget": int(candidate_50_summary.get("completed_count", 0)) == int(candidate_100_summary.get("completed_count", 0)),
        "canonical_drop_rate_static_across_budget": int(candidate_50_summary.get("dropped_count", 0)) == int(candidate_100_summary.get("dropped_count", 0)),
        "evaluation_action_distribution_static_across_budget": candidate_50_action_distribution == candidate_100_action_distribution,
        "policy_affects_reward": "true" if len(set(mean_rewards.values())) > 1 else "false",
        "policy_affects_terminal_outcomes": "true" if len({(count, dropped_counts[name]) for name, count in completion_counts.items()}) > 1 else "false",
        "policy_affects_reward_boolean": len(set(mean_rewards.values())) > 1,
        "policy_affects_terminal_outcomes_boolean": len({(count, dropped_counts[name]) for name, count in completion_counts.items()}) > 1,
        "candidate_action_distribution_changed_by_budget": candidate_50_action_distribution != candidate_100_action_distribution,
        "candidate_terminal_outcomes_changed_by_budget": (candidate_50_summary.get("completed_count", 0), candidate_50_summary.get("dropped_count", 0), candidate_50_summary.get("pending_count", 0)) != (candidate_100_summary.get("completed_count", 0), candidate_100_summary.get("dropped_count", 0), candidate_100_summary.get("pending_count", 0)),
        "candidate_policy_vertical_collapse_in_evaluation": float(candidate_100_action_distribution.get("vertical", 0)) / max(sum(candidate_100_action_distribution.values()), 1) >= 0.95,
        "candidate_policy_vertical_collapse_in_training_replay_window": float(candidate_100_replay.get("vertical", 0)) / max(sum(candidate_100_replay.values()), 1) >= 0.95 if candidate_100_replay else False,
        "evaluation_reward_static_after_terminal_repair": float(candidate_50_summary.get("reward_per_task", 0.0)) == float(candidate_100_summary.get("reward_per_task", 0.0))
        and float(candidate_50_summary.get("reward_per_task", 0.0)) == float(candidate_100_summary.get("reward_per_task", 0.0)),
        "policy_results": policy_results,
        "policy_summaries": policy_summaries,
        "candidate_policy_at_50": candidate_50_summary,
        "candidate_policy_at_100": candidate_100_summary,
        "fixed_policy_summaries": fixed_policy_summaries,
        "any_fixed_policy_completes": any_fixed_policy_completes,
        "candidate_reward_variation": abs(float(candidate_100_summary.get("mean_reward", 0.0)) - float(candidate_50_summary.get("mean_reward", 0.0))),
    }
