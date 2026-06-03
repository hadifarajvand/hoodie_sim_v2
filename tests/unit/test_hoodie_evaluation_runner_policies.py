from __future__ import annotations

import unittest

from src.analysis.hoodie_evaluation_runner.config import (
    POLICY_CLOUD_ONLY,
    POLICY_HOODIE_PROPOSED,
    POLICY_LOCAL_ONLY,
    POLICY_ORIGINAL_HOODIE_BASELINE,
    POLICY_RANDOM,
)
from src.analysis.hoodie_evaluation_runner.policies import build_policy_adapter
from src.policies.policy_interface import PolicyContext


class HoodieEvaluationRunnerPolicyTests(unittest.TestCase):
    def _context(self) -> PolicyContext:
        return PolicyContext(
            observation={
                "scenario_name": "mixed_local_horizontal_cloud_candidates",
                "workload": "medium",
                "deadline_pressure": "moderate",
                "fallback_hints": {"local": 1.0, "horizontal": 2.0, "vertical": 0.5},
                "queue_hints": {"local": 0.0, "horizontal": 1.0, "vertical": 2.0},
                "delay_hints": {"local": 3.0, "horizontal": 2.0, "vertical": 1.0},
                "reward_hints": {"local": -3.0, "horizontal": -2.0, "vertical": -1.0},
                "queue_load": 1.0,
                "task_id": "task-1",
            },
            legal_action_mask={
                "local": True,
                "compute_local": True,
                "horizontal": True,
                "offload_horizontal": True,
                "vertical": True,
                "offload_vertical": True,
            },
            trace_history=("trace",),
        )

    def test_local_and_cloud_only_adapters_attempt_primary_action(self) -> None:
        context = self._context()
        self.assertEqual(build_policy_adapter(POLICY_LOCAL_ONLY).choose_action(context), "local")
        self.assertEqual(build_policy_adapter(POLICY_CLOUD_ONLY).choose_action(context), "vertical")

    def test_seeded_random_policy_is_deterministic(self) -> None:
        context = self._context()
        first = build_policy_adapter(POLICY_RANDOM, seed=11).choose_action(context)
        second = build_policy_adapter(POLICY_RANDOM, seed=11).choose_action(context)
        self.assertEqual(first, second)
        self.assertIn(first, {"local", "horizontal", "vertical", "compute_local", "offload_horizontal", "offload_vertical"})

    def test_original_and_proposed_adapters_return_legal_actions(self) -> None:
        context = self._context()
        original = build_policy_adapter(POLICY_ORIGINAL_HOODIE_BASELINE).choose_action(context)
        proposed = build_policy_adapter(POLICY_HOODIE_PROPOSED).choose_action(context)
        self.assertTrue(context.legal_action_mask[original])
        self.assertTrue(context.legal_action_mask[proposed])

    def test_unknown_policy_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_policy_adapter("UNKNOWN")


if __name__ == "__main__":
    unittest.main()
