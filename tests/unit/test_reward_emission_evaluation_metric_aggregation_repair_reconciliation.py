from __future__ import annotations

import unittest

from src.analysis.reward_emission_evaluation_metric_aggregation_repair.diagnostics import build_diagnostic_decision
from src.analysis.reward_emission_evaluation_metric_aggregation_repair.reconciliation import build_canonical_task_reconciliation

from tests.unit.test_reward_emission_evaluation_metric_aggregation_repair_schema import _base_checkpoint_metric


def _task_records() -> dict[str, dict[str, object]]:
    return {
        "trace-1:0:1": {
            "trace_id": "trace-1",
            "episode_id": 0,
            "task_id": 1,
            "selected_action": "vertical",
            "first_decision_slot": 0,
            "arrival_slot": 0,
            "decision_record": {"selected_action": "vertical"},
            "terminal_event_records": [{"terminal_outcome": "dropped", "slot": 3}],
            "reward_event_records": [{"raw_reward": -40.0, "reward_available": True}],
            "finalized_records": [{"terminal_outcome": "dropped", "arrival_slot": 0, "completion_slot": 3}],
            "pending_evidence": False,
            "raw_terminal_event_count": 2,
            "raw_reward_event_count": 1,
            "raw_reward_total": -40.0,
            "terminal_outcome": "dropped",
            "terminal_slot": 3,
            "completion_or_drop_slot": 3,
            "latency_slots": 4,
            "canonical_reward": -40.0,
        },
        "trace-1:0:2": {
            "trace_id": "trace-1",
            "episode_id": 0,
            "task_id": 2,
            "selected_action": "vertical",
            "first_decision_slot": 1,
            "arrival_slot": 1,
            "decision_record": {"selected_action": "vertical"},
            "terminal_event_records": [{"terminal_outcome": "completed", "slot": 4}],
            "reward_event_records": [{"raw_reward": -4.0, "reward_available": True}],
            "finalized_records": [{"terminal_outcome": "completed", "arrival_slot": 1, "completion_slot": 4}],
            "pending_evidence": False,
            "raw_terminal_event_count": 1,
            "raw_reward_event_count": 1,
            "raw_reward_total": -4.0,
            "terminal_outcome": "completed",
            "terminal_slot": 4,
            "completion_or_drop_slot": 4,
            "latency_slots": 4,
            "canonical_reward": -4.0,
        },
        "trace-1:0:3": {
            "trace_id": "trace-1",
            "episode_id": 0,
            "task_id": 3,
            "selected_action": "horizontal",
            "first_decision_slot": 2,
            "arrival_slot": 2,
            "decision_record": {"selected_action": "horizontal"},
            "terminal_event_records": [{"terminal_outcome": "pending_at_horizon", "slot": 5}],
            "reward_event_records": [],
            "finalized_records": [],
            "pending_evidence": True,
            "raw_terminal_event_count": 0,
            "raw_reward_event_count": 0,
            "raw_reward_total": 0.0,
            "terminal_outcome": "pending_at_horizon",
            "terminal_slot": 5,
            "completion_or_drop_slot": None,
            "latency_slots": None,
            "canonical_reward": 0.0,
        },
    }


class RewardEmissionEvaluationMetricAggregationRepairReconciliationTests(unittest.TestCase):
    def test_canonical_task_aggregation_counts_each_task_once(self) -> None:
        result = build_canonical_task_reconciliation(
            checkpoint_budget=100,
            evaluation_decision_count=3,
            task_records=_task_records(),
        )
        overall = result["canonical_task_outcome_summary"]["overall"]
        self.assertEqual(overall["canonical_task_count"], 3)
        self.assertEqual(overall["canonical_terminal_task_count"], 2)
        self.assertEqual(overall["canonical_reward_count"], 2)
        self.assertEqual(result["raw_vs_canonical_reward_reconciliation"]["raw_vs_canonical_reward_delta"], 0.0)
        self.assertTrue(result["raw_vs_canonical_reward_reconciliation"]["reward_reconciled"])
        self.assertGreater(result["raw_vs_canonical_reward_reconciliation"]["duplicate_terminal_event_count"], 0)

    def test_reward_reconciliation_flags_match_diagnostic_decision(self) -> None:
        decision = build_diagnostic_decision(
            raw_reward_event_recovery_blocked=True,
            terminal_event_recovery_blocked=False,
            reward_reconciled=False,
            candidate_policy_vertical_collapse_in_evaluation=False,
            candidate_policy_vertical_collapse_in_training_replay_window=False,
            policy_affects_reward="false",
            policy_affects_terminal_outcomes="false",
        )
        self.assertEqual(decision["recommended_next_action"], "blocked_due_to_unresolved_reward_event_recovery")

    def test_checkpoint_metric_helper_matches_expected_budget(self) -> None:
        checkpoint = _base_checkpoint_metric(budget=100)
        self.assertEqual(checkpoint["training_budget"], 100)
        self.assertEqual(checkpoint["evaluation_reward_summary"]["raw_reward_event_count"], 3)


if __name__ == "__main__":
    unittest.main()
