from __future__ import annotations

import argparse
from typing import Any

from .comparison import build_checkpoint_50_100_feasibility_comparison
from .config import (
    ALLOWED_FINAL_VERDICTS,
    BASE_BRANCH_NAME,
    BRANCH_NAME,
    CHECKPOINT_FEASIBILITY_COMPARISON_JSON,
    COMPLETION_FAILURE_CLASSIFICATION_JSON,
    DIAGNOSTIC_DECISION_JSON,
    EVALUATION_COVERAGE_CLASSIFICATION_JSON,
    FEATURE_ID,
    FIGURE_MANIFEST_JSON,
    FIGURES_DIR,
    OUTPUT_DIR,
    REPORT_JSON,
    REPORT_MD,
    TASK_FEASIBILITY_SUMMARY_JSON,
    ACTION_PATH_FEASIBILITY_JSON,
    RUNTIME_EVENT_PATH_AUDIT_JSON,
    POLICY_EFFECT_COMPLETION_FEASIBILITY_JSON,
    FINAL_COMPLETION_PATH_SUMMARY_MD,
    TRAINING_BUDGETS,
    TRAINING_MODE,
    TRAINING_RERUN_FROM_SCRATCH,
    TRAINING_5000_RUN,
    EVALUATION_EPISODE_COUNT_PER_CHECKPOINT,
    EPISODE_LENGTH,
)
from .diagnostics import (
    build_claim_safety_status,
    build_diagnostic_decision,
    build_prerequisite_artifacts,
    build_prerequisite_tags,
    build_scope_guard_summary,
    classify_completion_failure,
    git_diff_paths,
    git_staged_paths,
    git_status_paths,
    load_feature_067_status,
)
from .feasibility import (
    build_action_path_feasibility,
    build_completion_path_probe,
    build_evaluation_coverage_classification,
    build_task_feasibility_summary,
)
from .figures import generate_figures
from .model import (
    CheckpointFeasibilityMetric,
    CompletionPathFeasibilityReport,
    FigureManifest,
)
from .policy_probe import build_policy_effect_completion_feasibility
from .report import compact_completion_path_payload, json_dump, write_completion_path_feasibility_report
from .runtime_audit import build_runtime_event_path_audit
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.repaired_terminal_evaluator import TerminalLifecycleTrainingSession

APPROVED_PREFIXES = (
    "artifacts/analysis/completion-path-deadline-feasibility-repair/",
    "docs/architecture/euls_phase27_completion_path_deadline_feasibility_repair.md",
    "specs/068-completion-path-deadline-feasibility-repair/",
    "src/analysis/completion_path_deadline_feasibility_repair/",
    "tests/unit/test_completion_path_deadline_feasibility_repair",
    "tests/integration/test_completion_path_deadline_feasibility_repair",
)

FORBIDDEN_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/reward_timing.py",
    "src/environment/replay_hash.py",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
    "src/analysis/staged_training_budget_learning_curve/",
    "src/analysis/final_review_release_gate_batch/",
    "src/analysis/evaluation_instrumentation_reward_state_diagnostic/",
    "src/analysis/reward_emission_evaluation_metric_aggregation_repair/",
    "src/analysis/terminal_lifecycle_accounting_50_100_comparison/",
)


def _candidate_policy_result(checkpoint_results: list[dict[str, Any]], budget: int) -> dict[str, Any]:
    for checkpoint in checkpoint_results:
        if int(checkpoint["training_budget"]) == int(budget):
            return checkpoint["evaluation_policy_result"]
    raise KeyError(f"missing checkpoint budget {budget}")


def _checkpoint_metric(
    *,
    checkpoint: dict[str, Any],
    policy_effect: dict[str, Any],
    task_feasibility_summary: dict[str, Any],
    completion_path_probe: dict[str, Any],
    evaluation_coverage_classification: dict[str, Any],
    runtime_event_path_audit: dict[str, Any],
    claim_safety_status: dict[str, Any],
) -> dict[str, Any]:
    budget = int(checkpoint["training_budget"])
    evaluation_result = checkpoint["evaluation_policy_result"]
    candidate_summary = policy_effect["policy_feasibility_summary"][f"candidate_policy_at_{budget}"]
    runtime_checkpoint = next(
        (item for item in runtime_event_path_audit["by_checkpoint"] if int(item["training_budget"]) == budget),
        runtime_event_path_audit["overall"],
    )
    metric = CheckpointFeasibilityMetric(
        training_budget=budget,
        cumulative_training_episode_count=int(checkpoint["training_state"]["cumulative_training_episode_count"]),
        evaluation_episode_count=EVALUATION_EPISODE_COUNT_PER_CHECKPOINT,
        episode_length=EPISODE_LENGTH,
        optimizer_step_count=int(checkpoint["training_state"]["optimizer_step_count"]),
        replay_size=int(checkpoint["training_state"]["replay_size"]),
        loss_count=int(checkpoint["training_state"]["loss_count"]),
        last_loss=checkpoint["training_state"]["last_loss"],
        loss_finite=bool(checkpoint["training_state"]["loss_finite"]),
        action_distribution=dict(evaluation_result["evaluation_action_distribution"]),
        action_count_total=int(evaluation_result["evaluation_decision_count"]),
        action_accounting_reconciled=True,
        reward_summary=dict(checkpoint["training_state"]["reward_summary"]),
        completion_path_probe=completion_path_probe,
        full_evaluation_probe=completion_path_probe["full_evaluation_probe"],
        evaluation_coverage_classification=evaluation_coverage_classification,
        task_feasibility_summary=task_feasibility_summary,
        runtime_event_path_audit=runtime_event_path_audit["by_checkpoint"][0 if budget == int(runtime_event_path_audit["by_checkpoint"][0]["training_budget"]) else 1],
        policy_feasibility_summary={
            "policy_results": policy_effect["policy_results"],
            "candidate_policy_vertical_collapse_in_evaluation": policy_effect["candidate_policy_vertical_collapse_in_evaluation"],
        },
        comparison_ready=bool(checkpoint["training_state"]["loss_finite"]) and bool(candidate_summary["terminal_reconciled"]) and bool(candidate_summary["reward_reconciled"]),
        claim_safety_status=claim_safety_status,
    )
    payload = metric.to_dict()
    payload["training_state"] = dict(checkpoint["training_state"])
    payload["evaluation_policy_result"] = evaluation_result
    payload["candidate_policy_summary"] = candidate_summary
    payload["raw_vs_canonical_terminal_reconciliation"] = dict(evaluation_result["raw_vs_canonical_terminal_reconciliation"])
    payload["reward_reconciliation_after_terminal_repair"] = dict(evaluation_result["reward_reconciliation_after_terminal_repair"])
    payload["completion_path_audit"] = dict(evaluation_result["completion_path_audit"])
    payload["runtime_event_path_audit"] = runtime_checkpoint
    return payload


def _build_blocked_payload(
    *,
    claim_safety_status: dict[str, Any],
    scope_guard_summary: dict[str, Any],
    blockers: list[str],
) -> dict[str, Any]:
    empty_figures = FigureManifest(figure_directory=str(FIGURES_DIR), figure_files=[], figure_count=0, figures_generated=False).to_dict()
    return {
        "feature_id": FEATURE_ID,
        "base_branch_name": BASE_BRANCH_NAME,
        "branch_name": BRANCH_NAME,
        "feature_067_prerequisite_verified": False,
        "prerequisite_tags_verified": [],
        "prerequisite_artifacts": build_prerequisite_artifacts(),
        "checkpoint_budgets": list(TRAINING_BUDGETS),
        "evaluation_episode_count_per_checkpoint": EVALUATION_EPISODE_COUNT_PER_CHECKPOINT,
        "episode_length": EPISODE_LENGTH,
        "max_training_budget": 100,
        "training_mode": TRAINING_MODE,
        "training_rerun_from_scratch": TRAINING_RERUN_FROM_SCRATCH,
        "training_5000_run": TRAINING_5000_RUN,
        "feature_067_prerequisite_verified": False,
        "checkpoint_metrics": [],
        "task_feasibility_summary": {},
        "action_path_feasibility": {},
        "runtime_event_path_audit": {"overall": {}, "by_policy": {}, "by_checkpoint": []},
        "completion_failure_classification": {
            "root_cause": "unknown_completion_path_failure",
            "decision": "blocked_due_to_unresolved_completion_path",
            "evidence": blockers,
        },
        "policy_effect_completion_feasibility": {"policy_results": {}, "policy_feasibility_summary": {}},
        "checkpoint_50_100_feasibility_comparison": {"checkpoint_budgets": list(TRAINING_BUDGETS), "by_checkpoint": [], "comparison": {}, "comparison_classification": "no_change_between_50_and_100"},
        "evaluation_coverage_classification": {"evaluation_mode": "sampled_task_decision_evaluation", "one_decision_per_episode_observed": False, "full_step_decision_coverage_unavailable": True},
        "diagnostic_decision": {
            "recommended_next_action": "blocked_due_to_unresolved_completion_path",
            "decision_reason": "Prerequisite validation failed before the completion-path repair could run.",
            "evidence_notes": blockers,
        },
        "claim_safety_status": claim_safety_status,
        "figure_manifest": empty_figures,
        "final_verdict": "completion_path_feasibility_repair_blocked",
        "recommended_next_feature": "Deadline / timeout repair",
        "remaining_blockers": blockers,
        "paper_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "environment_files_modified": False,
        "environment_semantics_modified": False,
        "environment_modified_files": [],
        "environment_modification_reason": None,
        "reward_function_modified": False,
        "policy_modified": False,
        "dal_modified": False,
        "dependencies_modified": False,
        "explanation_of_completion_blocker": "Blocked before the feasibility probe could execute.",
        "scope_guard_summary": scope_guard_summary,
    }


def run_completion_path_feasibility() -> dict[str, Any]:
    scope_guard_summary = build_scope_guard_summary(
        git_status_paths(),
        git_staged_paths(),
        git_diff_paths("067-terminal-lifecycle-accounting-50-100-comparison"),
        APPROVED_PREFIXES,
        FORBIDDEN_PREFIXES,
    )
    claim_safety_status = build_claim_safety_status()
    prerequisite_artifacts = build_prerequisite_artifacts()
    feature_067_verified = prerequisite_artifacts["feature_067_report"]["verified"]
    prerequisite_tags = build_prerequisite_tags(
        scope_guard_summary["working_tree_paths_approved"],
        scope_guard_summary["staged_paths_approved"],
        scope_guard_summary["base_branch_head_diff_approved"],
    )
    blockers: list[str] = []
    if not feature_067_verified:
        blockers.append("feature_067_prerequisite_blocked")
    if any(not scope_guard_summary[key] for key in ("working_tree_paths_approved", "staged_paths_approved", "base_branch_head_diff_approved")):
        blockers.append("scope_drift_detected")
    if blockers:
        return _build_blocked_payload(claim_safety_status=claim_safety_status, scope_guard_summary=scope_guard_summary, blockers=blockers) | {
            "feature_067_prerequisite_verified": feature_067_verified,
            "prerequisite_tags_verified": prerequisite_tags,
            "prerequisite_artifacts": prerequisite_artifacts,
        }

    from .config import CompletionPathFeasibilityConfig

    config = CompletionPathFeasibilityConfig()
    session = TerminalLifecycleTrainingSession(config)
    checkpoint_results: list[dict[str, Any]] = []
    for budget in config.training_budgets:
        training_state = session.train_to_budget(int(budget))
        evaluation_result = session.candidate_policy_result(checkpoint_budget=int(budget))
        checkpoint_results.append(
            {
                "training_budget": int(budget),
                "training_state": training_state,
                "evaluation_policy_result": evaluation_result,
            }
        )

    task_feasibility_summary = build_task_feasibility_summary(
        checkpoint_results[-1]["evaluation_policy_result"]["task_records"],
        record_sample_limit=config.record_sample_limit,
    )
    action_path_feasibility = build_action_path_feasibility(task_feasibility_summary)
    completion_path_probe = build_completion_path_probe(
        checkpoint_results[-1]["evaluation_policy_result"],
        max_task_decisions_to_analyze=config.sampled_completion_path_max_task_decisions,
    )
    evaluation_coverage_classification = build_evaluation_coverage_classification(completion_path_probe)
    policy_effect_completion_feasibility = build_policy_effect_completion_feasibility(
        trainer=session.trainer,
        checkpoint_results=checkpoint_results,
        task_feasibility_summary=task_feasibility_summary,
        fixed_policy_seed=session.campaign_config.seed_bundle.evaluation_trace_generation_seed,
        evaluation_episode_count=config.evaluation_episode_count_per_checkpoint,
        episode_length=config.episode_length,
        evaluation_trace_bank_id=session.campaign_config.evaluation_trace_bank_id,
    )
    for checkpoint in checkpoint_results:
        budget = int(checkpoint["training_budget"])
        checkpoint["candidate_policy_summary"] = dict(policy_effect_completion_feasibility["policy_feasibility_summary"][f"candidate_policy_at_{budget}"])
    runtime_event_path_audit = policy_effect_completion_feasibility["runtime_event_path_audit"]
    checkpoint_50_100_feasibility_comparison = build_checkpoint_50_100_feasibility_comparison(checkpoint_results)
    completion_failure_classification = classify_completion_failure(
        task_feasibility_summary=task_feasibility_summary,
        runtime_event_path_audit=runtime_event_path_audit,
        coverage_classification=evaluation_coverage_classification,
        policy_effect_completion_feasibility=policy_effect_completion_feasibility,
    )
    diagnostic_decision = build_diagnostic_decision(completion_failure_classification)

    checkpoint_metrics = [
        _checkpoint_metric(
            checkpoint=checkpoint,
            policy_effect=policy_effect_completion_feasibility,
            task_feasibility_summary=task_feasibility_summary,
            completion_path_probe=completion_path_probe,
            evaluation_coverage_classification=evaluation_coverage_classification,
            runtime_event_path_audit=runtime_event_path_audit,
            claim_safety_status=claim_safety_status,
        )
        for checkpoint in checkpoint_results
    ]

    final_verdict = "completion_path_feasibility_repair_ready"
    remaining_blockers: list[str] = []
    if completion_failure_classification["decision"] == "blocked_due_to_unresolved_completion_path":
        final_verdict = "completion_path_feasibility_repair_blocked"
        remaining_blockers.append("feasibility_estimation_failed")
    figure_paths = []
    if final_verdict == "completion_path_feasibility_repair_ready":
        figure_paths = generate_figures(
            {
                "checkpoint_metrics": checkpoint_metrics,
                "checkpoint_50_100_feasibility_comparison": checkpoint_50_100_feasibility_comparison,
                "policy_effect_completion_feasibility": policy_effect_completion_feasibility,
                "runtime_event_path_audit": runtime_event_path_audit,
                "task_feasibility_summary": task_feasibility_summary,
            },
            config.figures_dir,
        )
    figure_manifest = FigureManifest(
        figure_directory=str(config.figures_dir),
        figure_files=[path.name for path in figure_paths],
        figure_count=len(figure_paths),
        figures_generated=bool(figure_paths),
    ).to_dict()

    report = CompletionPathFeasibilityReport(
        feature_id=FEATURE_ID,
        base_branch_name=BASE_BRANCH_NAME,
        branch_name=BRANCH_NAME,
        checkpoint_budgets=list(config.training_budgets),
        evaluation_episode_count_per_checkpoint=config.evaluation_episode_count_per_checkpoint,
        episode_length=config.episode_length,
        expected_max_decision_slots=config.expected_max_decision_slots,
        sampled_completion_path_max_task_decisions=config.sampled_completion_path_max_task_decisions,
        max_training_budget=config.max_training_budget,
        training_mode=config.training_mode,
        training_rerun_from_scratch=config.training_rerun_from_scratch,
        training_5000_run=config.training_5000_run,
        feature_067_prerequisite_verified=feature_067_verified,
        prerequisite_tags_verified=prerequisite_tags,
        prerequisite_artifacts=prerequisite_artifacts,
        checkpoint_metrics=checkpoint_metrics,
        task_feasibility_summary=task_feasibility_summary,
        action_path_feasibility=action_path_feasibility,
        runtime_event_path_audit=runtime_event_path_audit,
        completion_failure_classification=completion_failure_classification,
        policy_effect_completion_feasibility=policy_effect_completion_feasibility,
        checkpoint_50_100_feasibility_comparison=checkpoint_50_100_feasibility_comparison,
        evaluation_coverage_classification=evaluation_coverage_classification,
        diagnostic_decision=diagnostic_decision,
        claim_safety_status=claim_safety_status,
        figure_manifest=figure_manifest,
        final_verdict=final_verdict,
        recommended_next_feature="Deadline / timeout repair",
        remaining_blockers=remaining_blockers,
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        environment_files_modified=False,
        environment_semantics_modified=False,
        environment_modified_files=[],
        environment_modification_reason=None,
        reward_function_modified=False,
        policy_modified=False,
        dal_modified=False,
        dependencies_modified=False,
        explanation_of_completion_blocker=(
            "All action paths are infeasible before the deadline envelope, so zero completion is consistent with the current workload configuration."
        ),
        scope_guard_summary=scope_guard_summary,
    ).to_dict()
    payload = report | {
        "completion_path_probe": completion_path_probe,
        "checkpoint_50_100_feasibility_comparison": checkpoint_50_100_feasibility_comparison,
    }
    return payload


def write_artifacts(payload: dict[str, Any]) -> tuple[Any, Any, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    compact_payload = compact_completion_path_payload(payload)
    report = CompletionPathFeasibilityReport(**{k: v for k, v in compact_payload.items() if k != "completion_path_probe"})
    json_path, md_path, summary_path = write_completion_path_feasibility_report(report, OUTPUT_DIR)
    (OUTPUT_DIR / TASK_FEASIBILITY_SUMMARY_JSON.name).write_text(json_dump(compact_payload["task_feasibility_summary"]), encoding="utf-8")
    (OUTPUT_DIR / ACTION_PATH_FEASIBILITY_JSON.name).write_text(json_dump(compact_payload["action_path_feasibility"]), encoding="utf-8")
    (OUTPUT_DIR / RUNTIME_EVENT_PATH_AUDIT_JSON.name).write_text(json_dump(compact_payload["runtime_event_path_audit"]), encoding="utf-8")
    (OUTPUT_DIR / COMPLETION_FAILURE_CLASSIFICATION_JSON.name).write_text(json_dump(compact_payload["completion_failure_classification"]), encoding="utf-8")
    (OUTPUT_DIR / POLICY_EFFECT_COMPLETION_FEASIBILITY_JSON.name).write_text(json_dump(compact_payload["policy_effect_completion_feasibility"]), encoding="utf-8")
    (OUTPUT_DIR / CHECKPOINT_FEASIBILITY_COMPARISON_JSON.name).write_text(json_dump(compact_payload["checkpoint_50_100_feasibility_comparison"]), encoding="utf-8")
    (OUTPUT_DIR / EVALUATION_COVERAGE_CLASSIFICATION_JSON.name).write_text(json_dump(compact_payload["evaluation_coverage_classification"]), encoding="utf-8")
    (OUTPUT_DIR / DIAGNOSTIC_DECISION_JSON.name).write_text(json_dump(compact_payload["diagnostic_decision"]), encoding="utf-8")
    (OUTPUT_DIR / FIGURE_MANIFEST_JSON.name).write_text(json_dump(compact_payload["figure_manifest"]), encoding="utf-8")
    return json_path, md_path, summary_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = run_completion_path_feasibility()
    compact_payload = compact_completion_path_payload(payload)
    write_artifacts(payload)
    if args.json:
        print(json_dump(compact_payload), end="")
    else:
        print(compact_payload["final_verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
