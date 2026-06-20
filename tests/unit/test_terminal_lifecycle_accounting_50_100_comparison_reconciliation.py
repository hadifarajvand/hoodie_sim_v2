from __future__ import annotations

import unittest

from src.analysis.terminal_lifecycle_accounting_50_100_comparison.comparison import build_budget_comparison
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.diagnostics import build_diagnostic_decision
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.reconciliation import (
    build_canonical_terminal_task_summary,
    build_completion_path_audit,
    build_paper_aligned_50_100_metrics,
    build_raw_vs_canonical_terminal_reconciliation,
    build_reward_reconciliation_after_terminal_repair,
    build_terminal_event_classification_summary,
)

from tests.unit.test_terminal_lifecycle_accounting_50_100_comparison_schema import _base_checkpoint_metric


def _fake_checkpoint_results() -> list[dict[str, object]]:
    def _evaluation_result(budget: int, *, vertical: int) -> dict[str, object]:
        base = _base_checkpoint_metric(budget=budget)
        base["evaluation_action_distribution"] = {"local": 0, "horizontal": 0, "vertical": vertical}
        base["evaluation_decision_count"] = vertical
        base["action_distribution"] = {"local": 0, "horizontal": 0, "vertical": vertical}
        base["action_count_total"] = vertical
        base["evaluation_reward_summary"] = {
            "evaluation_episode_count": 100,
            "mean_reward": -1.0,
            "completed_task_count": 0,
            "dropped_task_count": 100,
            "pending_at_horizon_count": 0,
            "unknown_task_count": 0,
            "terminal_transition_count": 100,
            "reward_bearing_transition_count": 100,
            "canonical_task_count": 100,
        }
        base["terminal_event_classification"] = {
            "terminal_outcome_event_count": 100,
            "lifecycle_only_event_count": 100,
            "reward_event_count": 100,
            "pending_event_count": 0,
            "event_type_counts": {"task_dropped": 100, "reward_emitted": 100, "deadline_reached": 100, "deadline_expired": 100},
            "sample_events": [],
        }
        base["canonical_terminal_task_summary"] = {
            "checkpoint_budget": budget,
            "overall": {
                "canonical_task_count": 100,
                "canonical_terminal_task_count": 100,
                "canonical_completion_count": 0,
                "canonical_drop_count": 100,
                "canonical_pending_count": 0,
                "canonical_unknown_count": 0,
                "raw_terminal_event_count": 100,
                "raw_reward_emission_count": 100,
                "raw_event_reward_total": -100.0,
                "raw_event_reward_count": 100,
                "canonical_task_reward_total": -100.0,
                "canonical_task_reward_count": 100,
                "raw_vs_canonical_reward_delta": 0.0,
                "duplicate_terminal_event_count": 0,
                "duplicate_reward_event_count": 0,
                "double_count_detected": False,
                "canonical_completion_ratio": 0.0,
                "canonical_drop_ratio": 1.0,
                "canonical_deadline_violation_ratio": 1.0,
                "canonical_pending_ratio": 0.0,
                "canonical_mean_completion_latency_slots": None,
                "canonical_mean_drop_latency_slots": 4.0,
                "canonical_mean_terminal_latency_slots": 4.0,
                "canonical_reward_per_task": -1.0,
                "canonical_reward_per_decision": -1.0,
                "canonical_tasks_per_decision": 1.0,
            },
            "sample_task_outcomes": [],
        }
        base["raw_vs_canonical_terminal_reconciliation"] = {
            "raw_terminal_event_count": 100,
            "canonical_terminal_task_count": 100,
            "terminal_event_coverage_ratio": 1.0,
            "duplicate_terminal_event_count": 0,
            "raw_reward_event_count": 100,
            "canonical_reward_event_count": 100,
            "reward_event_coverage_ratio": 1.0,
            "raw_event_reward_total": -100.0,
            "canonical_task_reward_total": -100.0,
            "raw_vs_canonical_reward_delta": 0.0,
            "terminal_reconciled": True,
            "reward_reconciled": True,
            "raw_reward_event_recovery_blocked": False,
            "terminal_event_recovery_blocked": False,
        }
        base["reward_reconciliation_after_terminal_repair"] = {
            "raw_event_reward_total": -100.0,
            "raw_event_reward_count": 100,
            "canonical_task_reward_total": -100.0,
            "canonical_task_reward_count": 100,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_reconciled": True,
            "reward_reconciliation_tolerance": 1e-9,
            "raw_reward_event_recovery_blocked": False,
            "terminal_event_recovery_blocked": False,
        }
        base["completion_path_audit"] = {
            "execution_completed_event_count": 0,
            "task_completed_event_count": 0,
            "completed_canonical_task_count": 0,
            "deadline_reached_event_count": 100,
            "deadline_expired_event_count": 100,
            "task_dropped_event_count": 100,
            "reward_emitted_event_count": 100,
            "pending_at_horizon_count": 0,
            "execution_completed_but_no_task_completed_detected": False,
            "task_completed_but_no_reward_detected": False,
            "deadline_reached_then_task_dropped_duplicate_detected": True,
            "reward_emitted_without_terminal_outcome_detected": False,
            "terminal_outcome_without_reward_detected": False,
        }
        base["paper_aligned_diagnostic_metrics"] = {
            "checkpoint_budget": budget,
            "canonical_completion_ratio": 0.0,
            "canonical_drop_ratio": 1.0,
            "canonical_deadline_violation_ratio": 1.0,
            "canonical_pending_ratio": 0.0,
            "canonical_mean_completion_latency_slots": None,
            "canonical_mean_drop_latency_slots": 4.0,
            "canonical_mean_terminal_latency_slots": 4.0,
            "canonical_reward_per_task": -1.0,
            "canonical_reward_per_decision": -1.0,
            "canonical_tasks_per_decision": 1.0,
            "reward_reconciliation_status": "passed",
            "raw_reward_event_coverage_ratio": 1.0,
            "terminal_event_coverage_ratio": 1.0,
        }
        return base

    return [
        {"training_budget": 50, "cumulative_training_episode_count": 50, "evaluation_policy_result": _evaluation_result(50, vertical=90)},
        {"training_budget": 100, "cumulative_training_episode_count": 100, "evaluation_policy_result": _evaluation_result(100, vertical=100)},
    ]


class TerminalLifecycleAccounting50_100ComparisonReconciliationTests(unittest.TestCase):
    def test_canonical_terminal_task_aggregation_counts_each_task_once(self) -> None:
        checkpoint_results = _fake_checkpoint_results()
        summary = build_canonical_terminal_task_summary(checkpoint_results)
        self.assertEqual(summary["overall"]["canonical_task_count"], 200)
        self.assertEqual(summary["overall"]["canonical_terminal_task_count"], 200)
        self.assertEqual(summary["overall"]["canonical_completion_count"], 0)

    def test_terminal_reconciliation_excludes_lifecycle_only_events(self) -> None:
        checkpoint_results = _fake_checkpoint_results()
        classification = build_terminal_event_classification_summary(checkpoint_results)
        recon = build_raw_vs_canonical_terminal_reconciliation(checkpoint_results)
        self.assertGreater(classification["overall"]["lifecycle_only_event_count"], 0)
        self.assertEqual(recon["overall"]["terminal_event_coverage_ratio"], 1.0)
        self.assertTrue(recon["overall"]["terminal_reconciled"])

    def test_reward_reconciliation_and_budget_comparison_exist(self) -> None:
        checkpoint_results = _fake_checkpoint_results()
        reward_recon = build_reward_reconciliation_after_terminal_repair(checkpoint_results)
        completion_audit = build_completion_path_audit(
            checkpoint_results,
            {
                "policy_results": {},
            },
        )
        paper_metrics = build_paper_aligned_50_100_metrics(checkpoint_results)
        comparison = build_budget_comparison(
            checkpoint_results,
            {
                "policy_results": {},
                "candidate_policy_vertical_collapse_in_evaluation": True,
                "candidate_policy_vertical_collapse_in_training_replay_window": True,
                "policy_affects_reward": "false",
                "policy_affects_terminal_outcomes": "false",
                "evaluation_reward_static_after_terminal_repair": True,
                "evaluation_action_distribution_static_across_budget": False,
            },
        )
        self.assertTrue(reward_recon["overall"]["reward_reconciled"])
        self.assertIn("by_policy", completion_audit)
        self.assertEqual(paper_metrics["checkpoint_budgets"], [50, 100])
        self.assertIn("comparison", comparison)

    def test_diagnostic_decision_uses_canonical_repair_signals(self) -> None:
        decision = build_diagnostic_decision(
            terminal_reconciliation_failed=False,
            reward_reconciliation_failed=False,
            candidate_policy_vertical_collapse_in_evaluation=True,
            candidate_policy_vertical_collapse_in_training_replay_window=True,
            all_fixed_policies_zero_completion=True,
            any_fixed_policy_completes=False,
            terminal_event_coverage_ratio=1.0,
            policy_affects_reward="false",
            policy_affects_terminal_outcomes="false",
        )
        self.assertEqual(decision["recommended_next_action"], "fix_completion_path_next")


if __name__ == "__main__":
    unittest.main()
