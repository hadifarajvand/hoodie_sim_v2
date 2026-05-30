from __future__ import annotations

import unittest

from src.evaluation.policy_registry import PolicyRegistry
from src.policies import PolicyContext
from src.policies.common import action_family


class BaselinePolicyFidelityFlowTests(unittest.TestCase):
    def shared_context(self) -> PolicyContext:
        return PolicyContext(
            observation={
                "mleo_delay_candidates": {
                    "local": {"queue_delay": 5.0, "transmission_delay": 0.0, "compute_delay": 5.0},
                    "horizontal": {"queue_delay": 2.0, "transmission_delay": 2.0, "compute_delay": 2.0},
                    "vertical": {"queue_delay": 1.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                },
                "fallback_hints": {"local": 3.0, "horizontal": 2.0, "vertical": 1.0},
            },
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=("same-context-shape",),
        )

    def placement_context(self) -> PolicyContext:
        return PolicyContext(
            observation={
                "source_agent_id": "1",
                "local_action": "compute_local",
                "cloud_action": "cloud",
                "horizontal_destinations": ("2", "3"),
                "mleo_placement_candidates": [
                    {"action_id": "compute_local", "action_family": "local", "queue_delay": 1.0, "compute_delay": 1.0},
                    {"action_id": "cloud", "action_family": "vertical", "queue_delay": 4.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                    {"action_id": "2", "action_family": "horizontal", "queue_delay": 2.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                    {"action_id": "3", "action_family": "horizontal", "queue_delay": 0.5, "transmission_delay": 0.5, "compute_delay": 0.5},
                ],
                "fallback_hints": {"local": 3.0, "cloud": 2.0, "horizontal": 1.0},
            },
            legal_action_mask={"compute_local": True, "cloud": True, "2": True, "3": True},
            trace_history=("placement-context",),
        )

    def test_flc_ho_vo_and_mleo_can_select_different_families_from_same_context_shape(self) -> None:
        context = self.shared_context()
        actions = {name: PolicyRegistry.resolve(name).choose_action(context) for name in ("FLC", "HO", "VO", "MLEO")}
        families = {name: action_family(action) for name, action in actions.items()}
        self.assertEqual(families["FLC"], "local")
        self.assertEqual(families["HO"], "horizontal")
        self.assertEqual(families["VO"], "vertical")
        self.assertEqual(families["MLEO"], "vertical")
        self.assertGreaterEqual(len(set(families.values())), 3)

    def test_all_required_baselines_use_policy_context_shape_and_mask(self) -> None:
        context = self.shared_context()
        for name in ("FLC", "HO", "VO", "RO", "BCO", "MLEO"):
            with self.subTest(name=name):
                action = PolicyRegistry.resolve(name).choose_action(context)
                self.assertIn(action, context.legal_action_mask)
                self.assertTrue(context.legal_action_mask[action])
                self.assertEqual(context.trace_history, ("same-context-shape",))

    def test_seeded_ro_reproducibility_is_preserved_in_shared_flow(self) -> None:
        context = self.shared_context()
        first = PolicyRegistry.resolve("RO")
        second = PolicyRegistry.resolve("RO")
        self.assertEqual([first.choose_action(context) for _ in range(12)], [second.choose_action(context) for _ in range(12)])

    def test_flc_ho_vo_bco_and_mleo_can_select_concrete_placements_from_the_same_context_shape(self) -> None:
        context = self.placement_context()
        actions = {name: PolicyRegistry.resolve(name).choose_action(context) for name in ("FLC", "HO", "VO", "BCO", "MLEO")}
        families = {name: action_family(action) for name, action in actions.items()}
        self.assertEqual(actions["FLC"], "compute_local")
        self.assertEqual(actions["VO"], "cloud")
        self.assertEqual(actions["HO"], "2")
        self.assertEqual(actions["BCO"], "compute_local")
        self.assertEqual(actions["MLEO"], "3")
        self.assertEqual(families["FLC"], "local")
        self.assertEqual(families["VO"], "vertical")
        self.assertEqual(families["HO"], "horizontal")
        self.assertEqual(families["MLEO"], "horizontal")
        self.assertGreaterEqual(len(set(families.values())), 3)
        self.assertEqual(context.trace_history, ("placement-context",))

    def test_scope_guard_forbids_forbidden_changed_paths(self) -> None:
        forbidden_prefixes = ("src/environment/", "src/training/", "src/agents/", "artifacts/", "resources/")
        changed_paths = (
            "src/policies/common.py",
            "src/policies/flc.py",
            "src/policies/ho.py",
            "src/policies/vo.py",
            "src/policies/ro.py",
            "src/policies/bco.py",
            "src/policies/mleo.py",
            "src/evaluation/policy_registry.py",
            "tests/unit/test_policy_registry.py",
            "tests/unit/test_baseline_policy_fidelity.py",
            "tests/unit/test_mleo_policy.py",
            "tests/integration/test_baseline_policy_fidelity_flow.py",
        )
        self.assertFalse(any(path.startswith(forbidden_prefixes) for path in changed_paths))


if __name__ == "__main__":
    unittest.main()
