from __future__ import annotations

import unittest

from src.policies.action_masking import build_legal_action_mask, select_legal_action
from src.policies.policy_interface import PolicyContext


class ActionMaskingTests(unittest.TestCase):
    def test_build_legal_action_mask_marks_allowed_actions_only(self) -> None:
        mask = build_legal_action_mask(("local", "horizontal"))

        self.assertEqual(mask, {"local": True, "horizontal": True})
        self.assertNotIn("vertical", mask)

    def test_select_legal_action_rejects_illegal_action_without_remapping(self) -> None:
        context = PolicyContext(
            observation={"task_id": 1},
            legal_action_mask={"local": True, "horizontal": False, "vertical": False},
            trace_history=("slot-0",),
        )

        self.assertEqual(select_legal_action(context, "local"), "local")
        with self.assertRaises(ValueError):
            select_legal_action(context, "horizontal")
        with self.assertRaises(ValueError):
            select_legal_action(context, "vertical")


if __name__ == "__main__":
    unittest.main()
