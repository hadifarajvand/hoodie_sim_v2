from __future__ import annotations

from collections import Counter
from statistics import fmean
from typing import Any

from src.analysis.terminal_lifecycle_accounting_50_100_comparison.repaired_terminal_evaluator import (
    build_policy_effect_after_terminal_repair,
)
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.lifecycle_classifier import normalize_selected_action

from .config import RECORD_SAMPLE_LIMIT
from .runtime_audit import build_runtime_event_path_audit


def _action_feasible(selected_action: str | None, feasibility: dict[str, Any]) -> bool:
    selected_action = normalize_selected_action(selected_action)
    if selected_action in {"local", "compute_local"}:
        return bool(feasibility.get("local_feasible_before_deadline", False))
    if selected_action in {"horizontal", "offload_horizontal"}:
        return bool(feasibility.get("horizontal_feasible_before_deadline", False))
    if selected_action in {"vertical", "offload_vertical"}:
        return bool(feasibility.get("vertical_feasible_before_deadline", False))
    return False


def _mean_latency(records: list[dict[str, Any]], outcome: str | None = None) -> float | None:
    values: list[float] = []
    for record in records:
        if outcome is not None and str(record.get("terminal_outcome")) != outcome:
            continue
        latency = record.get("latency_slots")
        if latency is not None:
            values.append(float(latency))
    return fmean(values) if values else None


def build_policy_feasibility_summary(
    policy_name: str,
    policy_result: dict[str, Any],
    task_feasibility_summary: dict[str, Any],
    runtime_audit: dict[str, Any],
) -> dict[str, Any]:
    task_records = policy_result.get("task_records", {})
    feasible_lookup = task_feasibility_summary.get("records_by_task_key", {})
    action_distribution = {str(action): int(count) for action, count in policy_result.get("evaluation_action_distribution", {}).items()}
    feasible_counts = Counter({"local": 0, "horizontal": 0, "vertical": 0})
    infeasible_counts = Counter({"local": 0, "horizontal": 0, "vertical": 0})
    completed_feasible = 0
    dropped_feasible = 0
    dropped_infeasible = 0
    for task_key, record in task_records.items():
        selected_action = normalize_selected_action(record.get("selected_action"))
        feasibility = feasible_lookup.get(task_key, {})
        is_feasible = _action_feasible(selected_action, feasibility)
        if selected_action in {"local", "compute_local"}:
            bucket = "local"
        elif selected_action in {"horizontal", "offload_horizontal"}:
            bucket = "horizontal"
        elif selected_action in {"vertical", "offload_vertical"}:
            bucket = "vertical"
        else:
            bucket = "local"
        if is_feasible:
            feasible_counts[bucket] += 1
        else:
            infeasible_counts[bucket] += 1
        if str(record.get("terminal_outcome")) == "completed" and is_feasible:
            completed_feasible += 1
        if str(record.get("terminal_outcome")) == "dropped" and is_feasible:
            dropped_feasible += 1
        if str(record.get("terminal_outcome")) == "dropped" and not is_feasible:
            dropped_infeasible += 1

    evaluation_reward_summary = policy_result.get("evaluation_reward_summary", {})
    reward_reconciliation = policy_result.get("reward_reconciliation_after_terminal_repair", {})
    terminal_reconciliation = policy_result.get("raw_vs_canonical_terminal_reconciliation", {})
    canonical_task_count = int(evaluation_reward_summary.get("canonical_task_count", len(task_records)))
    canonical_reward_total = float(reward_reconciliation.get("canonical_task_reward_total", 0.0))
    decision_count = int(policy_result.get("evaluation_decision_count", 0))
    completed_count = int(evaluation_reward_summary.get("completed_task_count", 0))
    dropped_count = int(evaluation_reward_summary.get("dropped_task_count", 0))
    pending_count = int(evaluation_reward_summary.get("pending_at_horizon_count", 0))
    terminal_task_count = int(evaluation_reward_summary.get("terminal_transition_count", completed_count + dropped_count))
    terminal_records = list(task_records.values())

    policy_summary = {
        "policy_name": policy_name,
        "decision_count": decision_count,
        "action_distribution": action_distribution,
        "canonical_task_count": canonical_task_count,
        "completed_count": completed_count,
        "dropped_count": dropped_count,
        "pending_count": pending_count,
        "completion_ratio": completed_count / canonical_task_count if canonical_task_count else 0.0,
        "drop_ratio": dropped_count / canonical_task_count if canonical_task_count else 0.0,
        "deadline_violation_ratio": dropped_count / canonical_task_count if canonical_task_count else 0.0,
        "mean_reward": float(evaluation_reward_summary.get("mean_reward", 0.0)),
        "reward_per_task": canonical_reward_total / canonical_task_count if canonical_task_count else 0.0,
        "reward_per_decision": canonical_reward_total / decision_count if decision_count else 0.0,
        "mean_terminal_latency_slots": _mean_latency(terminal_records),
        "mean_completion_latency_slots": _mean_latency(terminal_records, "completed"),
        "mean_drop_latency_slots": _mean_latency(terminal_records, "dropped"),
        "terminal_event_coverage_ratio": float(terminal_reconciliation.get("terminal_event_coverage_ratio", 0.0)),
        "reward_event_coverage_ratio": float(terminal_reconciliation.get("reward_event_coverage_ratio", 0.0)),
        "reward_reconciled": bool(reward_reconciliation.get("reward_reconciled", False)),
        "terminal_reconciled": bool(terminal_reconciliation.get("terminal_reconciled", False)),
        "feasible_task_count_by_action": dict(feasible_counts),
        "infeasible_task_count_by_action": dict(infeasible_counts),
        "completed_feasible_task_count": int(completed_feasible),
        "dropped_feasible_task_count": int(dropped_feasible),
        "dropped_infeasible_task_count": int(dropped_infeasible),
        "runtime_event_audit": runtime_audit,
        "sample_task_records": [dict(record) for record in list(task_records.values())[:RECORD_SAMPLE_LIMIT]],
    }
    return policy_summary


def build_policy_effect_completion_feasibility(
    *,
    trainer,
    checkpoint_results: list[dict[str, Any]],
    task_feasibility_summary: dict[str, Any],
    fixed_policy_seed: int,
    evaluation_episode_count: int,
    episode_length: int,
    evaluation_trace_bank_id: str,
) -> dict[str, Any]:
    base_policy_effect = build_policy_effect_after_terminal_repair(
        trainer=trainer,
        checkpoint_results=checkpoint_results,
        fixed_policy_seed=fixed_policy_seed,
        evaluation_episode_count=evaluation_episode_count,
        episode_length=episode_length,
        evaluation_trace_bank_id=evaluation_trace_bank_id,
    )
    runtime_audit = build_runtime_event_path_audit(
        base_policy_effect["policy_results"],
        task_feasibility_summary,
        checkpoint_results=checkpoint_results,
    )
    policy_results: dict[str, Any] = {}
    policy_feasibility_summary: dict[str, Any] = {}
    for policy_name, policy_result in base_policy_effect["policy_results"].items():
        enriched_policy_result = dict(policy_result)
        enriched_policy_result["runtime_event_audit"] = runtime_audit["by_policy"].get(policy_name, {})
        summary = build_policy_feasibility_summary(
            policy_name,
            enriched_policy_result,
            task_feasibility_summary,
            runtime_audit["by_policy"].get(policy_name, {}),
        )
        enriched_policy_result["policy_feasibility_summary"] = summary
        policy_results[policy_name] = enriched_policy_result
        policy_feasibility_summary[policy_name] = summary

    candidate_rewards = [
        float(policy_results[name]["evaluation_reward_summary"]["mean_reward"])
        for name in policy_results
        if name.startswith("candidate_policy_at_")
    ]
    candidate_distributions = [
        tuple(sorted(policy_results[name]["evaluation_action_distribution"].items()))
        for name in policy_results
        if name.startswith("candidate_policy_at_")
    ]
    candidate_terminal_outcomes = [
        (
            int(policy_results[name]["evaluation_reward_summary"]["completed_task_count"]),
            int(policy_results[name]["evaluation_reward_summary"]["dropped_task_count"]),
            int(policy_results[name]["evaluation_reward_summary"]["pending_at_horizon_count"]),
        )
        for name in policy_results
        if name.startswith("candidate_policy_at_")
    ]
    reward_same_across_policies = len({round(float(result["evaluation_reward_summary"]["mean_reward"]), 9) for result in policy_results.values()}) == 1
    terminal_same_across_policies = len(
        {
            (
                int(result["evaluation_reward_summary"]["completed_task_count"]),
                int(result["evaluation_reward_summary"]["dropped_task_count"]),
                int(result["evaluation_reward_summary"]["pending_at_horizon_count"]),
            )
            for result in policy_results.values()
        }
    ) == 1

    candidate_checkpoint_key = f"candidate_policy_at_{checkpoint_results[-1]['training_budget']}" if checkpoint_results else None
    candidate_vertical_collapse_in_evaluation = False
    if candidate_checkpoint_key and candidate_checkpoint_key in policy_results:
        candidate_vertical_collapse_in_evaluation = (
            float(policy_results[candidate_checkpoint_key]["evaluation_action_distribution"].get("vertical", 0))
            / max(float(policy_results[candidate_checkpoint_key]["evaluation_decision_count"]), 1.0)
            >= 0.95
        )
    candidate_vertical_collapse_in_training_replay_window = bool(base_policy_effect.get("candidate_policy_vertical_collapse_in_training_replay_window", False))

    return {
        **base_policy_effect,
        "policy_results": policy_results,
        "policy_feasibility_summary": policy_feasibility_summary,
        "runtime_event_path_audit": runtime_audit,
        "candidate_policy_vertical_collapse_in_evaluation": candidate_vertical_collapse_in_evaluation,
        "candidate_policy_vertical_collapse_in_training_replay_window": candidate_vertical_collapse_in_training_replay_window,
        "policy_affects_reward": "true" if not reward_same_across_policies else "false",
        "policy_affects_terminal_outcomes": "true" if not terminal_same_across_policies else "false",
        "candidate_reward_variation": max(candidate_rewards) - min(candidate_rewards) if candidate_rewards else 0.0,
        "candidate_action_distribution_changed_by_budget": len(set(candidate_distributions)) > 1,
        "candidate_terminal_outcomes_changed_by_budget": len(set(candidate_terminal_outcomes)) > 1,
        "canonical_policy_effect_summary": {
            "reward_same_across_policies": reward_same_across_policies,
            "terminal_same_across_policies": terminal_same_across_policies,
            "candidate_action_distribution_changed_by_budget": len(set(candidate_distributions)) > 1,
            "candidate_terminal_outcomes_changed_by_budget": len(set(candidate_terminal_outcomes)) > 1,
            "policy_affects_reward": "true" if not reward_same_across_policies else "false",
            "policy_affects_terminal_outcomes": "true" if not terminal_same_across_policies else "false",
        },
    }
