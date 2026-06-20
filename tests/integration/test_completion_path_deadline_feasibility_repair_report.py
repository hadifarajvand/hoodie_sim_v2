from __future__ import annotations

from src.analysis.completion_path_deadline_feasibility_repair.model import (
    CheckpointFeasibilityMetric,
    CompletionPathFeasibilityReport,
    FigureManifest,
)
from src.analysis.completion_path_deadline_feasibility_repair.report import write_completion_path_feasibility_report


def _report() -> CompletionPathFeasibilityReport:
    checkpoint_metric = CheckpointFeasibilityMetric(
        training_budget=50,
        cumulative_training_episode_count=50,
        evaluation_episode_count=100,
        episode_length=110,
        optimizer_step_count=1,
        replay_size=10,
        loss_count=1,
        last_loss=0.5,
        loss_finite=True,
        action_distribution={"local": 1, "horizontal": 0, "vertical": 0},
        action_count_total=1,
        action_accounting_reconciled=True,
        reward_summary={"reward_count": 1, "total_reward": 0.0, "mean_reward": 0.0},
        comparison_ready=True,
        claim_safety_status={"paper_reproduction_claim_made": False, "performance_superiority_claim_made": False, "baseline_superiority_claim_made": False, "claim_safety_passed": True},
        completion_path_probe={"sampled_completion_path_probe": {}, "full_evaluation_probe": {"evaluation_episode_count": 100, "episode_length": 110, "observed_decision_count": 100}},
        full_evaluation_probe={"evaluation_episode_count": 100, "episode_length": 110, "observed_decision_count": 100},
        evaluation_coverage_classification={"evaluation_mode": "full_episode_single_task_evaluation", "one_decision_per_episode_observed": True, "full_step_decision_coverage_unavailable": True},
        task_feasibility_summary={"local_feasible_task_count": 0, "horizontal_feasible_task_count": 0, "vertical_feasible_task_count": 0},
        runtime_event_path_audit={"execution_started_event_count": 0, "execution_progress_event_count": 0, "execution_completed_event_count": 0},
        policy_feasibility_summary={"policy_results": {}, "candidate_policy_vertical_collapse_in_evaluation": True},
    )
    return CompletionPathFeasibilityReport(
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
        checkpoint_metrics=[checkpoint_metric.to_dict()],
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


def test_report_writer_emits_expected_files(tmp_path):
    output_dir = tmp_path / "out"
    json_path, md_path, summary_path = write_completion_path_feasibility_report(_report(), output_dir)
    assert json_path.exists()
    assert md_path.exists()
    assert summary_path.exists()
    assert "Completion Path and Deadline Feasibility Repair" in md_path.read_text(encoding="utf-8")
