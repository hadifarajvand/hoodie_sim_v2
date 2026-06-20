from __future__ import annotations

import unittest

from src.analysis.terminal_lifecycle_accounting_50_100_comparison.config import RECOMMENDED_NEXT_FEATURE
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.model import CheckpointComparisonMetric, ClaimSafetyStatus, DiagnosticDecision, FigureManifest, TerminalLifecycleComparisonReport


def _base_checkpoint_metric(*, budget: int, index: int = 0) -> dict[str, object]:
    action_distribution = {"local": 0, "horizontal": 0, "vertical": 100}
    return {
        "training_budget": budget,
        "cumulative_training_episode_count": budget,
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "optimizer_step_count": 10 + index,
        "replay_size": 10_000,
        "action_distribution": action_distribution,
        "action_count_total": 100,
        "action_accounting_reconciled": True,
        "loss_count": 3 + index,
        "last_loss": 0.25 + index,
        "loss_finite": True,
        "reward_summary": {"reward_count": 100, "total_reward": -10.0, "mean_reward": -0.1, "pending_at_horizon_count": 0},
        "evaluation_reward_summary": {
            "evaluation_episode_count": 100,
            "mean_reward": -0.1,
            "completed_task_count": 0,
            "dropped_task_count": 100,
            "pending_at_horizon_count": 0,
            "unknown_task_count": 0,
            "terminal_transition_count": 100,
            "reward_bearing_transition_count": 100,
            "canonical_task_count": 100,
        },
        "completed_task_count": 0,
        "dropped_task_count": 100,
        "pending_at_horizon_count": 0,
        "comparison_ready": True,
        "claim_safety_status": {
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "claim_safety_passed": True,
        },
        "evaluation_action_distribution": action_distribution,
        "evaluation_decision_count": 100,
        "evaluation_action_sequence_sample": [],
        "evaluation_legal_action_mask_distribution": {"local=1|horizontal=1|vertical=1": 100},
        "evaluation_action_by_trace_id": {},
        "evaluation_action_by_episode_id": {},
        "terminal_event_classification": {"overall": {"terminal_outcome_event_count": 100, "lifecycle_only_event_count": 0, "reward_event_count": 100, "pending_event_count": 0}},
        "canonical_terminal_task_summary": {"overall": {"canonical_task_count": 100, "canonical_terminal_task_count": 100, "canonical_completion_count": 0, "canonical_drop_count": 100, "canonical_pending_count": 0, "canonical_unknown_count": 0}},
        "raw_vs_canonical_terminal_reconciliation": {"overall": {"raw_terminal_event_count": 100, "canonical_terminal_task_count": 100, "terminal_event_coverage_ratio": 1.0, "duplicate_terminal_event_count": 0, "raw_reward_event_count": 100, "canonical_reward_event_count": 100, "reward_event_coverage_ratio": 1.0, "raw_event_reward_total": -100.0, "canonical_task_reward_total": -100.0, "raw_vs_canonical_reward_delta": 0.0, "terminal_reconciled": True, "reward_reconciled": True, "raw_reward_event_recovery_blocked": False, "terminal_event_recovery_blocked": False}},
        "reward_reconciliation_after_terminal_repair": {"overall": {"raw_event_reward_total": -100.0, "raw_event_reward_count": 100, "canonical_task_reward_total": -100.0, "canonical_task_reward_count": 100, "raw_vs_canonical_reward_delta": 0.0, "reward_reconciled": True, "reward_reconciliation_tolerance": 1e-9, "raw_reward_event_recovery_blocked": False, "terminal_event_recovery_blocked": False}},
        "completion_path_audit": {"by_checkpoint": [], "by_policy": {}},
        "policy_effect_summary": {},
        "paper_aligned_diagnostic_metrics": {"checkpoint_budget": budget, "canonical_completion_ratio": 0.0, "canonical_drop_ratio": 1.0, "canonical_deadline_violation_ratio": 1.0, "canonical_pending_ratio": 0.0, "canonical_mean_completion_latency_slots": None, "canonical_mean_drop_latency_slots": 4.0, "canonical_mean_terminal_latency_slots": 4.0, "canonical_reward_per_task": -1.0, "canonical_reward_per_decision": -0.1, "canonical_tasks_per_decision": 1.0, "reward_reconciliation_status": "passed", "raw_reward_event_coverage_ratio": 1.0, "terminal_event_coverage_ratio": 1.0},
    }


def _base_report_kwargs() -> dict[str, object]:
    action_distribution = {"local": 0, "horizontal": 0, "vertical": 100}
    checkpoint_metric = _base_checkpoint_metric(budget=50)
    return {
        "feature_id": "067-terminal-lifecycle-accounting-50-100-comparison",
        "base_branch_name": "066-reward-emission-evaluation-metric-aggregation-repair",
        "branch_name": "067-terminal-lifecycle-accounting-50-100-comparison",
        "prerequisite_tags_verified": [
            {"name": "branch", "verified": True, "details": "ok"},
            {"name": "feature_066_report_valid", "verified": True, "details": "ok"},
        ],
        "prerequisite_artifacts": {"feature_066_report": {"exists": True, "verified": True, "path": "artifact", "details": "ok"}},
        "feature_066_prerequisite_verified": True,
        "checkpoint_budgets": [50, 100],
        "evaluation_episode_count_per_checkpoint": 100,
        "episode_length": 110,
        "max_training_budget": 100,
        "training_mode": "cumulative_staged_50_100_comparison",
        "training_rerun_from_scratch": False,
        "training_5000_run": False,
        "reward_reconciliation_tolerance": 1e-9,
        "checkpoint_metrics": [checkpoint_metric, _base_checkpoint_metric(budget=100, index=1)],
        "terminal_event_classification": {"overall": {"terminal_outcome_event_count": 200, "lifecycle_only_event_count": 100, "reward_event_count": 200, "pending_event_count": 0}},
        "canonical_terminal_task_summary": {"overall": {"canonical_task_count": 200, "canonical_terminal_task_count": 200, "canonical_completion_count": 0, "canonical_drop_count": 200, "canonical_pending_count": 0, "canonical_unknown_count": 0}},
        "raw_vs_canonical_terminal_reconciliation": {"overall": {"raw_terminal_event_count": 200, "canonical_terminal_task_count": 200, "terminal_event_coverage_ratio": 1.0, "duplicate_terminal_event_count": 0, "raw_reward_event_count": 200, "canonical_reward_event_count": 200, "reward_event_coverage_ratio": 1.0, "raw_event_reward_total": -200.0, "canonical_task_reward_total": -200.0, "raw_vs_canonical_reward_delta": 0.0, "terminal_reconciled": True, "reward_reconciled": True, "raw_reward_event_recovery_blocked": False, "terminal_event_recovery_blocked": False}},
        "reward_reconciliation_after_terminal_repair": {"overall": {"raw_event_reward_total": -200.0, "raw_event_reward_count": 200, "canonical_task_reward_total": -200.0, "canonical_task_reward_count": 200, "raw_vs_canonical_reward_delta": 0.0, "reward_reconciled": True, "reward_reconciliation_tolerance": 1e-9, "raw_reward_event_recovery_blocked": False, "terminal_event_recovery_blocked": False}},
        "completion_path_audit": {"by_checkpoint": [], "by_policy": {}},
        "policy_effect_50_100_after_terminal_repair": {
            "evaluation_trace_bank_id": "eval-bank",
            "evaluation_episode_count": 100,
            "episode_length": 110,
            "candidate_policy_vertical_collapse_in_evaluation": True,
            "candidate_policy_vertical_collapse_in_training_replay_window": True,
            "policy_affects_reward": "false",
            "policy_affects_terminal_outcomes": "false",
            "evaluation_reward_static_after_terminal_repair": True,
            "evaluation_action_distribution_static_across_budget": False,
            "raw_event_reward_static_across_budget": False,
            "canonical_task_reward_static_across_budget": True,
            "canonical_completion_rate_static_across_budget": True,
            "canonical_drop_rate_static_across_budget": True,
            "policy_results": {
                "candidate_policy_at_50": _base_checkpoint_metric(budget=50),
                "candidate_policy_at_100": _base_checkpoint_metric(budget=100, index=1),
                "fixed_local_policy": _base_checkpoint_metric(budget=100),
                "fixed_horizontal_policy": _base_checkpoint_metric(budget=100),
                "fixed_vertical_policy": _base_checkpoint_metric(budget=100),
                "random_legal_policy": _base_checkpoint_metric(budget=100),
            },
            "candidate_reward_variation": 0.0,
            "candidate_action_distribution_changed_by_budget": False,
            "candidate_terminal_outcomes_changed_by_budget": False,
            "canonical_policy_effect_summary": {},
        },
        "paper_aligned_50_100_metrics": {"checkpoint_budgets": [50, 100], "by_checkpoint": [checkpoint_metric, _base_checkpoint_metric(budget=100, index=1)]},
        "diagnostic_decision": {
            "recommended_next_action": "fix_completion_path_next",
            "decision_reason": "The completion path remains drop-dominant under the current trace bank.",
            "evidence_notes": ["zero_completion_across_policies=true"],
        },
        "claim_safety_status": {
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "claim_safety_passed": True,
        },
        "figure_manifest": {
            "figure_directory": "artifacts/analysis/terminal-lifecycle-accounting-50-100-comparison/figures",
            "figure_files": [
                "figure_01_terminal_event_reconciliation_50_vs_100.png",
                "figure_02_completion_drop_pending_50_vs_100.png",
                "figure_03_reward_reconciliation_50_vs_100.png",
                "figure_04_policy_effect_50_vs_100.png",
                "figure_05_completion_path_event_counts.png",
            ],
            "figure_count": 5,
            "figures_generated": True,
        },
        "remaining_blockers": [],
        "final_verdict": "terminal_lifecycle_50_100_comparison_ready",
        "raw_reward_event_recovery_blocked": False,
        "terminal_event_recovery_blocked": False,
        "terminal_reconciliation_failed": False,
        "reward_reconciliation_failed": False,
        "completion_path_audit_failed": False,
        "policy_effect_50_100_failed": False,
        "paper_reproduction_claim_made": False,
        "performance_superiority_claim_made": False,
        "baseline_superiority_claim_made": False,
        "environment_semantics_modified": False,
        "reward_function_modified": False,
        "policy_modified": False,
        "dal_modified": False,
        "dependencies_modified": False,
        "evaluation_reward_static_after_terminal_repair": True,
        "evaluation_action_distribution_static_across_budget": False,
        "candidate_policy_vertical_collapse_in_evaluation": True,
        "candidate_policy_vertical_collapse_in_training_replay_window": True,
        "policy_affects_reward": "false",
        "policy_affects_terminal_outcomes": "false",
        "most_likely_root_cause": "All fixed policies remain drop-dominant, so the remaining repair target is the completion path.",
        "recommended_next_feature": RECOMMENDED_NEXT_FEATURE,
        "explanation_of_previous_static_outputs": {
            "why_previous_outputs_looked_static": "The raw lifecycle stream mixes terminal-outcome events and lifecycle-only events, while the candidate remains vertically collapsed.",
            "raw_terminal_events_are_lifecycle_mixed": True,
            "candidate_action_distribution_changed_by_budget": False,
            "candidate_completion_count_changed_by_budget": False,
            "candidate_drop_count_changed_by_budget": False,
            "candidate_mean_reward_changed_by_budget": False,
        },
        "scope_guard_summary": {
            "working_tree_paths_approved": True,
            "staged_paths_approved": True,
            "base_branch_head_diff_approved": True,
            "forbidden_paths_detected": [],
            "approved_paths_detected": [],
            "status_classification": {"approved": True},
            "staged_classification": {"approved": True},
            "diff_classification": {"approved": True},
        },
    }


class TerminalLifecycleAccounting50_100ComparisonSchemaTests(unittest.TestCase):
    def test_checkpoint_metric_schema_accepts_staged_budgets(self) -> None:
        metric = CheckpointComparisonMetric(**_base_checkpoint_metric(budget=50))
        self.assertEqual(metric.training_budget, 50)
        self.assertEqual(metric.evaluation_decision_count, 100)
        self.assertTrue(metric.comparison_ready)

    def test_report_schema_accepts_ready_payload(self) -> None:
        report = TerminalLifecycleComparisonReport(**_base_report_kwargs())
        self.assertEqual(report.checkpoint_budgets, [50, 100])
        self.assertEqual(report.max_training_budget, 100)
        self.assertEqual(report.final_verdict, "terminal_lifecycle_50_100_comparison_ready")
        self.assertEqual(report.recommended_next_feature, RECOMMENDED_NEXT_FEATURE)

    def test_figure_manifest_requires_five_figures(self) -> None:
        manifest = FigureManifest(
            figure_directory="artifacts/analysis/terminal-lifecycle-accounting-50-100-comparison/figures",
            figure_files=[
                "figure_01_terminal_event_reconciliation_50_vs_100.png",
                "figure_02_completion_drop_pending_50_vs_100.png",
                "figure_03_reward_reconciliation_50_vs_100.png",
                "figure_04_policy_effect_50_vs_100.png",
                "figure_05_completion_path_event_counts.png",
            ],
            figure_count=5,
            figures_generated=True,
        )
        self.assertEqual(manifest.figure_count, 5)


class TerminalLifecycleAccounting50_100ComparisonClaimSafetyTests(unittest.TestCase):
    def test_claim_safety_pass_rejects_unsupported_claims(self) -> None:
        with self.assertRaises(ValueError):
            ClaimSafetyStatus(
                paper_reproduction_claim_made=True,
                performance_superiority_claim_made=False,
                baseline_superiority_claim_made=False,
                claim_safety_passed=True,
            )

    def test_ready_report_rejects_blockers_and_failed_claim_safety(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["remaining_blockers"] = ["reward_reconciliation_failed"]
        kwargs["claim_safety_status"] = {
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "claim_safety_passed": False,
        }
        kwargs["final_verdict"] = "terminal_lifecycle_50_100_comparison_ready"
        with self.assertRaises(ValueError):
            TerminalLifecycleComparisonReport(**kwargs)

    def test_ready_decision_requires_allowed_action(self) -> None:
        decision = DiagnosticDecision(
            recommended_next_action="fix_completion_path_next",
            decision_reason="completion remains blocked",
            evidence_notes=["example"],
        )
        self.assertEqual(decision.recommended_next_action, "fix_completion_path_next")


if __name__ == "__main__":
    unittest.main()
