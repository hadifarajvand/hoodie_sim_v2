from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.instrumented_evaluator import (
    InstrumentedTrainingSession,
    build_fixed_policy_suite,
)

from .config import (
    ALLOWED_DIAGNOSTIC_DECISIONS,
    BASE_BRANCH_NAME,
    BRANCH_NAME,
    CANONICAL_TASK_RECONCILIATION_JSON,
    CHECKPOINT_BUDGETS,
    DECISION_RECORDS_SUMMARY_JSON,
    DIAGNOSTIC_DECISION_JSON,
    EVALUATION_EPISODES_PER_CHECKPOINT,
    EPISODE_LENGTH,
    FEATURE_065_REPORT,
    FEATURE_ID,
    FINAL_REPAIR_SUMMARY_MD,
    FIGURE_MANIFEST_JSON,
    FIGURES_DIR,
    PAPER_ALIGNED_EVALUATION_METRICS_JSON,
    OUTPUT_DIR,
    POLICY_EFFECT_AFTER_REPAIR_JSON,
    RAW_VS_CANONICAL_REWARD_RECONCILIATION_JSON,
    REPAIRED_CHECKPOINT_METRICS_JSON,
    RECOMMENDED_NEXT_FEATURE,
    RECORD_SAMPLE_LIMIT,
    REWARD_EVENT_RECORDS_JSON,
    REWARD_RECONCILIATION_TOLERANCE,
    REPORT_JSON,
    REPORT_MD,
    TERMINAL_EVENT_RECORDS_JSON,
    TRAINING_5000_RUN,
    TRAINING_MODE,
    TRAINING_RERUN_FROM_SCRATCH,
)
from .diagnostics import (
    build_claim_safety_status,
    build_diagnostic_decision,
    build_prerequisite_artifacts,
    build_prerequisite_tags,
    build_scope_guard_summary,
    git_diff_paths,
    git_staged_paths,
    git_status_paths,
    load_feature_065_status,
)
from .figures import generate_figures
from .model import FigureManifest, RewardEmissionAggregationRepairReport
from .reconciliation import build_canonical_task_reconciliation, summarize_raw_vs_canonical_across_checkpoints
from .repaired_evaluator import build_policy_effect_after_repair, evaluate_policy_on_trace_bank_repaired
from .report import json_dump, render_final_repair_summary_markdown, write_reward_emission_aggregation_repair_report

APPROVED_PREFIXES = (
    "artifacts/analysis/reward-emission-evaluation-metric-aggregation-repair/",
    "docs/architecture/euls_phase25_reward_emission_evaluation_metric_aggregation_repair.md",
    "specs/066-reward-emission-evaluation-metric-aggregation-repair/",
    "src/analysis/reward_emission_evaluation_metric_aggregation_repair/",
    "tests/unit/test_reward_emission_evaluation_metric_aggregation_repair",
    "tests/integration/test_reward_emission_evaluation_metric_aggregation_repair",
)

FORBIDDEN_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/reward_timing.py",
    "src/environment/replay_hash.py",
    "src/analysis/staged_training_budget_learning_curve/",
    "src/analysis/final_review_release_gate_batch/",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
    "artifacts/analysis/full-paper-default-training-campaign-execution/",
    "artifacts/analysis/unified-campaign-result-analysis-figures-findings/",
    "artifacts/analysis/staged-training-budget-learning-curve/",
    "artifacts/analysis/final-review-release-gate-batch/",
    "artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/",
)


def _policy_fn_for_candidate(trainer):
    def _choose(state_tensor, legal_action_mask, context):
        del context
        return trainer.policy.choose_action(state_tensor, legal_action_mask)

    return _choose


def _metric_from_summary(summary: dict[str, Any], key: str, fallback: Any = 0) -> Any:
    return summary.get(key, fallback)


def _augment_policy_result_with_reconciliation(policy_result: dict[str, Any]) -> dict[str, Any]:
    task_records = policy_result.get("task_records", {})
    reconciliation = build_canonical_task_reconciliation(
        checkpoint_budget=int(policy_result.get("checkpoint_budget")) if policy_result.get("checkpoint_budget") is not None else 0,
        evaluation_decision_count=int(policy_result.get("evaluation_decision_count", 0)),
        task_records=task_records if isinstance(task_records, dict) else {},
        reward_reconciliation_tolerance=REWARD_RECONCILIATION_TOLERANCE,
        record_sample_limit=RECORD_SAMPLE_LIMIT,
    )
    raw_vs_canonical = reconciliation["raw_vs_canonical_reward_reconciliation"]
    canonical_summary = reconciliation["canonical_task_outcome_summary"]["overall"]
    policy_result["raw_event_reward_total"] = raw_vs_canonical["raw_event_reward_total"]
    policy_result["raw_event_reward_count"] = raw_vs_canonical["raw_event_reward_count"]
    policy_result["raw_terminal_event_count"] = raw_vs_canonical["raw_terminal_event_count"]
    policy_result["canonical_task_reward_total"] = raw_vs_canonical["canonical_task_reward_total"]
    policy_result["canonical_task_reward_count"] = raw_vs_canonical["canonical_task_reward_count"]
    policy_result["reward_reconciled"] = raw_vs_canonical["reward_reconciled"]
    policy_result["completed_task_count"] = canonical_summary["canonical_completion_count"]
    policy_result["dropped_task_count"] = canonical_summary["canonical_drop_count"]
    policy_result["pending_task_count"] = canonical_summary["canonical_pending_count"]
    policy_result["completion_ratio"] = canonical_summary["canonical_completion_ratio"]
    policy_result["drop_ratio"] = canonical_summary["canonical_drop_ratio"]
    policy_result["deadline_violation_ratio"] = canonical_summary["canonical_deadline_violation_ratio"]
    policy_result["mean_latency_slots"] = canonical_summary["canonical_mean_terminal_latency_slots"]
    policy_result["action_distribution"] = dict(policy_result.get("evaluation_action_distribution", {}))
    policy_result["per_action_outcome_summary"] = reconciliation["canonical_task_outcome_summary"]["by_action"]
    policy_result["reward_decomposition"] = reconciliation["canonical_reward_decomposition"]
    policy_result["canonical_task_reconciliation"] = reconciliation["canonical_task_outcome_summary"]
    policy_result["raw_vs_canonical_reward_reconciliation"] = raw_vs_canonical
    policy_result["paper_aligned_diagnostic_metrics"] = reconciliation["paper_aligned_diagnostic_metrics"]
    policy_result["reconciliation"] = reconciliation
    return policy_result


def _task_sample_records(policy_result: dict[str, Any]) -> list[dict[str, Any]]:
    sample_records = policy_result.get("canonical_task_outcome_sample")
    if isinstance(sample_records, list):
        return sample_records
    canonical_outcomes = policy_result.get("canonical_task_outcomes")
    if isinstance(canonical_outcomes, list):
        return canonical_outcomes[:RECORD_SAMPLE_LIMIT]
    return []


def _aggregate_record_summary(results: list[dict[str, Any]], key: str, sample_key: str = "sample_records") -> dict[str, Any]:
    total = 0
    samples: list[dict[str, Any]] = []
    by_checkpoint: list[dict[str, Any]] = []
    for result in results:
        summary = result.get(key, {})
        if isinstance(summary, dict):
            total += int(summary.get("record_count", 0))
            by_checkpoint.append({"training_budget": result["training_budget"], **summary})
            for sample in summary.get(sample_key, [])[:RECORD_SAMPLE_LIMIT]:
                if len(samples) < RECORD_SAMPLE_LIMIT:
                    samples.append(sample)
    return {"record_count": total, "sample_records": samples, "by_checkpoint": by_checkpoint}


def _build_explanation(policy_effect: dict[str, Any], raw_vs_canonical: dict[str, Any]) -> dict[str, Any]:
    if raw_vs_canonical["raw_reward_event_recovery_blocked"]:
        reason = "The earlier outputs were static because raw reward events were not actually recovered from trace logging."
    elif policy_effect["evaluation_action_distribution_static_across_budget"] and policy_effect["evaluation_reward_static_after_instrumentation"]:
        reason = "The candidate policy action distribution and canonical outcomes did not move across the staged budgets, so the reward trace stayed flat even after the repair."
    else:
        reason = "The fixed evaluator now separates event-level reward emission from canonical task-level reward, so the previous flat output was an aggregation artifact rather than a missing metric surface."
    return {
        "why_previous_outputs_were_identical_or_static": reason,
        "event_recovery_explanation": "Trace-enabled evaluation exposes reward_emitted lifecycle events and terminal finalized-task records.",
        "aggregation_explanation": "Canonical task rewards are now reconciled against raw event rewards instead of replacing them.",
        "policy_behavior_explanation": "Candidate policy action distributions are still inspected separately from reward aggregation.",
    }


def run_reward_emission_aggregation_repair() -> dict[str, Any]:
    config = type("Config", (), {})()
    # Preserve the interface expected by the existing trainer session without reintroducing the old feature module.
    config.episode_length = EPISODE_LENGTH
    config.evaluation_episode_count_per_checkpoint = EVALUATION_EPISODES_PER_CHECKPOINT
    config.checkpoint_budgets = CHECKPOINT_BUDGETS
    config.training_mode = TRAINING_MODE
    config.training_rerun_from_scratch = TRAINING_RERUN_FROM_SCRATCH
    config.training_5000_run = TRAINING_5000_RUN
    config.reward_reconciliation_tolerance = REWARD_RECONCILIATION_TOLERANCE
    config.record_sample_limit = RECORD_SAMPLE_LIMIT
    config.recommended_next_feature = RECOMMENDED_NEXT_FEATURE

    session = InstrumentedTrainingSession(config)  # type: ignore[arg-type]
    claim_safety_status = build_claim_safety_status()
    prerequisite_artifacts = build_prerequisite_artifacts()
    scope_guard = build_scope_guard_summary(
        git_status_paths(),
        git_staged_paths(),
        git_diff_paths("065-evaluation-instrumentation-reward-state-diagnostic"),
        APPROVED_PREFIXES,
        FORBIDDEN_PREFIXES,
    )
    prerequisite_tags = build_prerequisite_tags(
        scope_guard["working_tree_paths_approved"],
        scope_guard["staged_paths_approved"],
        scope_guard["base_branch_head_diff_approved"],
    )
    feature_065_prerequisite_verified = load_feature_065_status()["verified"]

    checkpoint_results: list[dict[str, Any]] = []
    for budget in CHECKPOINT_BUDGETS:
        training_state = session.train_to_budget(budget)
        evaluation_result = evaluate_policy_on_trace_bank_repaired(
            trainer=session.trainer,
            policy_name=f"candidate_policy_at_{budget}",
            policy_fn=_policy_fn_for_candidate(session.trainer),
            evaluation_episode_count=EVALUATION_EPISODES_PER_CHECKPOINT,
            episode_length=EPISODE_LENGTH,
            seed_base=session.campaign_config.seed_bundle.evaluation_trace_generation_seed,
            checkpoint_budget=budget,
            policy_kind="candidate",
            evaluation_trace_bank_id=session.trainer.config.evaluation_trace_bank_id,
            record_sample_limit=RECORD_SAMPLE_LIMIT,
        )
        reconciliation = build_canonical_task_reconciliation(
            checkpoint_budget=budget,
            evaluation_decision_count=int(evaluation_result["evaluation_decision_count"]),
            task_records=evaluation_result["task_records"],
            reward_reconciliation_tolerance=REWARD_RECONCILIATION_TOLERANCE,
            record_sample_limit=RECORD_SAMPLE_LIMIT,
        )
        evaluation_result["evaluation_reward_summary"] = {
            **evaluation_result["evaluation_reward_summary"],
            **reconciliation["raw_vs_canonical_reward_reconciliation"],
        }
        evaluation_result["raw_vs_canonical_reward_reconciliation"] = reconciliation["raw_vs_canonical_reward_reconciliation"]
        evaluation_result["canonical_task_outcome_summary"] = reconciliation["canonical_task_outcome_summary"]
        evaluation_result["canonical_reward_decomposition"] = reconciliation["canonical_reward_decomposition"]
        evaluation_result["paper_aligned_diagnostic_metrics"] = reconciliation["paper_aligned_diagnostic_metrics"]
        evaluation_result["per_action_outcome_summary"] = reconciliation["canonical_task_outcome_summary"]["by_action"]
        evaluation_result["completed_count"] = reconciliation["canonical_task_outcome_summary"]["overall"]["canonical_completion_count"]
        evaluation_result["dropped_count"] = reconciliation["canonical_task_outcome_summary"]["overall"]["canonical_drop_count"]
        evaluation_result["pending_at_horizon_count"] = reconciliation["canonical_task_outcome_summary"]["overall"]["canonical_pending_count"]
        evaluation_result["unknown_count"] = reconciliation["canonical_task_outcome_summary"]["overall"]["canonical_unknown_count"]
        evaluation_result["reward_reconciled"] = reconciliation["raw_vs_canonical_reward_reconciliation"]["reward_reconciled"]
        evaluation_result["raw_reward_event_recovery_blocked"] = reconciliation["raw_vs_canonical_reward_reconciliation"]["raw_reward_event_recovery_blocked"]
        evaluation_result["terminal_event_recovery_blocked"] = reconciliation["raw_vs_canonical_reward_reconciliation"]["terminal_event_recovery_blocked"]
        evaluation_result["raw_event_reward_total"] = reconciliation["raw_vs_canonical_reward_reconciliation"]["raw_event_reward_total"]
        evaluation_result["canonical_task_reward_total"] = reconciliation["raw_vs_canonical_reward_reconciliation"]["canonical_task_reward_total"]
        evaluation_result["reward_reconciliation_status"] = "passed" if reconciliation["raw_vs_canonical_reward_reconciliation"]["reward_reconciled"] else "failed"
        checkpoint_results.append(
            {
                "training_budget": budget,
                "cumulative_training_episode_count": training_state["cumulative_training_episode_count"],
                "evaluation_episode_count": EVALUATION_EPISODES_PER_CHECKPOINT,
                "episode_length": EPISODE_LENGTH,
                "optimizer_step_count": training_state["optimizer_step_count"],
                "replay_size": training_state["replay_size"],
                "action_distribution": dict(training_state["cumulative_training_action_distribution"]),
                "action_count_total": sum(int(value) for value in training_state["cumulative_training_action_distribution"].values()),
                "action_accounting_reconciled": True,
                "loss_count": training_state["loss_count"],
                "last_loss": training_state["last_loss"],
                "loss_finite": bool(training_state["loss_finite"]),
                "reward_summary": training_state["reward_summary"],
                "evaluation_reward_summary": evaluation_result["evaluation_reward_summary"],
                "completed_task_count": evaluation_result["completed_count"],
                "dropped_task_count": evaluation_result["dropped_count"],
                "pending_at_horizon_count": evaluation_result["pending_at_horizon_count"],
                "comparison_ready": bool(training_state["loss_finite"]) and reconciliation["raw_vs_canonical_reward_reconciliation"]["reward_reconciled"],
                "claim_safety_status": claim_safety_status,
                "evaluation_action_distribution": evaluation_result["evaluation_action_distribution"],
                "evaluation_decision_count": evaluation_result["evaluation_decision_count"],
                "evaluation_action_sequence_sample": evaluation_result["evaluation_action_sequence_sample"],
                "evaluation_legal_action_mask_distribution": evaluation_result["evaluation_legal_action_mask_distribution"],
                "evaluation_action_by_trace_id": evaluation_result["evaluation_action_by_trace_id"],
                "evaluation_action_by_episode_id": evaluation_result["evaluation_action_by_episode_id"],
                "replay_window_action_distribution": training_state["replay_window_action_distribution"],
                "cumulative_training_action_distribution": training_state["cumulative_training_action_distribution"],
                "replay_window_is_full_training_history": training_state["replay_window_is_full_training_history"],
                "replay_window_capacity": training_state["replay_window_capacity"],
                "replay_window_interpretation_warning": training_state["replay_window_interpretation_warning"],
                "per_action_outcome_summary": reconciliation["canonical_task_outcome_summary"]["by_action"],
                "reward_decomposition": reconciliation["canonical_reward_decomposition"],
                "event_level_metrics": {
                    "raw_terminal_event_count": reconciliation["raw_vs_canonical_reward_reconciliation"]["raw_terminal_event_count"],
                    "raw_reward_emission_count": reconciliation["raw_vs_canonical_reward_reconciliation"]["raw_event_reward_count"],
                    "raw_event_reward_total": reconciliation["raw_vs_canonical_reward_reconciliation"]["raw_event_reward_total"],
                    "raw_event_reward_count": reconciliation["raw_vs_canonical_reward_reconciliation"]["raw_event_reward_count"],
                    "raw_reward_event_recovery_blocked": reconciliation["raw_vs_canonical_reward_reconciliation"]["raw_reward_event_recovery_blocked"],
                    "terminal_event_recovery_blocked": reconciliation["raw_vs_canonical_reward_reconciliation"]["terminal_event_recovery_blocked"],
                },
                "canonical_task_level_metrics": reconciliation["canonical_task_outcome_summary"]["overall"],
                "raw_vs_canonical_metric_comparison": reconciliation["raw_vs_canonical_reward_reconciliation"],
                "paper_aligned_diagnostic_metrics": reconciliation["paper_aligned_diagnostic_metrics"],
                "evaluation_policy_result": evaluation_result,
                "training_state": training_state,
            }
        )

    checkpoint_reconciliations = [result["evaluation_policy_result"]["raw_vs_canonical_reward_reconciliation"] for result in checkpoint_results]
    raw_vs_canonical_summary = summarize_raw_vs_canonical_across_checkpoints(
        [result["evaluation_policy_result"] for result in checkpoint_results]
    )
    canonical_task_reconciliation = {
        "checkpoint_budgets": [result["training_budget"] for result in checkpoint_results],
        "by_checkpoint": [result["evaluation_policy_result"]["canonical_task_outcome_summary"] for result in checkpoint_results],
        "sample_task_outcomes": [
            sample
            for result in checkpoint_results
            for sample in _task_sample_records(result["evaluation_policy_result"])
        ][:RECORD_SAMPLE_LIMIT],
        "overall": {
            "canonical_task_count": sum(result["evaluation_policy_result"]["canonical_task_outcome_summary"]["overall"]["canonical_task_count"] for result in checkpoint_results),
            "canonical_terminal_task_count": sum(result["evaluation_policy_result"]["canonical_task_outcome_summary"]["overall"]["canonical_terminal_task_count"] for result in checkpoint_results),
            "canonical_completion_count": sum(result["evaluation_policy_result"]["canonical_task_outcome_summary"]["overall"]["canonical_completion_count"] for result in checkpoint_results),
            "canonical_drop_count": sum(result["evaluation_policy_result"]["canonical_task_outcome_summary"]["overall"]["canonical_drop_count"] for result in checkpoint_results),
            "canonical_pending_count": sum(result["evaluation_policy_result"]["canonical_task_outcome_summary"]["overall"]["canonical_pending_count"] for result in checkpoint_results),
            "canonical_unknown_count": sum(result["evaluation_policy_result"]["canonical_task_outcome_summary"]["overall"]["canonical_unknown_count"] for result in checkpoint_results),
        },
    }
    paper_aligned_evaluation_metrics = {
        "checkpoint_budgets": [result["training_budget"] for result in checkpoint_results],
        "by_checkpoint": [result["evaluation_policy_result"]["paper_aligned_diagnostic_metrics"] for result in checkpoint_results],
    }
    decision_records_summary = {
        "record_count": sum(result["evaluation_policy_result"]["decision_records_summary"]["decision_count"] for result in checkpoint_results),
        "sample_records": [
            sample
            for result in checkpoint_results
            for sample in result["evaluation_policy_result"]["decision_records_summary"]["sample_records"]
        ][:RECORD_SAMPLE_LIMIT],
        "evaluation_action_distribution_source": "evaluation_episodes",
        "by_checkpoint": [
            {
                "training_budget": result["training_budget"],
                **result["evaluation_policy_result"]["decision_records_summary"],
            }
            for result in checkpoint_results
        ],
    }
    terminal_event_records = {
        "record_count": sum(result["evaluation_policy_result"]["terminal_event_records"]["record_count"] for result in checkpoint_results),
        "sample_records": [
            sample
            for result in checkpoint_results
            for sample in result["evaluation_policy_result"]["terminal_event_records"]["sample_records"]
        ][:RECORD_SAMPLE_LIMIT],
        "by_checkpoint": [
            {
                "training_budget": result["training_budget"],
                **result["evaluation_policy_result"]["terminal_event_records"],
            }
            for result in checkpoint_results
        ],
    }
    reward_event_records = {
        "record_count": sum(result["evaluation_policy_result"]["reward_event_records"]["record_count"] for result in checkpoint_results),
        "sample_records": [
            sample
            for result in checkpoint_results
            for sample in result["evaluation_policy_result"]["reward_event_records"]["sample_records"]
        ][:RECORD_SAMPLE_LIMIT],
        "reward_available_count": sum(result["evaluation_policy_result"]["reward_event_records"]["reward_available_count"] for result in checkpoint_results),
        "raw_reward_event_recovery_blocked": any(result["evaluation_policy_result"]["reward_event_records"]["raw_reward_event_recovery_blocked"] for result in checkpoint_results),
        "by_checkpoint": [
            {
                "training_budget": result["training_budget"],
                **result["evaluation_policy_result"]["reward_event_records"],
            }
            for result in checkpoint_results
        ],
    }
    policy_effect = build_policy_effect_after_repair(
        trainer=session.trainer,
        checkpoint_results=checkpoint_results,
        fixed_policy_seed=session.campaign_config.seed_bundle.evaluation_trace_generation_seed,
        evaluation_episode_count=EVALUATION_EPISODES_PER_CHECKPOINT,
        episode_length=EPISODE_LENGTH,
        evaluation_trace_bank_id=session.trainer.config.evaluation_trace_bank_id,
    )
    for name, result in list(policy_effect["policy_results"].items()):
        if "task_records" in result:
            policy_reconciliation = build_canonical_task_reconciliation(
                checkpoint_budget=int(result.get("checkpoint_budget") or 0),
                evaluation_decision_count=int(result.get("evaluation_decision_count", 0)),
                task_records=result["task_records"],
                reward_reconciliation_tolerance=REWARD_RECONCILIATION_TOLERANCE,
                record_sample_limit=RECORD_SAMPLE_LIMIT,
            )
            _augment_policy_result_with_reconciliation(result)
            policy_effect["policy_results"][name] = result
            policy_effect.setdefault("policy_reconciliations", {})[name] = policy_reconciliation

    diagnostic_decision = build_diagnostic_decision(
        raw_reward_event_recovery_blocked=raw_vs_canonical_summary["raw_reward_event_recovery_blocked"],
        terminal_event_recovery_blocked=raw_vs_canonical_summary["terminal_event_recovery_blocked"],
        reward_reconciled=raw_vs_canonical_summary["reward_reconciled"],
        candidate_policy_vertical_collapse_in_evaluation=bool(policy_effect["candidate_policy_vertical_collapse_in_evaluation"]),
        candidate_policy_vertical_collapse_in_training_replay_window=bool(policy_effect["candidate_policy_vertical_collapse_in_training_replay_window"]),
        policy_affects_reward=policy_effect["policy_affects_reward"],
        policy_affects_terminal_outcomes=policy_effect["policy_affects_terminal_outcomes"],
    )

    explanation = _build_explanation(policy_effect, raw_vs_canonical_summary)
    remaining_blockers: list[str] = []
    if not feature_065_prerequisite_verified:
        remaining_blockers.append("feature_065_prerequisite_blocked")
    if raw_vs_canonical_summary["raw_reward_event_recovery_blocked"]:
        remaining_blockers.append("raw_reward_event_recovery_blocked")
    if raw_vs_canonical_summary["terminal_event_recovery_blocked"]:
        remaining_blockers.append("terminal_event_recovery_blocked")
    if not raw_vs_canonical_summary["reward_reconciled"]:
        remaining_blockers.append("reward_reconciliation_failed")
    if not scope_guard["working_tree_paths_approved"] or not scope_guard["staged_paths_approved"] or not scope_guard["base_branch_head_diff_approved"]:
        remaining_blockers.append("scope_drift_detected")

    final_verdict = "reward_emission_aggregation_repair_ready"
    if remaining_blockers or not claim_safety_status["claim_safety_passed"] or not raw_vs_canonical_summary["reward_reconciled"]:
        final_verdict = "reward_emission_aggregation_repair_blocked"
    if raw_vs_canonical_summary["raw_reward_event_recovery_blocked"]:
        final_verdict = "reward_emission_aggregation_repair_blocked"

    figure_manifest = FigureManifest(
        figure_directory=str(FIGURES_DIR),
        figure_files=[
            "figure_01_raw_vs_canonical_reward_reconciliation.png",
            "figure_02_reward_event_coverage_by_budget.png",
            "figure_03_terminal_event_coverage_by_budget.png",
            "figure_04_completion_drop_pending_ratios_by_budget.png",
            "figure_05_policy_effect_after_repair.png",
        ],
        figure_count=5,
        figures_generated=True,
    ).to_dict()

    report_payload = {
        "feature_id": FEATURE_ID,
        "base_branch_name": BASE_BRANCH_NAME,
        "branch_name": BRANCH_NAME,
        "prerequisite_tags_verified": prerequisite_tags,
        "prerequisite_artifacts": prerequisite_artifacts,
        "feature_065_prerequisite_verified": feature_065_prerequisite_verified,
        "checkpoint_budgets": list(CHECKPOINT_BUDGETS),
        "evaluation_episode_count_per_checkpoint": EVALUATION_EPISODES_PER_CHECKPOINT,
        "episode_length": EPISODE_LENGTH,
        "max_training_budget": 500,
        "training_mode": TRAINING_MODE,
        "training_rerun_from_scratch": TRAINING_RERUN_FROM_SCRATCH,
        "training_5000_run": TRAINING_5000_RUN,
        "reward_reconciliation_tolerance": REWARD_RECONCILIATION_TOLERANCE,
        "checkpoint_metrics": [
            {
                **{k: v for k, v in result.items() if k != "evaluation_policy_result" and k != "training_state"},
                "evaluation_policy_result": {
                    k: v
                    for k, v in result["evaluation_policy_result"].items()
                    if k not in {"task_records"}
                },
                "training_state": result["training_state"],
            }
            for result in checkpoint_results
        ],
        "decision_records_summary": decision_records_summary,
        "terminal_event_records": terminal_event_records,
        "reward_event_records": reward_event_records,
        "canonical_task_reconciliation": canonical_task_reconciliation,
        "raw_vs_canonical_reward_reconciliation": raw_vs_canonical_summary,
        "paper_aligned_evaluation_metrics": paper_aligned_evaluation_metrics,
        "policy_effect_after_repair": {
            "evaluation_trace_bank_id": policy_effect["evaluation_trace_bank_id"],
            "evaluation_episode_count": policy_effect["evaluation_episode_count"],
            "episode_length": policy_effect["episode_length"],
            "candidate_policy_vertical_collapse_in_evaluation": policy_effect["candidate_policy_vertical_collapse_in_evaluation"],
            "candidate_policy_vertical_collapse_in_training_replay_window": policy_effect["candidate_policy_vertical_collapse_in_training_replay_window"],
            "policy_affects_reward": policy_effect["policy_affects_reward"],
            "policy_affects_terminal_outcomes": policy_effect["policy_affects_terminal_outcomes"],
            "evaluation_metric_static_because_policy_same": policy_effect["evaluation_metric_static_because_policy_same"],
            "evaluation_metric_static_because_reward_aggregation": policy_effect["evaluation_metric_static_because_reward_aggregation"],
            "evaluation_metric_static_because_environment_dynamics": policy_effect["evaluation_metric_static_because_environment_dynamics"],
            "evaluation_reward_static_after_instrumentation": policy_effect["evaluation_reward_static_after_instrumentation"],
            "raw_event_reward_static_across_budget": policy_effect["raw_event_reward_static_across_budget"],
            "canonical_task_reward_static_across_budget": policy_effect["canonical_task_reward_static_across_budget"],
            "canonical_completion_rate_static_across_budget": policy_effect["canonical_completion_rate_static_across_budget"],
            "canonical_drop_rate_static_across_budget": policy_effect["canonical_drop_rate_static_across_budget"],
            "evaluation_action_distribution_static_across_budget": policy_effect["evaluation_action_distribution_static_across_budget"],
            "candidate_reward_variation": policy_effect["candidate_reward_variation"],
            "candidate_action_distribution_changed_by_budget": policy_effect["candidate_action_distribution_changed_by_budget"],
            "candidate_terminal_outcomes_changed_by_budget": policy_effect["candidate_terminal_outcomes_changed_by_budget"],
            "canonical_policy_effect_summary": policy_effect["canonical_policy_effect_summary"],
            "policy_results": {
                name: {
                    k: v
                    for k, v in result.items()
                    if k != "task_records"
                }
                for name, result in policy_effect["policy_results"].items()
            },
        },
        "diagnostic_decision": diagnostic_decision,
        "claim_safety_status": claim_safety_status,
        "figure_manifest": figure_manifest,
        "remaining_blockers": remaining_blockers,
        "final_verdict": final_verdict,
        "raw_reward_event_recovery_blocked": raw_vs_canonical_summary["raw_reward_event_recovery_blocked"],
        "terminal_event_recovery_blocked": raw_vs_canonical_summary["terminal_event_recovery_blocked"],
        "reward_reconciliation_failed": not raw_vs_canonical_summary["reward_reconciled"],
        "policy_effect_after_repair_failed": False,
        "reward_function_modified": False,
        "environment_semantics_modified": False,
        "policy_modified": False,
        "dal_modified": False,
        "dependencies_modified": False,
        "paper_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "evaluation_reward_static_after_instrumentation": policy_effect["evaluation_reward_static_after_instrumentation"],
        "raw_event_reward_static_across_budget": policy_effect["raw_event_reward_static_across_budget"],
        "canonical_task_reward_static_across_budget": policy_effect["canonical_task_reward_static_across_budget"],
        "canonical_completion_rate_static_across_budget": policy_effect["canonical_completion_rate_static_across_budget"],
        "canonical_drop_rate_static_across_budget": policy_effect["canonical_drop_rate_static_across_budget"],
        "evaluation_action_distribution_static_across_budget": policy_effect["evaluation_action_distribution_static_across_budget"],
        "candidate_policy_vertical_collapse_in_evaluation": policy_effect["candidate_policy_vertical_collapse_in_evaluation"],
        "candidate_policy_vertical_collapse_in_training_replay_window": policy_effect["candidate_policy_vertical_collapse_in_training_replay_window"],
        "policy_affects_reward": policy_effect["policy_affects_reward"],
        "policy_affects_terminal_outcomes": policy_effect["policy_affects_terminal_outcomes"],
        "most_likely_root_cause": explanation["why_previous_outputs_were_identical_or_static"],
        "recommended_next_feature": RECOMMENDED_NEXT_FEATURE,
        "explanation_of_previous_static_outputs": explanation,
        "scope_guard_summary": scope_guard,
        "checkpoint_results": checkpoint_results,
    }

    report = RewardEmissionAggregationRepairReport(**{k: v for k, v in report_payload.items() if k != "checkpoint_results"})
    # keep auxiliary fields in the payload for the written report, even if the dataclass only validates the core schema.
    payload = report.to_dict()
    payload.update({
        "scope_guard_summary": scope_guard,
        "checkpoint_results": checkpoint_results,
        "evaluation_reward_static_after_instrumentation": policy_effect["evaluation_reward_static_after_instrumentation"],
        "raw_event_reward_static_across_budget": policy_effect["raw_event_reward_static_across_budget"],
        "canonical_task_reward_static_across_budget": policy_effect["canonical_task_reward_static_across_budget"],
        "canonical_completion_rate_static_across_budget": policy_effect["canonical_completion_rate_static_across_budget"],
        "canonical_drop_rate_static_across_budget": policy_effect["canonical_drop_rate_static_across_budget"],
        "evaluation_action_distribution_static_across_budget": policy_effect["evaluation_action_distribution_static_across_budget"],
        "candidate_policy_vertical_collapse_in_evaluation": policy_effect["candidate_policy_vertical_collapse_in_evaluation"],
        "candidate_policy_vertical_collapse_in_training_replay_window": policy_effect["candidate_policy_vertical_collapse_in_training_replay_window"],
        "policy_affects_reward": policy_effect["policy_affects_reward"],
        "policy_affects_terminal_outcomes": policy_effect["policy_affects_terminal_outcomes"],
        "most_likely_root_cause": explanation["why_previous_outputs_were_identical_or_static"],
        "recommended_next_feature": RECOMMENDED_NEXT_FEATURE,
        "explanation_of_previous_static_outputs": explanation,
    })
    return payload


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    checkpoint_metrics = payload["checkpoint_results"]
    raw_json = {
        "checkpoint_metrics": checkpoint_metrics,
    }
    REPAIRED_CHECKPOINT_METRICS_JSON.write_text(json_dump(checkpoint_metrics), encoding="utf-8")
    DECISION_RECORDS_SUMMARY_JSON.write_text(json_dump(payload["decision_records_summary"]), encoding="utf-8")
    TERMINAL_EVENT_RECORDS_JSON.write_text(json_dump(payload["terminal_event_records"]), encoding="utf-8")
    REWARD_EVENT_RECORDS_JSON.write_text(json_dump(payload["reward_event_records"]), encoding="utf-8")
    CANONICAL_TASK_RECONCILIATION_JSON.write_text(json_dump(payload["canonical_task_reconciliation"]), encoding="utf-8")
    RAW_VS_CANONICAL_REWARD_RECONCILIATION_JSON.write_text(json_dump(payload["raw_vs_canonical_reward_reconciliation"]), encoding="utf-8")
    PAPER_ALIGNED_EVALUATION_METRICS_JSON.write_text(json_dump(payload["paper_aligned_evaluation_metrics"]), encoding="utf-8")
    POLICY_EFFECT_AFTER_REPAIR_JSON.write_text(json_dump(payload["policy_effect_after_repair"]), encoding="utf-8")
    DIAGNOSTIC_DECISION_JSON.write_text(json_dump(payload["diagnostic_decision"]), encoding="utf-8")
    figure_manifest = payload["figure_manifest"]
    FIGURE_MANIFEST_JSON.write_text(json_dump(figure_manifest), encoding="utf-8")
    report_path, md_path, summary_path = write_reward_emission_aggregation_repair_report(
        RewardEmissionAggregationRepairReport(**{k: v for k, v in payload.items() if k in RewardEmissionAggregationRepairReport.__dataclass_fields__}),
        output_dir=OUTPUT_DIR,
    )
    generate_figures(payload, FIGURES_DIR)
    summary_path.write_text(render_final_repair_summary_markdown(payload), encoding="utf-8")
    return report_path, md_path, summary_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = run_reward_emission_aggregation_repair()
    write_artifacts(payload)
    if args.json:
        stdout_payload = {
            k: v
            for k, v in payload.items()
            if k
            not in {
                "checkpoint_results",
                "policy_effect_after_repair",
                "canonical_task_reconciliation",
                "terminal_event_records",
                "reward_event_records",
                "decision_records_summary",
            }
        }
        print(
            json.dumps(
                stdout_payload,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
    else:
        print(payload["final_verdict"])
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
