from __future__ import annotations

import unittest

from src.environment.evaluation_gym_adapter import EvaluationHoodieGymEnvironment
from src.evaluation.trace_protocol import build_deterministic_trace, trace_signature


class PaperTraceProtocolTests(unittest.TestCase):
    def test_each_ea_has_an_independent_arrival_opportunity_per_decision_slot(self) -> None:
        trace = build_deterministic_trace(
            "all-arrivals",
            seed=7,
            episode_length=5,
            agent_count=3,
            arrival_probability=1.0,
            timeout_length=2,
            drain_slots=2,
        )

        self.assertEqual(len(trace.tasks), 9)
        self.assertEqual({task.arrival_slot for task in trace.tasks}, {0, 1, 2})
        for slot in (0, 1, 2):
            self.assertEqual(
                {task.source_agent_id for task in trace.tasks if task.arrival_slot == slot},
                {1, 2, 3},
            )
        self.assertFalse(any(task.arrival_slot >= 3 for task in trace.tasks))

    def test_trace_is_reproducible_and_signature_preserves_horizon(self) -> None:
        first = build_deterministic_trace(
            "paired",
            seed=11,
            episode_length=110,
            agent_count=20,
            arrival_probability=0.5,
            timeout_length=20,
            drain_slots=10,
        )
        second = build_deterministic_trace(
            "paired",
            seed=11,
            episode_length=110,
            agent_count=20,
            arrival_probability=0.5,
            timeout_length=20,
            drain_slots=10,
        )

        self.assertEqual(first, second)
        signature = trace_signature(first)
        self.assertEqual(signature["episode_length"], 110)
        self.assertEqual(signature["decision_slots"], 100)
        self.assertEqual(signature["drain_slots"], 10)
        self.assertEqual(signature["task_count"], len(first.tasks))

    def test_evaluation_environment_uses_the_supplied_trace(self) -> None:
        trace = build_deterministic_trace(
            "injected",
            seed=3,
            episode_length=4,
            agent_count=1,
            arrival_probability=1.0,
            timeout_length=2,
            drain_slots=3,
        )
        env = EvaluationHoodieGymEnvironment(
            episode_length=4,
            policy_name="FLC",
            supplied_trace=trace,
        )

        env.reset(seed=999)

        self.assertIs(env.trace, trace)
        self.assertIsNotNone(env.current_task)
        self.assertEqual(env.current_task.task_id, trace.tasks[0].task_id)
        self.assertEqual(env.current_task.arrival_slot, 0)


if __name__ == "__main__":
    unittest.main()
