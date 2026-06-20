from __future__ import annotations

import unittest

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.config import RECOMMENDED_NEXT_FEATURE
from src.analysis.evaluation_instrumentation_reward_state_diagnostic.model import (
    CheckpointMetric,
    ClaimSafetyStatus,
    DiagnosticDecision,
    EvaluationInstrumentationDiagnosticReport,
)


def _base_checkpoint_metric(*, budget: int, index: int = 0) -> dict[str, object]:
    return {
        "training_budget": budget,
        "cumulative_training_episode_count": budget,
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "optimizer_step_count": 10 + index,
        "replay_size": 10_000,
        "action_distribution": {"local": 0, "horizontal": 0, "vertical": 100},
        "action_count_total": 100,
        "action_accounting_reconciled": True,
        "loss_count": 3 + index,
        "last_loss": 0.25 + index,
        "loss_finite": True,
        "reward_summary": {"reward_count": 100, "total_reward": -10.0, "mean_reward": -0.1, "pending_at_horizon_count": 0},
        "evaluation_reward_summary": {
            "evaluation_episode_count": 100,
            "mean_reward": -0.1,
            "completed_task_count": 1,
            "dropped_task_count": 2,
            "terminal_transition_count": 3,
            "reward_bearing_transition_count": 3,
        },
        "completed_task_count": 1,
        "dropped_task_count": 2,
        "pending_at_horizon_count": 0,
        "comparison_ready": False,
        "claim_safety_status": {
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "claim_safety_passed": False,
        },
        "evaluation_action_distribution": {"local": 0, "horizontal": 0, "vertical": 100},
        "evaluation_decision_count": 100,
        "evaluation_action_sequence_sample": [],
        "evaluation_legal_action_mask_distribution": {"local=1|horizontal=1|vertical=1": 100},
        "evaluation_action_by_trace_id": {},
        "evaluation_action_by_episode_id": {},
        "replay_window_action_distribution": {"local": 0, "horizontal": 0, "vertical": 100},
        "cumulative_training_action_distribution": {"local": 0, "horizontal": 0, "vertical": 100},
        "replay_window_is_full_training_history": False,
        "replay_window_capacity": 10_000,
        "replay_window_interpretation_warning": True,
        "per_action_outcome_summary": {
            "local": {
                "decision_count": 0,
                "completed_count": 0,
                "dropped_count": 0,
                "pending_at_horizon_count": 0,
                "terminal_transition_count": 0,
                "reward_bearing_transition_count": 0,
                "total_reward": 0.0,
                "mean_reward": 0.0,
                "completion_reward_count": 0,
                "drop_penalty_count": 0,
                "mean_completion_latency_slots": None,
                "mean_drop_latency_slots": None,
            },
            "horizontal": {
                "decision_count": 0,
                "completed_count": 0,
                "dropped_count": 0,
                "pending_at_horizon_count": 0,
                "terminal_transition_count": 0,
                "reward_bearing_transition_count": 0,
                "total_reward": 0.0,
                "mean_reward": 0.0,
                "completion_reward_count": 0,
                "drop_penalty_count": 0,
                "mean_completion_latency_slots": None,
                "mean_drop_latency_slots": None,
            },
            "vertical": {
                "decision_count": 100,
                "completed_count": 1,
                "dropped_count": 2,
                "pending_at_horizon_count": 0,
                "terminal_transition_count": 3,
                "reward_bearing_transition_count": 3,
                "total_reward": -10.0,
                "mean_reward": -0.1,
                "completion_reward_count": 1,
                "drop_penalty_count": 2,
                "mean_completion_latency_slots": 4.0,
                "mean_drop_latency_slots": 5.0,
            },
            "overall": {
                "decision_count": 100,
                "completed_count": 1,
                "dropped_count": 2,
                "pending_at_horizon_count": 0,
                "terminal_transition_count": 3,
                "reward_bearing_transition_count": 3,
                "total_reward": -10.0,
                "mean_reward": -0.1,
                "mean_completion_latency_slots": 4.0,
                "mean_drop_latency_slots": 5.0,
            },
        },
        "reward_decomposition": {
            "reward_by_action": {"local": 0.0, "horizontal": 0.0, "vertical": -10.0},
            "reward_by_terminal_outcome": {"completed": -2.0, "dropped": -8.0},
            "reward_by_action_and_terminal_outcome": {
                "local": {"completed": {"count": 0, "total_reward": 0.0, "mean_reward": 0.0}, "dropped": {"count": 0, "total_reward": 0.0, "mean_reward": 0.0}},
                "horizontal": {"completed": {"count": 0, "total_reward": 0.0, "mean_reward": 0.0}, "dropped": {"count": 0, "total_reward": 0.0, "mean_reward": 0.0}},
                "vertical": {"completed": {"count": 1, "total_reward": -2.0, "mean_reward": -2.0}, "dropped": {"count": 2, "total_reward": -8.0, "mean_reward": -4.0}},
            },
            "drop_penalty_count_by_action": {"local": 0, "horizontal": 0, "vertical": 2},
            "completion_reward_count_by_action": {"local": 0, "horizontal": 0, "vertical": 1},
            "nan_reward_count": 0,
            "zero_reward_count": 0,
            "reward_available_count": 3,
        },
    }


def _base_report_kwargs() -> dict[str, object]:
    checkpoint_metrics = [_base_checkpoint_metric(budget=budget, index=index) for index, budget in enumerate([100, 150, 200, 500])]
    return {
        "feature_id": "065-evaluation-instrumentation-reward-state-diagnostic",
        "base_branch_name": "064-final-review-release-gate-batch",
        "branch_name": "065-evaluation-instrumentation-reward-state-diagnostic",
        "prerequisite_tags_verified": [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "feature_064_report_valid", "verified": True, "details": "064"},
            {"name": "feature_063_report_valid", "verified": True, "details": "063"},
        ],
        "prerequisite_artifacts": {
            "feature_064_report": {"path": "064", "exists": True, "verified": True, "details": ""},
        },
        "feature_064_prerequisite_verified": True,
        "checkpoint_budgets": [100, 150, 200, 500],
        "evaluation_episode_count_per_checkpoint": 100,
        "episode_length": 110,
        "max_training_budget": 500,
        "training_mode": "cumulative_staged_diagnostic",
        "training_rerun_from_scratch": False,
        "training_5000_run": False,
        "checkpoint_metrics": checkpoint_metrics,
        "evaluation_action_distribution": {"source": "evaluation_episodes", "by_checkpoint": {}},
        "per_action_outcome_summary": {"by_checkpoint": {}},
        "reward_decomposition": {"by_checkpoint": {}},
        "replay_window_vs_cumulative_training_actions": {"checkpoint_budgets": [100, 150, 200, 500], "by_checkpoint": {}},
        "state_feature_coverage_audit": [],
        "policy_effect_diagnostic": {"policy_results": {}},
        "diagnostic_decision": {
            "recommended_next_action": "blocked_due_to_unresolved_instrumentation",
            "decision_reason": "blocked",
            "evidence_notes": [],
        },
        "claim_safety_status": {
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "claim_safety_passed": False,
        },
        "figure_manifest": {"figure_directory": "artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/figures", "figure_files": [], "figure_count": 0, "figures_generated": False},
        "diagnostic_findings": {
            "feature_064_prerequisite_verified": True,
            "evaluation_reward_static_across_budget": True,
            "vertical_action_collapse_detected": True,
            "replay_window_rolling_only": True,
            "evaluation_signal_sufficient_for_claims": False,
            "questions": {},
            "checkpoint_budgets": [100, 150, 200, 500],
        },
        "evaluation_action_logging_repair_result": {
            "evaluation_action_distribution_present": True,
            "evaluation_action_distribution_source": "evaluation_episodes",
            "evaluation_decision_count_per_checkpoint": {"100": 100},
            "evaluation_action_sequence_sample_limit": 25,
            "evaluation_action_sequence_sample_present": True,
        },
        "replay_rolling_window_interpretation_repair_result": {
            "replay_window_is_full_training_history": False,
            "replay_window_capacity": 10_000,
            "replay_window_interpretation_warning": True,
            "by_checkpoint": {},
        },
        "per_action_outcome_attribution_result": {"per_action_outcome_summary_present": True, "by_checkpoint": {}},
        "reward_decomposition_result": {"reward_decomposition_present": True, "by_checkpoint": {}},
        "state_feature_coverage_audit_result": {
            "state_feature_coverage_audit_present": True,
            "field_count": 18,
            "high_risk_missing_fields": ["queue_load"],
            "audit": [],
        },
        "policy_effect_diagnostic_result": {
            "policy_results_present": True,
            "evaluation_reward_static_after_instrumentation": True,
            "candidate_policy_vertical_collapse_in_evaluation": True,
            "candidate_policy_vertical_collapse_in_training_replay_window": True,
            "policy_affects_reward": "false",
            "policy_affects_terminal_outcomes": "false",
            "evaluation_metric_static_because_policy_same": "false",
            "evaluation_metric_static_because_reward_aggregation": "true",
            "evaluation_metric_static_because_environment_dynamics": "uncertain",
            "policy_results": {},
        },
        "explanation_of_previous_static_outputs": {
            "mean_rewards_by_budget": {100: -1.0, 150: -1.0, 200: -1.0, 500: -1.0},
            "evaluation_reward_static_across_budget": True,
            "evaluation_action_distribution_from_evaluation_episodes": True,
            "replay_window_is_not_full_history": True,
            "reward_decomposition_available": True,
            "state_feature_gaps": ["queue_load"],
            "policy_effect_summary": {},
            "evidence_notes": [],
        },
        "evaluation_reward_static_after_instrumentation": True,
        "evaluation_action_distribution_changed_by_budget": True,
        "candidate_policy_vertical_collapse_in_evaluation": True,
        "candidate_policy_vertical_collapse_in_training_replay_window": True,
        "policy_affects_reward": "false",
        "policy_affects_terminal_outcomes": "false",
        "most_likely_root_cause": "reward aggregation masks action-level differences",
        "recommended_next_feature": RECOMMENDED_NEXT_FEATURE,
        "remaining_blockers": ["evaluation_signal_insufficient_for_claims"],
        "final_verdict": "evaluation_instrumentation_diagnostic_blocked",
    }


class EvaluationInstrumentationRewardStateDiagnosticSchemaTests(unittest.TestCase):
    def test_checkpoint_metric_round_trip_schema(self) -> None:
        metric = CheckpointMetric(**_base_checkpoint_metric(budget=100))
        payload = metric.to_dict()
        self.assertEqual(payload["training_budget"], 100)
        self.assertEqual(payload["evaluation_decision_count"], 100)
        self.assertTrue(payload["replay_window_interpretation_warning"])

    def test_report_round_trip_schema(self) -> None:
        report = EvaluationInstrumentationDiagnosticReport(**_base_report_kwargs())
        payload = report.to_dict()
        self.assertEqual(payload["checkpoint_budgets"], [100, 150, 200, 500])
        self.assertEqual(payload["max_training_budget"], 500)
        self.assertEqual(payload["training_mode"], "cumulative_staged_diagnostic")
        self.assertEqual(payload["final_verdict"], "evaluation_instrumentation_diagnostic_blocked")

    def test_report_rejects_unsupported_claims_when_passed(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["final_verdict"] = "evaluation_instrumentation_diagnostic_ready"
        kwargs["remaining_blockers"] = []
        kwargs["claim_safety_status"] = {
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "claim_safety_passed": True,
        }
        kwargs["figure_manifest"] = {
            "figure_directory": "artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/figures",
            "figure_files": ["a", "b", "c", "d", "e", "f", "g"],
            "figure_count": 7,
            "figures_generated": True,
        }
        report = EvaluationInstrumentationDiagnosticReport(**kwargs)
        self.assertEqual(report.final_verdict, "evaluation_instrumentation_diagnostic_ready")
        self.assertEqual(report.to_dict()["figure_manifest"]["figure_count"], 7)


if __name__ == "__main__":
    unittest.main()
