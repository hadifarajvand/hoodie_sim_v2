from __future__ import annotations

import unittest

from src.analysis.reward_emission_evaluation_metric_aggregation_repair.reconciliation import build_canonical_task_reconciliation

from tests.unit.test_reward_emission_evaluation_metric_aggregation_repair_reconciliation import _task_records


class RewardEmissionEvaluationMetricAggregationRepairRewardEventTests(unittest.TestCase):
    def test_reward_event_records_are_recovered_and_reconciled(self) -> None:
        result = build_canonical_task_reconciliation(
            checkpoint_budget=150,
            evaluation_decision_count=3,
            task_records=_task_records(),
        )
        reconciliation = result["raw_vs_canonical_reward_reconciliation"]
        self.assertGreater(reconciliation["raw_event_reward_count"], 0)
        self.assertEqual(reconciliation["raw_event_reward_count"], reconciliation["canonical_task_reward_count"])
        self.assertEqual(reconciliation["raw_event_reward_total"], reconciliation["canonical_task_reward_total"])
        self.assertTrue(reconciliation["reward_reconciled"])
        self.assertEqual(result["canonical_reward_decomposition"]["reward_available_count"], 2)

    def test_pending_tasks_are_not_counted_as_reward_bearing_tasks(self) -> None:
        result = build_canonical_task_reconciliation(
            checkpoint_budget=200,
            evaluation_decision_count=3,
            task_records=_task_records(),
        )
        overall = result["canonical_task_outcome_summary"]["overall"]
        self.assertEqual(overall["canonical_pending_count"], 1)
        self.assertEqual(overall["canonical_task_reward_count"], 2)
        self.assertEqual(overall["raw_reward_event_count"], 2)


if __name__ == "__main__":
    unittest.main()
