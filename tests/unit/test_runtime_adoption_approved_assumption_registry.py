from __future__ import annotations

import math
import unittest

from src.analysis.runtime_adoption_approved_assumption_registry import load_runtime_adoption_contracts
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.link_rate_config import LinkRateConfig
from src.evaluation.aggregate_metrics import aggregate_terminal_rewards


class RuntimeAdoptionApprovedAssumptionRegistryUnitTests(unittest.TestCase):
    def test_topology_figure7_adjacency_invariants(self) -> None:
        contracts = load_runtime_adoption_contracts()
        topology = contracts.topology

        self.assertEqual(len(topology.node_ids), 20)
        self.assertEqual(tuple(topology.node_ids), tuple(str(index) for index in range(1, 21)))
        self.assertEqual(len(topology.legal_adjacency), 20)
        self.assertTrue(all(len(destinations) == 3 for destinations in topology.legal_adjacency.values()))
        self.assertTrue(all(source not in destinations for source, destinations in topology.legal_adjacency.items()))
        self.assertTrue(all(destination != "cloud" for destinations in topology.legal_adjacency.values() for destination in destinations))
        self.assertTrue(all(topology.is_legal_destination(source, destination) for source, destinations in topology.legal_adjacency.items() for destination in destinations))
        self.assertEqual(sum(len(destinations) for destinations in topology.legal_adjacency.values()) // 2, 30)
        self.assertTrue(
            all(
                source in topology.legal_adjacency.get(destination, ())
                for source, destinations in topology.legal_adjacency.items()
                for destination in destinations
            )
        )

    def test_horizontal_legality_neighbor_only_no_self_no_non_neighbor(self) -> None:
        contracts = load_runtime_adoption_contracts()
        topology = contracts.topology
        env = HoodieGymEnvironment(episode_length=1, topology=topology)
        env.reset(seed=7)
        task = env.current_task
        self.assertIsNotNone(task)
        self.assertTrue(env.legal_action_mask(task)["horizontal"])
        source_id = str(task.source_agent_id)
        self.assertNotIn(source_id, topology.legal_horizontal_destinations(source_id))
        self.assertNotIn("cloud", topology.legal_horizontal_destinations(source_id))
        self.assertTrue(all(destination in topology.legal_adjacency[source_id] for destination in topology.legal_horizontal_destinations(source_id)))

    def test_action_mask_rejects_non_neighbor_horizontal_destinations(self) -> None:
        topology = load_runtime_adoption_contracts().topology
        env = HoodieGymEnvironment(episode_length=1, topology=topology)
        env.reset(seed=11)
        task = env.current_task
        self.assertIsNotNone(task)
        legal_mask = env.legal_action_mask(task)
        self.assertTrue(legal_mask["horizontal"])
        source_id = str(task.source_agent_id)
        horizontal_destinations = topology.legal_horizontal_destinations(source_id)
        self.assertTrue(horizontal_destinations)
        self.assertEqual(env._resolve_destination(task, "horizontal"), horizontal_destinations[0])
        self.assertTrue(all(topology.is_legal_destination(source_id, destination) for destination in horizontal_destinations))

    def test_vertical_cloud_action_not_constrained_by_horizontal_adjacency(self) -> None:
        topology = load_runtime_adoption_contracts().topology
        cloud_topology = topology.__class__(
            node_ids=("1", "2", "cloud"),
            legal_adjacency={"1": ("2", "cloud")},
        )
        env = HoodieGymEnvironment(episode_length=1, topology=cloud_topology)
        env.reset(seed=13)
        task = env.current_task
        self.assertIsNotNone(task)
        self.assertTrue(env.legal_action_mask(task)["vertical"])
        self.assertEqual(env._resolve_destination(task, "vertical"), "cloud")

    def test_cloud_vertical_rate_uses_rv_10mbps_no_fake_cloud_rate(self) -> None:
        link_rate_config = LinkRateConfig()

        self.assertEqual(link_rate_config.vertical_data_rate_mbps, 10.0)
        self.assertEqual(link_rate_config.cloud_facing_vertical_rate_mbps, 10.0)
        self.assertEqual(link_rate_config.horizontal_data_rate_mbps, 30.0)
        self.assertIsNone(link_rate_config.cloud_data_rate_mbps)

    def test_timeout_contract_20_slots_2_seconds(self) -> None:
        traffic = load_runtime_adoption_contracts().traffic_config

        self.assertEqual(traffic.timeout_slots, 20)
        self.assertEqual(traffic.slot_duration_seconds, 0.1)
        self.assertEqual(traffic.timeout_slots * traffic.slot_duration_seconds, 2.0)

    def test_aggregation_per_agent_episode_sum_then_mean(self) -> None:
        value = aggregate_terminal_rewards([[1.0, 2.0, None], [3.0, float("nan")], [None]])

        self.assertEqual(value, 3.0)

    def test_aggregation_excludes_nan_no_task_omitted_slots(self) -> None:
        value = aggregate_terminal_rewards([[None, float("nan")], [2.0, None], [4.0]])

        self.assertEqual(value, 3.0)
        self.assertFalse(math.isnan(value))


if __name__ == "__main__":
    unittest.main()
