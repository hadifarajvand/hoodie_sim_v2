from __future__ import annotations

import unittest

from src.environment.paper_state import build_paper_state_snapshot
from src.environment.topology import TopologyGraph


class PaperStateVectorTests(unittest.TestCase):
    def test_state_contains_explicit_waiting_times_and_history(self) -> None:
        topology = TopologyGraph.from_approved_assumption_registry()
        snapshot = build_paper_state_snapshot(
            source_agent_id="1",
            task_size_mbits=12.0,
            topology=topology,
            public_queue_lengths_by_destination={"2": 1, "6": 2, "11": 0, "16": 3},
            active_queue_counts_by_node={**{node: index for index, node in enumerate(topology.node_ids, start=1)}, "cloud": 2},
            private_waiting_time_slots=4,
            offloading_waiting_time_slots=7,
        )
        payload = snapshot.to_dict()
        self.assertIn("legacy_compact_state", payload)
        self.assertEqual(len(payload["load_history_matrix"]), 10)
        self.assertEqual(len(payload["load_history_matrix"][0]), 21)
        self.assertEqual(payload["forecast_input_source"], "active_queue_counts_by_node")

    def test_legacy_compact_state_is_labeled_and_not_used_as_primary_state(self) -> None:
        topology = TopologyGraph.from_approved_assumption_registry()
        snapshot = build_paper_state_snapshot(
            source_agent_id="1",
            task_size_mbits=9.0,
            topology=topology,
            public_queue_lengths_by_destination={"2": 1},
            active_queue_counts_by_node={**{node: 1 for node in topology.node_ids}, "cloud": 1},
            private_waiting_time_slots=1,
            offloading_waiting_time_slots=2,
        )
        self.assertIsNotNone(snapshot.legacy_compact_state)
        self.assertEqual(len(snapshot.legacy_compact_state), 3)


if __name__ == "__main__":
    unittest.main()
