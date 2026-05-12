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
        self.assertEqual(entries["cloud_data_rate"].assumption_status, "approved")
        self.assertTrue(entries["cloud_data_rate"].runtime_use_allowed)
        self.assertEqual(entries["timeout_value"].assumption_status, "approved")
        self.assertTrue(entries["timeout_value"].runtime_use_allowed)
        self.assertEqual(entries["multi_agent_aggregation_reduction_order"].assumption_status, "approved")
        self.assertTrue(entries["multi_agent_aggregation_reduction_order"].runtime_use_allowed)
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
        data_rate = entries["cloud_data_rate"].to_dict()["proposed_value"]
        self.assertEqual(data_rate["source"], "user_supplied_table4_ocr_extraction")
        self.assertEqual(data_rate["symbol"], "R_V")
        self.assertEqual(data_rate["rate_mbps"], 10.0)
        self.assertEqual(data_rate["rate_bps"], 10000000.0)
        self.assertEqual(data_rate["interpretation"], "cloud-facing vertical offload data rate")
        self.assertFalse(data_rate["separate_cloud_specific_rate_claim"])
        self.assertFalse(data_rate["runtime_patch_applied"])
        timeout = entries["timeout_value"].to_dict()["proposed_value"]
        self.assertEqual(timeout["source"], "user_supplied_table4_ocr_extraction")
        self.assertEqual(timeout["symbol"], "φ_n")
        self.assertEqual(timeout["timeout_slots"], 20)
        self.assertEqual(timeout["slot_duration_seconds"], 0.1)
        self.assertEqual(timeout["timeout_seconds"], 2.0)
        self.assertEqual(timeout["conversion_formula"], "timeout_seconds = timeout_slots * slot_duration_seconds")
        self.assertEqual(timeout["interpretation"], "task timeout/drop deadline threshold")
        self.assertFalse(timeout["runtime_patch_applied"])
        aggregation = entries["multi_agent_aggregation_reduction_order"].to_dict()["proposed_value"]
        self.assertEqual(aggregation["source"], "user_approved_safe_reporting_rule")
        self.assertEqual(aggregation["rule"], "per_agent_episode_sum_then_arithmetic_mean_across_agents")
        self.assertEqual(aggregation["agent_level_reduction"], "sum terminal task rewards per agent per episode")
        self.assertEqual(aggregation["cross_agent_reduction"], "arithmetic_mean")
        self.assertEqual(aggregation["no_task_slots"], "excluded_or_omitted_not_zero")
        self.assertEqual(aggregation["nan_policy"], "exclude_from_numeric_aggregation")
        self.assertFalse(aggregation["slot_level_direct_average"])
        self.assertFalse(aggregation["seed_or_run_level_aggregation_in_scope"])
        self.assertFalse(aggregation["runtime_patch_applied"])

    def test_proposed_values_remain_report_only(self) -> None:
        entries = {entry.item_id: entry for entry in build_registry_entries()}
        self.assertEqual(entries["multi_agent_aggregation_reduction_order"].assumption_status, "approved")
        self.assertTrue(entries["multi_agent_aggregation_reduction_order"].runtime_use_allowed)


if __name__ == "__main__":
    unittest.main()
