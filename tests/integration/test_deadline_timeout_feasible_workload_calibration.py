from __future__ import annotations

from pathlib import Path

from src.analysis.deadline_timeout_feasible_workload_calibration.config import (
    ALLOWED_FINAL_VERDICTS,
    BASE_BRANCH_NAME,
    BRANCH_NAME,
    CALIBRATED_ACTION_PATH_FEASIBILITY_JSON,
    CALIBRATED_POLICY_EFFECT_COMPARISON_JSON,
    CALIBRATED_TASK_FEASIBILITY_SUMMARY_JSON,
    CALIBRATION_CHANGE_LOG_JSON,
    CHECKPOINT_50_100_CALIBRATED_COMPARISON_JSON,
    DIAGNOSTIC_DECISION_JSON,
    FINAL_CALIBRATION_SUMMARY_MD,
    FIGURE_MANIFEST_JSON,
    OUTPUT_DIR,
    PAPER_ALIGNED_CALIBRATED_METRICS_JSON,
    REPORT_JSON,
    REPORT_MD,
    RUNTIME_EVENT_PATH_AFTER_CALIBRATION_JSON,
)
from src.analysis.deadline_timeout_feasible_workload_calibration.figures import generate_figures
from src.analysis.deadline_timeout_feasible_workload_calibration.model import FigureManifest
from src.analysis.deadline_timeout_feasible_workload_calibration.report import write_deadline_timeout_calibration_report


def _dummy_report() -> dict:
    policy_effect = {
        "policy_results": {
            "candidate_policy_at_50": {"evaluation_action_distribution": {"local": 1}, "evaluation_reward_summary": {"mean_reward": 1.0, "canonical_task_count": 1, "completed_task_count": 1, "dropped_task_count": 0, "pending_at_horizon_count": 0, "canonical_task_reward_total": 1.0}},
            "candidate_policy_at_100": {"evaluation_action_distribution": {"local": 2}, "evaluation_reward_summary": {"mean_reward": 2.0, "canonical_task_count": 1, "completed_task_count": 1, "dropped_task_count": 0, "pending_at_horizon_count": 0, "canonical_task_reward_total": 2.0}},
            "fixed_local_policy": {"evaluation_action_distribution": {"local": 3}, "evaluation_reward_summary": {"mean_reward": 3.0, "canonical_task_count": 1, "completed_task_count": 1, "dropped_task_count": 0, "pending_at_horizon_count": 0, "canonical_task_reward_total": 3.0}, "task_records": {}},
            "fixed_horizontal_policy": {"evaluation_action_distribution": {"horizontal": 3}, "evaluation_reward_summary": {"mean_reward": 0.0, "canonical_task_count": 1, "completed_task_count": 0, "dropped_task_count": 1, "pending_at_horizon_count": 0, "canonical_task_reward_total": 0.0}},
            "fixed_vertical_policy": {"evaluation_action_distribution": {"vertical": 3}, "evaluation_reward_summary": {"mean_reward": 0.0, "canonical_task_count": 1, "completed_task_count": 0, "dropped_task_count": 1, "pending_at_horizon_count": 0, "canonical_task_reward_total": 0.0}},
            "random_legal_policy": {"evaluation_action_distribution": {"random": 3}, "evaluation_reward_summary": {"mean_reward": 0.0, "canonical_task_count": 1, "completed_task_count": 0, "dropped_task_count": 1, "pending_at_horizon_count": 0, "canonical_task_reward_total": 0.0}},
        },
        "policy_summaries": {},
        "fixed_policy_summaries": {},
        "any_fixed_policy_completes": True,
        "raw_event_reward_static_across_budget": False,
        "canonical_task_reward_static_across_budget": False,
        "canonical_completion_rate_static_across_budget": False,
        "canonical_drop_rate_static_across_budget": False,
        "evaluation_action_distribution_static_across_budget": False,
        "policy_affects_reward": "true",
        "policy_affects_terminal_outcomes": "true",
        "candidate_action_distribution_changed_by_budget": True,
        "candidate_terminal_outcomes_changed_by_budget": True,
        "candidate_policy_vertical_collapse_in_evaluation": False,
        "candidate_policy_vertical_collapse_in_training_replay_window": False,
        "evaluation_reward_static_after_terminal_repair": False,
    }
    policy_effect["policy_summaries"] = {
        name: {
            "policy_name": name,
            "checkpoint_budget": 50,
            "decision_count": 1,
            "action_distribution": {"local": 1},
            "feasible_task_count": 1,
            "infeasible_task_count": 0,
            "feasible_task_count_by_action": {"local": 1},
            "infeasible_task_count_by_action": {"local": 0},
            "completed_count": 1 if name == "fixed_local_policy" else 0,
            "dropped_count": 0 if name == "fixed_local_policy" else 1,
            "pending_count": 0,
            "completion_ratio": 1.0 if name == "fixed_local_policy" else 0.0,
            "drop_ratio": 0.0 if name == "fixed_local_policy" else 1.0,
            "deadline_violation_ratio": 0.0 if name == "fixed_local_policy" else 1.0,
            "mean_reward": 3.0 if name == "fixed_local_policy" else 0.0,
            "reward_per_task": 3.0 if name == "fixed_local_policy" else 0.0,
            "reward_per_decision": 3.0 if name == "fixed_local_policy" else 0.0,
            "mean_completion_latency_slots": 1.0 if name == "fixed_local_policy" else None,
            "mean_drop_latency_slots": None,
            "mean_terminal_latency_slots": 1.0 if name == "fixed_local_policy" else None,
            "completion_path_audit": {},
            "paper_aligned_diagnostic_metrics": {},
            "reward_reconciliation_after_terminal_repair": {},
            "raw_vs_canonical_terminal_reconciliation": {},
            "evaluation_action_distribution_source": "evaluation_episodes",
            "evaluation_trace_bank_id": "trace-bank",
            "same_evaluation_trace_bank": True,
            "reward_event_records": {"record_count": 1},
            "terminal_event_records": {"record_count": 1},
        }
        for name in ("candidate_policy_at_50", "candidate_policy_at_100", "fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy")
    }
    return {
        "feature_id": "069-deadline-timeout-feasible-workload-calibration",
        "base_branch_name": BASE_BRANCH_NAME,
        "branch_name": BRANCH_NAME,
        "calibration_profile_name": "paper_aligned_feasible_v1",
        "checkpoint_budgets": [50, 100],
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "max_training_budget": 100,
        "training_mode": "cumulative_staged_50_100_feasible_workload_calibration",
        "training_rerun_from_scratch": False,
        "training_5000_run": False,
        "calibration_change_log": [{"field_name": "timeout_length", "before_value": 5, "after_value": 15, "reason": "feasibility", "paper_alignment_note": "paper-aligned"}],
        "before_overall_feasible_task_ratio": 0.0,
        "after_overall_feasible_task_ratio": 0.57,
        "before_completion_count": 0,
        "after_completion_count": 12,
        "before_drop_ratio": 1.0,
        "after_drop_ratio": 0.42,
        "before_deadline_violation_ratio": 1.0,
        "after_deadline_violation_ratio": 0.42,
        "before_action_path_feasibility": {"local_feasible_ratio": 0.0, "horizontal_feasible_ratio": 0.0, "vertical_feasible_ratio": 0.0},
        "after_action_path_feasibility": {"local_feasible_ratio": 0.57, "horizontal_feasible_ratio": 0.28, "vertical_feasible_ratio": 0.26},
        "before_after_feasibility_comparison": {"before_overall_feasible_task_ratio": 0.0, "after_overall_feasible_task_ratio": 0.57},
        "calibrated_task_feasibility_summary": {"overall_feasible_task_ratio": 0.57, "local_feasible_ratio": 0.57, "horizontal_feasible_ratio": 0.28, "vertical_feasible_ratio": 0.26, "sample_records": []},
        "calibrated_policy_effect_comparison": policy_effect,
        "checkpoint_50_100_calibrated_comparison": {
            "checkpoint_budgets": [50, 100],
            "by_checkpoint": [
                {"training_budget": 50, "reward_per_task": 1.0},
                {"training_budget": 100, "reward_per_task": 2.0},
            ],
        },
        "paper_aligned_calibrated_metrics": {"calibration_is_nontrivial": True},
        "runtime_event_path_after_calibration": {},
        "diagnostic_decision": {"recommended_next_action": "safe_to_proceed_to_state_representation_repair", "decision_reason": "feasible", "evidence_notes": []},
        "claim_safety_status": {"paper_reproduction_claim_made": False, "performance_superiority_claim_made": False, "baseline_superiority_claim_made": False, "claim_safety_passed": True},
        "figure_manifest": FigureManifest(figure_directory="figures", figure_files=["a.png", "b.png", "c.png", "d.png", "e.png"], figure_count=5, figures_generated=True).to_dict(),
        "final_verdict": ALLOWED_FINAL_VERDICTS[0],
        "remaining_blockers": [],
        "recommended_next_feature": "State representation repair",
        "calibration_is_nontrivial": True,
        "actions_have_different_feasibility": True,
        "deadline_constraints_still_active": True,
        "completion_count_nonzero": True,
        "drop_count_nonzero": True,
        "paper_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "reward_function_modified": False,
        "policy_modified": False,
        "state_representation_modified": False,
        "dal_modified": False,
        "dependencies_modified": False,
        "environment_or_generator_files_modified": False,
        "modified_files": [],
        "environment_semantics_modified": False,
        "calibration_profile_explicit": True,
        "scope_guard_summary": {"working_tree_paths_approved": True, "staged_paths_approved": True, "base_branch_head_diff_approved": True, "forbidden_paths_detected": [], "approved_paths_detected": []},
        "environment_modification_reason": None,
        "feature_068_prerequisite_verified": True,
        "prerequisite_artifacts": {"feature_068_report": {"verified": True}},
        "prerequisite_tags_verified": [],
    }


def test_generate_figures_and_write_report(tmp_path: Path):
    payload = _dummy_report()
    figures = generate_figures(
        {
            "before_after_feasibility_comparison": payload["before_after_feasibility_comparison"],
            "after_action_path_feasibility": payload["after_action_path_feasibility"],
            "calibrated_policy_effect_comparison": payload["calibrated_policy_effect_comparison"],
            "checkpoint_50_100_calibrated_comparison": payload["checkpoint_50_100_calibrated_comparison"],
            "calibrated_task_feasibility_summary": payload["calibrated_task_feasibility_summary"],
        },
        tmp_path / "figures",
    )
    assert len(figures) == 5
    for name in figures:
        assert (tmp_path / "figures" / name).exists()

    json_path, md_path = write_deadline_timeout_calibration_report(payload, tmp_path)
    assert json_path.exists()
    assert md_path.exists()
    for path in [
        CALIBRATION_CHANGE_LOG_JSON,
        CALIBRATED_TASK_FEASIBILITY_SUMMARY_JSON,
        CALIBRATED_ACTION_PATH_FEASIBILITY_JSON,
        CALIBRATED_POLICY_EFFECT_COMPARISON_JSON,
        CHECKPOINT_50_100_CALIBRATED_COMPARISON_JSON,
        PAPER_ALIGNED_CALIBRATED_METRICS_JSON,
        RUNTIME_EVENT_PATH_AFTER_CALIBRATION_JSON,
        DIAGNOSTIC_DECISION_JSON,
        FIGURE_MANIFEST_JSON,
        REPORT_JSON,
        REPORT_MD,
        FINAL_CALIBRATION_SUMMARY_MD,
    ]:
        assert (tmp_path / path.name).exists()
