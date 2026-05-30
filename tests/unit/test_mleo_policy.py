from __future__ import annotations

import unittest

from src.policies import MinimumLatencyEstimateOffloadingPolicy, PolicyContext


class MinimumLatencyEstimateOffloadingPolicyTests(unittest.TestCase):
    def test_ranks_n_plus_one_candidates_by_delay(self) -> None:
        policy = MinimumLatencyEstimateOffloadingPolicy()
        context = PolicyContext(
            observation={
                "source_agent_id": "1",
                "mleo_placement_candidates": {
                    "local": ["local"],
                    "horizontal": ["2", "3"],
                    "vertical": ["cloud"],
                },
                "queue_delay_estimates": {
                    "local": 3.0,
                    "2": 1.5,
                    "3": 2.0,
                    "cloud": 4.0,
                },
            },
            legal_action_mask={"local": True, "2": True, "3": True, "cloud": True},
        )

        self.assertEqual(policy.choose_action(context), "2")
        self.assertIsNone(policy.last_fallback_reason)

    def test_excludes_unavailable_candidates_before_ranking(self) -> None:
        policy = MinimumLatencyEstimateOffloadingPolicy()
        context = PolicyContext(
            observation={
                "source_agent_id": "1",
                "mleo_placement_candidates": {
                    "local": ["local"],
                    "horizontal": ["2", "3"],
                    "vertical": ["cloud"],
                },
                "queue_delay_estimates": {
                    "local": 3.0,
                    "2": 0.5,
                    "3": 2.0,
                    "cloud": 1.0,
                },
            },
            legal_action_mask={"local": True, "2": False, "3": True, "cloud": False},
        )

        self.assertEqual(policy.choose_action(context), "3")

    def test_missing_queue_data_exposes_visible_fallback_reason(self) -> None:
        policy = MinimumLatencyEstimateOffloadingPolicy()
        context = PolicyContext(
            observation={
                "source_agent_id": "1",
                "mleo_placement_candidates": {"local": ["local"]},
            },
            legal_action_mask={"local": True},
        )

        self.assertEqual(policy.choose_action(context), "local")
        self.assertIsNotNone(policy.last_fallback_reason)
        self.assertIn("fallback", policy.last_fallback_reason or "")


if __name__ == "__main__":
    unittest.main()
