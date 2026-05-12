from __future__ import annotations

import unittest

from src.analysis.user_approved_assumption_patch_registry.registry import build_registry_entries


class UserApprovedAssumptionPatchRegistryPolicyGuardTest(unittest.TestCase):
    def test_blocked_items_do_not_invent_topology_or_timeout(self) -> None:
        entries = {entry.item_id: entry for entry in build_registry_entries()}
        self.assertEqual(entries["Figure_7_adjacency"].assumption_status, "approved")
        self.assertTrue(entries["Figure_7_adjacency"].runtime_use_allowed)
        self.assertEqual(entries["legal_horizontal_destinations"].assumption_status, "blocked_no_assumption")
        self.assertEqual(entries["timeout_value"].assumption_status, "blocked_no_assumption")
        figure = entries["Figure_7_adjacency"].to_dict()["proposed_value"]
        self.assertEqual(figure["node_count"], 20)
        self.assertEqual(figure["edge_count"], 30)
        self.assertEqual(figure["graph_type"], "undirected_unweighted")
        self.assertEqual(figure["source"], "user_supplied_manual_extraction")
        self.assertFalse(figure["paper_recovery_claim"])
        self.assertEqual(entries["legal_horizontal_destinations"].proposed_value, "")
        self.assertEqual(entries["timeout_value"].proposed_value, "")

    def test_proposed_values_remain_report_only(self) -> None:
        entries = {entry.item_id: entry for entry in build_registry_entries()}
        for item_id in [
            "EA_private_cpu_capacity",
            "EA_public_cpu_capacity",
            "cloud_cpu_capacity",
            "cloud_data_rate",
            "multi_agent_aggregation_reduction_order",
        ]:
            self.assertEqual(entries[item_id].assumption_status, "proposed")
            self.assertFalse(entries[item_id].runtime_use_allowed)


if __name__ == "__main__":
    unittest.main()
