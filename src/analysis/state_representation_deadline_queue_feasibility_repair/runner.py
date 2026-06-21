from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .comparison import (
    build_action_collapse_diagnostics,
    build_legacy_vs_new_state_profile_comparison,
    build_policy_summaries,
    build_reconciliation_after_state_repair,
    build_selected_action_feasibility_diagnostics,
    build_state_profile_50_100_comparison,
    load_legacy_state_profile_report,
)
from .config import (
    BASE_BRANCH_NAME,
    BRANCH_NAME,
    CHECKPOINT_BUDGETS,
    DIAGNOSTIC_DECISION_JSON,
    EVALUATION_EPISODE_COUNT,
    EPISODE_LENGTH,
    FEATURE_ID,
    FIGURES_DIR,
    FIGURE_MANIFEST_JSON,
    FINAL_STATE_REPAIR_SUMMARY_MD,
    LEGACY_STATE_REPRESENTATION_PROFILE,
    LEGACY_VS_NEW_STATE_PROFILE_COMPARISON_JSON,
    MAX_TRAINING_BUDGET,
    NEW_STATE_REPRESENTATION_PROFILE,
    OUTPUT_DIR,
    REPORT_JSON,
    REPORT_MD,
    SELECTED_ACTION_FEASIBILITY_DIAGNOSTICS_JSON,
    STATE_FEATURE_COVERAGE_AUDIT_JSON,
    STATE_NORMALIZATION_AUDIT_JSON,
    STATE_PROFILE_50_100_COMPARISON_JSON,
    STATE_REPRESENTATION_REPAIR_REPORT_JSON,
    STATE_REPRESENTATION_REPAIR_REPORT_MD,
    StateRepresentationRepairConfig,
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
    load_feature_070_status,
)
from .figures import generate_figures
from .model import (
    ActionCollapseDiagnostics,
    FigureManifest,
    SelectedActionFeasibilityDiagnostics,
    StateFeatureCoverageAudit,
    StateNormalizationAudit,
    StateProfileComparison,
    StateRepresentationRepairReport,
)
from .policy_probe import StateRepresentationTrainingSession, build_state_representation_policy_effect_comparison
from .report import write_state_representation_repair_outputs
from .state_audit import build_state_feature_coverage_audit, build_state_normalization_audit
from .state_profile_adapter import build_profiled_campaign_config


def _build_checkpoint_results(
    session: StateRepresentationTrainingSession,
    checkpoint_budgets: tuple[int, ...],
) -> list[dict[str, Any]]:
    checkpoint_results: list[dict[str, Any]] = []
    for budget in checkpoint_budgets:
        training_state = session.train_to_budget(int(budget))
        evaluation_result = session.candidate_policy_result(checkpoint_budget=int(budget))
        checkpoint_results.append(
            {
                "training_budget": int(budget),
                "training_state": training_state,
                "evaluation_policy_result": evaluation_result,
            }
        )
    return checkpoint_results


def _state_feature_groups_complete(state_feature_coverage_audit: dict[str, Any]) -> bool:
    groups = dict(state_feature_coverage_audit.get("state_feature_group_coverage", {}))
    required_groups = ("minimal", "deadline_timeout", "action_path_feasibility", "queue_pressure", "legal_availability", "source_context")
    return all(bool(groups.get(group, {}).get("covered", False)) for group in required_groups)


def _queue_feature_group_complete(state_feature_coverage_audit: dict[str, Any]) -> bool:
    groups = dict(state_feature_coverage_audit.get("state_feature_group_coverage", {}))
    return bool(groups.get("queue_pressure", {}).get("covered", False))


def _modified_core_state_files(scope_guard_summary: dict[str, Any]) -> list[str]:
    allowed = {
        "src/analysis/full_training_reproduction_campaign/replay.py",
        "src/analysis/full_training_reproduction_campaign/trainer.py",
        "src/analysis/full_training_reproduction_campaign/config.py",
    }
    return [path for path in scope_guard_summary.get("diff_paths", []) if path in allowed]


def _build_blocked_payload(*, blockers: list[str], claim_safety_status: dict[str, Any], scope_guard_summary: dict[str, Any], prerequisite_artifacts: dict[str, Any], prerequisite_tags: list[dict[str, Any]]) -> dict[str, Any]:
    empty_audit = {
        "legacy_state_dim": 3,
        "new_state_dim": 30,
        "added_feature_count": 27,
        "added_feature_names": [],
        "missing_or_approximated_state_features": [],
        "state_feature_group_coverage": {},
        "state_normalization_summary": {
            "no_nan_in_state_vector": False,
            "no_inf_in_state_vector": False,
            "state_vector_min": 0.0,
            "state_vector_max": 0.0,
            "state_dim_consistent_across_train_eval": False,
        },
        "state_sample_records": [],
        "train_eval_state_dim_match": False,
        "calibration_profile_name": "paper_aligned_feasible_v1",
    }
    blocked_decision = build_diagnostic_decision(
        state_dim_match=False,
        no_nan_or_inf=False,
        state_feature_coverage_complete=False,
        reward_reconciliation_passed=False,
        terminal_reconciliation_passed=False,
        completion_count_nonzero=False,
        fixed_policy_completion_present=False,
        action_collapse_reduced=False,
        selected_action_feasibility_improved=False,
        queue_feature_coverage_complete=False,
    )
    report = StateRepresentationRepairReport(
        feature_id=FEATURE_ID,
        base_branch_name=BASE_BRANCH_NAME,
        branch_name=BRANCH_NAME,
        feature_070_prerequisite_verified=False,
        metric_universe_consistency_passed=False,
        prerequisite_artifacts=prerequisite_artifacts,
        prerequisite_tags_verified=prerequisite_tags,
        scope_guard_summary=scope_guard_summary,
        calibration_profile_name="paper_aligned_feasible_v1",
        state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE,
        legacy_state_representation_profile=LEGACY_STATE_REPRESENTATION_PROFILE,
        checkpoint_budgets=list(CHECKPOINT_BUDGETS),
        evaluation_episode_count=EVALUATION_EPISODE_COUNT,
        episode_length=EPISODE_LENGTH,
        max_training_budget=MAX_TRAINING_BUDGET,
        training_mode=TRAINING_MODE,
        training_rerun_from_scratch=TRAINING_RERUN_FROM_SCRATCH,
        training_5000_run=TRAINING_5000_RUN,
        legacy_state_dim=3,
        new_state_dim=30,
        state_feature_coverage_audit=empty_audit,
        state_normalization_audit=empty_audit["state_normalization_summary"],
        legacy_vs_new_state_profile_comparison={},
        state_profile_50_100_comparison={},
        action_collapse_diagnostics={},
        selected_action_feasibility_diagnostics={},
        policy_effect_after_state_repair={},
        reconciliation_after_state_repair={
            "reward_reconciliation_passed": False,
            "terminal_reconciliation_passed": False,
            "raw_vs_canonical_reward_delta_max": 0.0,
            "policies_with_reward_reconciled_false": [],
            "policies_with_terminal_reconciled_false": [],
        },
        diagnostic_decision=blocked_decision,
        claim_safety_status=claim_safety_status,
        figure_manifest={"figure_directory": str(FIGURES_DIR), "figure_files": [], "figure_count": 0, "figures_generated": False},
        final_verdict="state_representation_deadline_queue_feasibility_blocked",
        remaining_blockers=blockers,
        recommended_next_feature="Reward alignment",
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        reward_function_modified=False,
        environment_semantics_modified=False,
        policy_algorithm_modified=False,
        dal_modified=False,
        dependencies_modified=False,
        core_state_builder_modified=bool(
            _modified_core_state_files(scope_guard_summary)
        ),
        modified_core_state_files=_modified_core_state_files(scope_guard_summary),
        modification_reason="profile-aware state representation",
        legacy_profile_preserved=True,
    ).to_dict()
    return report


def run_state_representation_repair() -> dict[str, Any]:
    claim_safety_status = build_claim_safety_status()
    prerequisite_artifacts = build_prerequisite_artifacts()
    prerequisite_070 = prerequisite_artifacts["feature_070_report"]["verified"]
    scope_guard_summary = build_scope_guard_summary(
        git_status_paths(),
        git_staged_paths(),
        git_diff_paths("070-calibration-metric-consistency-reconciliation-fix"),
    )
    prerequisite_tags = build_prerequisite_tags(
        scope_guard_summary["working_tree_paths_approved"],
        scope_guard_summary["staged_paths_approved"],
        scope_guard_summary["base_branch_head_diff_approved"],
    )

    if not prerequisite_070:
        return _build_blocked_payload(
            blockers=["feature_070_prerequisite_blocked"],
            claim_safety_status=claim_safety_status,
            scope_guard_summary=scope_guard_summary,
            prerequisite_artifacts=prerequisite_artifacts,
            prerequisite_tags=prerequisite_tags,
        )
    if not scope_guard_summary["working_tree_paths_approved"] or not scope_guard_summary["staged_paths_approved"] or not scope_guard_summary["base_branch_head_diff_approved"]:
        return _build_blocked_payload(
            blockers=["scope_drift_detected"],
            claim_safety_status=claim_safety_status,
            scope_guard_summary=scope_guard_summary,
            prerequisite_artifacts=prerequisite_artifacts,
            prerequisite_tags=prerequisite_tags,
        )

    feature_config = StateRepresentationRepairConfig()
    config = build_profiled_campaign_config(state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE)
    session = StateRepresentationTrainingSession(config=feature_config, state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE)
    checkpoint_results = _build_checkpoint_results(session, feature_config.checkpoint_budgets)

    state_feature_coverage_audit = build_state_feature_coverage_audit(sample_limit=feature_config.record_sample_limit)
    state_normalization_audit = build_state_normalization_audit(state_feature_coverage_audit)

    policy_effect_after_state_repair = build_state_representation_policy_effect_comparison(
        session=session,
        checkpoint_results=checkpoint_results,
        record_sample_limit=feature_config.record_sample_limit,
    )
    policy_summaries = dict(policy_effect_after_state_repair.get("policy_summaries", {}))
    if not policy_summaries:
        policy_summaries = build_policy_summaries(dict(policy_effect_after_state_repair.get("policy_results", {})))
    policy_effect_after_state_repair = dict(policy_effect_after_state_repair)
    policy_effect_after_state_repair["policy_summaries"] = policy_summaries
    policy_effect_after_state_repair["any_fixed_policy_completes"] = any(
        int(policy_summaries.get(name, {}).get("completed_count", 0)) > 0
        for name in ("fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy")
    )
    for policy_name, summary in policy_summaries.items():
        policy_effect_after_state_repair[policy_name] = summary

    legacy_report = load_legacy_state_profile_report()
    legacy_vs_new_state_profile_comparison = build_legacy_vs_new_state_profile_comparison(
        legacy_report=legacy_report,
        new_state_audit=state_feature_coverage_audit,
        policy_summaries=policy_summaries,
    )
    state_profile_50_100_comparison = build_state_profile_50_100_comparison(policy_summaries)

    legacy_candidate_100 = list(legacy_report.get("consistent_50_100_comparison", {}).get("by_checkpoint", []))
    legacy_candidate_100_summary = legacy_candidate_100[1] if len(legacy_candidate_100) > 1 else {}
    new_candidate_100_summary = dict(policy_summaries.get("candidate_policy_at_100", {}))
    action_collapse_diagnostics = build_action_collapse_diagnostics(legacy_candidate_100_summary, new_candidate_100_summary)
    selected_action_feasibility_diagnostics = build_selected_action_feasibility_diagnostics(legacy_candidate_100_summary, new_candidate_100_summary)
    reconciliation_after_state_repair = build_reconciliation_after_state_repair(policy_summaries)

    reward_reconciliation_passed = bool(reconciliation_after_state_repair["reward_reconciliation_passed"])
    terminal_reconciliation_passed = bool(reconciliation_after_state_repair["terminal_reconciliation_passed"])
    state_dim_match = bool(state_normalization_audit["state_dim_consistent_across_train_eval"])
    no_nan_or_inf = bool(state_normalization_audit["no_nan_in_state_vector"]) and bool(state_normalization_audit["no_inf_in_state_vector"])
    state_feature_coverage_complete = _state_feature_groups_complete(state_feature_coverage_audit)
    queue_feature_coverage_complete = _queue_feature_group_complete(state_feature_coverage_audit)
    completion_count_nonzero = int(policy_summaries.get("candidate_policy_at_100", {}).get("completed_count", 0)) > 0
    fixed_policy_completion_present = any(int(policy_summaries.get(name, {}).get("completed_count", 0)) > 0 for name in ("fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy"))
    action_collapse_reduced = bool(action_collapse_diagnostics["action_collapse_reduced"])
    selected_action_feasibility_improved = float(selected_action_feasibility_diagnostics["selected_action_feasible_ratio_delta"]) > 0.0

    diagnostic_decision = build_diagnostic_decision(
        state_dim_match=state_dim_match,
        no_nan_or_inf=no_nan_or_inf,
        state_feature_coverage_complete=state_feature_coverage_complete,
        reward_reconciliation_passed=reward_reconciliation_passed,
        terminal_reconciliation_passed=terminal_reconciliation_passed,
        completion_count_nonzero=completion_count_nonzero,
        fixed_policy_completion_present=fixed_policy_completion_present,
        action_collapse_reduced=action_collapse_reduced,
        selected_action_feasibility_improved=selected_action_feasibility_improved,
        queue_feature_coverage_complete=queue_feature_coverage_complete,
    )

    if not reward_reconciliation_passed:
        remaining_blockers = ["reward_reconciliation_failed"]
        final_verdict = "state_representation_deadline_queue_feasibility_blocked"
    elif not terminal_reconciliation_passed:
        remaining_blockers = ["terminal_reconciliation_failed"]
        final_verdict = "state_representation_deadline_queue_feasibility_blocked"
    elif not state_dim_match:
        remaining_blockers = ["state_dim_mismatch"]
        final_verdict = "state_representation_deadline_queue_feasibility_blocked"
    elif not no_nan_or_inf:
        remaining_blockers = ["state_nan_or_inf_detected"]
        final_verdict = "state_representation_deadline_queue_feasibility_blocked"
    elif not state_feature_coverage_complete:
        remaining_blockers = ["state_feature_coverage_incomplete"]
        final_verdict = "state_representation_deadline_queue_feasibility_blocked"
    elif not completion_count_nonzero:
        remaining_blockers = ["completion_count_zero"]
        final_verdict = "state_representation_deadline_queue_feasibility_blocked"
    else:
        remaining_blockers = []
        final_verdict = "state_representation_deadline_queue_feasibility_ready"

    report = StateRepresentationRepairReport(
        feature_id=FEATURE_ID,
        base_branch_name=BASE_BRANCH_NAME,
        branch_name=BRANCH_NAME,
        feature_070_prerequisite_verified=prerequisite_070,
        metric_universe_consistency_passed=True,
        prerequisite_artifacts=prerequisite_artifacts,
        prerequisite_tags_verified=prerequisite_tags,
        scope_guard_summary=scope_guard_summary,
        calibration_profile_name="paper_aligned_feasible_v1",
        state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE,
        legacy_state_representation_profile=LEGACY_STATE_REPRESENTATION_PROFILE,
        checkpoint_budgets=list(CHECKPOINT_BUDGETS),
        evaluation_episode_count=EVALUATION_EPISODE_COUNT,
        episode_length=EPISODE_LENGTH,
        max_training_budget=MAX_TRAINING_BUDGET,
        training_mode=TRAINING_MODE,
        training_rerun_from_scratch=TRAINING_RERUN_FROM_SCRATCH,
        training_5000_run=TRAINING_5000_RUN,
        legacy_state_dim=int(state_feature_coverage_audit["legacy_state_dim"]),
        new_state_dim=int(state_feature_coverage_audit["new_state_dim"]),
        state_feature_coverage_audit=state_feature_coverage_audit,
        state_normalization_audit=state_normalization_audit,
        legacy_vs_new_state_profile_comparison=legacy_vs_new_state_profile_comparison,
        state_profile_50_100_comparison=state_profile_50_100_comparison,
        action_collapse_diagnostics=ActionCollapseDiagnostics(
            legacy_state_dim=int(action_collapse_diagnostics["legacy_state_dim"]),
            new_state_dim=int(action_collapse_diagnostics["new_state_dim"]),
            legacy_action_entropy=float(action_collapse_diagnostics["legacy"]["action_entropy"]),
            new_action_entropy=float(action_collapse_diagnostics["new_state"]["action_entropy"]),
            legacy_dominant_action_share=float(action_collapse_diagnostics["legacy"]["dominant_action_share"]),
            new_dominant_action_share=float(action_collapse_diagnostics["new_state"]["dominant_action_share"]),
            legacy_is_action_collapsed=bool(action_collapse_diagnostics["legacy"]["is_action_collapsed"]),
            new_is_action_collapsed=bool(action_collapse_diagnostics["new_state"]["is_action_collapsed"]),
            legacy_dominant_action_name=action_collapse_diagnostics["legacy"]["dominant_action_name"],
            new_dominant_action_name=action_collapse_diagnostics["new_state"]["dominant_action_name"],
            action_collapse_reduced=bool(action_collapse_diagnostics["action_collapse_reduced"]),
        ).to_dict(),
        selected_action_feasibility_diagnostics=SelectedActionFeasibilityDiagnostics(
            legacy_selected_action_feasible_ratio=float(selected_action_feasibility_diagnostics["legacy_selected_action_feasible_ratio"]),
            new_state_selected_action_feasible_ratio=float(selected_action_feasibility_diagnostics["new_state_selected_action_feasible_ratio"]),
            selected_action_feasible_ratio_delta=float(selected_action_feasibility_diagnostics["selected_action_feasible_ratio_delta"]),
            completed_selected_action_feasible_delta=int(selected_action_feasibility_diagnostics["completed_selected_action_feasible_delta"]),
            dropped_selected_action_infeasible_delta=int(selected_action_feasibility_diagnostics["dropped_selected_action_infeasible_delta"]),
            legacy_completed_selected_action_feasible_count=int(legacy_candidate_100_summary.get("completed_selected_action_feasible_count", 0)),
            new_completed_selected_action_feasible_count=int(new_candidate_100_summary.get("completed_selected_action_feasible_count", 0)),
            legacy_dropped_selected_action_feasible_count=int(legacy_candidate_100_summary.get("dropped_selected_action_feasible_count", 0)),
            new_dropped_selected_action_feasible_count=int(new_candidate_100_summary.get("dropped_selected_action_feasible_count", 0)),
            legacy_selected_action_feasible_task_count=int(legacy_candidate_100_summary.get("selected_action_feasible_task_count", 0)),
            new_state_selected_action_feasible_task_count=int(new_candidate_100_summary.get("selected_action_feasible_task_count", 0)),
        ).to_dict(),
        policy_effect_after_state_repair=policy_effect_after_state_repair,
        reconciliation_after_state_repair=reconciliation_after_state_repair,
        diagnostic_decision=diagnostic_decision,
        claim_safety_status=claim_safety_status,
        figure_manifest={},
        final_verdict=final_verdict,
        remaining_blockers=remaining_blockers,
        recommended_next_feature="Reward alignment" if final_verdict == "state_representation_deadline_queue_feasibility_ready" else "Policy exploration",
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        reward_function_modified=False,
        environment_semantics_modified=False,
        policy_algorithm_modified=False,
        dal_modified=False,
        dependencies_modified=False,
        core_state_builder_modified=True,
        modified_core_state_files=_modified_core_state_files(scope_guard_summary),
        modification_reason="profile-aware state representation",
        legacy_profile_preserved=True,
    )

    payload = report.to_dict()
    figure_paths = generate_figures(
        {
            "state_feature_coverage_audit": state_feature_coverage_audit,
            "legacy_vs_new_state_profile_comparison": legacy_vs_new_state_profile_comparison,
            "action_collapse_diagnostics": action_collapse_diagnostics,
            "selected_action_feasibility_diagnostics": selected_action_feasibility_diagnostics,
            "state_profile_50_100_comparison": state_profile_50_100_comparison,
            "policy_effect_after_state_repair": policy_effect_after_state_repair,
        },
        FIGURES_DIR,
    )
    payload["figure_manifest"] = FigureManifest(
        figure_directory=str(FIGURES_DIR),
        figure_files=[path.name for path in figure_paths],
        figure_count=len(figure_paths),
        figures_generated=bool(figure_paths),
    ).to_dict()

    write_state_representation_repair_outputs(payload, output_dir=OUTPUT_DIR)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Feature 071 state representation repair diagnostics")
    parser.add_argument("--json", action="store_true", help="Emit the final report as JSON on stdout")
    args = parser.parse_args(argv)
    payload = run_state_representation_repair()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
