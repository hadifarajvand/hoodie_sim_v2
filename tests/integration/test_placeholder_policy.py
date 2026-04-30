from __future__ import annotations

import unittest

from src.environment.environment import apply_policy_action
from src.environment.task import Task
from src.policies import PolicyContext, SharedPolicy, build_legal_action_mask


class PlaceholderPolicy:
    def choose_action(self, context: PolicyContext) -> str:
        self.seen_context = context
        return "local"


class PlaceholderPolicyTests(unittest.TestCase):
    def test_placeholder_policy_uses_shared_interface_path(self) -> None:
        policy = PlaceholderPolicy()
        task = Task(2, 2, 0, 12, 2, 4, 4)
        context = PolicyContext(
            observation={"task_id": task.task_id, "kind": "stub"},
            legal_action_mask=build_legal_action_mask(("local", "horizontal")),
            trace_history=("trace-a",),
        )

        action = policy.choose_action(context)
        apply_policy_action(task, context, action, resolved_destination="self")

        self.assertIsInstance(policy, SharedPolicy)
        self.assertEqual(action, "local")
        self.assertEqual(task.selected_action, "local")
        self.assertEqual(policy.seen_context.observation["kind"], "stub")
        self.assertEqual(policy.seen_context.trace_history, ("trace-a",))


if __name__ == "__main__":
    unittest.main()
