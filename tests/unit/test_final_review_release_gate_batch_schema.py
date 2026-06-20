from __future__ import annotations

import pytest

from src.analysis.final_review_release_gate_batch.config import (
    ALLOWED_NEXT_ACTIONS,
    CHECKPOINT_BUDGETS,
    EPISODE_LENGTH,
    EVALUATION_EPISODES_PER_CHECKPOINT,
    FinalReviewReleaseGateBatchConfig,
)
from src.analysis.final_review_release_gate_batch.model import (
    ActionCollapseReview,
    ClaimSafetyStatus,
    DiagnosticFindings,
    EvaluationSignalReview,
    NextActionDecision,
    ReplayBufferReview,
    RewardStabilityReview,
)


def test_config_contract_matches_feature_prompt() -> None:
    config = FinalReviewReleaseGateBatchConfig()
    assert config.checkpoint_budgets == CHECKPOINT_BUDGETS
    assert list(config.checkpoint_budgets) == [100, 150, 200, 500]
    assert config.evaluation_episode_count_per_checkpoint == EVALUATION_EPISODES_PER_CHECKPOINT
    assert config.episode_length == EPISODE_LENGTH
    assert config.training_rerun_from_scratch is False
    assert config.total_max_training_budget == 500
    assert config.recommended_next_action == "audit_reward_and_evaluation_design_before_more_training"
    assert "release_ready_for_thesis_drafting" in ALLOWED_NEXT_ACTIONS


def test_leaf_schemas_round_trip_to_dict() -> None:
    reward_review = RewardStabilityReview(
        evaluation_reward_static_across_budget=True,
        checkpoint_budgets=[100, 150, 200, 500],
        evaluation_mean_rewards={100: -1.0, 150: -1.0, 200: -1.0, 500: -1.0},
        same_evaluation_trace_bank=True,
        deterministic_evaluation_path=True,
        policy_not_affecting_evaluation_reward=True,
        likely_causes=["same_evaluation_trace_bank"],
        evidence_notes=["note"],
    )
    action_review = ActionCollapseReview(
        vertical_action_collapse_detected=True,
        checkpoint_budgets=[100, 150, 200, 500],
        action_distributions={100: {"local": 1, "horizontal": 1, "vertical": 1}},
        vertical_share_by_budget={100: 0.33},
        dominant_action="vertical",
        possible_causes=["degenerate_policy_collapse"],
        evidence_notes=["note"],
    )
    replay_review = ReplayBufferReview(
        replay_buffer_capacity=10_000,
        observed_replay_size_by_checkpoint={100: 10_000},
        replay_size_cap_detected=True,
        is_cap_expected=True,
        is_cap_blocking_larger_training=True,
        cap_type="configured_cap",
        evidence_notes=["note"],
    )
    evaluation_review = EvaluationSignalReview(
        reward_available=True,
        drop_count_available=True,
        completed_task_count_available=True,
        delay_metric_available=False,
        timeout_metric_available=False,
        train_eval_separation_available=True,
        baseline_metrics_available=True,
        thesis_level_sufficient=False,
        missing_or_null_metrics=["delay", "timeout"],
        comparison_ready=True,
        evidence_notes=["note"],
    )
    next_action = NextActionDecision(
        recommended_next_action="audit_reward_and_evaluation_design_before_more_training",
        decision_reason="reason",
        should_run_larger_training_next=False,
        should_audit_reward_and_evaluation_design_first=True,
        should_fix_action_collapse_first=True,
        should_fix_replay_capacity_or_reporting_first=False,
    )
    diagnostic_findings = DiagnosticFindings(
        feature_060_prerequisite_verified=True,
        feature_062_prerequisite_verified=True,
        feature_063_prerequisite_verified=True,
        evaluation_reward_static_across_budget=True,
        vertical_action_collapse_detected=True,
        replay_size_cap_detected=True,
        evaluation_signal_sufficient_for_claims=False,
        recommended_next_action="audit_reward_and_evaluation_design_before_more_training",
        questions={"q1": {"answer": "a"}},
    )
    claim_safety = ClaimSafetyStatus(
        paper_reproduction_claim_made=False,
        performance_superiority_claim_made=False,
        baseline_superiority_claim_made=False,
        claim_safety_passed=True,
    )

    assert reward_review.to_dict()["evaluation_reward_static_across_budget"] is True
    assert action_review.to_dict()["dominant_action"] == "vertical"
    assert replay_review.to_dict()["replay_buffer_capacity"] == 10_000
    assert evaluation_review.to_dict()["thesis_level_sufficient"] is False
    assert next_action.to_dict()["recommended_next_action"] == "audit_reward_and_evaluation_design_before_more_training"
    assert diagnostic_findings.to_dict()["evaluation_signal_sufficient_for_claims"] is False
    assert claim_safety.to_dict()["claim_safety_passed"] is True


def test_invalid_recommended_next_action_is_rejected() -> None:
    with pytest.raises(ValueError):
        FinalReviewReleaseGateBatchConfig(recommended_next_action="not_allowed")
