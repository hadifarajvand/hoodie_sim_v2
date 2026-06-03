from __future__ import annotations

import unittest

from src.analysis.hoodie_runtime_evaluation_runner.config import (
    POLICY_CLOUD_ONLY,
    POLICY_HOODIE_PROPOSED,
    POLICY_LOCAL_ONLY,
    POLICY_ORIGINAL_HOODIE_BASELINE,
    POLICY_RANDOM_POLICY,
)
from src.analysis.hoodie_runtime_evaluation_runner.policies import build_policy_adapter
from src.policies.policy_interface import PolicyContext


class HoodieRuntimeEvaluationRunnerPolicyTests(unittest.TestCase):
    def _context(self, *, scenario_name: str, workload: str, deadline_pressure: str, delay_hints: dict[str, float]) -> PolicyContext:
        queue_hints = {"local": 1.0, "horizontal": 2.0, "vertical": 3.0}
        reward_hints = {family: delay - 10.0 for family, delay in delay_hints.items()}
        legal_action_mask = {
            "local": True,
            "compute_local": True,
            "horizontal": True,
            "offload_horizontal": True,
            "vertical": True,
            "offload_vertical": True,
        }
        return PolicyContext(
            observation={
                "scenario_name": scenario_name,
                "workload": workload,
                "deadline_pressure": deadline_pressure,
                "task_id": "task-1",
                "source_agent_id": "1",
                "candidate_actions": ("local", "horizontal", "vertical"),
                "legal_horizontal_destinations": ("6",),
                "illegal_horizontal_destinations": ("2",),
                "cloud_available": True,
                "placement_actions": {"local": ("local",), "horizontal": ("6",), "vertical": ("vertical",), "cloud": ("vertical",)},
                "delay_hints": delay_hints,
                "queue_hints": queue_hints,
                "reward_hints": reward_hints,
                "mleo_delay_candidates": {
                    "local": {"action_id": "local", "action_family": "local", "total_delay": delay_hints["local"], "available": True},
                    "horizontal": {"action_id": "6", "action_family": "horizontal", "total_delay": delay_hints["horizontal"], "available": True},
                    "vertical": {"action_id": "vertical", "action_family": "vertical", "total_delay": delay_hints["vertical"], "available": True},
                },
                "latency_estimates": delay_hints,
                "queue_history": (1, 2, 3),
            },
            legal_action_mask=legal_action_mask,
            trace_history=("scenario", workload, deadline_pressure, "7"),
        )

    def test_policy_identity_flags_are_not_compatibility_shims(self) -> None:
        self.assertFalse(build_policy_adapter(POLICY_HOODIE_PROPOSED).compatibility_mode_used)
        self.assertFalse(build_policy_adapter(POLICY_ORIGINAL_HOODIE_BASELINE).compatibility_mode_used)
        self.assertFalse(build_policy_adapter(POLICY_RANDOM_POLICY).compatibility_mode_used)
        self.assertFalse(build_policy_adapter(POLICY_LOCAL_ONLY).compatibility_mode_used)
        self.assertFalse(build_policy_adapter(POLICY_CLOUD_ONLY).compatibility_mode_used)

    def test_proposed_policy_is_hybrid_not_local_only(self) -> None:
        proposed = build_policy_adapter(POLICY_HOODIE_PROPOSED)
        action = proposed.choose_action(
            self._context(
                scenario_name="legal_horizontal_offload",
                workload="low",
                deadline_pressure="moderate",
                delay_hints={"local": 4.0, "horizontal": 3.0, "vertical": 4.0},
            )
        )
        self.assertEqual(action, "horizontal")
        self.assertIn("policy=HOODIE_PROPOSED", proposed.last_decision_trace)
        self.assertIn("selected_action=horizontal", proposed.last_decision_trace)

    def test_original_baseline_is_paper_aligned_not_cloud_only(self) -> None:
        baseline = build_policy_adapter(POLICY_ORIGINAL_HOODIE_BASELINE)
        action = baseline.choose_action(
            self._context(
                scenario_name="legal_horizontal_offload",
                workload="low",
                deadline_pressure="moderate",
                delay_hints={"local": 4.0, "horizontal": 3.0, "vertical": 4.0},
            )
        )
        self.assertEqual(action, "horizontal")
        self.assertIn("policy=ORIGINAL_HOODIE_BASELINE", baseline.last_decision_trace)
        self.assertIn("selected_action=horizontal", baseline.last_decision_trace)

    def test_random_policy_is_seeded(self) -> None:
        context = self._context(
            scenario_name="mixed_local_horizontal_cloud_candidates",
            workload="medium",
            deadline_pressure="tight",
            delay_hints={"local": 3.0, "horizontal": 2.0, "vertical": 4.0},
        )
        first = build_policy_adapter(POLICY_RANDOM_POLICY, seed=11).choose_action(context)
        second = build_policy_adapter(POLICY_RANDOM_POLICY, seed=11).choose_action(context)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
