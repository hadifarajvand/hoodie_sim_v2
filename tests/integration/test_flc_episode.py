from __future__ import annotations

import unittest

from src.environment.environment import apply_policy_action
from src.environment.task import Task
from src.policies import FullLocalComputingPolicy, PolicyContext, build_legal_action_mask


class FLCIntegrationTests(unittest.TestCase):
    def test_flc_runs_through_shared_environment_path(self) -> None:
        policy = FullLocalComputingPolicy()
        task = Task(1, 1, 0, 10, 1, 3, 3)
        context = PolicyContext(
            observation={"task_id": task.task_id},
            legal_action_mask=build_legal_action_mask(("local", "horizontal", "vertical")),
            trace_history=("slot-0",),
        )

        action = policy.choose_action(context)
        apply_policy_action(task, context, action, resolved_destination="self")

        self.assertEqual(action, "local")
        self.assertEqual(task.selected_action, "local")
        self.assertEqual(task.resolved_destination, "self")


if __name__ == "__main__":
    unittest.main()
