from __future__ import annotations

import unittest

from src.environment.paper_action_space import build_legal_action_mask, build_paper_action_space
from src.environment.topology import TopologyGraph


class PaperActionSpaceTests(unittest.TestCase):
    def test_destination_specific_action_mapping_includes_cloud_and_local(self) -> None:
        topology = TopologyGraph.from_approved_assumption_registry()
        action_space = build_paper_action_space(topology, source_agent_id="1", include_reserved_invalid=False)
        self.assertEqual(action_space.local_action_index, 0)
        self.assertEqual(action_space.cloud_action_index, 21)
        self.assertEqual(action_space.paper_action_count, 22)
        self.assertIn("6", action_space.action_index_to_destination)

    def test_legal_mask_respects_neighbors_and_self_illegality(self) -> None:
        topology = TopologyGraph.from_approved_assumption_registry()
        mask = build_legal_action_mask(topology, source_agent_id="1", include_reserved_invalid=False, cloud_disabled=False)
        self.assertEqual(len(mask["legal_action_mask"]), 22)
        self.assertTrue(mask["legal_action_mask"][0])
        self.assertTrue(mask["legal_action_mask"][6])
        self.assertTrue(mask["legal_action_mask"][11])
        self.assertTrue(mask["legal_action_mask"][16])
        self.assertTrue(mask["legal_action_mask"][21])
        self.assertFalse(mask["legal_action_mask"][1])
        self.assertIn("1", mask["illegal_action_reasons"])


if __name__ == "__main__":
    unittest.main()
