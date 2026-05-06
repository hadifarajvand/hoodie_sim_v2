from __future__ import annotations

import unittest

from src.policies.adaptive_offloading import AdaptiveOffloadingPolicy
from src.policies.policy_interface import PolicyContext


class AdaptiveOffloadingPolicyTests(unittest.TestCase):
    def _context(
        self,
        *,
        legal_action_mask: dict[str, bool],
        queue_load: int = 0,
        observed_arrival_probability: float | None = None,
        latency_estimates: dict[str, float] | None = None,
        balance_hint: dict[str, float] | None = None,
        cycles_remaining: float = 0.6237,
        cycles_required: float = 0.6237,
        current_slot: int = 4,
        deadline: int = 24,
    ) -> PolicyContext:
        observation: dict[str, object] = {
            "slot": current_slot,
            "queue_load": queue_load,
            "task_id": 17,
            "source_agent_id": 1,
            "size": 2.1,
            "processing_density": 0.297,
            "cycles_required": cycles_required,
            "cycles_remaining": cycles_remaining,
            "timeout_length": 20,
            "absolute_deadline_slot": deadline,
            "legal_action_mask": legal_action_mask,
            "fallback_hints": {"local": 1.0, "horizontal": 2.0, "vertical": 3.0},
        }
        if observed_arrival_probability is not None:
            observation["traffic_summary"] = {"observed_arrival_probability": observed_arrival_probability}
        if latency_estimates is not None:
            observation["latency_estimates"] = latency_estimates
        if balance_hint is not None:
            observation["balance_hint"] = balance_hint
        return PolicyContext(observation=observation, legal_action_mask=legal_action_mask)

    def test_local_only_topology_returns_local(self) -> None:
        policy = AdaptiveOffloadingPolicy()
        context = self._context(legal_action_mask={"local": True, "compute_local": True})

        self.assertEqual(policy.choose_action(context), "local")

    def test_horizontal_legal_vertical_illegal_with_high_load_prefers_horizontal(self) -> None:
        policy = AdaptiveOffloadingPolicy()
        context = self._context(
            legal_action_mask={"local": False, "horizontal": True, "vertical": False},
            queue_load=4,
            observed_arrival_probability=0.9,
        )

        self.assertEqual(policy.choose_action(context), "horizontal")

    def test_vertical_legal_horizontal_illegal_with_high_load_prefers_vertical(self) -> None:
        policy = AdaptiveOffloadingPolicy()
        context = self._context(
            legal_action_mask={"local": False, "horizontal": False, "vertical": True},
            queue_load=4,
            observed_arrival_probability=0.9,
        )

        self.assertEqual(policy.choose_action(context), "vertical")

    def test_all_actions_legal_low_load_prefers_local(self) -> None:
        policy = AdaptiveOffloadingPolicy()
        context = self._context(
            legal_action_mask={"local": True, "compute_local": True, "horizontal": True, "vertical": True},
            queue_load=0,
            observed_arrival_probability=0.1,
        )

        self.assertEqual(policy.choose_action(context), "local")

    def test_all_actions_legal_high_load_prefers_horizontal(self) -> None:
        policy = AdaptiveOffloadingPolicy()
        context = self._context(
            legal_action_mask={"local": True, "compute_local": True, "horizontal": True, "vertical": True},
            queue_load=5,
            observed_arrival_probability=0.9,
        )

        self.assertEqual(policy.choose_action(context), "horizontal")

    def test_missing_adaptive_fields_falls_back_to_canonical_order(self) -> None:
        policy = AdaptiveOffloadingPolicy()
        context = PolicyContext(
            observation={"task_id": 1, "slot": 0},
            legal_action_mask={"local": True, "compute_local": True, "horizontal": True, "vertical": True},
        )

        self.assertEqual(policy.choose_action(context), "local")

    def test_deterministic_repeated_calls(self) -> None:
        policy = AdaptiveOffloadingPolicy()
        context = self._context(
            legal_action_mask={"local": True, "compute_local": True, "horizontal": True, "vertical": True},
            queue_load=3,
            observed_arrival_probability=0.75,
            latency_estimates={"local": 3.0, "horizontal": 1.0, "vertical": 2.0},
            balance_hint={"local": 3.0, "horizontal": 1.0, "vertical": 2.0},
        )

        actions = [policy.choose_action(context) for _ in range(5)]

        self.assertEqual(actions, ["horizontal"] * 5)

    def test_legal_actions_only_never_returns_illegal_choice(self) -> None:
        policy = AdaptiveOffloadingPolicy()
        context = self._context(
            legal_action_mask={"local": False, "compute_local": False, "horizontal": True, "vertical": False},
            queue_load=5,
            observed_arrival_probability=0.9,
        )

        self.assertEqual(policy.choose_action(context), "horizontal")


if __name__ == "__main__":
    unittest.main()
