from __future__ import annotations

from typing import Any

from .config import RECORD_SAMPLE_LIMIT, REWARD_RECONCILIATION_TOLERANCE


def _sample_records(records: list[dict[str, Any]], limit: int = RECORD_SAMPLE_LIMIT) -> list[dict[str, Any]]:
    return [dict(record) for record in records[:limit]]


def _checkpoint_episode_count(checkpoint: dict[str, Any]) -> int:
    training_state = checkpoint.get("training_state", checkpoint)
    return int(
        checkpoint.get(
            "cumulative_training_episode_count",
            training_state.get("cumulative_training_episode_count", 0),
        )
    )


def build_checkpoint_comparison(checkpoint_results: list[dict[str, Any]]) -> dict[str, Any]:
    by_checkpoint: list[dict[str, Any]] = []
    for checkpoint in checkpoint_results:
        evaluation = checkpoint["evaluation_policy_result"]
        terminal_recon = evaluation["raw_vs_canonical_terminal_reconciliation"]
        reward_recon = evaluation["reward_reconciliation_after_terminal_repair"]
        completion_audit = evaluation["completion_path_audit"]
        paper_metrics = evaluation["paper_aligned_diagnostic_metrics"]
        by_checkpoint.append(
            {
                "training_budget": checkpoint["training_budget"],
                "cumulative_training_episode_count": _checkpoint_episode_count(checkpoint),
                "evaluation_decision_count": evaluation["evaluation_decision_count"],
                "evaluation_action_distribution": evaluation["evaluation_action_distribution"],
                "completed_count": evaluation["evaluation_reward_summary"]["completed_task_count"],
                "dropped_count": evaluation["evaluation_reward_summary"]["dropped_task_count"],
                "pending_count": evaluation["evaluation_reward_summary"]["pending_at_horizon_count"],
                "mean_reward": evaluation["evaluation_reward_summary"]["mean_reward"],
                "reward_per_task": paper_metrics["canonical_reward_per_task"],
                "reward_per_decision": paper_metrics["canonical_reward_per_decision"],
                "mean_terminal_latency_slots": paper_metrics["canonical_mean_terminal_latency_slots"],
                "terminal_event_coverage_ratio": terminal_recon["terminal_event_coverage_ratio"],
                "reward_event_coverage_ratio": terminal_recon["reward_event_coverage_ratio"],
                "raw_vs_canonical_reward_delta": reward_recon["raw_vs_canonical_reward_delta"],
                "duplicate_terminal_event_count": terminal_recon["duplicate_terminal_event_count"],
                "duplicate_reward_event_count": int(
                    reward_recon.get("raw_reward_event_count", reward_recon.get("raw_event_reward_count", 0))
                )
                - int(reward_recon.get("canonical_task_reward_count", reward_recon.get("canonical_reward_event_count", 0))),
                "reward_reconciled": reward_recon["reward_reconciled"],
                "terminal_reconciled": terminal_recon["terminal_reconciled"],
                "completion_path_audit": completion_audit,
            }
        )
    if len(by_checkpoint) == 2:
        first, second = by_checkpoint
        comparison = {
            "budget_pair": [first["training_budget"], second["training_budget"]],
            "mean_reward_delta": float(second["mean_reward"]) - float(first["mean_reward"]),
            "reward_per_task_delta": float(second["reward_per_task"]) - float(first["reward_per_task"]),
            "reward_per_decision_delta": float(second["reward_per_decision"]) - float(first["reward_per_decision"]),
            "completed_count_delta": int(second["completed_count"]) - int(first["completed_count"]),
            "dropped_count_delta": int(second["dropped_count"]) - int(first["dropped_count"]),
            "pending_count_delta": int(second["pending_count"]) - int(first["pending_count"]),
            "terminal_event_coverage_delta": float(second["terminal_event_coverage_ratio"]) - float(first["terminal_event_coverage_ratio"]),
            "reward_event_coverage_delta": float(second["reward_event_coverage_ratio"]) - float(first["reward_event_coverage_ratio"]),
            "raw_vs_canonical_reward_delta_change": float(second["raw_vs_canonical_reward_delta"]) - float(first["raw_vs_canonical_reward_delta"]),
            "action_distribution_changed": first["evaluation_action_distribution"] != second["evaluation_action_distribution"],
        }
    else:
        comparison = {}
    return {
        "checkpoint_budgets": [checkpoint["training_budget"] for checkpoint in checkpoint_results],
        "by_checkpoint": by_checkpoint,
        "comparison": comparison,
    }


def build_terminal_event_classification_summary(checkpoint_results: list[dict[str, Any]]) -> dict[str, Any]:
    by_checkpoint = []
    overall = {
        "terminal_outcome_event_count": 0,
        "lifecycle_only_event_count": 0,
        "reward_event_count": 0,
        "pending_event_count": 0,
        "event_type_counts": {},
    }
    for checkpoint in checkpoint_results:
        classification = checkpoint["evaluation_policy_result"]["terminal_event_classification"]
        classification_overall = classification.get("overall", classification)
        by_checkpoint.append({"training_budget": checkpoint["training_budget"], **classification_overall})
        overall["terminal_outcome_event_count"] += int(classification_overall["terminal_outcome_event_count"])
        overall["lifecycle_only_event_count"] += int(classification_overall["lifecycle_only_event_count"])
        overall["reward_event_count"] += int(classification_overall["reward_event_count"])
        overall["pending_event_count"] += int(classification_overall["pending_event_count"])
        for event_type, count in classification_overall["event_type_counts"].items():
            overall["event_type_counts"][event_type] = overall["event_type_counts"].get(event_type, 0) + int(count)
    return {
        "checkpoint_budgets": [checkpoint["training_budget"] for checkpoint in checkpoint_results],
        "by_checkpoint": by_checkpoint,
        "overall": overall,
        "sample_events": _sample_records(
            [
                event
                for checkpoint in checkpoint_results
                for event in checkpoint["evaluation_policy_result"]["terminal_event_classification"].get(
                    "sample_events",
                    checkpoint["evaluation_policy_result"]["terminal_event_classification"].get("overall", {}).get("sample_events", []),
                )
            ]
        ),
    }


def build_canonical_terminal_task_summary(checkpoint_results: list[dict[str, Any]]) -> dict[str, Any]:
    by_checkpoint = []
    overall = {
        "canonical_task_count": 0,
        "canonical_terminal_task_count": 0,
        "canonical_completion_count": 0,
        "canonical_drop_count": 0,
        "canonical_pending_count": 0,
        "canonical_unknown_count": 0,
        "raw_terminal_event_count": 0,
        "raw_reward_event_count": 0,
        "canonical_task_reward_total": 0.0,
        "canonical_task_reward_count": 0,
        "raw_vs_canonical_reward_delta": 0.0,
    }
    sample_task_outcomes: list[dict[str, Any]] = []
    for checkpoint in checkpoint_results:
        summary = checkpoint["evaluation_policy_result"]["canonical_terminal_task_summary"]
        by_checkpoint.append({"training_budget": checkpoint["training_budget"], **summary})
        overall["canonical_task_count"] += int(summary["overall"]["canonical_task_count"])
        overall["canonical_terminal_task_count"] += int(summary["overall"]["canonical_terminal_task_count"])
        overall["canonical_completion_count"] += int(summary["overall"]["canonical_completion_count"])
        overall["canonical_drop_count"] += int(summary["overall"]["canonical_drop_count"])
        overall["canonical_pending_count"] += int(summary["overall"]["canonical_pending_count"])
        overall["canonical_unknown_count"] += int(summary["overall"]["canonical_unknown_count"])
        overall["raw_terminal_event_count"] += int(summary["overall"]["raw_terminal_event_count"])
        overall["raw_reward_event_count"] += int(summary["overall"].get("raw_reward_event_count", summary["overall"].get("raw_reward_emission_count", 0)))
        overall["canonical_task_reward_total"] += float(summary["overall"]["canonical_task_reward_total"])
        overall["canonical_task_reward_count"] += int(summary["overall"].get("canonical_task_reward_count", summary["overall"].get("canonical_reward_event_count", 0)))
        overall["raw_vs_canonical_reward_delta"] += float(summary["overall"]["raw_vs_canonical_reward_delta"])
        sample_task_outcomes.extend(summary.get("sample_task_outcomes", []))
    return {
        "checkpoint_budgets": [checkpoint["training_budget"] for checkpoint in checkpoint_results],
        "by_checkpoint": by_checkpoint,
        "overall": overall,
        "sample_task_outcomes": _sample_records(sample_task_outcomes),
    }


def build_raw_vs_canonical_terminal_reconciliation(checkpoint_results: list[dict[str, Any]]) -> dict[str, Any]:
    by_checkpoint = []
    overall = {
        "raw_terminal_event_count": 0,
        "canonical_terminal_task_count": 0,
        "terminal_event_coverage_ratio": 0.0,
        "duplicate_terminal_event_count": 0,
        "raw_reward_event_count": 0,
        "canonical_reward_event_count": 0,
        "reward_event_coverage_ratio": 0.0,
        "raw_event_reward_total": 0.0,
        "canonical_task_reward_total": 0.0,
        "raw_vs_canonical_reward_delta": 0.0,
        "terminal_reconciled": False,
        "reward_reconciled": False,
        "raw_reward_event_recovery_blocked": False,
        "terminal_event_recovery_blocked": False,
    }
    for checkpoint in checkpoint_results:
        reconciliation = checkpoint["evaluation_policy_result"]["raw_vs_canonical_terminal_reconciliation"]
        by_checkpoint.append({"training_budget": checkpoint["training_budget"], **reconciliation})
        overall["raw_terminal_event_count"] += int(reconciliation["raw_terminal_event_count"])
        overall["canonical_terminal_task_count"] += int(reconciliation["canonical_terminal_task_count"])
        overall["duplicate_terminal_event_count"] += int(reconciliation["duplicate_terminal_event_count"])
        overall["raw_reward_event_count"] += int(reconciliation.get("raw_reward_event_count", reconciliation.get("raw_event_reward_count", 0)))
        overall["canonical_reward_event_count"] += int(reconciliation.get("canonical_reward_event_count", reconciliation.get("canonical_task_reward_count", 0)))
        overall["raw_event_reward_total"] += float(reconciliation["raw_event_reward_total"])
        overall["canonical_task_reward_total"] += float(reconciliation["canonical_task_reward_total"])
        overall["raw_vs_canonical_reward_delta"] += float(reconciliation["raw_vs_canonical_reward_delta"])
    overall["terminal_event_coverage_ratio"] = (
        float(overall["raw_terminal_event_count"]) / float(overall["canonical_terminal_task_count"]) if overall["canonical_terminal_task_count"] else 0.0
    )
    overall["reward_event_coverage_ratio"] = (
        float(overall["raw_reward_event_count"]) / float(overall["canonical_reward_event_count"]) if overall["canonical_reward_event_count"] else 0.0
    )
    overall["terminal_reconciled"] = overall["raw_terminal_event_count"] == overall["canonical_terminal_task_count"] and overall["duplicate_terminal_event_count"] == 0
    overall["reward_reconciled"] = abs(overall["raw_vs_canonical_reward_delta"]) <= REWARD_RECONCILIATION_TOLERANCE
    overall["raw_reward_event_recovery_blocked"] = overall["canonical_reward_event_count"] > 0 and overall["raw_reward_event_count"] == 0
    overall["terminal_event_recovery_blocked"] = overall["canonical_terminal_task_count"] > 0 and overall["raw_terminal_event_count"] == 0
    return {
        "checkpoint_budgets": [checkpoint["training_budget"] for checkpoint in checkpoint_results],
        "by_checkpoint": by_checkpoint,
        "overall": overall,
    }


def build_reward_reconciliation_after_terminal_repair(checkpoint_results: list[dict[str, Any]]) -> dict[str, Any]:
    by_checkpoint = []
    overall = {
        "raw_event_reward_total": 0.0,
        "raw_event_reward_count": 0,
        "canonical_task_reward_total": 0.0,
        "canonical_task_reward_count": 0,
        "raw_vs_canonical_reward_delta": 0.0,
        "reward_reconciled": False,
        "reward_reconciliation_tolerance": REWARD_RECONCILIATION_TOLERANCE,
        "raw_reward_event_recovery_blocked": False,
        "terminal_event_recovery_blocked": False,
    }
    for checkpoint in checkpoint_results:
        reconciliation = checkpoint["evaluation_policy_result"]["reward_reconciliation_after_terminal_repair"]
        by_checkpoint.append({"training_budget": checkpoint["training_budget"], **reconciliation})
        overall["raw_event_reward_total"] += float(reconciliation["raw_event_reward_total"])
        overall["raw_event_reward_count"] += int(reconciliation["raw_event_reward_count"])
        overall["canonical_task_reward_total"] += float(reconciliation["canonical_task_reward_total"])
        overall["canonical_task_reward_count"] += int(reconciliation["canonical_task_reward_count"])
        overall["raw_vs_canonical_reward_delta"] += float(reconciliation["raw_vs_canonical_reward_delta"])
    overall["reward_reconciled"] = abs(overall["raw_vs_canonical_reward_delta"]) <= REWARD_RECONCILIATION_TOLERANCE
    overall["raw_reward_event_recovery_blocked"] = overall["canonical_task_reward_count"] > 0 and overall["raw_event_reward_count"] == 0
    overall["terminal_event_recovery_blocked"] = overall["canonical_task_reward_count"] > 0 and overall["raw_event_reward_total"] == 0.0
    return {
        "checkpoint_budgets": [checkpoint["training_budget"] for checkpoint in checkpoint_results],
        "by_checkpoint": by_checkpoint,
        "overall": overall,
    }


def build_completion_path_audit(checkpoint_results: list[dict[str, Any]], policy_effect: dict[str, Any]) -> dict[str, Any]:
    by_checkpoint = []
    for checkpoint in checkpoint_results:
        audit = dict(checkpoint["evaluation_policy_result"]["completion_path_audit"])
        by_checkpoint.append({"training_budget": checkpoint["training_budget"], **audit})
    by_policy = {
        policy_name: dict(result["completion_path_audit"])
        for policy_name, result in policy_effect["policy_results"].items()
    }
    return {
        "by_checkpoint": by_checkpoint,
        "by_policy": by_policy,
    }


def build_paper_aligned_50_100_metrics(checkpoint_results: list[dict[str, Any]]) -> dict[str, Any]:
    by_checkpoint = []
    for checkpoint in checkpoint_results:
        metric = dict(checkpoint["evaluation_policy_result"]["paper_aligned_diagnostic_metrics"])
        by_checkpoint.append({"training_budget": checkpoint["training_budget"], **metric})
    return {"checkpoint_budgets": [checkpoint["training_budget"] for checkpoint in checkpoint_results], "by_checkpoint": by_checkpoint}
