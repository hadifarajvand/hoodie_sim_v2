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

        self.assertEqual(entries["legal_horizontal_destinations"].assumption_status, "blocked_no_assumption")
        self.assertEqual(entries["timeout_value"].assumption_status, "blocked_no_assumption")
        for item_id in [
            "EA_private_cpu_capacity",
            "EA_public_cpu_capacity",
            "cloud_cpu_capacity",
            "cloud_data_rate",
            "multi_agent_aggregation_reduction_order",
        ]:
            self.assertEqual(entries[item_id].assumption_status, "proposed")
            self.assertFalse(entries[item_id].runtime_use_allowed)
            self.assertTrue(entries[item_id].approval_required)

    def test_runtime_use_requires_approved_status(self) -> None:
        entries = build_registry_entries()
        self.assertEqual(sum(1 for entry in entries if entry.runtime_use_allowed), 1)
        self.assertTrue(all(entry.assumption_status == "approved" or not entry.runtime_use_allowed for entry in entries))
        self.assertTrue(any(entry.assumption_status == "approved" for entry in entries))

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
