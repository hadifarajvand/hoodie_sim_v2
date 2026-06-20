from __future__ import annotations

from src.analysis.deadline_timeout_feasible_workload_calibration.report import compact_deadline_timeout_calibration_payload


def _report_payload() -> dict:
    return {
        "feature_id": "069-deadline-timeout-feasible-workload-calibration",
        "base_branch_name": "068-completion-path-deadline-feasibility-repair",
        "branch_name": "069-deadline-timeout-feasible-workload-calibration",
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
        "calibrated_policy_effect_comparison": {"any_fixed_policy_completes": True, "fixed_policy_summaries": {}, "policy_results": {}, "policy_summaries": {}, "raw_event_reward_static_across_budget": False, "canonical_task_reward_static_across_budget": False, "canonical_completion_rate_static_across_budget": False, "canonical_drop_rate_static_across_budget": False, "evaluation_action_distribution_static_across_budget": False, "policy_affects_reward": "true", "policy_affects_terminal_outcomes": "true", "candidate_action_distribution_changed_by_budget": True, "candidate_terminal_outcomes_changed_by_budget": True, "candidate_policy_vertical_collapse_in_evaluation": False, "candidate_policy_vertical_collapse_in_training_replay_window": False, "evaluation_reward_static_after_terminal_repair": False},
        "checkpoint_50_100_calibrated_comparison": {"checkpoint_budgets": [50, 100], "by_checkpoint": [{"training_budget": 50}, {"training_budget": 100}]},
        "paper_aligned_calibrated_metrics": {"calibration_is_nontrivial": True},
        "runtime_event_path_after_calibration": {},
        "diagnostic_decision": {"recommended_next_action": "safe_to_proceed_to_state_representation_repair", "decision_reason": "feasible", "evidence_notes": []},
        "claim_safety_status": {"paper_reproduction_claim_made": False, "performance_superiority_claim_made": False, "baseline_superiority_claim_made": False, "claim_safety_passed": True},
        "figure_manifest": {"figure_directory": "figures", "figure_files": ["a.png", "b.png", "c.png", "d.png", "e.png"], "figure_count": 5, "figures_generated": True},
        "final_verdict": "deadline_timeout_feasible_workload_calibration_ready",
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


def test_report_payload_contains_required_sections():
    payload = compact_deadline_timeout_calibration_payload(_report_payload())

    assert payload["final_verdict"] == "deadline_timeout_feasible_workload_calibration_ready"
    assert payload["calibrated_task_feasibility_summary"]["overall_feasible_task_ratio"] >= 0.20
    assert payload["calibrated_policy_effect_comparison"]["any_fixed_policy_completes"] is True
    assert payload["paper_reproduction_claim_made"] is False
    assert payload["performance_superiority_claim_made"] is False
    assert payload["baseline_superiority_claim_made"] is False
