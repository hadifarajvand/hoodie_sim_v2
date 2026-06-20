from __future__ import annotations

import pytest

from src.analysis.completion_path_deadline_feasibility_repair.diagnostics import build_diagnostic_decision, classify_completion_failure
from src.analysis.completion_path_deadline_feasibility_repair.model import ClaimSafetyStatus


def test_unsupported_claims_cannot_pass_safety():
    with pytest.raises(ValueError):
        ClaimSafetyStatus(
            paper_reproduction_claim_made=True,
            performance_superiority_claim_made=False,
            baseline_superiority_claim_made=False,
            claim_safety_passed=True,
        )


def test_diagnostic_decision_prefers_deadline_repair_for_infeasible_tasks():
    classification = classify_completion_failure(
        task_feasibility_summary={"all_actions_infeasible": True, "local_feasible_task_count": 0, "horizontal_feasible_task_count": 0, "vertical_feasible_task_count": 0},
        runtime_event_path_audit={"overall": {"execution_completed_event_count": 0, "tasks_with_positive_execution_progress_count": 0}},
        coverage_classification={"evaluation_mode": "full_episode_single_task_evaluation", "observed_decision_count": 100, "expected_max_decision_slots": 11000},
        policy_effect_completion_feasibility={"policy_results": {"candidate_policy_at_100": {}}, "policy_feasibility_summary": {}},
    )
    decision = build_diagnostic_decision(classification)
    assert decision["recommended_next_action"] == "fix_deadline_timeout_configuration_next"
