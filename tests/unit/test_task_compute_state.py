from __future__ import annotations

import unittest

from src.evaluation.trace_protocol import TraceTaskBlueprint
from src.environment.task import Task


class TaskComputeStateTests(unittest.TestCase):
    def test_task_construction_derives_cycles_from_fractional_paper_values(self) -> None:
        task = Task(
            task_id=1,
            source_agent_id=2,
            arrival_slot=3,
            size=2.1,
            processing_density=0.297,
            timeout_length=20,
            absolute_deadline_slot=23,
        )

        self.assertAlmostEqual(task.cycles_required, 2.1 * 0.297)
        self.assertAlmostEqual(task.cycles_remaining, 2.1 * 0.297)
        self.assertIsInstance(task.cycles_required, float)
        self.assertIsInstance(task.cycles_remaining, float)

    def test_task_construction_preserves_explicit_cycles(self) -> None:
        task = Task(
            task_id=7,
            source_agent_id=5,
            arrival_slot=1,
            size=10.0,
            processing_density=1.0,
            timeout_length=4,
            absolute_deadline_slot=5,
            cycles_required=10.0,
            cycles_remaining=4.5,
        )

        self.assertEqual(task.cycles_required, 10.0)
        self.assertEqual(task.cycles_remaining, 4.5)

    def test_trace_blueprint_build_carries_compute_state(self) -> None:
        blueprint = TraceTaskBlueprint(
            task_id=3,
            source_agent_id=4,
            arrival_slot=0,
            size=2.1,
            processing_density=0.297,
            timeout_length=20,
            absolute_deadline_slot=20,
        )

        task = blueprint.build()

        self.assertAlmostEqual(task.cycles_required, 2.1 * 0.297)
        self.assertAlmostEqual(task.cycles_remaining, 2.1 * 0.297)


if __name__ == "__main__":
    unittest.main()
