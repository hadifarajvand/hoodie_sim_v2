from __future__ import annotations

import unittest

from src.environment.hoodie_neighbor_graph import HoodieNeighborGraph
from src.environment.topology import TopologyGraph


class HoodieNeighborGraphTests(unittest.TestCase):
    def test_deterministic_neighbors_and_reachability(self) -> None:
        graph = HoodieNeighborGraph.build(TopologyGraph.from_approved_assumption_registry())
        neighbors = graph.get_neighbors("1")
        self.assertTrue(neighbors)
        self.assertTrue(graph.is_reachable("1", neighbors[0]))
        self.assertTrue(graph.is_reachable("1", "cloud"))

    def test_available_destinations_filter_congested_neighbors(self) -> None:
        graph = HoodieNeighborGraph.build(TopologyGraph.from_approved_assumption_registry())
        available = graph.get_available_destinations("1", {dst: True for dst in graph.get_neighbors("1")})
        self.assertEqual(available, ("cloud",))


if __name__ == "__main__":
    unittest.main()

