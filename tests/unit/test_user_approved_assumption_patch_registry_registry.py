from __future__ import annotations

import unittest

from src.analysis.user_approved_assumption_patch_registry.registry import build_registry_entries


class UserApprovedAssumptionPatchRegistryRegistryTest(unittest.TestCase):
    def test_entries_have_required_semantic_fields(self) -> None:
        entries = build_registry_entries()
        for entry in entries:
            payload = entry.to_dict()
            self.assertTrue(payload["no_paper_recovery_claim"])
            self.assertTrue(str(payload["rationale"]).strip())
            self.assertTrue(str(payload["scientific_risk"]).strip())
            self.assertTrue(str(payload["validation_plan"]).strip())
            self.assertIsInstance(payload["affected_runtime_components"], list)
            self.assertGreater(len(payload["affected_runtime_components"]), 0)

    def test_initial_statuses_match_feature_031_policy(self) -> None:
        entries = {entry.item_id: entry for entry in build_registry_entries()}
        figure = entries["Figure_7_adjacency"]
        self.assertEqual(figure.assumption_status, "approved")
        self.assertTrue(figure.runtime_use_allowed)
        self.assertFalse(figure.approval_required)
        self.assertEqual(figure.approval_source, "user_supplied_manual_extraction")
        self.assertEqual(figure.value_type, "adjacency_matrix")
        self.assertTrue(figure.no_paper_recovery_claim)
        payload = figure.to_dict()["proposed_value"]
        self.assertEqual(payload["node_count"], 20)
        self.assertEqual(payload["node_order"], "1_to_20")
        self.assertEqual(payload["graph_type"], "undirected_unweighted")
        self.assertEqual(payload["edge_count"], 30)
        self.assertEqual(payload["degree_regular"], 3)
        self.assertTrue(payload["symmetric_required"])
        self.assertTrue(payload["zero_diagonal_required"])
        self.assertEqual(payload["source"], "user_supplied_manual_extraction")
        self.assertFalse(payload["paper_recovery_claim"])
        matrix = payload["adjacency_matrix"]
        edges = payload["edge_list"]
        self.assertEqual(len(matrix), 20)
        self.assertTrue(all(len(row) == 20 for row in matrix))
        self.assertTrue(all(matrix[i][i] == 0 for i in range(20)))
        self.assertTrue(all(matrix[i][j] == matrix[j][i] for i in range(20) for j in range(20)))
        self.assertTrue(all(sum(row) == 3 for row in matrix))
        self.assertEqual(sum(sum(row) for row in matrix) // 2, 30)
        derived_edges = sorted({tuple(sorted((i + 1, j + 1))) for i, row in enumerate(matrix) for j, value in enumerate(row) if value and i < j})
        self.assertEqual(derived_edges, sorted(tuple(sorted(edge)) for edge in edges))

        legal = entries["legal_horizontal_destinations"]
        self.assertEqual(legal.assumption_status, "approved")
        self.assertTrue(legal.runtime_use_allowed)
        self.assertFalse(legal.approval_required)
        self.assertEqual(legal.approval_source, "derived_from_user_approved_adjacency_neighbor_rule")
        self.assertEqual(legal.value_type, "horizontal_destination_rule")
        self.assertTrue(legal.no_paper_recovery_claim)
        legal_payload = legal.to_dict()["proposed_value"]
        self.assertEqual(legal_payload["rule"], "neighbor_only_horizontal_legality")
        self.assertEqual(legal_payload["source_item_id"], "Figure_7_adjacency")
        self.assertEqual(legal_payload["source_assumption_status_required"], "approved")
        self.assertEqual(legal_payload["node_order"], "1_to_20")
        self.assertTrue(legal_payload["no_self_offload"])
        self.assertFalse(legal_payload["non_neighbor_horizontal_offload_allowed"])
        self.assertTrue(legal_payload["vertical_cloud_offload_separate"])
        destinations = legal_payload["destinations"]
        self.assertEqual(len(destinations), 20)
        self.assertEqual(destinations["1"], [6, 11, 16])
        self.assertEqual(destinations["20"], [5, 10, 15])
        self.assertTrue(all(len(destinations[str(node)]) == 3 for node in range(1, 21)))
        self.assertTrue(all(str(node) not in {str(dest) for dest in destinations[str(node)]} for node in range(1, 21)))

        timeout = entries["timeout_value"]
        self.assertEqual(timeout.assumption_status, "approved")
        self.assertTrue(timeout.runtime_use_allowed)
        self.assertFalse(timeout.approval_required)
        self.assertEqual(timeout.approval_source, "user_supplied_table4_ocr_extraction")
        self.assertEqual(timeout.value_type, "rule")
        self.assertTrue(timeout.no_paper_recovery_claim)
        timeout_payload = timeout.to_dict()["proposed_value"]
        self.assertEqual(timeout_payload["source"], "user_supplied_table4_ocr_extraction")
        self.assertEqual(timeout_payload["symbol"], "φ_n")
        self.assertEqual(timeout_payload["timeout_slots"], 20)
        self.assertEqual(timeout_payload["slot_duration_seconds"], 0.1)
        self.assertEqual(timeout_payload["timeout_seconds"], 2.0)
        self.assertEqual(timeout_payload["conversion_formula"], "timeout_seconds = timeout_slots * slot_duration_seconds")
        self.assertEqual(timeout_payload["interpretation"], "task timeout/drop deadline threshold")
        self.assertFalse(timeout_payload["runtime_patch_applied"])
        self.assertFalse(timeout_payload["paper_recovery_claim"])
        private = entries["EA_private_cpu_capacity"]
        self.assertEqual(private.assumption_status, "approved")
        self.assertTrue(private.runtime_use_allowed)
        self.assertFalse(private.approval_required)
        self.assertEqual(private.approval_source, "user_supplied_table4_ocr_extraction")
        self.assertEqual(private.value_type, "numeric_derived_capacity")
        self.assertTrue(private.no_paper_recovery_claim)
        private_payload = private.to_dict()["proposed_value"]
        self.assertEqual(private_payload["source"], "user_supplied_table4_ocr_extraction")
        self.assertEqual(private_payload["symbol"], "f_n^{EA,priv}")
        self.assertEqual(private_payload["frequency_ghz"], 5.0)
        self.assertEqual(private_payload["slot_duration_seconds"], 0.1)
        self.assertEqual(private_payload["derived_capacity_gcycles_per_slot"], 0.5)
        self.assertEqual(private_payload["conversion_formula"], "derived_capacity_gcycles_per_slot = frequency_ghz * slot_duration_seconds")
        self.assertEqual(private_payload["previous_runtime_default_gcycles_per_slot"], 32.0)
        self.assertEqual(private_payload["previous_runtime_default_ratio_to_approved"], 64.0)
        self.assertFalse(private_payload["runtime_patch_applied"])
        self.assertFalse(private_payload["paper_recovery_claim"])

        for item_id in [
            "multi_agent_aggregation_reduction_order",
        ]:
            self.assertEqual(entries[item_id].assumption_status, "proposed")
            self.assertFalse(entries[item_id].runtime_use_allowed)
            self.assertTrue(entries[item_id].approval_required)

        public = entries["EA_public_cpu_capacity"]
        self.assertEqual(public.assumption_status, "approved")
        self.assertTrue(public.runtime_use_allowed)
        self.assertFalse(public.approval_required)
        self.assertEqual(public.approval_source, "user_supplied_table4_ocr_extraction")
        self.assertEqual(public.value_type, "numeric_derived_capacity")
        self.assertTrue(public.no_paper_recovery_claim)
        self.assertEqual(public.paper_status, "unrecoverable_after_evidence_exhaustion")
        self.assertEqual(public.paper_confidence, "invalid")
        public_payload = public.to_dict()["proposed_value"]
        self.assertEqual(public_payload["source"], "user_supplied_table4_ocr_extraction")
        self.assertEqual(public_payload["symbol"], "f_n^{EA,pub}")
        self.assertEqual(public_payload["frequency_ghz"], 5.0)
        self.assertEqual(public_payload["slot_duration_seconds"], 0.1)
        self.assertEqual(public_payload["derived_capacity_gcycles_per_slot"], 0.5)
        self.assertEqual(public_payload["conversion_formula"], "derived_capacity_gcycles_per_slot = frequency_ghz * slot_duration_seconds")
        self.assertEqual(public_payload["previous_runtime_default_gcycles_per_slot"], 64.0)
        self.assertEqual(public_payload["previous_runtime_default_ratio_to_approved"], 128.0)
        self.assertFalse(public_payload["runtime_patch_applied"])
        self.assertFalse(public_payload["paper_recovery_claim"])

        cloud = entries["cloud_cpu_capacity"]
        self.assertEqual(cloud.assumption_status, "approved")
        self.assertTrue(cloud.runtime_use_allowed)
        self.assertFalse(cloud.approval_required)
        self.assertEqual(cloud.approval_source, "user_supplied_table4_ocr_extraction")
        self.assertEqual(cloud.value_type, "numeric_derived_capacity")
        self.assertTrue(cloud.no_paper_recovery_claim)
        self.assertEqual(cloud.paper_status, "unrecoverable_after_evidence_exhaustion")
        self.assertEqual(cloud.paper_confidence, "invalid")
        cloud_payload = cloud.to_dict()["proposed_value"]
        self.assertEqual(cloud_payload["source"], "user_supplied_table4_ocr_extraction")
        self.assertEqual(cloud_payload["symbol"], "f^{Cloud}")
        self.assertEqual(cloud_payload["frequency_ghz"], 30.0)
        self.assertEqual(cloud_payload["slot_duration_seconds"], 0.1)
        self.assertEqual(cloud_payload["derived_capacity_gcycles_per_slot"], 3.0)
        self.assertEqual(cloud_payload["conversion_formula"], "derived_capacity_gcycles_per_slot = frequency_ghz * slot_duration_seconds")
        self.assertEqual(cloud_payload["previous_runtime_default_gcycles_per_slot"], 128.0)
        self.assertAlmostEqual(cloud_payload["previous_runtime_default_ratio_to_approved"], 42.6666666667)
        self.assertFalse(cloud_payload["runtime_patch_applied"])
        self.assertFalse(cloud_payload["paper_recovery_claim"])

        data_rate = entries["cloud_data_rate"]
        self.assertEqual(data_rate.assumption_status, "approved")
        self.assertTrue(data_rate.runtime_use_allowed)
        self.assertFalse(data_rate.approval_required)
        self.assertEqual(data_rate.approval_source, "user_supplied_table4_ocr_extraction")
        self.assertEqual(data_rate.value_type, "numeric_data_rate")
        self.assertTrue(data_rate.no_paper_recovery_claim)
        self.assertEqual(data_rate.paper_status, "unrecoverable_after_evidence_exhaustion")
        self.assertEqual(data_rate.paper_confidence, "invalid")
        data_payload = data_rate.to_dict()["proposed_value"]
        self.assertEqual(data_payload["source"], "user_supplied_table4_ocr_extraction")
        self.assertEqual(data_payload["symbol"], "R_V")
        self.assertEqual(data_payload["rate_mbps"], 10.0)
        self.assertEqual(data_payload["rate_bps"], 10000000.0)
        self.assertEqual(data_payload["interpretation"], "cloud-facing vertical offload data rate")
        self.assertFalse(data_payload["separate_cloud_specific_rate_claim"])
        self.assertFalse(data_payload["runtime_patch_applied"])
        self.assertFalse(data_payload["paper_recovery_claim"])

    def test_runtime_use_requires_approved_status(self) -> None:
        entries = build_registry_entries()
        self.assertEqual(sum(1 for entry in entries if entry.runtime_use_allowed), 7)
        approved_ids = [entry.item_id for entry in entries if entry.assumption_status == "approved"]
        self.assertEqual(approved_ids, ["Figure_7_adjacency", "legal_horizontal_destinations", "EA_private_cpu_capacity", "EA_public_cpu_capacity", "cloud_cpu_capacity", "cloud_data_rate", "timeout_value"])
        self.assertTrue(all(entry.assumption_status == "approved" or not entry.runtime_use_allowed for entry in entries))

    def test_semantic_fields_reject_empty_values(self) -> None:
        from src.analysis.user_approved_assumption_patch_registry.report import _validate_non_empty_fields

        with self.assertRaises(ValueError):
            _validate_non_empty_fields(
                [
                    {
                        "item_id": "broken",
                        "rationale": "",
                        "scientific_risk": "risk",
                        "affected_runtime_components": ["x"],
                        "validation_plan": "plan",
                    }
                ]
            )


if __name__ == "__main__":
    unittest.main()
