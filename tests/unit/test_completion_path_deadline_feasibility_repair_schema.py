from __future__ import annotations

from types import SimpleNamespace

from src.analysis.completion_path_deadline_feasibility_repair.config import CompletionPathFeasibilityConfig, TRAINING_BUDGETS, MAX_TRAINING_BUDGET
from src.analysis.completion_path_deadline_feasibility_repair.model import (
    CheckpointFeasibilityMetric,
    ClaimSafetyStatus,
    CompletionPathFeasibilityReport,
    DiagnosticDecision,
    FigureManifest,
)


def _checkpoint_metric_dict() -> dict[str, object]:
    return CheckpointFeasibilityMetric(
        training_budget=50,
        cumulative_training_episode_count=50,
        evaluation_episode_count=100,
        episode_length=110,
        optimizer_step_count=1,
        replay_size=10,
        loss_count=1,
        last_loss=0.5,
        loss_finite=True,
        action_distribution={"local": 10, "horizontal": 0, "vertical": 0},
        action_count_total=10,
        action_accounting_reconciled=True,
        reward_summary={"reward_count": 1, "total_reward": 0.0, "mean_reward": 0.0},
        comparison_ready=True,
        claim_safety_status={
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "claim_safety_passed": True,
        },
        completion_path_probe={"sampled_completion_path_probe": {}, "full_evaluation_probe": {"evaluation_episode_count": 100, "episode_length": 110, "observed_decision_count": 100}},
        full_evaluation_probe={"evaluation_episode_count": 100, "episode_length": 110, "observed_decision_count": 100},
        evaluation_coverage_classification={"evaluation_mode": "full_episode_single_task_evaluation", "one_decision_per_episode_observed": True, "full_step_decision_coverage_unavailable": True},
        task_feasibility_summary={"local_feasible_task_count": 0, "horizontal_feasible_task_count": 0, "vertical_feasible_task_count": 0},
        runtime_event_path_audit={"execution_started_event_count": 0, "execution_progress_event_count": 0, "execution_completed_event_count": 0},
        policy_feasibility_summary={"policy_results": {}, "candidate_policy_vertical_collapse_in_evaluation": True},
    ).to_dict()


def test_config_schema_values():
    config = CompletionPathFeasibilityConfig()
    assert config.training_budgets == TRAINING_BUDGETS
    assert config.max_training_budget == MAX_TRAINING_BUDGET
    assert config.training_5000_run is False
    assert config.training_rerun_from_scratch is False
    assert config.to_dict()["sampled_completion_path_max_task_decisions"] == 100


def test_model_schema_accepts_required_payloads():
    metric = _checkpoint_metric_dict()
    report = CompletionPathFeasibilityReport(
        feature_id="068-completion-path-deadline-feasibility-repair",
        base_branch_name="067-terminal-lifecycle-accounting-50-100-comparison",
        branch_name="068-completion-path-deadline-feasibility-repair",
        checkpoint_budgets=[50, 100],
        evaluation_episode_count_per_checkpoint=100,
        episode_length=110,
        expected_max_decision_slots=11000,
        sampled_completion_path_max_task_decisions=100,
        max_training_budget=100,
        training_mode="cumulative_staged_50_100_completion_feasibility",
        training_rerun_from_scratch=False,
        training_5000_run=False,
        feature_067_prerequisite_verified=True,
        prerequisite_tags_verified=[],
        prerequisite_artifacts={},
        checkpoint_metrics=[metric],
        task_feasibility_summary={"local_feasible_task_count": 0, "horizontal_feasible_task_count": 0, "vertical_feasible_task_count": 0},
        action_path_feasibility={"total_task_count": 0},
        runtime_event_path_audit={"overall": {"execution_started_event_count": 0, "execution_progress_event_count": 0, "execution_completed_event_count": 0}, "by_policy": {}},
        completion_failure_classification={"root_cause": "all_tasks_infeasible_under_current_deadlines", "decision": "fix_deadline_timeout_configuration_next", "evidence": []},
        policy_effect_completion_feasibility={"policy_results": {}, "policy_feasibility_summary": {}},
        checkpoint_50_100_feasibility_comparison={"checkpoint_budgets": [50, 100], "by_checkpoint": [], "comparison": {}, "comparison_classification": "no_change_between_50_and_100"},
        evaluation_coverage_classification={"evaluation_mode": "full_episode_single_task_evaluation", "one_decision_per_episode_observed": True, "full_step_decision_coverage_unavailable": True},
        diagnostic_decision={"recommended_next_action": "fix_deadline_timeout_configuration_next", "decision_reason": "deadlines are infeasible", "evidence_notes": []},
        claim_safety_status={"paper_reproduction_claim_made": False, "performance_superiority_claim_made": False, "baseline_superiority_claim_made": False, "claim_safety_passed": True},
        figure_manifest=FigureManifest(figure_directory="artifacts", figure_files=["a.png"] * 5, figure_count=5, figures_generated=True).to_dict(),
        final_verdict="completion_path_feasibility_repair_ready",
        recommended_next_feature="Deadline / timeout repair",
        remaining_blockers=[],
        explanation_of_completion_blocker="deadlines too short",
        scope_guard_summary={"working_tree_paths_approved": True},
    )
    assert report.to_dict()["final_verdict"] == "completion_path_feasibility_repair_ready"


def test_claim_safety_and_diagnostic_decision_validation():
    status = ClaimSafetyStatus(False, False, False, True)
    assert status.claim_safety_passed is True
    decision = DiagnosticDecision("fix_deadline_timeout_configuration_next", "deadlines are infeasible", ["evidence"])
    assert decision.recommended_next_action == "fix_deadline_timeout_configuration_next"
