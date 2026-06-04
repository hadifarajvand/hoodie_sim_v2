from __future__ import annotations

import unittest

from src.analysis.hoodie_runtime_evaluation_runner.config import (
    POLICY_BCO,
    POLICY_FLC,
    POLICY_HO,
    POLICY_HOODIE,
    POLICY_MLEO,
    POLICY_ORIGINAL_HOODIE_BASELINE,
    POLICY_RO,
    POLICY_VO,
    REQUIRED_POLICIES,
)
from src.analysis.hoodie_runtime_evaluation_runner.policies import build_policy_adapter
from src.policies.common import action_family
from src.policies.policy_interface import PolicyContext


class HoodieRuntimeEvaluationRunnerPolicyTests(unittest.TestCase):
    def _context(self, *, queue_hints: dict[str, float], legal_horizontal_destinations: tuple[str, ...] = ("6",)) -> PolicyContext:
        legal_action_mask = {
            "local": True,
            "compute_local": True,
            "horizontal": bool(legal_horizontal_destinations),
            "offload_horizontal": bool(legal_horizontal_destinations),
            "vertical": True,
            "offload_vertical": True,
        }
        return PolicyContext(
            observation={
                "scenario_name": "mixed_local_horizontal_cloud_candidates",
                "workload": "medium",
                "deadline_pressure": "moderate",
                "task_id": "task-1",
                "source_agent_id": "1",
                "topology": ("1", *legal_horizontal_destinations, "cloud"),
                "candidate_actions": ("local", "horizontal", "vertical"),
                "legal_horizontal_destinations": legal_horizontal_destinations,
                "illegal_horizontal_destinations": ("2",),
                "cloud_available": True,
                "placement_actions": {"local": ("local",), "horizontal": legal_horizontal_destinations, "vertical": ("vertical",), "cloud": ("vertical",)},
                "queue_hints": queue_hints,
                "mqo_queue_hints": queue_hints,
                "fallback_hints": {"local": 1.0, "horizontal": 2.0, "vertical": 4.0},
                "delay_hints": {"local": 4.0, "horizontal": 2.0, "vertical": 3.0},
                "reward_hints": {"local": -4.0, "horizontal": -2.0, "vertical": -3.0},
                "latency_estimates": {"local": 4.0, "horizontal": 2.0, "vertical": 3.0},
                "queue_history": (queue_hints["local"], queue_hints["horizontal"], queue_hints["vertical"]),
            },
            legal_action_mask=legal_action_mask,
            trace_history=("scenario", "medium", "moderate", "7"),
        )

    def test_required_policy_set_matches_feature_085(self) -> None:
        self.assertEqual(REQUIRED_POLICIES, (POLICY_HOODIE, POLICY_RO, POLICY_FLC, POLICY_VO, POLICY_HO, POLICY_BCO, POLICY_MLEO))

    def test_original_baseline_is_not_active(self) -> None:
        with self.assertRaises(ValueError):
            build_policy_adapter(POLICY_ORIGINAL_HOODIE_BASELINE)

    def test_hoodie_uses_feature_080_proposed_path(self) -> None:
        hoodie = build_policy_adapter(POLICY_HOODIE)
        action = hoodie.choose_action(self._context(queue_hints={"local": 3.0, "horizontal": 2.0, "vertical": 4.0}))
        self.assertNotIn(action_family(action), {"local"})
        trace = " | ".join(hoodie.last_decision_trace)
        self.assertIn("policy=HOODIE", trace)
        self.assertIn("state_value=", trace)
        self.assertIn("raw_advantages=", trace)
        self.assertIn("mean_advantage=", trace)
        self.assertIn("adjusted_q_values=", trace)
        self.assertIn("policy=HOODIE", trace)

    def test_ro_random_behavior_is_seed_controlled(self) -> None:
        context = self._context(queue_hints={"local": 3.0, "horizontal": 2.0, "vertical": 4.0})
        first = build_policy_adapter(POLICY_RO, seed=11).choose_action(context)
        second = build_policy_adapter(POLICY_RO, seed=11).choose_action(context)
        self.assertEqual(first, second)

    def test_flc_always_local(self) -> None:
        flc = build_policy_adapter(POLICY_FLC)
        action = flc.choose_action(self._context(queue_hints={"local": 3.0, "horizontal": 2.0, "vertical": 4.0}))
        self.assertIn(action, {"local", "compute_local"})
        self.assertIn("policy=FLC", " | ".join(flc.last_decision_trace))

    def test_vo_always_vertical(self) -> None:
        vo = build_policy_adapter(POLICY_VO)
        action = vo.choose_action(self._context(queue_hints={"local": 3.0, "horizontal": 2.0, "vertical": 1.0}))
        self.assertIn(action, {"vertical", "offload_vertical"})
        self.assertIn("policy=VO", " | ".join(vo.last_decision_trace))

    def test_ho_prefers_horizontal_when_legal_destination_exists(self) -> None:
        ho = build_policy_adapter(POLICY_HO)
        action = ho.choose_action(self._context(queue_hints={"local": 4.0, "horizontal": 1.0, "vertical": 3.0}))
        self.assertIn(action, {"horizontal", "offload_horizontal"})
        self.assertIn("selected_family=horizontal", " | ".join(ho.last_decision_trace))

    def test_bco_cycles_through_local_vertical_horizontal(self) -> None:
        bco = build_policy_adapter(POLICY_BCO)
        context = self._context(queue_hints={"local": 4.0, "horizontal": 2.0, "vertical": 1.0})
        first = bco.choose_action(context)
        second = bco.choose_action(context)
        third = bco.choose_action(context)
        self.assertIn(first, {"local", "compute_local"})
        self.assertIn(second, {"vertical", "offload_vertical"})
        self.assertIn(third, {"horizontal", "offload_horizontal"})

    def test_mleo_selects_minimum_latency_destination(self) -> None:
        mleo = build_policy_adapter(POLICY_MLEO)
        action = mleo.choose_action(self._context(queue_hints={"local": 5.0, "horizontal": 2.0, "vertical": 3.0}))
        self.assertIn(action_family(action), {"horizontal"})
        trace = " | ".join(mleo.last_decision_trace)
        self.assertIn("policy=MLEO", trace)
        self.assertIn("candidate_count=", trace)
        self.assertIn("minimum latency estimate offloader", trace.lower())


if __name__ == "__main__":
    unittest.main()
