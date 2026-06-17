from __future__ import annotations

import unittest
from unittest import mock

from src.dal.advisory import build_dal_advisory_payload
from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.replay_hash import build_euls_replay_payload, stable_replay_hash
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.policies.action_masking import select_legal_action as real_select_legal_action
from src.policies.policy_interface import PolicyContext


class DALPolicyContextTests(unittest.TestCase):
    def _env(self) -> HoodieGymEnvironment:
        env = HoodieGymEnvironment(
            episode_length=5,
            topology=TopologyGraph(node_ids=("1", "2", "cloud"), legal_adjacency={"1": ("2", "cloud")}),
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=2.0, cpu_capacity_per_slot_cloud=2.0),
            policy_name="FLC",
        )
        env.reset(seed=3)
        return env

    def test_policy_context_remains_backward_compatible(self) -> None:
        context = PolicyContext(observation={"slot": 0}, legal_action_mask={"local": True})
        self.assertEqual(context.observation, {"slot": 0})
        self.assertEqual(context.legal_action_mask, {"local": True})
        self.assertEqual(context.trace_history, ())
        self.assertIsNone(context.dal_advisory)

    def test_dal_advisory_is_present_during_action_selection_context(self) -> None:
        env = self._env()
        captured: list[PolicyContext] = []
        expected = build_dal_advisory_payload(env, env.current_task)

        def capture(context: PolicyContext, action: str) -> str:
            captured.append(context)
            return action

        with mock.patch("src.environment.gym_adapter.select_legal_action", side_effect=capture):
            env.step("local")

        self.assertTrue(captured)
        self.assertIsNotNone(captured[0].dal_advisory)
        self.assertEqual(captured[0].dal_advisory, expected)

    def test_action_selection_remains_unchanged(self) -> None:
        env = self._env()
        selected_actions: list[str] = []

        def capture(context: PolicyContext, action: str) -> str:
            selected_actions.append(action)
            return real_select_legal_action(context, action)

        with mock.patch("src.environment.gym_adapter.select_legal_action", side_effect=capture):
            env.step("local")

        self.assertEqual(selected_actions, ["local"])

    def test_legal_action_mask_unchanged(self) -> None:
        env = self._env()
        before = env.legal_action_mask(env.current_task)
        env.dal_advisory()
        after = env.legal_action_mask(env.current_task)
        self.assertEqual(before, after)

    def test_replay_hash_is_stable_across_dal_calls(self) -> None:
        env = self._env()
        before_payload = build_euls_replay_payload(env)
        before_hash = stable_replay_hash(before_payload)
        env.dal_advisory()
        after_payload = build_euls_replay_payload(env)
        after_hash = stable_replay_hash(after_payload)
        self.assertEqual(before_payload, after_payload)
        self.assertEqual(before_hash, after_hash)


if __name__ == "__main__":
    unittest.main()
