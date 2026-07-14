from __future__ import annotations

import unittest

from src.echo_action_space import build_echo_action_space, build_physical_action_mask
from src.environment.topology import TopologyGraph


class FixedEchoActionSpaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.topology = TopologyGraph(
            node_ids=("1", "2", "3", "cloud"),
            legal_adjacency={
                "1": ("2", "cloud"),
                "2": ("1", "3", "cloud"),
                "3": ("2", "cloud"),
                "cloud": ("1", "2", "3"),
            },
        )

    def test_output_dimension_is_constant_for_smaller_topologies(self) -> None:
        action_space = build_echo_action_space(
            self.topology,
            source_agent_id=1,
            max_edge_agents=30,
        )

        self.assertEqual(action_space.count, 32)
        self.assertEqual(action_space.actions[0].action_id, "local")
        self.assertEqual(action_space.actions[1].action_id, "horizontal_self_1")
        self.assertEqual(action_space.actions[30].action_id, "horizontal_30")
        self.assertEqual(action_space.actions[31].action_id, "cloud")

    def test_absent_self_and_disconnected_destinations_are_masked(self) -> None:
        action_space = build_echo_action_space(
            self.topology,
            source_agent_id=1,
            max_edge_agents=30,
        )
        mask = build_physical_action_mask(action_space, self.topology)

        self.assertEqual(mask.values[0], 1)   # local
        self.assertEqual(mask.values[1], 0)   # self horizontal
        self.assertEqual(mask.values[2], 1)   # connected EA 2
        self.assertEqual(mask.values[3], 0)   # disconnected EA 3
        self.assertEqual(mask.values[4], 0)   # absent padded EA 4
        self.assertEqual(mask.values[31], 1)  # cloud


if __name__ == "__main__":
    unittest.main()
