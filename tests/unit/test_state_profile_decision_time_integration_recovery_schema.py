from __future__ import annotations

from dataclasses import dataclass

from src.analysis.state_profile_decision_time_integration_recovery.config import (
    ALLOWED_DIAGNOSTIC_DECISIONS,
    ALLOWED_FINAL_VERDICTS,
    CHECKPOINT_BUDGETS,
    EVALUATION_EPISODE_COUNT,
    EPISODE_LENGTH,
    LEGACY_STATE_DIM,
    LEGACY_STATE_REPRESENTATION_PROFILE,
    MAX_TRAINING_BUDGET,
    NEW_STATE_DIM,
    NEW_STATE_REPRESENTATION_PROFILE,
    TRAINING_5000_RUN,
    TRAINING_BUDGETS,
    StateRepresentationRepairConfig,
)
from src.analysis.state_profile_decision_time_integration_recovery.model import (
    ActionCollapseDiagnostics,
    ClaimSafetyStatus,
    DiagnosticDecision,
    FigureManifest,
    SelectedActionFeasibilityDiagnostics,
    StateRepresentationRepairReport,
)
from src.analysis.full_training_reproduction_campaign.replay import build_state_vector, state_dimension_for_profile


@dataclass
class FakeTask:
    task_id: int = 1
    size: float = 12.0
    processing_density: float = 0.5
    timeout_length: int = 15
    absolute_deadline_slot: int = 18
    arrival_slot: int = 2
    source_agent_id: int = 1


def make_state_feature_coverage_audit() -> dict[str, object]:
    return {
        "legacy_state_dim": LEGACY_STATE_DIM,
        "new_state_dim": NEW_STATE_DIM,
        "added_feature_count": NEW_STATE_DIM - LEGACY_STATE_DIM,
        "added_feature_names": ["deadline_timeout", "action_path_feasibility", "queue_pressure"],
        "missing_or_approximated_state_features": ["previous_action", "previous_reward"],
        "state_feature_group_coverage": {
            "minimal": {"covered": True, "feature_names": ["slot_norm", "task_size_norm", "processing_density_norm"]},
            "deadline_timeout": {"covered": True, "feature_names": ["timeout_length_norm"]},
            "action_path_feasibility": {"covered": True, "feature_names": ["local_estimated_total_slots_norm"]},
            "queue_pressure": {"covered": True, "feature_names": ["pending_task_pressure_norm"]},
            "legal_availability": {"covered": True, "feature_names": ["legal_local", "legal_horizontal", "legal_vertical"]},
            "source_context": {"covered": True, "feature_names": ["source_agent_id_norm"]},
        },
        "state_normalization_summary": {
            "no_nan_in_state_vector": True,
            "no_inf_in_state_vector": True,
            "state_vector_min": 0.0,
            "state_vector_max": 1.0,
            "state_dim_consistent_across_train_eval": True,
        },
        "state_sample_records": [],
        "train_eval_state_dim_match": True,
        "calibration_profile_name": "paper_aligned_feasible_v1",
    }


def make_policy_summary(
    *,
    policy_name: str,
    checkpoint_budget: int,
    action_distribution: dict[str, int],
    selected_action_feasible_task_count: int,
    selected_action_infeasible_task_count: int,
    completed_count: int,
    dropped_count: int,
    pending_count: int,
    mean_reward: float,
    reward_per_task: float,
    reward_per_decision: float,
    reward_reconciled: bool = True,
    terminal_reconciled: bool = True,
    raw_vs_canonical_reward_delta: float = 0.0,
    dominant_action_share: float | None = None,
) -> dict[str, object]:
    unique_task_count = completed_count + dropped_count + pending_count
    dominant_action_share = dominant_action_share if dominant_action_share is not None else max(action_distribution.values()) / max(sum(action_distribution.values()), 1)
    return {
        "policy_name": policy_name,
        "checkpoint_budget": checkpoint_budget,
        "decision_count": unique_task_count,
        "unique_task_count": unique_task_count,
        "action_distribution": action_distribution,
        "selected_action_feasible_task_count": selected_action_feasible_task_count,
        "selected_action_infeasible_task_count": selected_action_infeasible_task_count,
        "selected_action_feasible_ratio": selected_action_feasible_task_count / max(unique_task_count, 1),
        "completed_selected_action_feasible_count": min(completed_count, selected_action_feasible_task_count),
        "completed_selected_action_infeasible_count": max(0, completed_count - selected_action_feasible_task_count),
        "dropped_selected_action_feasible_count": min(dropped_count, selected_action_feasible_task_count),
        "dropped_selected_action_infeasible_count": max(0, dropped_count - selected_action_feasible_task_count),
        "completed_count": completed_count,
        "dropped_count": dropped_count,
        "pending_count": pending_count,
        "completion_ratio": completed_count / max(unique_task_count, 1),
        "drop_ratio": dropped_count / max(unique_task_count, 1),
        "deadline_violation_ratio": dropped_count / max(unique_task_count, 1),
        "mean_reward": mean_reward,
        "reward_per_task": reward_per_task,
        "reward_per_decision": reward_per_decision,
        "mean_completion_latency_slots": 3.0,
        "mean_drop_latency_slots": 5.0,
        "mean_terminal_latency_slots": 4.0,
        "reward_reconciled": reward_reconciled,
        "terminal_reconciled": terminal_reconciled,
        "raw_vs_canonical_reward_delta": raw_vs_canonical_reward_delta,
        "feasible_task_count": selected_action_feasible_task_count,
        "infeasible_task_count": selected_action_infeasible_task_count,
        "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
        "feasible_task_count_universe": "U_selected_action_tasks",
        "completed_feasible_task_count": min(completed_count, selected_action_feasible_task_count),
        "completed_feasible_task_count_universe": "U_selected_action_tasks",
        "completed_infeasible_task_count": max(0, completed_count - selected_action_feasible_task_count),
        "dropped_feasible_task_count": min(dropped_count, selected_action_feasible_task_count),
        "dropped_infeasible_task_count": max(0, dropped_count - selected_action_feasible_task_count),
        "action_entropy": 0.5,
        "dominant_action_share": dominant_action_share,
        "is_action_collapsed": dominant_action_share >= 0.95,
        "dominant_action_name": max(action_distribution, key=action_distribution.get),
    }


def make_policy_effect() -> dict[str, object]:
    candidate_50 = make_policy_summary(
        policy_name="candidate_policy_at_50",
        checkpoint_budget=50,
        action_distribution={"local": 5, "horizontal": 0, "vertical": 95},
        selected_action_feasible_task_count=5,
        selected_action_infeasible_task_count=95,
        completed_count=10,
        dropped_count=85,
        pending_count=5,
        mean_reward=-10.0,
        reward_per_task=-10.0,
        reward_per_decision=-10.0,
        dominant_action_share=0.95,
    )
    candidate_100 = make_policy_summary(
        policy_name="candidate_policy_at_100",
        checkpoint_budget=100,
        action_distribution={"local": 20, "horizontal": 10, "vertical": 70},
        selected_action_feasible_task_count=18,
        selected_action_infeasible_task_count=82,
        completed_count=18,
        dropped_count=72,
        pending_count=10,
        mean_reward=-8.0,
        reward_per_task=-8.0,
        reward_per_decision=-8.0,
        dominant_action_share=0.70,
    )
    fixed_local = make_policy_summary(
        policy_name="fixed_local_policy",
        checkpoint_budget=100,
        action_distribution={"local": 100, "horizontal": 0, "vertical": 0},
        selected_action_feasible_task_count=100,
        selected_action_infeasible_task_count=0,
        completed_count=22,
        dropped_count=70,
        pending_count=8,
        mean_reward=-7.0,
        reward_per_task=-7.0,
        reward_per_decision=-7.0,
        dominant_action_share=1.0,
    )
    fixed_horizontal = make_policy_summary(
        policy_name="fixed_horizontal_policy",
        checkpoint_budget=100,
        action_distribution={"local": 0, "horizontal": 100, "vertical": 0},
        selected_action_feasible_task_count=88,
        selected_action_infeasible_task_count=12,
        completed_count=15,
        dropped_count=78,
        pending_count=7,
        mean_reward=-9.0,
        reward_per_task=-9.0,
        reward_per_decision=-9.0,
        dominant_action_share=1.0,
    )
    fixed_vertical = make_policy_summary(
        policy_name="fixed_vertical_policy",
        checkpoint_budget=100,
        action_distribution={"local": 0, "horizontal": 0, "vertical": 100},
        selected_action_feasible_task_count=70,
        selected_action_infeasible_task_count=30,
        completed_count=12,
        dropped_count=80,
        pending_count=8,
        mean_reward=-11.0,
        reward_per_task=-11.0,
        reward_per_decision=-11.0,
        dominant_action_share=1.0,
    )
    random_legal = make_policy_summary(
        policy_name="random_legal_policy",
        checkpoint_budget=100,
        action_distribution={"local": 34, "horizontal": 33, "vertical": 33},
        selected_action_feasible_task_count=66,
        selected_action_infeasible_task_count=34,
        completed_count=20,
        dropped_count=72,
        pending_count=8,
        mean_reward=-8.5,
        reward_per_task=-8.5,
        reward_per_decision=-8.5,
        dominant_action_share=0.34,
    )
    policy_results = {
        name: {"task_records": {f"{name}-1": {"terminal_outcome": "completed", "selected_action": "vertical", "latency_slots": 3, "raw_reward_total": -1.0, "canonical_reward": -1.0, "arrival_slot": 1, "completion_or_drop_slot": 3, "terminal_slot": 3}}, "evaluation_reward_summary": {"canonical_task_count": 100, "completed_task_count": summary["completed_count"], "dropped_task_count": summary["dropped_count"], "pending_at_horizon_count": summary["pending_count"], "mean_reward": summary["mean_reward"], "canonical_task_reward_total": summary["reward_per_task"] * 100}, "reward_reconciliation_after_terminal_repair": {"reward_reconciled": summary["reward_reconciled"], "raw_vs_canonical_reward_delta": summary["raw_vs_canonical_reward_delta"]}, "raw_vs_canonical_terminal_reconciliation": {"terminal_reconciled": summary["terminal_reconciled"]}, "evaluation_action_distribution": summary["action_distribution"], "evaluation_decision_count": summary["decision_count"]}
        for name, summary in {
            "candidate_policy_at_50": candidate_50,
            "candidate_policy_at_100": candidate_100,
            "fixed_local_policy": fixed_local,
            "fixed_horizontal_policy": fixed_horizontal,
            "fixed_vertical_policy": fixed_vertical,
            "random_legal_policy": random_legal,
        }.items()
    }
    return {
        "evaluation_trace_bank_id": "eval-bank",
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "candidate_policy_vertical_collapse_in_evaluation": True,
        "candidate_policy_vertical_collapse_in_training_replay_window": False,
        "policy_affects_reward": "true",
        "policy_affects_terminal_outcomes": "true",
        "evaluation_reward_static_after_terminal_repair": False,
        "evaluation_action_distribution_static_across_budget": False,
        "raw_event_reward_static_across_budget": False,
        "canonical_task_reward_static_across_budget": False,
        "canonical_completion_rate_static_across_budget": False,
        "canonical_drop_rate_static_across_budget": False,
        "policy_results": policy_results,
        "policy_summaries": {
            "candidate_policy_at_50": candidate_50,
            "candidate_policy_at_100": candidate_100,
            "fixed_local_policy": fixed_local,
            "fixed_horizontal_policy": fixed_horizontal,
            "fixed_vertical_policy": fixed_vertical,
            "random_legal_policy": random_legal,
        },
        "candidate_policy_at_50": candidate_50,
        "candidate_policy_at_100": candidate_100,
        "fixed_policy_summaries": {
            "fixed_local_policy": fixed_local,
            "fixed_horizontal_policy": fixed_horizontal,
            "fixed_vertical_policy": fixed_vertical,
            "random_legal_policy": random_legal,
        },
        "any_fixed_policy_completes": True,
        "candidate_reward_variation": 2.0,
        "candidate_action_distribution_changed_by_budget": True,
        "candidate_terminal_outcomes_changed_by_budget": True,
        "canonical_policy_effect_summary": {},
    }


def make_repair_payload() -> dict[str, object]:
    state_feature_coverage_audit = make_state_feature_coverage_audit()
    policy_effect = make_policy_effect()
    legacy_candidate_50 = make_policy_summary(
        policy_name="candidate_policy_at_50",
        checkpoint_budget=50,
        action_distribution={"local": 0, "horizontal": 0, "vertical": 100},
        selected_action_feasible_task_count=4,
        selected_action_infeasible_task_count=96,
        completed_count=8,
        dropped_count=87,
        pending_count=5,
        mean_reward=-12.0,
        reward_per_task=-12.0,
        reward_per_decision=-12.0,
        dominant_action_share=1.0,
    )
    legacy_candidate_100 = make_policy_summary(
        policy_name="candidate_policy_at_100",
        checkpoint_budget=100,
        action_distribution={"local": 1, "horizontal": 0, "vertical": 99},
        selected_action_feasible_task_count=6,
        selected_action_infeasible_task_count=94,
        completed_count=10,
        dropped_count=85,
        pending_count=5,
        mean_reward=-11.0,
        reward_per_task=-11.0,
        reward_per_decision=-11.0,
        dominant_action_share=0.99,
    )
    legacy_report = {
        "feature_id": "070-calibration-metric-consistency-reconciliation-fix",
        "legacy_state_dim": 3,
        "consistent_50_100_comparison": {"by_checkpoint": [legacy_candidate_50, legacy_candidate_100]},
    }
    return {
        "feature_id": "071-state-profile-decision-time-integration-recovery",
        "base_branch_name": "070-calibration-metric-consistency-reconciliation-fix",
        "branch_name": "071-state-profile-decision-time-integration-recovery",
        "feature_070_prerequisite_verified": True,
        "metric_universe_consistency_passed": True,
        "prerequisite_artifacts": {"feature_070_report": {"verified": True}},
        "prerequisite_tags_verified": [{"name": "branch", "verified": True}],
        "scope_guard_summary": {"working_tree_paths_approved": True, "staged_paths_approved": True, "base_branch_head_diff_approved": True, "diff_paths": []},
        "calibration_profile_name": "paper_aligned_feasible_v1",
        "state_representation_profile": NEW_STATE_REPRESENTATION_PROFILE,
        "legacy_state_representation_profile": LEGACY_STATE_REPRESENTATION_PROFILE,
        "checkpoint_budgets": [50, 100],
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "max_training_budget": 100,
        "training_mode": "cumulative_staged_50_100_state_representation_repair",
        "training_rerun_from_scratch": False,
        "training_5000_run": False,
        "legacy_state_dim": LEGACY_STATE_DIM,
        "new_state_dim": NEW_STATE_DIM,
        "state_feature_coverage_audit": state_feature_coverage_audit,
        "state_normalization_audit": {
            "no_nan_in_state_vector": True,
            "no_inf_in_state_vector": True,
            "state_vector_min": 0.0,
            "state_vector_max": 1.0,
            "state_dim_consistent_across_train_eval": True,
        },
        "legacy_vs_new_state_profile_comparison": {
            "legacy_state_dim": 3,
            "new_state_dim": NEW_STATE_DIM,
            "legacy_candidate_50": legacy_candidate_50,
            "legacy_candidate_100": legacy_candidate_100,
            "new_candidate_50": policy_effect["candidate_policy_at_50"],
            "new_candidate_100": policy_effect["candidate_policy_at_100"],
            "comparison": {"state_dim_increased": True, "action_distribution_changed": True, "selected_action_feasibility_improved": True, "action_collapse_reduced": True, "completion_ratio_changed": True, "reward_changed": True},
        },
        "state_profile_50_100_comparison": {
            "checkpoint_budgets": [50, 100],
            "by_checkpoint": [policy_effect["candidate_policy_at_50"], policy_effect["candidate_policy_at_100"]],
            "comparison": {
                "50_to_100_action_distribution_changed": True,
                "50_to_100_completion_changed": True,
                "50_to_100_drop_changed": True,
                "50_to_100_reward_changed": True,
                "50_to_100_selected_action_feasibility_changed": True,
            },
            "comparison_classification": "completion_path_changed",
        },
        "action_collapse_diagnostics": {
            "legacy_state_dim": 3,
            "new_state_dim": NEW_STATE_DIM,
            "legacy_action_entropy": 0.2,
            "new_action_entropy": 0.6,
            "legacy_dominant_action_share": 0.99,
            "new_dominant_action_share": 0.70,
            "legacy_is_action_collapsed": True,
            "new_is_action_collapsed": False,
            "legacy_dominant_action_name": "vertical",
            "new_dominant_action_name": "vertical",
            "action_collapse_reduced": True,
        },
        "selected_action_feasibility_diagnostics": {
            "legacy_selected_action_feasible_ratio": 0.06,
            "new_state_selected_action_feasible_ratio": 0.18,
            "selected_action_feasible_ratio_delta": 0.12,
            "completed_selected_action_feasible_delta": 12,
            "dropped_selected_action_infeasible_delta": -8,
            "legacy_completed_selected_action_feasible_count": 6,
            "new_completed_selected_action_feasible_count": 18,
            "legacy_dropped_selected_action_feasible_count": 2,
            "new_dropped_selected_action_feasible_count": 10,
            "legacy_selected_action_feasible_task_count": 6,
            "new_state_selected_action_feasible_task_count": 18,
        },
        "policy_effect_after_state_repair": policy_effect,
        "reconciliation_after_state_repair": {
            "reward_reconciliation_passed": True,
            "terminal_reconciliation_passed": True,
            "raw_vs_canonical_reward_delta_max": 0.0,
            "policies_with_reward_reconciled_false": [],
            "policies_with_terminal_reconciled_false": [],
        },
        "diagnostic_decision": {
            "recommended_next_action": "safe_to_proceed_to_reward_function_alignment",
            "decision_reason": "ok",
            "evidence_notes": ["state_profile_passed"],
        },
        "claim_safety_status": {"paper_reproduction_claim_made": False, "performance_superiority_claim_made": False, "baseline_superiority_claim_made": False, "claim_safety_passed": True},
        "figure_manifest": {"figure_directory": "figures", "figure_files": ["a", "b", "c", "d", "e"], "figure_count": 5, "figures_generated": True},
        "final_verdict": "state_representation_deadline_queue_feasibility_ready",
        "remaining_blockers": [],
        "recommended_next_feature": "Reward alignment",
        "paper_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "reward_function_modified": False,
        "environment_semantics_modified": False,
        "policy_algorithm_modified": False,
        "dal_modified": False,
        "dependencies_modified": False,
        "core_state_builder_modified": True,
        "modified_core_state_files": ["src/analysis/full_training_reproduction_campaign/replay.py", "src/analysis/full_training_reproduction_campaign/trainer.py", "src/analysis/full_training_reproduction_campaign/config.py"],
        "modification_reason": "profile-aware state representation",
        "legacy_profile_preserved": True,
    }


def test_schema_constants_and_models():
    assert TRAINING_BUDGETS == (50, 100)
    assert MAX_TRAINING_BUDGET == 100
    assert EVALUATION_EPISODE_COUNT == 100
    assert EPISODE_LENGTH == 110
    assert TRAINING_5000_RUN is False
    assert LEGACY_STATE_REPRESENTATION_PROFILE == "legacy_minimal"
    assert NEW_STATE_REPRESENTATION_PROFILE == "deadline_queue_feasibility_v1"
    assert state_dimension_for_profile(LEGACY_STATE_REPRESENTATION_PROFILE) == LEGACY_STATE_DIM
    assert state_dimension_for_profile(NEW_STATE_REPRESENTATION_PROFILE) == NEW_STATE_DIM

    config = StateRepresentationRepairConfig()
    assert config.checkpoint_budgets == CHECKPOINT_BUDGETS
    assert config.max_training_budget == MAX_TRAINING_BUDGET
    assert config.training_5000_run is False
    assert config.state_dim == NEW_STATE_DIM
    assert config.legacy_state_dim == LEGACY_STATE_DIM

    claim = ClaimSafetyStatus(False, False, False, True)
    assert claim.to_dict()["claim_safety_passed"] is True
    decision = DiagnosticDecision("safe_to_proceed_to_reward_function_alignment", "ok", ["evidence"])
    assert decision.to_dict()["recommended_next_action"] == "safe_to_proceed_to_reward_function_alignment"
    manifest = FigureManifest("figures", ["a.png", "b.png", "c.png", "d.png", "e.png"], 5, True)
    assert manifest.to_dict()["figure_count"] == 5
    report = StateRepresentationRepairReport(
        feature_id="071-state-profile-decision-time-integration-recovery",
        base_branch_name="070-calibration-metric-consistency-reconciliation-fix",
        branch_name="071-state-profile-decision-time-integration-recovery",
        feature_070_prerequisite_verified=True,
        metric_universe_consistency_passed=True,
        prerequisite_artifacts={"feature_070_report": {"verified": True}},
        prerequisite_tags_verified=[{"name": "branch", "verified": True}],
        scope_guard_summary={"working_tree_paths_approved": True},
        calibration_profile_name="paper_aligned_feasible_v1",
        state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE,
        legacy_state_representation_profile=LEGACY_STATE_REPRESENTATION_PROFILE,
        checkpoint_budgets=[50, 100],
        evaluation_episode_count=100,
        episode_length=110,
        max_training_budget=100,
        training_mode="cumulative_staged_50_100_state_representation_repair",
        training_rerun_from_scratch=False,
        training_5000_run=False,
        legacy_state_dim=LEGACY_STATE_DIM,
        new_state_dim=NEW_STATE_DIM,
        state_feature_coverage_audit=make_state_feature_coverage_audit(),
        state_normalization_audit={"no_nan_in_state_vector": True, "no_inf_in_state_vector": True, "state_vector_min": 0.0, "state_vector_max": 1.0, "state_dim_consistent_across_train_eval": True},
        legacy_vs_new_state_profile_comparison={},
        state_profile_50_100_comparison={},
        action_collapse_diagnostics=ActionCollapseDiagnostics(LEGACY_STATE_DIM, NEW_STATE_DIM, 0.2, 0.6, 0.99, 0.7, True, False, "vertical", "vertical", True).to_dict(),
        selected_action_feasibility_diagnostics=SelectedActionFeasibilityDiagnostics(0.06, 0.18, 0.12, 12, -8, 6, 18, 2, 10, 6, 18).to_dict(),
        policy_effect_after_state_repair=make_policy_effect(),
        reconciliation_after_state_repair={"reward_reconciliation_passed": True, "terminal_reconciliation_passed": True, "raw_vs_canonical_reward_delta_max": 0.0, "policies_with_reward_reconciled_false": [], "policies_with_terminal_reconciled_false": []},
        diagnostic_decision={"recommended_next_action": "safe_to_proceed_to_reward_function_alignment", "decision_reason": "ok", "evidence_notes": ["state_profile_passed"]},
        claim_safety_status=claim.to_dict(),
        figure_manifest=manifest.to_dict(),
        final_verdict="state_representation_deadline_queue_feasibility_ready",
        remaining_blockers=[],
        recommended_next_feature="Reward alignment",
    )
    assert report.to_dict()["final_verdict"] == "state_representation_deadline_queue_feasibility_ready"


def test_state_vector_profiles_and_dimensions():
    task = FakeTask()
    observation = {
        "slot": 3,
        "queue_load": 4,
        "history_length": 2,
        "task_size": task.size,
        "processing_density": task.processing_density,
        "timeout_length": task.timeout_length,
        "absolute_deadline_slot": task.absolute_deadline_slot,
        "arrival_slot": task.arrival_slot,
        "source_agent_id": task.source_agent_id,
        "legal_action_mask": {"local": True, "horizontal": False, "vertical": True},
    }
    legacy = build_state_vector(observation=observation, current_task=task, episode_length=110, state_representation_profile=LEGACY_STATE_REPRESENTATION_PROFILE)
    new = build_state_vector(observation=observation, current_task=task, episode_length=110, state_representation_profile=NEW_STATE_REPRESENTATION_PROFILE)
    assert len(legacy) == LEGACY_STATE_DIM
    assert len(new) == NEW_STATE_DIM
    assert all(value == value for value in new)
    assert all(value not in {float("inf"), float("-inf")} for value in new)


def test_synthetic_payload_helper_exposes_needed_artifacts():
    payload = make_repair_payload()
    assert payload["checkpoint_budgets"] == [50, 100]
    assert payload["metric_universe_consistency_passed"] is True
    assert payload["state_feature_coverage_audit"]["state_feature_group_coverage"]["queue_pressure"]["covered"] is True
    assert payload["state_profile_50_100_comparison"]["comparison_classification"] == "completion_path_changed"
