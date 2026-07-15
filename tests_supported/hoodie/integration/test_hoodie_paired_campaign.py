from __future__ import annotations

import unittest

from src.evaluation.paired_evaluation import TaskRecord, paired_metric_summary, validate_fairness


class HoodiePairedCampaignIntegrationTests(unittest.TestCase):
    def test_independent_records_aggregate_deterministically(self) -> None:
        records = [
            TaskRecord("campaign", "run-a", "policy-a", 11, "trace-a", "task-1", "src-1", 1, 2, "local", "dest-1", 4, "completed", 3.0, 1.0, 0.5, 1.5, 2.0, "owner-1", "chk-a", "cfg-a"),
            TaskRecord("campaign", "run-b", "policy-b", 11, "trace-a", "task-2", "src-1", 2, 3, "vertical", "dest-2", None, "dropped", None, None, None, None, -1.0, "owner-1", "chk-b", "cfg-a"),
        ]
        summary = paired_metric_summary(records)
        self.assertEqual(summary.offered_tasks, 2)
        self.assertEqual(summary.completed_tasks, 1)
        self.assertEqual(summary.dropped_tasks, 1)
        self.assertEqual(summary.action_distribution, {"local": 1, "vertical": 1})
        self.assertEqual(summary.per_agent_metrics["src-1"]["tasks"], 2.0)

    def test_fairness_rejects_trace_mutation(self) -> None:
        reference = {
            "trace_hash": "trace-a",
            "offered_tasks": 2,
            "task_ids": ["task-1", "task-2"],
            "topology_hash": "topology-a",
            "physical_configuration": "physical-a",
            "horizon": 10,
            "seed_set": [11],
            "metric_denominator": 2,
            "warmup_handling": "same",
            "checkpoint_selection_rule": "same",
        }
        with self.assertRaises(ValueError):
            validate_fairness(reference, {**reference, "task_ids": ["task-1", "task-x"]})


if __name__ == "__main__":
    unittest.main()
