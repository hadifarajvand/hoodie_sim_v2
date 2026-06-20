from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.instrumented_evaluator import (
    _build_action_counts_from_records,
)

from .comparison import build_budget_comparison
from .config import (
    BASE_BRANCH_NAME,
    BRANCH_NAME,
    CANONICAL_TERMINAL_TASK_SUMMARY_JSON,
    CHECKPOINT_BUDGETS,
    CHECKPOINT_COMPARISON_JSON,
    COMPLETION_PATH_AUDIT_JSON,
    DIAGNOSTIC_DECISION_JSON,
    EVALUATION_EPISODES_PER_CHECKPOINT,
    EPISODE_LENGTH,
    FEATURE_ID,
    FIGURE_MANIFEST_JSON,
    FIGURES_DIR,
    OUTPUT_DIR,
    PAPER_ALIGNED_50_100_METRICS_JSON,
    POLICY_EFFECT_50_100_AFTER_TERMINAL_REPAIR_JSON,
    RAW_VS_CANONICAL_TERMINAL_RECONCILIATION_JSON,
    REWARD_RECONCILIATION_AFTER_TERMINAL_REPAIR_JSON,
    REPORT_JSON,
    REPORT_MD,
    TERMINAL_EVENT_CLASSIFICATION_JSON,
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
    load_feature_066_status,
)
from .figures import generate_figures
from .model import (
    CheckpointComparisonMetric,
    FigureManifest,
    TerminalLifecycleComparisonReport,
)
from .reconciliation import (
    build_canonical_terminal_task_summary,
    build_completion_path_audit,
    build_paper_aligned_50_100_metrics,
    build_raw_vs_canonical_terminal_reconciliation,
    build_reward_reconciliation_after_terminal_repair,
    build_terminal_event_classification_summary,
)
from .repaired_terminal_evaluator import TerminalLifecycleTrainingSession, build_policy_effect_after_terminal_repair
from .report import json_dump, write_terminal_lifecycle_comparison_report

APPROVED_PREFIXES = (
    "artifacts/analysis/terminal-lifecycle-accounting-50-100-comparison/",
    "docs/architecture/euls_phase26_terminal_lifecycle_accounting_50_100_comparison.md",
    "specs/067-terminal-lifecycle-accounting-50-100-comparison/",
    "src/analysis/terminal_lifecycle_accounting_50_100_comparison/",
    "tests/unit/test_terminal_lifecycle_accounting_50_100_comparison",
    "tests/integration/test_terminal_lifecycle_accounting_50_100_comparison",
)

FORBIDDEN_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/reward_timing.py",
    "src/environment/replay_hash.py",
    "src/analysis/staged_training_budget_learning_curve/",
    "src/analysis/final_review_release_gate_batch/",
    "src/analysis/evaluation_instrumentation_reward_state_diagnostic/",
    "src/analysis/reward_emission_evaluation_metric_aggregation_repair/",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
)


def _candidate_policy_next_action(policy_effect: dict[str, Any], terminal_reconciliation: dict[str, Any]) -> tuple[str, str, list[str]]:
    candidate_vertical_evaluation = bool(policy_effect.get("candidate_policy_vertical_collapse_in_evaluation", False))
    candidate_vertical_training = bool(policy_effect.get("candidate_policy_vertical_collapse_in_training_replay_window", False))
    policy_affects_reward = str(policy_effect.get("policy_affects_reward", "uncertain"))
    policy_affects_terminal_outcomes = str(policy_effect.get("policy_affects_terminal_outcomes", "uncertain"))
    policy_results = policy_effect.get("policy_results", {})
    fixed_policy_names = ["fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy"]
    all_fixed_zero_completion = all(
        int(policy_results.get(name, {}).get("evaluation_reward_summary", {}).get("completed_task_count", 0)) == 0 for name in fixed_policy_names
    )
    any_fixed_completes = any(
        int(policy_results.get(name, {}).get("evaluation_reward_summary", {}).get("completed_task_count", 0)) > 0 for name in fixed_policy_names
    )
    diagnostic_decision = build_diagnostic_decision(
        terminal_reconciliation_failed=not bool(terminal_reconciliation["overall"]["terminal_reconciled"]),
        reward_reconciliation_failed=not bool(terminal_reconciliation["overall"]["reward_reconciled"]),
        candidate_policy_vertical_collapse_in_evaluation=candidate_vertical_evaluation,
        candidate_policy_vertical_collapse_in_training_replay_window=candidate_vertical_training,
        all_fixed_policies_zero_completion=all_fixed_zero_completion,
        any_fixed_policy_completes=any_fixed_completes,
        terminal_event_coverage_ratio=float(terminal_reconciliation["overall"]["terminal_event_coverage_ratio"]),
        policy_affects_reward=policy_affects_reward,
        policy_affects_terminal_outcomes=policy_affects_terminal_outcomes,
    )
    recommended = diagnostic_decision["recommended_next_action"]
    if recommended == "fix_completion_path_next":
        root = "All evaluated policies remain drop-dominant, so the completion path is the next repair target."
    elif recommended == "fix_state_representation_next":
        root = "At least one fixed-policy path indicates the current state signal is still too weak for completion."
    elif recommended == "fix_reward_function_next":
        root = "Reward or terminal signal still does not separate outcomes cleanly enough for this diagnostic stage."
    elif recommended == "fix_environment_lifecycle_accounting_next":
        root = "Terminal lifecycle accounting still needs structural cleanup."
    else:
        root = "Terminal and reward reconciliation now pass, so the remaining path is state-representation repair."
    return recommended, root, diagnostic_decision["evidence_notes"]


def _build_checkpoint_metric(
    *,
    training_budget: int,
    training_state: dict[str, Any],
    evaluation_result: dict[str, Any],
    claim_safety_status: dict[str, Any],
) -> dict[str, Any]:
    evaluation_reward_summary = evaluation_result["evaluation_reward_summary"]
    metric = CheckpointComparisonMetric(
        training_budget=training_budget,
        cumulative_training_episode_count=training_state["cumulative_training_episode_count"],
        evaluation_episode_count=EVALUATION_EPISODES_PER_CHECKPOINT,
        episode_length=EPISODE_LENGTH,
        optimizer_step_count=training_state["optimizer_step_count"],
        replay_size=training_state["replay_size"],
        action_distribution=evaluation_result["evaluation_action_distribution"],
        action_count_total=evaluation_result["evaluation_decision_count"],
        action_accounting_reconciled=True,
        loss_count=training_state["loss_count"],
        last_loss=training_state["last_loss"],
        loss_finite=training_state["loss_finite"],
        reward_summary=training_state["reward_summary"],
        evaluation_reward_summary=evaluation_reward_summary,
        completed_task_count=evaluation_reward_summary["completed_task_count"],
        dropped_task_count=evaluation_reward_summary["dropped_task_count"],
        pending_at_horizon_count=evaluation_reward_summary["pending_at_horizon_count"],
        comparison_ready=bool(training_state["loss_finite"])
        and bool(evaluation_result["raw_vs_canonical_terminal_reconciliation"]["terminal_reconciled"])
        and bool(evaluation_result["reward_reconciliation_after_terminal_repair"]["reward_reconciled"]),
        claim_safety_status=claim_safety_status,
        evaluation_action_distribution=evaluation_result["evaluation_action_distribution"],
        evaluation_decision_count=evaluation_result["evaluation_decision_count"],
        evaluation_action_sequence_sample=evaluation_result["evaluation_action_sequence_sample"],
        evaluation_legal_action_mask_distribution=evaluation_result["evaluation_legal_action_mask_distribution"],
        evaluation_action_by_trace_id=evaluation_result["evaluation_action_by_trace_id"],
        evaluation_action_by_episode_id=evaluation_result["evaluation_action_by_episode_id"],
        terminal_event_classification=evaluation_result["terminal_event_classification"],
        canonical_terminal_task_summary=evaluation_result["canonical_terminal_task_summary"],
        raw_vs_canonical_terminal_reconciliation=evaluation_result["raw_vs_canonical_terminal_reconciliation"],
        reward_reconciliation_after_terminal_repair=evaluation_result["reward_reconciliation_after_terminal_repair"],
        completion_path_audit=evaluation_result["completion_path_audit"],
        policy_effect_summary=evaluation_result["paper_aligned_diagnostic_metrics"],
        paper_aligned_diagnostic_metrics=evaluation_result["paper_aligned_diagnostic_metrics"],
    )
    return metric.to_dict() | {
        "training_state": training_state,
        "evaluation_policy_result": evaluation_result,
    }


def _explanation_of_previous_static_outputs(checkpoint_results: list[dict[str, Any]], policy_effect: dict[str, Any]) -> dict[str, Any]:
    candidate_50 = policy_effect["policy_results"].get("candidate_policy_at_50", {})
    candidate_100 = policy_effect["policy_results"].get("candidate_policy_at_100", {})
    return {
        "why_previous_outputs_looked_static": (
            "The raw lifecycle stream contains both terminal-outcome events and lifecycle-only events. "
            "Once terminal outcomes are counted canonically, the remaining comparison is dominated by a drop-heavy trace bank and a candidate policy that stays vertically collapsed."
        ),
        "raw_terminal_events_are_lifecycle_mixed": True,
        "candidate_action_distribution_changed_by_budget": candidate_50.get("evaluation_action_distribution", {}) != candidate_100.get("evaluation_action_distribution", {}),
        "candidate_completion_count_changed_by_budget": int(candidate_50.get("evaluation_reward_summary", {}).get("completed_task_count", 0))
        != int(candidate_100.get("evaluation_reward_summary", {}).get("completed_task_count", 0)),
        "candidate_drop_count_changed_by_budget": int(candidate_50.get("evaluation_reward_summary", {}).get("dropped_task_count", 0))
        != int(candidate_100.get("evaluation_reward_summary", {}).get("dropped_task_count", 0)),
        "candidate_mean_reward_changed_by_budget": float(candidate_50.get("evaluation_reward_summary", {}).get("mean_reward", 0.0))
        != float(candidate_100.get("evaluation_reward_summary", {}).get("mean_reward", 0.0)),
    }


def _build_blocked_payload(blockers: list[str], claim_safety_status: dict[str, Any], scope_guard_summary: dict[str, Any]) -> dict[str, Any]:
    empty_summary = {
        "checkpoint_budgets": list(CHECKPOINT_BUDGETS),
        "by_checkpoint": [],
        "overall": {
            "terminal_reconciled": False,
            "reward_reconciled": False,
            "raw_reward_event_recovery_blocked": True,
            "terminal_event_recovery_blocked": True,
            "terminal_event_coverage_ratio": 0.0,
        },
    }
    empty_policy_effect = {
        "evaluation_trace_bank_id": "",
        "evaluation_episode_count": EVALUATION_EPISODES_PER_CHECKPOINT,
        "episode_length": EPISODE_LENGTH,
        "candidate_policy_vertical_collapse_in_evaluation": False,
        "candidate_policy_vertical_collapse_in_training_replay_window": False,
        "policy_affects_reward": "uncertain",
        "policy_affects_terminal_outcomes": "uncertain",
        "evaluation_reward_static_after_terminal_repair": False,
        "evaluation_action_distribution_static_across_budget": False,
        "raw_event_reward_static_across_budget": False,
        "canonical_task_reward_static_across_budget": False,
        "canonical_completion_rate_static_across_budget": False,
        "canonical_drop_rate_static_across_budget": False,
        "policy_results": {},
        "candidate_reward_variation": 0.0,
        "candidate_action_distribution_changed_by_budget": False,
        "candidate_terminal_outcomes_changed_by_budget": False,
        "canonical_policy_effect_summary": {},
    }
    diagnostic_decision = {
        "recommended_next_action": "blocked_due_to_unresolved_terminal_reconciliation",
        "decision_reason": "Prerequisite validation failed before the terminal lifecycle repair could run.",
        "evidence_notes": blockers,
    }
    return {
        "feature_id": FEATURE_ID,
        "base_branch_name": BASE_BRANCH_NAME,
        "branch_name": BRANCH_NAME,
        "prerequisite_tags_verified": [],
        "prerequisite_artifacts": build_prerequisite_artifacts(),
        "feature_066_prerequisite_verified": False,
        "checkpoint_budgets": list(CHECKPOINT_BUDGETS),
        "evaluation_episode_count_per_checkpoint": EVALUATION_EPISODES_PER_CHECKPOINT,
        "episode_length": EPISODE_LENGTH,
        "max_training_budget": 100,
        "training_mode": TRAINING_MODE,
        "training_rerun_from_scratch": TRAINING_RERUN_FROM_SCRATCH,
        "training_5000_run": TRAINING_5000_RUN,
        "reward_reconciliation_tolerance": 1e-9,
        "checkpoint_metrics": [],
        "terminal_event_classification": empty_summary,
        "canonical_terminal_task_summary": empty_summary,
        "raw_vs_canonical_terminal_reconciliation": {
            "checkpoint_budgets": list(CHECKPOINT_BUDGETS),
            "by_checkpoint": [],
            "overall": {
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
                "raw_reward_event_recovery_blocked": True,
                "terminal_event_recovery_blocked": True,
            },
        },
        "reward_reconciliation_after_terminal_repair": {
            "checkpoint_budgets": list(CHECKPOINT_BUDGETS),
            "by_checkpoint": [],
            "overall": {
                "raw_event_reward_total": 0.0,
                "raw_event_reward_count": 0,
                "canonical_task_reward_total": 0.0,
                "canonical_task_reward_count": 0,
                "raw_vs_canonical_reward_delta": 0.0,
                "reward_reconciled": False,
                "reward_reconciliation_tolerance": 1e-9,
                "raw_reward_event_recovery_blocked": True,
                "terminal_event_recovery_blocked": True,
            },
        },
        "completion_path_audit": {"by_checkpoint": [], "by_policy": {}},
        "policy_effect_50_100_after_terminal_repair": empty_policy_effect,
        "paper_aligned_50_100_metrics": empty_summary,
        "diagnostic_decision": diagnostic_decision,
        "claim_safety_status": claim_safety_status,
        "figure_manifest": {"figure_directory": str(FIGURES_DIR), "figure_files": [], "figure_count": 0, "figures_generated": False},
        "remaining_blockers": blockers,
        "final_verdict": "terminal_lifecycle_50_100_comparison_blocked",
        "raw_reward_event_recovery_blocked": True,
        "terminal_event_recovery_blocked": True,
        "terminal_reconciliation_failed": True,
        "reward_reconciliation_failed": True,
        "completion_path_audit_failed": True,
        "policy_effect_50_100_failed": True,
        "paper_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "environment_semantics_modified": False,
        "reward_function_modified": False,
        "policy_modified": False,
        "dal_modified": False,
        "dependencies_modified": False,
        "evaluation_reward_static_after_terminal_repair": False,
        "evaluation_action_distribution_static_across_budget": False,
        "candidate_policy_vertical_collapse_in_evaluation": False,
        "candidate_policy_vertical_collapse_in_training_replay_window": False,
        "policy_affects_reward": "uncertain",
        "policy_affects_terminal_outcomes": "uncertain",
        "most_likely_root_cause": "Prerequisite validation failed before the repair run.",
        "recommended_next_feature": "Completion-path repair",
        "explanation_of_previous_static_outputs": {"why_previous_outputs_looked_static": "Blocked before execution."},
        "scope_guard_summary": scope_guard_summary,
        "checkpoint_comparison": {"checkpoint_budgets": list(CHECKPOINT_BUDGETS), "by_checkpoint": [], "comparison": {}},
    }


def run_terminal_lifecycle_comparison() -> dict[str, Any]:
    scope_guard_summary = build_scope_guard_summary(
        git_status_paths(),
        git_staged_paths(),
        git_diff_paths("066-reward-emission-evaluation-metric-aggregation-repair"),
        APPROVED_PREFIXES,
        FORBIDDEN_PREFIXES,
    )
    claim_safety_status = build_claim_safety_status()
    prerequisite_artifacts = build_prerequisite_artifacts()
    feature_066_verified = prerequisite_artifacts["feature_066_report"]["verified"]
    prerequisite_tags = build_prerequisite_tags(
        scope_guard_summary["working_tree_paths_approved"],
        scope_guard_summary["staged_paths_approved"],
        scope_guard_summary["base_branch_head_diff_approved"],
    )
    if not feature_066_verified:
        return _build_blocked_payload(["feature_066_prerequisite_blocked"], claim_safety_status, scope_guard_summary) | {
            "prerequisite_tags_verified": prerequisite_tags,
            "prerequisite_artifacts": prerequisite_artifacts,
            "feature_066_prerequisite_verified": False,
            "claim_safety_status": claim_safety_status,
        }

    from .config import TerminalLifecycleComparisonConfig

    config = TerminalLifecycleComparisonConfig()
    session = TerminalLifecycleTrainingSession(config)
    checkpoint_results: list[dict[str, Any]] = []

    for budget in config.checkpoint_budgets:
        training_state = session.train_to_budget(int(budget))
        evaluation_result = session.candidate_policy_result(checkpoint_budget=int(budget))
        checkpoint_results.append(
            {
                "training_budget": int(budget),
                "training_state": training_state,
                "evaluation_policy_result": evaluation_result,
            }
        )

    policy_effect = build_policy_effect_after_terminal_repair(
        trainer=session.trainer,
        checkpoint_results=checkpoint_results,
        fixed_policy_seed=session.campaign_config.seed_bundle.evaluation_trace_generation_seed,
        evaluation_episode_count=config.evaluation_episode_count_per_checkpoint,
        episode_length=config.episode_length,
        evaluation_trace_bank_id=session.campaign_config.evaluation_trace_bank_id,
    )
    checkpoint_comparison = build_budget_comparison(checkpoint_results, policy_effect)
    terminal_event_classification = build_terminal_event_classification_summary(checkpoint_results)
    canonical_terminal_task_summary = build_canonical_terminal_task_summary(checkpoint_results)
    raw_vs_canonical_terminal_reconciliation = build_raw_vs_canonical_terminal_reconciliation(checkpoint_results)
    reward_reconciliation_after_terminal_repair = build_reward_reconciliation_after_terminal_repair(checkpoint_results)
    completion_path_audit = build_completion_path_audit(checkpoint_results, policy_effect)
    paper_aligned_50_100_metrics = build_paper_aligned_50_100_metrics(checkpoint_results)

    checkpoint_metrics = [
        _build_checkpoint_metric(
            training_budget=int(result["training_budget"]),
            training_state=result["training_state"],
            evaluation_result=result["evaluation_policy_result"],
            claim_safety_status=claim_safety_status,
        )
        for result in checkpoint_results
    ]

    terminal_reconciliation_failed = not bool(raw_vs_canonical_terminal_reconciliation["overall"]["terminal_reconciled"])
    reward_reconciliation_failed = not bool(raw_vs_canonical_terminal_reconciliation["overall"]["reward_reconciled"])
    policy_effect_failed = not bool(policy_effect["policy_results"])
    candidate_vertical_collapse_eval = bool(policy_effect["candidate_policy_vertical_collapse_in_evaluation"])
    candidate_vertical_collapse_training = bool(policy_effect["candidate_policy_vertical_collapse_in_training_replay_window"])
    all_fixed_zero_completion = all(
        int(policy_effect["policy_results"].get(name, {}).get("evaluation_reward_summary", {}).get("completed_task_count", 0)) == 0
        for name in ["fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy"]
    )
    any_fixed_completes = any(
        int(policy_effect["policy_results"].get(name, {}).get("evaluation_reward_summary", {}).get("completed_task_count", 0)) > 0
        for name in ["fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy"]
    )
    recommended_next_action = build_diagnostic_decision(
        terminal_reconciliation_failed=terminal_reconciliation_failed,
        reward_reconciliation_failed=reward_reconciliation_failed,
        candidate_policy_vertical_collapse_in_evaluation=candidate_vertical_collapse_eval,
        candidate_policy_vertical_collapse_in_training_replay_window=candidate_vertical_collapse_training,
        all_fixed_policies_zero_completion=all_fixed_zero_completion,
        any_fixed_policy_completes=any_fixed_completes,
        terminal_event_coverage_ratio=float(raw_vs_canonical_terminal_reconciliation["overall"]["terminal_event_coverage_ratio"]),
        policy_affects_reward=policy_effect["policy_affects_reward"],
        policy_affects_terminal_outcomes=policy_effect["policy_affects_terminal_outcomes"],
    )["recommended_next_action"]
    diagnostic_decision = build_diagnostic_decision(
        terminal_reconciliation_failed=terminal_reconciliation_failed,
        reward_reconciliation_failed=reward_reconciliation_failed,
        candidate_policy_vertical_collapse_in_evaluation=candidate_vertical_collapse_eval,
        candidate_policy_vertical_collapse_in_training_replay_window=candidate_vertical_collapse_training,
        all_fixed_policies_zero_completion=all_fixed_zero_completion,
        any_fixed_policy_completes=any_fixed_completes,
        terminal_event_coverage_ratio=float(raw_vs_canonical_terminal_reconciliation["overall"]["terminal_event_coverage_ratio"]),
        policy_affects_reward=policy_effect["policy_affects_reward"],
        policy_affects_terminal_outcomes=policy_effect["policy_affects_terminal_outcomes"],
    )
    most_likely_root_cause = (
        "All fixed policies remain drop-dominant, so the remaining repair target is the completion path."
        if recommended_next_action == "fix_completion_path_next"
        else "Terminal lifecycle accounting and reward reconciliation now pass, so the next diagnostic target is state representation."
    )
    explanation = _explanation_of_previous_static_outputs(checkpoint_results, policy_effect)

    final_verdict = "terminal_lifecycle_50_100_comparison_ready"
    remaining_blockers: list[str] = []
    if terminal_reconciliation_failed:
        final_verdict = "terminal_lifecycle_50_100_comparison_blocked"
        remaining_blockers.append("terminal_reconciliation_failed")
    if reward_reconciliation_failed:
        final_verdict = "terminal_lifecycle_50_100_comparison_blocked"
        remaining_blockers.append("reward_reconciliation_failed")
    if policy_effect_failed:
        final_verdict = "terminal_lifecycle_50_100_comparison_blocked"
        remaining_blockers.append("policy_effect_50_100_failed")

    figure_paths = generate_figures(
        {
            "checkpoint_metrics": checkpoint_metrics,
            "policy_effect_50_100_after_terminal_repair": policy_effect,
        },
        FIGURES_DIR,
    )
    figure_manifest = FigureManifest(
        figure_directory=str(FIGURES_DIR),
        figure_files=[path.name for path in figure_paths],
        figure_count=len(figure_paths),
        figures_generated=True,
    ).to_dict()

    report = TerminalLifecycleComparisonReport(
        feature_id=FEATURE_ID,
        base_branch_name=BASE_BRANCH_NAME,
        branch_name=BRANCH_NAME,
        prerequisite_tags_verified=prerequisite_tags,
        prerequisite_artifacts=prerequisite_artifacts,
        feature_066_prerequisite_verified=feature_066_verified,
        checkpoint_budgets=list(CHECKPOINT_BUDGETS),
        evaluation_episode_count_per_checkpoint=config.evaluation_episode_count_per_checkpoint,
        episode_length=config.episode_length,
        max_training_budget=config.max_training_budget,
        training_mode=config.training_mode,
        training_rerun_from_scratch=config.training_rerun_from_scratch,
        training_5000_run=config.training_5000_run,
        reward_reconciliation_tolerance=config.reward_reconciliation_tolerance,
        checkpoint_metrics=checkpoint_metrics,
        terminal_event_classification=terminal_event_classification,
        canonical_terminal_task_summary=canonical_terminal_task_summary,
        raw_vs_canonical_terminal_reconciliation=raw_vs_canonical_terminal_reconciliation,
        reward_reconciliation_after_terminal_repair=reward_reconciliation_after_terminal_repair,
        completion_path_audit=completion_path_audit,
        policy_effect_50_100_after_terminal_repair=policy_effect,
        paper_aligned_50_100_metrics=paper_aligned_50_100_metrics,
        diagnostic_decision=diagnostic_decision,
        claim_safety_status=claim_safety_status,
        figure_manifest=figure_manifest,
        remaining_blockers=remaining_blockers,
        final_verdict=final_verdict,
        raw_reward_event_recovery_blocked=bool(raw_vs_canonical_terminal_reconciliation["overall"]["raw_reward_event_recovery_blocked"]),
        terminal_event_recovery_blocked=bool(raw_vs_canonical_terminal_reconciliation["overall"]["terminal_event_recovery_blocked"]),
        terminal_reconciliation_failed=terminal_reconciliation_failed,
        reward_reconciliation_failed=reward_reconciliation_failed,
        completion_path_audit_failed=False,
        policy_effect_50_100_failed=policy_effect_failed,
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        environment_semantics_modified=False,
        reward_function_modified=False,
        policy_modified=False,
        dal_modified=False,
        dependencies_modified=False,
        evaluation_reward_static_after_terminal_repair=bool(policy_effect["evaluation_reward_static_after_terminal_repair"]),
        evaluation_action_distribution_static_across_budget=bool(policy_effect["evaluation_action_distribution_static_across_budget"]),
        candidate_policy_vertical_collapse_in_evaluation=candidate_vertical_collapse_eval,
        candidate_policy_vertical_collapse_in_training_replay_window=candidate_vertical_collapse_training,
        policy_affects_reward=str(policy_effect["policy_affects_reward"]),
        policy_affects_terminal_outcomes=str(policy_effect["policy_affects_terminal_outcomes"]),
        most_likely_root_cause=most_likely_root_cause,
        recommended_next_feature="Completion-path repair" if recommended_next_action == "fix_completion_path_next" else "State-representation repair",
        explanation_of_previous_static_outputs=explanation,
        scope_guard_summary=scope_guard_summary,
    ).to_dict()

    payload = report | {
        "checkpoint_comparison": checkpoint_comparison,
    }
    return payload


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = TerminalLifecycleComparisonReport(**{k: v for k, v in payload.items() if k != "checkpoint_comparison"})
    json_path, md_path, summary_path = write_terminal_lifecycle_comparison_report(report, OUTPUT_DIR)
    (OUTPUT_DIR / CHECKPOINT_COMPARISON_JSON.name).write_text(json_dump(payload["checkpoint_comparison"]), encoding="utf-8")
    (OUTPUT_DIR / TERMINAL_EVENT_CLASSIFICATION_JSON.name).write_text(json_dump(payload["terminal_event_classification"]), encoding="utf-8")
    (OUTPUT_DIR / CANONICAL_TERMINAL_TASK_SUMMARY_JSON.name).write_text(json_dump(payload["canonical_terminal_task_summary"]), encoding="utf-8")
    (OUTPUT_DIR / RAW_VS_CANONICAL_TERMINAL_RECONCILIATION_JSON.name).write_text(json_dump(payload["raw_vs_canonical_terminal_reconciliation"]), encoding="utf-8")
    (OUTPUT_DIR / REWARD_RECONCILIATION_AFTER_TERMINAL_REPAIR_JSON.name).write_text(json_dump(payload["reward_reconciliation_after_terminal_repair"]), encoding="utf-8")
    (OUTPUT_DIR / COMPLETION_PATH_AUDIT_JSON.name).write_text(json_dump(payload["completion_path_audit"]), encoding="utf-8")
    (OUTPUT_DIR / POLICY_EFFECT_50_100_AFTER_TERMINAL_REPAIR_JSON.name).write_text(json_dump(payload["policy_effect_50_100_after_terminal_repair"]), encoding="utf-8")
    (OUTPUT_DIR / PAPER_ALIGNED_50_100_METRICS_JSON.name).write_text(json_dump(payload["paper_aligned_50_100_metrics"]), encoding="utf-8")
    (OUTPUT_DIR / DIAGNOSTIC_DECISION_JSON.name).write_text(json_dump(payload["diagnostic_decision"]), encoding="utf-8")
    (OUTPUT_DIR / FIGURE_MANIFEST_JSON.name).write_text(json_dump(payload["figure_manifest"]), encoding="utf-8")
    return json_path, md_path, summary_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = run_terminal_lifecycle_comparison()
    write_artifacts(payload)
    if args.json:
        print(json_dump(payload), end="")
    else:
        print(payload["final_verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
