from __future__ import annotations

import unittest

from src.environment.paper_load_history import build_paper_load_history
from src.environment.topology import TopologyGraph


class PaperLoadHistoryTests(unittest.TestCase):
    def test_load_history_shape_is_w_by_n_plus_one(self) -> None:
        topology = TopologyGraph.from_approved_assumption_registry()
        active = {**{node: index for index, node in enumerate(topology.node_ids, start=1)}, "cloud": 3}
        history = build_paper_load_history(topology, active, window_w=10)
        self.assertEqual(history.load_history_shape, (10, 21))
        self.assertEqual(history.window_w, 10)
        self.assertEqual(len(history.node_order), 21)

    def test_active_queue_counts_are_preserved_per_node(self) -> None:
        topology = TopologyGraph.from_approved_assumption_registry()
        active = {**{node: 1 for node in topology.node_ids}, "cloud": 2}
        history = build_paper_load_history(topology, active, window_w=10)
        self.assertEqual(history.active_queue_counts_by_node["cloud"], 2)
        self.assertTrue(all(len(row) == 21 for row in history.load_history_matrix))


if __name__ == "__main__":
    unittest.main()
