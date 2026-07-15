from __future__ import annotations

import unittest

from src.evaluation.paired_evaluation import TaskRecord, paired_metric_summary, validate_fairness


class PairedEvaluationTests(unittest.TestCase):
    def test_task_record_schema_and_provenance(self) -> None:
        record = TaskRecord(
            campaign_id="campaign-1",
            run_id="run-1",
            policy="HOODIE",
            seed=7,
            trace_hash="trace-hash",
            task_id="task-1",
            source_agent="1",
            arrival_slot=2,
            decision_slot=3,
            selected_action="local",
            destination="private",
            completion_or_drop_slot=5,
            outcome="completed",
            end_to_end_delay=3.0,
            queue_delay=1.0,
            transmission_delay=0.5,
            service_delay=1.5,
            reward=1.0,
            learner_owner="agent-1",
            checkpoint_hash="checkpoint-hash",
            configuration_hash="config-hash",
        )
        self.assertEqual(record.policy, "HOODIE")
        self.assertEqual(record.task_id, "task-1")
        self.assertEqual(record.checkpoint_hash, "checkpoint-hash")

    def test_paired_metrics_deterministic(self) -> None:
        records = [
            TaskRecord("c", "r", "p", 1, "trace", "t1", "a", 1, 2, "local", "dest", 3, "completed", 2.0, 0.5, 0.2, 1.3, 1.0, "owner", "chk", "cfg"),
            TaskRecord("c", "r", "p", 1, "trace", "t2", "a", 2, 3, "horizontal", "dest", None, "dropped", None, None, None, None, -1.0, "owner", "chk", "cfg"),
        ]
        first = paired_metric_summary(records)
        second = paired_metric_summary(records)
        self.assertEqual(first, second)
        self.assertEqual(first.offered_tasks, 2)
        self.assertEqual(first.completed_tasks, 1)
        self.assertEqual(first.dropped_tasks, 1)

    def test_validate_fairness_rejects_changed_inputs(self) -> None:
        reference = {
            "trace_hash": "trace",
            "offered_tasks": 2,
            "task_ids": ["t1", "t2"],
            "topology_hash": "topology",
            "physical_configuration": "physical",
            "horizon": 10,
            "seed_set": [1, 2],
            "metric_denominator": 2,
            "warmup_handling": "same",
            "checkpoint_selection_rule": "same",
        }
        with self.assertRaises(ValueError):
            validate_fairness(reference, {**reference, "trace_hash": "other"})
        with self.assertRaises(ValueError):
            validate_fairness(reference, {**reference, "topology_hash": "changed"})
        with self.assertRaises(ValueError):
            validate_fairness(reference, {**reference, "seed_set": [1, 3]})


if __name__ == "__main__":
    unittest.main()
