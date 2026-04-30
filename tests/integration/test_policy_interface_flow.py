from __future__ import annotations

import unittest

from src.environment.environment import apply_policy_action
from src.environment.task import Task
from src.policies.action_masking import build_legal_action_mask
from src.policies.policy_interface import PolicyContext, SharedPolicy


class DummyPolicy:
    def choose_action(self, context: PolicyContext) -> str:
        self.last_context = context
        return "local"


class PolicyInterfaceFlowTests(unittest.TestCase):
    def test_policy_context_exposes_only_inputs_and_environment_mutates_task(self) -> None:
        policy = DummyPolicy()
        task = Task(1, 1, 0, 10, 1, 3, 3)
        context = PolicyContext(
            observation={"task_id": task.task_id},
            legal_action_mask=build_legal_action_mask(("local", "offload")),
            trace_history=("slot-1",),
        )

        action = policy.choose_action(context)

        self.assertIsInstance(policy, SharedPolicy)
        self.assertEqual(action, "local")
        self.assertIsNone(task.selected_action)
        self.assertIsNone(task.resolved_destination)

        selected_action = apply_policy_action(task, context, action, resolved_destination="self")

        self.assertEqual(selected_action, "local")
        self.assertEqual(task.selected_action, "local")
        self.assertEqual(task.resolved_destination, "self")
        self.assertEqual(policy.last_context.legal_action_mask, {"local": True, "offload": True})
        self.assertEqual(policy.last_context.trace_history, ("slot-1",))


if __name__ == "__main__":
    unittest.main()
