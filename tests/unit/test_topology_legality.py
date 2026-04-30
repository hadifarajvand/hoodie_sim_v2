from __future__ import annotations

import unittest

from src.environment.topology import TopologyGraph


class TopologyLegalityTests(unittest.TestCase):
    def test_topology_reports_legal_destinations_from_adjacency(self) -> None:
        topology = TopologyGraph(
            node_ids=("ea1", "ea2", "cloud"),
            legal_adjacency={
                "ea1": ("ea2", "cloud"),
                "ea2": ("ea1", "cloud"),
            },
        )

        self.assertTrue(topology.is_legal_destination("ea1", "ea2"))
        self.assertTrue(topology.is_legal_destination("ea1", "cloud"))
        self.assertFalse(topology.is_legal_destination("ea2", "ea2"))

    def test_topology_defaults_to_illegal_for_unknown_source(self) -> None:
        topology = TopologyGraph(node_ids=("ea1", "cloud"))

        self.assertFalse(topology.is_legal_destination("missing", "cloud"))


if __name__ == "__main__":
    unittest.main()

