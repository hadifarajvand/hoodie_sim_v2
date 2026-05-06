from __future__ import annotations

import unittest

from src.environment.task import Task
from src.policies.adaptive_context import AdaptiveDecisionContext, build_adaptive_context
from src.policies.policy_interface import PolicyContext


class AdaptiveContextTests(unittest.TestCase):
    def test_builds_from_flat_observation_and_preserves_legal_mask(self) -> None:
        legal_mask = {"local": True, "compute_local": True, "horizontal": False, "vertical": False}
        context = PolicyContext(
            observation={
                "slot": 4,
                "queue_load": 2,
                "load_hint": 2,
                "task_id": 17,
                "source_agent_id": 3,
                "arrival_slot": 4,
                "size": 2.1,
                "processing_density": 0.297,
                "cycles_required": 0.6237,
                "cycles_remaining": 0.5237,
                "timeout_length": 20,
                "absolute_deadline_slot": 24,
                "topology": ("1", "2"),
                "legal_action_mask": legal_mask,
                "fallback_hints": {"local": 1.0, "horizontal": 2.0, "vertical": 3.0},
                "latency_estimates": {"local": 1.0, "horizontal": 2.0, "vertical": 3.0},
                "balance_hint": {"local": 0.5, "horizontal": 0.4, "vertical": 0.3},
            },
            legal_action_mask=legal_mask,
        )

        adaptive = build_adaptive_context(
            context,
            traffic_summary={
                "observed_arrival_probability": 0.5,
                "arrivals_per_slot": (1, 0, 1),
                "arrivals_per_agent": {"1": 2, "2": 1},
            },
            execution_summary={"mean_latency": 2.0},
        )

        self.assertIsInstance(adaptive, AdaptiveDecisionContext)
        self.assertEqual(adaptive.agent_id, 3)
        self.assertEqual(adaptive.current_slot, 4)
        self.assertEqual(adaptive.task_id, 17)
        self.assertEqual(adaptive.task_size, 2.1)
        self.assertEqual(adaptive.processing_density, 0.297)
        self.assertEqual(adaptive.cycles_required, 0.6237)
        self.assertEqual(adaptive.cycles_remaining, 0.5237)
        self.assertEqual(adaptive.timeout_length, 20)
        self.assertEqual(adaptive.absolute_deadline_slot, 24)
        self.assertEqual(adaptive.legal_action_mask, legal_mask)
        self.assertEqual(adaptive.queue_load, 2)
        self.assertEqual(adaptive.observed_arrival_probability, 0.5)
        self.assertEqual(adaptive.arrivals_per_slot, (1, 0, 1))
        self.assertEqual(adaptive.arrivals_per_agent, {"1": 2, "2": 1})
        self.assertEqual(adaptive.latency_estimates, {"local": 1.0, "horizontal": 2.0, "vertical": 3.0})
        self.assertEqual(adaptive.balance_hint, {"local": 0.5, "horizontal": 0.4, "vertical": 0.3})
        self.assertEqual(adaptive.topology, ("1", "2"))
        self.assertEqual(adaptive.traffic_summary["observed_arrival_probability"], 0.5)
        self.assertEqual(adaptive.execution_summary, {"mean_latency": 2.0})

    def test_builds_from_nested_environment_observation(self) -> None:
        legal_mask = {"local": True, "horizontal": True, "vertical": True}
        context = PolicyContext(
            observation={
                "1": {
                    "slot": 7,
                    "queue_load": 1,
                    "task_id": 9,
                    "source_agent_id": 1,
                    "size": 2.1,
                    "processing_density": 0.297,
                    "cycles_required": 0.6237,
                    "cycles_remaining": 0.1237,
                    "timeout_length": 20,
                    "absolute_deadline_slot": 27,
                    "legal_action_mask": legal_mask,
                }
            },
            legal_action_mask=legal_mask,
        )

        adaptive = build_adaptive_context(context)

        self.assertEqual(adaptive.agent_id, 1)
        self.assertEqual(adaptive.current_slot, 7)
        self.assertEqual(adaptive.task_id, 9)
        self.assertEqual(adaptive.task_size, 2.1)
        self.assertEqual(adaptive.processing_density, 0.297)
        self.assertEqual(adaptive.cycles_required, 0.6237)
        self.assertEqual(adaptive.cycles_remaining, 0.1237)
        self.assertEqual(adaptive.legal_action_mask, legal_mask)
        self.assertIsNone(adaptive.observed_arrival_probability)
        self.assertIsNone(adaptive.traffic_summary)
        self.assertIsNone(adaptive.execution_summary)

    def test_missing_optional_summaries_fall_back_safely(self) -> None:
        context = PolicyContext(observation={"slot": 0}, legal_action_mask={"local": True})

        adaptive = build_adaptive_context(context)

        self.assertIsNone(adaptive.task_id)
        self.assertIsNone(adaptive.task_size)
        self.assertIsNone(adaptive.processing_density)
        self.assertIsNone(adaptive.cycles_required)
        self.assertIsNone(adaptive.cycles_remaining)
        self.assertIsNone(adaptive.observed_arrival_probability)
        self.assertIsNone(adaptive.arrivals_per_slot)
        self.assertIsNone(adaptive.arrivals_per_agent)
        self.assertIsNone(adaptive.traffic_summary)
        self.assertIsNone(adaptive.execution_summary)

    def test_context_is_frozen_from_callers_perspective(self) -> None:
        legal_mask = {"local": True}
        context = PolicyContext(observation={"task_id": 1}, legal_action_mask=legal_mask)

        adaptive = build_adaptive_context(context)

        legal_mask["local"] = False
        self.assertTrue(adaptive.legal_action_mask["local"])
        with self.assertRaises(Exception):
            adaptive.task_id = 2  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
