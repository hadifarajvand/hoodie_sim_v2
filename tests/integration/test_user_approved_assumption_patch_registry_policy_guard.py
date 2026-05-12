from __future__ import annotations

import unittest

from src.analysis.user_approved_assumption_patch_registry.registry import build_registry_entries


class UserApprovedAssumptionPatchRegistryPolicyGuardTest(unittest.TestCase):
    def test_blocked_items_do_not_invent_topology_or_timeout(self) -> None:
        entries = {entry.item_id: entry for entry in build_registry_entries()}
        self.assertEqual(entries["Figure_7_adjacency"].assumption_status, "approved")
        self.assertTrue(entries["Figure_7_adjacency"].runtime_use_allowed)
        self.assertEqual(entries["legal_horizontal_destinations"].assumption_status, "approved")
        self.assertTrue(entries["legal_horizontal_destinations"].runtime_use_allowed)
        self.assertEqual(entries["EA_private_cpu_capacity"].assumption_status, "approved")
        self.assertTrue(entries["EA_private_cpu_capacity"].runtime_use_allowed)
        self.assertEqual(entries["EA_public_cpu_capacity"].assumption_status, "approved")
        self.assertTrue(entries["EA_public_cpu_capacity"].runtime_use_allowed)
        self.assertEqual(entries["cloud_cpu_capacity"].assumption_status, "approved")
        self.assertTrue(entries["cloud_cpu_capacity"].runtime_use_allowed)
        self.assertEqual(entries["timeout_value"].assumption_status, "blocked_no_assumption")
        figure = entries["Figure_7_adjacency"].to_dict()["proposed_value"]
        self.assertEqual(figure["node_count"], 20)
        self.assertEqual(figure["edge_count"], 30)
        self.assertEqual(figure["graph_type"], "undirected_unweighted")
        self.assertEqual(figure["source"], "user_supplied_manual_extraction")
        self.assertFalse(figure["paper_recovery_claim"])
        legal = entries["legal_horizontal_destinations"].to_dict()["proposed_value"]
        self.assertEqual(legal["rule"], "neighbor_only_horizontal_legality")
        self.assertEqual(legal["source_item_id"], "Figure_7_adjacency")
        self.assertEqual(legal["source_assumption_status_required"], "approved")
        self.assertTrue(legal["no_self_offload"])
        self.assertFalse(legal["non_neighbor_horizontal_offload_allowed"])
        private = entries["EA_private_cpu_capacity"].to_dict()["proposed_value"]
        self.assertEqual(private["source"], "user_supplied_table4_ocr_extraction")
        self.assertEqual(private["frequency_ghz"], 5.0)
        self.assertEqual(private["slot_duration_seconds"], 0.1)
        self.assertEqual(private["derived_capacity_gcycles_per_slot"], 0.5)
        self.assertEqual(private["previous_runtime_default_gcycles_per_slot"], 32.0)
        self.assertEqual(private["previous_runtime_default_ratio_to_approved"], 64.0)
        self.assertFalse(private["runtime_patch_applied"])
        public = entries["EA_public_cpu_capacity"].to_dict()["proposed_value"]
        self.assertEqual(public["source"], "user_supplied_table4_ocr_extraction")
        self.assertEqual(public["frequency_ghz"], 5.0)
        self.assertEqual(public["slot_duration_seconds"], 0.1)
        self.assertEqual(public["derived_capacity_gcycles_per_slot"], 0.5)
        self.assertEqual(public["previous_runtime_default_gcycles_per_slot"], 64.0)
        self.assertEqual(public["previous_runtime_default_ratio_to_approved"], 128.0)
        self.assertFalse(public["runtime_patch_applied"])
        cloud = entries["cloud_cpu_capacity"].to_dict()["proposed_value"]
        self.assertEqual(cloud["source"], "user_supplied_table4_ocr_extraction")
        self.assertEqual(cloud["frequency_ghz"], 30.0)
        self.assertEqual(cloud["slot_duration_seconds"], 0.1)
        self.assertEqual(cloud["derived_capacity_gcycles_per_slot"], 3.0)
        self.assertEqual(cloud["previous_runtime_default_gcycles_per_slot"], 128.0)
        self.assertAlmostEqual(cloud["previous_runtime_default_ratio_to_approved"], 42.6666666667)
        self.assertFalse(cloud["runtime_patch_applied"])
        self.assertEqual(entries["timeout_value"].proposed_value, "")

    def test_proposed_values_remain_report_only(self) -> None:
        entries = {entry.item_id: entry for entry in build_registry_entries()}
        for item_id in [
            "cloud_data_rate",
            "multi_agent_aggregation_reduction_order",
        ]:
            self.assertEqual(entries[item_id].assumption_status, "proposed")
            self.assertFalse(entries[item_id].runtime_use_allowed)


if __name__ == "__main__":
    unittest.main()
