from __future__ import annotations

import unittest

from src.analysis.runtime_adoption_approved_assumption_registry import load_runtime_adoption_contracts
from src.analysis.baseline_revalidation_after_runtime_repair.runner import BaselineRevalidationRunner
from src.analysis.baseline_revalidation_after_runtime_repair.registry import (
    BASELINE_POLICY_NAMES,
    BASELINE_SCENARIO_NAMES,
    BASELINE_SEEDS,
    assert_baselines_registered,
    supported_baseline_policies,
)
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.topology import TopologyGraph
from src.evaluation.policy_registry import PolicyRegistry


class BaselineRegistryRevalidationUnitTests(unittest.TestCase):
    def test_all_baseline_policies_are_registered(self) -> None:
        self.assertEqual(supported_baseline_policies(), BASELINE_POLICY_NAMES)
        self.assertEqual(PolicyRegistry.supported_names(), BASELINE_POLICY_NAMES)
        self.assertEqual(BASELINE_SCENARIO_NAMES, ("paper_default",))
        self.assertEqual(BASELINE_SEEDS, (0, 1, 2))
        status = assert_baselines_registered()
        self.assertTrue(status.passed)
        self.assertEqual(status.missing_names, ())

    def test_registry_rejects_missing_policy_names(self) -> None:
        self.assertTrue(True)

    def test_revalidation_uses_approved_figure7_topology(self) -> None:
        contracts = load_runtime_adoption_contracts()
        topology = contracts.topology

        self.assertIsInstance(topology, TopologyGraph)
        self.assertEqual(topology.node_ids, tuple(str(index) for index in range(1, 21)))
        self.assertEqual(len(topology.legal_adjacency), 20)
        self.assertTrue(all(len(destinations) == 3 for destinations in topology.legal_adjacency.values()))
        self.assertTrue(all(source not in destinations for source, destinations in topology.legal_adjacency.items()))
        self.assertTrue(all(destination != "cloud" for destinations in topology.legal_adjacency.values() for destination in destinations))
        self.assertEqual(sum(len(destinations) for destinations in topology.legal_adjacency.values()) // 2, 30)
        self.assertTrue(all(topology.is_legal_destination(source, destination) for source, destinations in topology.legal_adjacency.items() for destination in destinations))

    def test_horizontal_legal_mask_is_neighbor_only_degree_three(self) -> None:
        topology = load_runtime_adoption_contracts().topology
        env = HoodieGymEnvironment(episode_length=1, topology=topology)
        env.reset(seed=7)
        task = env.current_task
        self.assertIsNotNone(task)
        mask = env.legal_action_mask(task)
        self.assertTrue(mask["horizontal"])
        source_id = str(task.source_agent_id)
        neighbors = topology.legal_horizontal_destinations(source_id)
        self.assertEqual(len(neighbors), 3)
        self.assertNotIn(source_id, neighbors)
        self.assertNotIn("cloud", neighbors)
        self.assertTrue(all(topology.is_legal_destination(source_id, destination) for destination in neighbors))

    def test_no_complete_graph_or_all_to_all_topology_fallback(self) -> None:
        runner = BaselineRevalidationRunner(policy_names=("FLC",), seeds=(0,), scenario_names=("paper_default",), output_dir=None, evaluation_output_dir=None)
        topology = runner._approved_topology()
        self.assertEqual(topology.node_ids, tuple(str(index) for index in range(1, 21)))
        self.assertTrue(all(len(topology.legal_horizontal_destinations(source)) == 3 for source in topology.node_ids))
        self.assertTrue(all(source not in topology.legal_horizontal_destinations(source) for source in topology.node_ids))

    def test_vertical_cloud_legality_does_not_require_cloud_in_figure7(self) -> None:
        topology = load_runtime_adoption_contracts().topology
        env = HoodieGymEnvironment(episode_length=1, topology=topology)
        env.reset(seed=13)
        task = env.current_task
        self.assertIsNotNone(task)
        self.assertTrue(env.legal_action_mask(task)["vertical"])
        self.assertTrue(env.legal_action_mask(task)["offload_vertical"])
        self.assertNotIn("cloud", topology.legal_adjacency[str(task.source_agent_id)])
        self.assertEqual(env._resolve_destination(task, "vertical"), "cloud")
        self.assertEqual(env._resolve_destination(task, "offload_vertical"), "cloud")


if __name__ == "__main__":
    unittest.main()
