from __future__ import annotations

import copy
from pathlib import Path
import unittest

from src.dal.advisory import build_dal_advisory_payload
from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.replay_hash import build_euls_replay_payload, stable_replay_hash
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.policy_registry import PolicyRegistry
from src.policies.dal_shadow_policy import DALShadowPolicy
from src.policies.policy_interface import PolicyContext


class DALShadowPolicyTests(unittest.TestCase):
    def _env(self) -> HoodieGymEnvironment:
        env = HoodieGymEnvironment(
            episode_length=5,
            topology=TopologyGraph(node_ids=("1", "2", "cloud"), legal_adjacency={"1": ("2", "cloud")}),
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(
                cpu_capacity_per_slot_agent=64.0,
                cpu_capacity_per_slot_edge=2.0,
                cpu_capacity_per_slot_cloud=2.0,
            ),
            policy_name="FLC",
        )
        env.reset(seed=7)
        return env

    def _context(self, legal_action_mask: dict[str, bool], advisory: dict[str, object] | None = None) -> PolicyContext:
        return PolicyContext(
            observation={"slot": 0, "task_id": 1},
            legal_action_mask=legal_action_mask,
            dal_advisory=advisory,
        )

    def test_policy_returns_only_legal_actions(self) -> None:
        policy = DALShadowPolicy()
        context = self._context({"local": False, "compute_local": True, "horizontal": True, "offload_horizontal": False, "vertical": False, "offload_vertical": False})
        self.assertEqual(policy.choose_action(context), "compute_local")

    def test_policy_reads_dal_advisory_without_mutation(self) -> None:
        policy = DALShadowPolicy()
        advisory = build_dal_advisory_payload(self._env(), None)
        advisory_copy = copy.deepcopy(advisory)
        context = self._context({"local": True, "compute_local": False, "horizontal": False, "offload_horizontal": False, "vertical": False, "offload_vertical": False}, advisory=advisory)
        action = policy.choose_action(context)
        self.assertEqual(action, "local")
        self.assertEqual(advisory, advisory_copy)

    def test_no_dal_advisory_fallback_is_deterministic(self) -> None:
        policy = DALShadowPolicy()
        context = self._context({"local": False, "compute_local": True, "horizontal": True, "offload_horizontal": True, "vertical": False, "offload_vertical": False})
        self.assertEqual(policy.choose_action(context), policy.choose_action(context))

    def test_critical_deadline_prefers_local_if_legal(self) -> None:
        policy = DALShadowPolicy()
        context = self._context(
            {"local": True, "compute_local": False, "horizontal": True, "offload_horizontal": False, "vertical": True, "offload_vertical": False},
            advisory={"deadline_pressure": "critical", "private_queue_load": 1, "offloading_queue_load": 0, "public_queue_load": 0, "total_queue_load": 1},
        )
        self.assertEqual(policy.choose_action(context), "local")

    def test_queue_pressure_with_low_deadline_pressure_prefers_offload_if_legal(self) -> None:
        policy = DALShadowPolicy()
        context = self._context(
            {"local": True, "compute_local": False, "horizontal": True, "offload_horizontal": False, "vertical": True, "offload_vertical": True},
            advisory={"deadline_pressure": "low", "private_queue_load": 0, "offloading_queue_load": 3, "public_queue_load": 2, "total_queue_load": 5},
        )
        self.assertEqual(policy.choose_action(context), "vertical")

    def test_registry_opt_in_adds_shadow_policy_without_replacing_defaults(self) -> None:
        self.assertEqual(
            PolicyRegistry.supported_names(),
            ("FLC", "VO", "HO", "RO", "BCO", "MLEO", "ADAPTIVE"),
        )
        self.assertEqual(PolicyRegistry.resolve("FLC").__class__.__name__, "FullLocalComputingPolicy")
        self.assertEqual(PolicyRegistry.resolve("HOODIE").__class__.__name__, "AdaptiveOffloadingPolicy")
        self.assertEqual(PolicyRegistry.resolve("DAL_SHADOW").__class__.__name__, "DALShadowPolicy")

    def test_policy_module_does_not_import_training_or_torch(self) -> None:
        source = Path("src/policies/dal_shadow_policy.py").read_text(encoding="utf-8")
        self.assertNotIn("import torch", source)
        self.assertNotIn("from torch", source)
        self.assertNotIn("training", source.lower())
        self.assertNotIn("optimizer", source.lower())

    def test_replay_hash_is_stable_across_dal_shadow_policy_use(self) -> None:
        env = self._env()
        before_payload = build_euls_replay_payload(env)
        before_hash = stable_replay_hash(before_payload)
        policy = DALShadowPolicy()
        context = self._context(env.legal_action_mask(env.current_task), advisory=build_dal_advisory_payload(env, env.current_task))
        policy.choose_action(context)
        after_payload = build_euls_replay_payload(env)
        after_hash = stable_replay_hash(after_payload)
        self.assertEqual(before_payload, after_payload)
        self.assertEqual(before_hash, after_hash)


if __name__ == "__main__":
    unittest.main()
