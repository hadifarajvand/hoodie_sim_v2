from __future__ import annotations

import unittest

from src.evaluation.policy_registry import PolicyRegistry
from src.policies import PolicyContext


class BaselinePolicyFidelityFlowTests(unittest.TestCase):
    def test_legacy_family_fallback_remains_available(self) -> None:
        policies = {name: PolicyRegistry.resolve(name) for name in ("FLC", "VO", "HO", "RO", "BCO", "MLEO")}
        context = PolicyContext(
            observation={"fallback_hints": {"local": 1.0, "horizontal": 2.0, "vertical": 3.0}},
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
        )

        self.assertEqual(policies["FLC"].choose_action(context), "local")
        self.assertEqual(policies["VO"].choose_action(context), "vertical")
        self.assertIn(policies["HO"].choose_action(context), {"horizontal", "offload_horizontal"})
        self.assertIn(policies["RO"].choose_action(context), {"local", "horizontal", "vertical"})
        self.assertIn(policies["BCO"].choose_action(context), {"local", "horizontal", "vertical"})
        self.assertIn(policies["MLEO"].choose_action(context), {"local", "horizontal", "vertical"})


if __name__ == "__main__":
    unittest.main()
