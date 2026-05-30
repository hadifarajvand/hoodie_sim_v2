from __future__ import annotations

import unittest

from src.evaluation.policy_registry import PolicyRegistry
from src.policies import PolicyContext
from src.policies.common import action_family


class BaselinePolicyFidelityTests(unittest.TestCase):
    def context(self, mask: dict[str, bool], observation: dict[str, object] | None = None) -> PolicyContext:
        return PolicyContext(observation=observation or {}, legal_action_mask=mask, trace_history=("shared",))

    def test_flc_prefers_local_when_available(self) -> None:
        policy = PolicyRegistry.resolve("FLC")
        context = self.context({"local": True, "horizontal": True, "vertical": True})
        self.assertEqual(policy.choose_action(context), "local")

    def test_flc_falls_back_when_local_is_unavailable(self) -> None:
        policy = PolicyRegistry.resolve("FLC")
        context = self.context({"local": False, "horizontal": True, "vertical": True})
        action = policy.choose_action(context)
        self.assertEqual(action, "horizontal")
        self.assertTrue(context.legal_action_mask[action])

    def test_vo_prefers_vertical_and_falls_back_when_unavailable(self) -> None:
        policy = PolicyRegistry.resolve("VO")
        preferred = self.context({"local": True, "horizontal": True, "vertical": True})
        fallback = self.context({"local": True, "horizontal": True, "vertical": False})
        self.assertEqual(policy.choose_action(preferred), "vertical")
        self.assertEqual(policy.choose_action(fallback), "local")

    def test_ho_prefers_horizontal_and_falls_back_when_unavailable(self) -> None:
        policy = PolicyRegistry.resolve("HO")
        preferred = self.context({"local": True, "horizontal": True, "vertical": True})
        fallback = self.context({"local": True, "horizontal": False, "vertical": True})
        self.assertEqual(policy.choose_action(preferred), "horizontal")
        self.assertEqual(policy.choose_action(fallback), "local")

    def test_ho_falls_back_when_horizontal_family_exists_without_destination(self) -> None:
        policy = PolicyRegistry.resolve("HO")
        context = self.context(
            {"local": True, "horizontal": False, "offload_horizontal": False, "vertical": True},
            {"horizontal_destinations": ()},
        )
        self.assertEqual(policy.choose_action(context), "local")

    def test_flc_prefers_concrete_local_action_when_available(self) -> None:
        policy = PolicyRegistry.resolve("FLC")
        context = self.context(
            {"compute_local": True, "cloud": False, "2": False},
            {"local_action": "compute_local"},
        )
        self.assertEqual(policy.choose_action(context), "compute_local")

    def test_vo_prefers_concrete_cloud_action_when_available(self) -> None:
        policy = PolicyRegistry.resolve("VO")
        context = self.context(
            {"cloud": True, "local": True, "2": True},
            {"cloud_action": "cloud"},
        )
        self.assertEqual(policy.choose_action(context), "cloud")

    def test_ho_prefers_concrete_horizontal_destination_when_available(self) -> None:
        policy = PolicyRegistry.resolve("HO")
        context = self.context(
            {"local": True, "2": True, "3": True},
            {"source_agent_id": "1", "horizontal_destinations": ("1", "2", "3")},
        )
        action = policy.choose_action(context)
        self.assertEqual(action, "2")
        self.assertNotEqual(action, "1")

    def test_ro_seeded_sampling_is_reproducible_and_legal(self) -> None:
        first = PolicyRegistry.resolve("RO")
        second = PolicyRegistry.resolve("RO")
        context = self.context({"local": True, "horizontal": False, "vertical": True})
        first_actions = [first.choose_action(context) for _ in range(8)]
        second_actions = [second.choose_action(context) for _ in range(8)]
        self.assertEqual(first_actions, second_actions)
        self.assertTrue(all(context.legal_action_mask[action] for action in first_actions))

    def test_ro_single_action_mask_always_returns_that_action(self) -> None:
        policy = PolicyRegistry.resolve("RO")
        context = self.context({"local": False, "horizontal": False, "vertical": True})
        self.assertEqual([policy.choose_action(context) for _ in range(5)], ["vertical"] * 5)

    def test_ro_concrete_horizontal_destinations_are_sampled_reproducibly(self) -> None:
        first = PolicyRegistry.resolve("RO")
        second = PolicyRegistry.resolve("RO")
        context = self.context(
            {"2": True, "3": True},
            {"source_agent_id": "1", "horizontal_destinations": ("2", "3")},
        )
        first_actions = [first.choose_action(context) for _ in range(8)]
        second_actions = [second.choose_action(context) for _ in range(8)]
        self.assertEqual(first_actions, second_actions)
        self.assertTrue(all(action in {"2", "3"} for action in first_actions))

    def test_bco_uses_balance_hint_before_rollover(self) -> None:
        policy = PolicyRegistry.resolve("BCO")
        context = self.context(
            {"local": True, "horizontal": True, "vertical": True},
            {"balance_hint": {"local": 3.0, "horizontal": 1.0, "vertical": 2.0}},
        )
        self.assertEqual(policy.choose_action(context), "horizontal")

    def test_bco_rotates_over_concrete_placements_in_paper_order(self) -> None:
        policy = PolicyRegistry.resolve("BCO")
        context = self.context(
            {"compute_local": True, "cloud": True, "2": True, "3": True},
            {"local_action": "compute_local", "cloud_action": "cloud", "horizontal_destinations": ("2", "3")},
        )
        self.assertEqual([policy.choose_action(context) for _ in range(5)], ["compute_local", "cloud", "2", "3", "compute_local"])

    def test_bco_rollover_is_deterministic_and_mask_compliant(self) -> None:
        policy = PolicyRegistry.resolve("BCO")
        context = self.context({"local": True, "horizontal": True, "vertical": True})
        self.assertEqual([policy.choose_action(context) for _ in range(5)], ["local", "horizontal", "vertical", "local", "horizontal"])

    def test_bco_rollover_skips_unavailable_families(self) -> None:
        policy = PolicyRegistry.resolve("BCO")
        context = self.context({"local": False, "horizontal": True, "vertical": True})
        actions = [policy.choose_action(context) for _ in range(4)]
        self.assertEqual(actions, ["horizontal", "vertical", "horizontal", "vertical"])
        self.assertTrue(all(context.legal_action_mask[action] for action in actions))

    def test_every_baseline_returns_only_legal_actions_when_preferred_family_is_disabled(self) -> None:
        cases = {
            "FLC": self.context({"local": False, "horizontal": True, "vertical": False}),
            "VO": self.context({"local": True, "horizontal": True, "vertical": False}),
            "HO": self.context({"local": True, "horizontal": False, "vertical": True}),
            "RO": self.context({"local": False, "horizontal": True, "vertical": False}),
            "BCO": self.context({"local": False, "horizontal": True, "vertical": False}),
            "MLEO": self.context(
                {"local": False, "horizontal": True, "vertical": True},
                {
                    "mleo_delay_candidates": {
                        "local": {"total_delay": 1.0},
                        "horizontal": {"total_delay": 2.0},
                        "vertical": {"total_delay": 3.0},
                    }
                },
            ),
        }
        for name, context in cases.items():
            with self.subTest(name=name):
                action = PolicyRegistry.resolve(name).choose_action(context)
                self.assertTrue(context.legal_action_mask[action])
                if name in {"FLC", "VO", "HO"}:
                    disabled_family = {"FLC": "local", "VO": "vertical", "HO": "horizontal"}[name]
                    self.assertNotEqual(action_family(action), disabled_family)

    def test_no_legal_action_reports_no_choice(self) -> None:
        for name in ("FLC", "VO", "HO", "RO", "BCO", "MLEO"):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "No legal actions available"):
                    PolicyRegistry.resolve(name).choose_action(self.context({"local": False, "horizontal": False, "vertical": False}))


if __name__ == "__main__":
    unittest.main()
