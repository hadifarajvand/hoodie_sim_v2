from __future__ import annotations

import unittest

from src.analysis.hoodie_runtime_evaluation_runner.config import POLICY_CLOUD_ONLY, POLICY_HOODIE_PROPOSED, POLICY_LOCAL_ONLY, POLICY_ORIGINAL_HOODIE_BASELINE, POLICY_RANDOM_POLICY
from src.analysis.hoodie_runtime_evaluation_runner.policies import build_policy_adapter
from src.policies.policy_interface import PolicyContext


class HoodieRuntimeEvaluationRunnerPolicyTests(unittest.TestCase):
    def _context(self) -> PolicyContext:
        return PolicyContext(
            observation={
                "task_id": "task-1",
                "source_agent_id": "1",
                "candidate_actions": ("local", "horizontal", "vertical"),
                "legal_horizontal_destinations": ("6",),
                "illegal_horizontal_destinations": ("2",),
                "cloud_available": True,
                "placement_actions": {"local": ("local",), "horizontal": ("6",), "vertical": ("vertical",), "cloud": ("vertical",)},
                "mleo_delay_candidates": {
                    "local": {"action_id": "local", "action_family": "local", "total_delay": 10.0, "available": True},
                    "horizontal": {"action_id": "6", "action_family": "horizontal", "total_delay": 4.0, "available": True},
                    "vertical": {"action_id": "vertical", "action_family": "vertical", "total_delay": 6.0, "available": True},
                },
                "latency_estimates": {"local": 10.0, "horizontal": 4.0, "vertical": 6.0},
                "queue_history": (1, 2, 3),
            },
            legal_action_mask={
                "local": True,
                "compute_local": True,
                "horizontal": True,
                "offload_horizontal": True,
                "vertical": True,
                "offload_vertical": True,
            },
            trace_history=("scenario", "low", "tight", "7"),
        )

    def test_compatibility_policies_are_annotated(self) -> None:
        self.assertTrue(build_policy_adapter(POLICY_HOODIE_PROPOSED).compatibility_mode_used)
        self.assertTrue(build_policy_adapter(POLICY_ORIGINAL_HOODIE_BASELINE).compatibility_mode_used)
        self.assertFalse(build_policy_adapter(POLICY_RANDOM_POLICY).compatibility_mode_used)
        self.assertFalse(build_policy_adapter(POLICY_LOCAL_ONLY).compatibility_mode_used)
        self.assertFalse(build_policy_adapter(POLICY_CLOUD_ONLY).compatibility_mode_used)

    def test_direct_policies_choose_primary_actions(self) -> None:
        self.assertEqual(build_policy_adapter(POLICY_LOCAL_ONLY).choose_action(self._context()), "local")
        self.assertEqual(build_policy_adapter(POLICY_CLOUD_ONLY).choose_action(self._context()), "vertical")

    def test_random_policy_is_seeded(self) -> None:
        context = self._context()
        first = build_policy_adapter(POLICY_RANDOM_POLICY, seed=11).choose_action(context)
        second = build_policy_adapter(POLICY_RANDOM_POLICY, seed=11).choose_action(context)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
