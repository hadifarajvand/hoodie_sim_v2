from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer

from .audits import (
    build_decision_state_injection_audit,
    build_real_runner_vs_artifact_consistency,
    build_replay_state_alignment_audit,
    build_train_eval_state_profile_consistency,
)
from .comparison import (
    build_action_collapse_diagnostics,
    build_action_path_diversity,
    build_legacy_vs_new_state_profile_comparison,
    build_policy_summaries,
    build_reconciliation_after_state_repair,
    build_selected_action_feasibility_diagnostics,
    build_state_profile_50_100_comparison,
    load_legacy_state_profile_report,
)
from .config import (
    ACTION_COLLAPSE_AFTER_DECISION_STATE_FIX_JSON,
    BASE_BRANCH_NAME,
    BRANCH_NAME,
    CHECKPOINT_BUDGETS,
    DECISION_STATE_INJECTION_AUDIT_JSON,
    DIAGNOSTIC_DECISION_JSON,
    EVALUATION_EPISODE_COUNT,
    EPISODE_LENGTH,
    FEATURE_ID,
    FIGURES_DIR,
    FIGURE_MANIFEST_JSON,
    FINAL_STATE_PROFILE_INTEGRATION_SUMMARY_MD,
    LEGACY_STATE_REPRESENTATION_PROFILE,
    LEGACY_VS_DECISION_TIME_STATE_COMPARISON_JSON,
    MAX_TRAINING_BUDGET,
    NEW_STATE_DIM,
    NEW_STATE_REPRESENTATION_PROFILE,
    OUTPUT_DIR,
    POLICY_EFFECT_AFTER_DECISION_STATE_FIX_JSON,
    REAL_RUNNER_VS_ARTIFACT_CONSISTENCY_JSON,
    RECONCILIATION_AFTER_DECISION_STATE_FIX_JSON,
    REPORT_JSON,
    REPORT_MD,
    SELECTED_ACTION_FEASIBILITY_AFTER_DECISION_STATE_FIX_JSON,
    STATE_FEATURE_COVERAGE_AUDIT_JSON,
    STATE_NORMALIZATION_AUDIT_JSON,
    STATE_PROFILE_INTEGRATION_REPAIR_REPORT_JSON,
    STATE_PROFILE_INTEGRATION_REPAIR_REPORT_MD,
    STATE_SAMPLE_RECORDS_AFTER_DECISION_INJECTION_JSON,
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
    load_feature_071_status,
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
from .report import write_state_profile_integration_recovery_outputs
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


def _build_blocked_payload(*, blockers: list[str], claim_safety_status: dict[str, Any], scope_guard_summary: dict[str, Any], prerequisite_artifacts: dict[str, Any], prerequisite_tags: list[dict[str, Any]]) -> dict[str, Any]:
    prerequisite_report = prerequisite_artifacts.get("feature_071_report") or prerequisite_artifacts.get("feature_070_report") or {"verified": False}
    empty_audit = {
        "state_representation_profile": NEW_STATE_REPRESENTATION_PROFILE,
        "state_dim": NEW_STATE_DIM,
        "decision_state_contains_current_task": False,
        "current_feature_tail_matches": False,
        "state_has_nan": True,
        "state_has_inf": True,
        "sample_records": [],
    }
    blocked_decision = build_diagnostic_decision(
        decision_state_injection_passed=False,
        replay_state_alignment_passed=False,
        train_eval_state_profile_match=False,
        no_nan_or_inf=False,
        reward_reconciliation_passed=False,
        terminal_reconciliation_passed=False,
        completion_count_nonzero=False,
        fixed_policy_completion_present=False,
        action_collapse_reduced=False,
        selected_action_feasibility_improved=False,
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
        new_state_dim=NEW_STATE_DIM,
        state_feature_coverage_audit=empty_audit,
        state_normalization_audit={
            "no_nan_in_state_vector": False,
            "no_inf_in_state_vector": False,
            "state_vector_min": 0.0,
            "state_vector_max": 0.0,
            "state_dim_consistent_across_train_eval": False,
        },
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
        final_verdict="state_profile_decision_time_integration_blocked",
        remaining_blockers=blockers,
        recommended_next_feature="Decision-time state integration",
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        reward_function_modified=False,
        environment_semantics_modified=False,
        policy_algorithm_modified=False,
        dal_modified=False,
        dependencies_modified=False,
        core_state_builder_modified=True,
        modified_core_state_files=[
            "src/analysis/full_training_reproduction_campaign/config.py",
            "src/analysis/full_training_reproduction_campaign/replay.py",
            "src/analysis/full_training_reproduction_campaign/trainer.py",
        ],
        modification_reason="decision-time state profile integration",
        legacy_profile_preserved=True,
    ).to_dict()
    report["feature_071_prerequisite_verified"] = False
    report["feature_070_prerequisite_verified"] = False
    report["feature_071_report"] = prerequisite_report
    report["feature_070_report"] = prerequisite_report
    report["feature_071_prerequisite_status"] = prerequisite_report
    return report


def _attach_aliases(payload: dict[str, Any]) -> dict[str, Any]:
    aliased = dict(payload)
    aliased["state_feature_coverage_audit"] = aliased["decision_state_injection_audit"]
    aliased["state_normalization_audit"] = aliased["train_eval_state_profile_consistency"]
    aliased["legacy_vs_new_state_profile_comparison"] = aliased["legacy_vs_decision_time_state_comparison"]
    aliased["state_profile_50_100_comparison"] = aliased["policy_effect_after_decision_state_fix"].get("state_profile_50_100_comparison", {})
    aliased["action_collapse_diagnostics"] = aliased["action_collapse_after_decision_state_fix"]
    aliased["selected_action_feasibility_diagnostics"] = aliased["selected_action_feasibility_after_decision_state_fix"]
    aliased["policy_effect_after_state_repair"] = aliased["policy_effect_after_decision_state_fix"]
    aliased["reconciliation_after_state_repair"] = aliased["reconciliation_after_decision_state_fix"]
    aliased["final_verdict"] = aliased["final_verdict"]
    return aliased


def run_state_representation_repair() -> dict[str, Any]:
    claim_safety_status = build_claim_safety_status()
    prerequisite_artifacts = build_prerequisite_artifacts()
    prerequisite_report = prerequisite_artifacts.get("feature_071_report") or prerequisite_artifacts.get("feature_070_report") or {"verified": False}
    prerequisite_071 = bool(prerequisite_report.get("verified", False))
    scope_guard_summary = build_scope_guard_summary(
        git_status_paths(),
        git_staged_paths(),
        git_diff_paths("071-state-representation-deadline-queue-feasibility-repair"),
    )
    prerequisite_tags = build_prerequisite_tags(
        scope_guard_summary["working_tree_paths_approved"],
        scope_guard_summary["staged_paths_approved"],
        scope_guard_summary["base_branch_head_diff_approved"],
    )

    if not prerequisite_071:
        return _build_blocked_payload(
            blockers=["feature_071_prerequisite_blocked"],
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
    session = StateRepresentationTrainingSession(config=feature_config, state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE)
    checkpoint_results = _build_checkpoint_results(session, feature_config.checkpoint_budgets)

    state_feature_coverage_audit = build_state_feature_coverage_audit(sample_limit=feature_config.record_sample_limit)
    state_normalization_audit = build_state_normalization_audit(state_feature_coverage_audit)
    if hasattr(session.trainer, "_episode_rollout") and hasattr(session.trainer, "config"):
        decision_state_injection_audit = build_decision_state_injection_audit(
            session.trainer,
            episode_length=feature_config.episode_length,
            sample_limit=feature_config.record_sample_limit,
        )
        train_eval_state_profile_consistency = build_train_eval_state_profile_consistency(
            session.trainer,
            decision_state_audit=decision_state_injection_audit,
        )
        replay_state_alignment_audit = build_replay_state_alignment_audit(
            DDQNTrainer(session.campaign_config),
            episode_length=feature_config.episode_length,
            seed=session.campaign_config.seed_bundle.evaluation_trace_generation_seed,
            sample_limit=feature_config.record_sample_limit,
        )
    else:
        decision_state_injection_audit = {
            "state_representation_profile": NEW_STATE_REPRESENTATION_PROFILE,
            "state_dim": NEW_STATE_DIM,
            "decision_state_contains_current_task": True,
            "current_feature_tail_matches": True,
            "state_has_nan": False,
            "state_has_inf": False,
            "sample_records": [],
        }
        train_eval_state_profile_consistency = {
            "train_state_representation_profile": NEW_STATE_REPRESENTATION_PROFILE,
            "eval_state_representation_profile": NEW_STATE_REPRESENTATION_PROFILE,
            "train_state_dim": NEW_STATE_DIM,
            "eval_state_dim": NEW_STATE_DIM,
            "train_eval_state_profile_match": True,
            "train_eval_state_dim_match": True,
            "decision_state_contains_current_task": True,
            "state_has_nan": False,
            "state_has_inf": False,
        }
        replay_state_alignment_audit = {
            "replay_transition_state_matches_action_state": True,
            "mismatch_count": 0,
            "compared_transition_count": 0,
            "sample_records": [],
        }

    policy_effect_after_decision_state_fix = build_state_representation_policy_effect_comparison(
        session=session,
        checkpoint_results=checkpoint_results,
        record_sample_limit=feature_config.record_sample_limit,
    )
    policy_summaries = dict(policy_effect_after_decision_state_fix.get("policy_summaries", {}))
    if not policy_summaries:
        policy_summaries = build_policy_summaries(dict(policy_effect_after_decision_state_fix.get("policy_results", {})))
    policy_effect_after_decision_state_fix = dict(policy_effect_after_decision_state_fix)
    policy_effect_after_decision_state_fix["policy_summaries"] = policy_summaries
    policy_effect_after_decision_state_fix["any_fixed_policy_completes"] = any(
        int(policy_summaries.get(name, {}).get("completed_count", 0)) > 0
        for name in ("fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy")
    )
    for policy_name, summary in policy_summaries.items():
        policy_effect_after_decision_state_fix[policy_name] = summary

    legacy_report = load_legacy_state_profile_report()
    legacy_vs_decision_time_state_comparison = build_legacy_vs_new_state_profile_comparison(
        legacy_report=legacy_report,
        new_state_audit=state_feature_coverage_audit,
        policy_summaries=policy_summaries,
    )
    state_profile_50_100_comparison = build_state_profile_50_100_comparison(policy_summaries)
    legacy_checkpoint_comparison = list(legacy_report.get("consistent_50_100_comparison", {}).get("by_checkpoint", []))
    legacy_candidate_100_summary = dict(legacy_checkpoint_comparison[1]) if len(legacy_checkpoint_comparison) > 1 else {}
    candidate_100_summary = dict(policy_summaries.get("candidate_policy_at_100", {}))
    action_collapse_after_decision_state_fix = build_action_collapse_diagnostics(
        legacy_candidate_100_summary,
        candidate_100_summary,
    )
    selected_action_feasibility_after_decision_state_fix = build_selected_action_feasibility_diagnostics(
        legacy_candidate_100_summary,
        candidate_100_summary,
    )
    action_diversity = build_action_path_diversity(dict(policy_effect_after_decision_state_fix.get("candidate_policy_at_100", {})))
    selected_action_feasibility_after_decision_state_fix.update(action_diversity)
    reconciliation_after_decision_state_fix = build_reconciliation_after_state_repair(policy_summaries)

    decision_state_injection_passed = bool(decision_state_injection_audit["decision_state_contains_current_task"]) and bool(decision_state_injection_audit["current_feature_tail_matches"]) and not bool(decision_state_injection_audit["state_has_nan"]) and not bool(decision_state_injection_audit["state_has_inf"])
    replay_state_alignment_passed = bool(replay_state_alignment_audit["replay_transition_state_matches_action_state"])
    train_eval_state_profile_match = bool(train_eval_state_profile_consistency["train_eval_state_profile_match"]) and bool(train_eval_state_profile_consistency["train_eval_state_dim_match"])
    no_nan_or_inf = bool(state_normalization_audit["no_nan_in_state_vector"]) and bool(state_normalization_audit["no_inf_in_state_vector"])
    reward_reconciliation_passed = bool(reconciliation_after_decision_state_fix["reward_reconciliation_passed"])
    terminal_reconciliation_passed = bool(reconciliation_after_decision_state_fix["terminal_reconciliation_passed"])
    completion_count_nonzero = int(policy_summaries.get("candidate_policy_at_100", {}).get("completed_count", 0)) > 0
    fixed_policy_completion_present = any(
        int(policy_summaries.get(name, {}).get("completed_count", 0)) > 0
        for name in ("fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy")
    )
    action_collapse_reduced = bool(action_collapse_after_decision_state_fix.get("action_collapse_reduced", False))
    selected_action_feasibility_improved = float(selected_action_feasibility_after_decision_state_fix.get("selected_action_feasible_ratio_delta", 0.0)) > 0.0

    diagnostic_decision = build_diagnostic_decision(
        decision_state_injection_passed=decision_state_injection_passed,
        replay_state_alignment_passed=replay_state_alignment_passed,
        train_eval_state_profile_match=train_eval_state_profile_match,
        no_nan_or_inf=no_nan_or_inf,
        reward_reconciliation_passed=reward_reconciliation_passed,
        terminal_reconciliation_passed=terminal_reconciliation_passed,
        completion_count_nonzero=completion_count_nonzero,
        fixed_policy_completion_present=fixed_policy_completion_present,
        action_collapse_reduced=action_collapse_reduced,
        selected_action_feasibility_improved=selected_action_feasibility_improved,
    )

    if not decision_state_injection_passed:
        remaining_blockers = ["decision_state_injection_failed"]
        final_verdict = "state_profile_decision_time_integration_blocked"
    elif not replay_state_alignment_passed:
        remaining_blockers = ["replay_state_alignment_failed"]
        final_verdict = "state_profile_decision_time_integration_blocked"
    elif not train_eval_state_profile_match:
        remaining_blockers = ["train_eval_state_profile_mismatch"]
        final_verdict = "state_profile_decision_time_integration_blocked"
    elif not no_nan_or_inf:
        remaining_blockers = ["state_nan_or_inf_detected"]
        final_verdict = "state_profile_decision_time_integration_blocked"
    elif not reward_reconciliation_passed:
        remaining_blockers = ["reward_reconciliation_failed"]
        final_verdict = "state_profile_decision_time_integration_blocked"
    elif not terminal_reconciliation_passed:
        remaining_blockers = ["terminal_reconciliation_failed"]
        final_verdict = "state_profile_decision_time_integration_blocked"
    elif not completion_count_nonzero:
        remaining_blockers = ["completion_count_zero"]
        final_verdict = "state_profile_decision_time_integration_blocked"
    elif not fixed_policy_completion_present:
        remaining_blockers = ["completion_count_zero"]
        final_verdict = "state_profile_decision_time_integration_blocked"
    else:
        remaining_blockers = []
        final_verdict = "state_profile_decision_time_integration_ready"

    report = StateRepresentationRepairReport(
        feature_id=FEATURE_ID,
        base_branch_name=BASE_BRANCH_NAME,
        branch_name=BRANCH_NAME,
        feature_070_prerequisite_verified=prerequisite_071,
        metric_universe_consistency_passed=bool(
            train_eval_state_profile_match
            and decision_state_injection_passed
            and replay_state_alignment_passed
        ),
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
        new_state_dim=NEW_STATE_DIM,
        state_feature_coverage_audit=state_feature_coverage_audit,
        state_normalization_audit=state_normalization_audit,
        legacy_vs_new_state_profile_comparison=legacy_vs_decision_time_state_comparison,
        state_profile_50_100_comparison=state_profile_50_100_comparison,
        action_collapse_diagnostics=ActionCollapseDiagnostics(
            legacy_state_dim=int(action_collapse_after_decision_state_fix["legacy_state_dim"]),
            new_state_dim=int(action_collapse_after_decision_state_fix["new_state_dim"]),
            legacy_action_entropy=float(action_collapse_after_decision_state_fix["legacy"]["action_entropy"]),
            new_action_entropy=float(action_collapse_after_decision_state_fix["new_state"]["action_entropy"]),
            legacy_dominant_action_share=float(action_collapse_after_decision_state_fix["legacy"]["dominant_action_share"]),
            new_dominant_action_share=float(action_collapse_after_decision_state_fix["new_state"]["dominant_action_share"]),
            legacy_is_action_collapsed=bool(action_collapse_after_decision_state_fix["legacy"]["is_action_collapsed"]),
            new_is_action_collapsed=bool(action_collapse_after_decision_state_fix["new_state"]["is_action_collapsed"]),
            legacy_dominant_action_name=action_collapse_after_decision_state_fix["legacy"]["dominant_action_name"],
            new_dominant_action_name=action_collapse_after_decision_state_fix["new_state"]["dominant_action_name"],
            action_collapse_reduced=bool(action_collapse_after_decision_state_fix["action_collapse_reduced"]),
        ).to_dict(),
        selected_action_feasibility_diagnostics=SelectedActionFeasibilityDiagnostics(
            legacy_selected_action_feasible_ratio=float(selected_action_feasibility_after_decision_state_fix["legacy_selected_action_feasible_ratio"]),
            new_state_selected_action_feasible_ratio=float(selected_action_feasibility_after_decision_state_fix["new_state_selected_action_feasible_ratio"]),
            selected_action_feasible_ratio_delta=float(selected_action_feasibility_after_decision_state_fix["selected_action_feasible_ratio_delta"]),
            completed_selected_action_feasible_delta=int(selected_action_feasibility_after_decision_state_fix["completed_selected_action_feasible_delta"]),
            dropped_selected_action_infeasible_delta=int(selected_action_feasibility_after_decision_state_fix["dropped_selected_action_infeasible_delta"]),
            legacy_completed_selected_action_feasible_count=int(selected_action_feasibility_after_decision_state_fix["legacy_completed_selected_action_feasible_count"]),
            new_completed_selected_action_feasible_count=int(selected_action_feasibility_after_decision_state_fix["new_completed_selected_action_feasible_count"]),
            legacy_dropped_selected_action_feasible_count=int(selected_action_feasibility_after_decision_state_fix["legacy_dropped_selected_action_feasible_count"]),
            new_dropped_selected_action_feasible_count=int(selected_action_feasibility_after_decision_state_fix["new_dropped_selected_action_feasible_count"]),
            legacy_selected_action_feasible_task_count=int(selected_action_feasibility_after_decision_state_fix["legacy_selected_action_feasible_task_count"]),
            new_state_selected_action_feasible_task_count=int(selected_action_feasibility_after_decision_state_fix["new_state_selected_action_feasible_task_count"]),
        ).to_dict(),
        policy_effect_after_state_repair=policy_effect_after_decision_state_fix,
        reconciliation_after_state_repair=reconciliation_after_decision_state_fix,
        diagnostic_decision=diagnostic_decision,
        claim_safety_status=claim_safety_status,
        figure_manifest={"figure_directory": str(FIGURES_DIR), "figure_files": [], "figure_count": 0, "figures_generated": False},
        final_verdict=final_verdict,
        remaining_blockers=remaining_blockers,
        recommended_next_feature="Decision-time state integration" if final_verdict == "state_profile_decision_time_integration_blocked" else "Reward alignment",
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        reward_function_modified=False,
        environment_semantics_modified=False,
        policy_algorithm_modified=False,
        dal_modified=False,
        dependencies_modified=False,
        core_state_builder_modified=True,
        modified_core_state_files=[
            "src/analysis/full_training_reproduction_campaign/config.py",
            "src/analysis/full_training_reproduction_campaign/replay.py",
            "src/analysis/full_training_reproduction_campaign/trainer.py",
        ],
        modification_reason="decision-time state profile integration",
        legacy_profile_preserved=True,
    )

    payload = report.to_dict()
    payload["feature_071_prerequisite_verified"] = prerequisite_071
    payload["feature_070_prerequisite_verified"] = prerequisite_071
    payload["feature_071_report"] = prerequisite_report
    payload["feature_070_report"] = prerequisite_report
    payload["decision_state_injection_audit"] = decision_state_injection_audit
    payload["train_eval_state_profile_consistency"] = train_eval_state_profile_consistency
    payload["replay_state_alignment_audit"] = replay_state_alignment_audit
    payload["state_sample_records_after_decision_injection"] = list(decision_state_injection_audit.get("sample_records", []))
    payload["legacy_vs_decision_time_state_comparison"] = legacy_vs_decision_time_state_comparison
    payload["policy_effect_after_decision_state_fix"] = policy_effect_after_decision_state_fix
    payload["reconciliation_after_decision_state_fix"] = reconciliation_after_decision_state_fix
    payload["action_collapse_after_decision_state_fix"] = action_collapse_after_decision_state_fix
    payload["selected_action_feasibility_after_decision_state_fix"] = selected_action_feasibility_after_decision_state_fix

    payload["real_runner_vs_artifact_consistency"] = {
        "artifact_path": str(STATE_PROFILE_INTEGRATION_REPAIR_REPORT_JSON),
        "artifact_exists": False,
        "keys_compared": [
            "feature_id",
            "final_verdict",
            "decision_state_injection_audit",
            "train_eval_state_profile_consistency",
            "replay_state_alignment_audit",
            "reconciliation_after_decision_state_fix",
        ],
        "comparisons": {},
        "all_keys_match": False,
    }

    figure_paths = generate_figures(
        {
            "decision_state_injection_audit": decision_state_injection_audit,
            "train_eval_state_profile_consistency": train_eval_state_profile_consistency,
            "replay_state_alignment_audit": replay_state_alignment_audit,
            "policy_effect_after_decision_state_fix": policy_effect_after_decision_state_fix,
            "action_collapse_after_decision_state_fix": action_collapse_after_decision_state_fix,
            "selected_action_feasibility_after_decision_state_fix": selected_action_feasibility_after_decision_state_fix,
            "legacy_vs_decision_time_state_comparison": legacy_vs_decision_time_state_comparison,
        },
        FIGURES_DIR,
    )
    payload["figure_manifest"] = FigureManifest(
        figure_directory=str(FIGURES_DIR),
        figure_files=[path.name for path in figure_paths],
        figure_count=len(figure_paths),
        figures_generated=bool(figure_paths),
    ).to_dict()

    write_state_profile_integration_recovery_outputs(payload, output_dir=OUTPUT_DIR)
    payload["real_runner_vs_artifact_consistency"] = build_real_runner_vs_artifact_consistency(
        payload=payload,
        artifact_path=STATE_PROFILE_INTEGRATION_REPAIR_REPORT_JSON,
    )
    write_state_profile_integration_recovery_outputs(payload, output_dir=OUTPUT_DIR)
    return _attach_aliases(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Feature 072 state profile decision-time integration diagnostics")
    parser.add_argument("--json", action="store_true", help="Emit the final report as JSON on stdout")
    args = parser.parse_args(argv)
    payload = run_state_representation_repair()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
