from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.analysis.user_approved_assumption_patch_registry.report import build_assumption_patch_report, write_assumption_patch_report
from src.analysis.user_approved_assumption_patch_registry.registry import build_user_approved_assumption_registry


class UserApprovedAssumptionPatchRegistryReportIntegrationTest(unittest.TestCase):
    def test_report_has_required_schema_and_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            registry_path = tmp_path / "resources/papers/hoodie/recovered/user-approved-assumption-registry.json"
            report = build_assumption_patch_report()
            json_path, md_path = write_assumption_patch_report(report, tmp_path / "artifacts/analysis/user-approved-assumption-patch-registry")

            self.assertEqual(report.final_verdict, "registry_created_with_runtime_approved_assumptions")
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            registry = build_user_approved_assumption_registry()
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            required = {
                "feature_id",
                "schema_version",
                "source_gates",
                "registry_path",
                "item_count",
                "status_counts",
                "runtime_usable_items",
                "proposed_items",
                "blocked_items",
                "rejected_items",
                "entries",
                "no_paper_recovery_claims",
                "no_runtime_behavior_change",
                "no_training_or_policy_drift",
                "no_dependency_drift",
                "final_verdict",
            }
            self.assertTrue(required.issubset(payload.keys()))
            self.assertEqual(payload["item_count"], 8)
            self.assertEqual(payload["status_counts"]["approved"], 3)
            self.assertEqual(payload["status_counts"]["proposed"], 4)
            self.assertEqual(payload["status_counts"]["blocked_no_assumption"], 1)
            self.assertEqual(len(payload["entries"]), 8)
            self.assertTrue(payload["no_paper_recovery_claims"])
            self.assertEqual([item["item_id"] for item in payload["runtime_usable_items"]], ["Figure_7_adjacency", "legal_horizontal_destinations", "EA_private_cpu_capacity"])
            self.assertEqual(payload["registry_path"], "resources/papers/hoodie/recovered/user-approved-assumption-registry.json")
            figure = next(item for item in payload["entries"] if item["item_id"] == "Figure_7_adjacency")
            self.assertEqual(figure["assumption_status"], "approved")
            self.assertTrue(figure["runtime_use_allowed"])
            self.assertFalse(figure["approval_required"])
            self.assertEqual(figure["approval_source"], "user_supplied_manual_extraction")
            self.assertEqual(figure["value_type"], "adjacency_matrix")
            self.assertTrue(figure["no_paper_recovery_claim"])
            payload_value = figure["proposed_value"]
            self.assertEqual(payload_value["node_count"], 20)
            self.assertEqual(payload_value["edge_count"], 30)
            self.assertEqual(payload_value["graph_type"], "undirected_unweighted")
            self.assertEqual(payload_value["source"], "user_supplied_manual_extraction")
            self.assertFalse(payload_value["paper_recovery_claim"])
            matrix = payload_value["adjacency_matrix"]
            self.assertEqual(len(matrix), 20)
            self.assertTrue(all(len(row) == 20 for row in matrix))
            self.assertTrue(all(matrix[i][i] == 0 for i in range(20)))
            self.assertTrue(all(matrix[i][j] == matrix[j][i] for i in range(20) for j in range(20)))
            self.assertTrue(all(sum(row) == 3 for row in matrix))
            self.assertEqual(sum(sum(row) for row in matrix) // 2, 30)
            legal = next(item for item in payload["entries"] if item["item_id"] == "legal_horizontal_destinations")
            self.assertEqual(legal["assumption_status"], "approved")
            self.assertTrue(legal["runtime_use_allowed"])
            self.assertFalse(legal["approval_required"])
            self.assertEqual(legal["approval_source"], "derived_from_user_approved_adjacency_neighbor_rule")
            legal_payload = legal["proposed_value"]
            self.assertEqual(legal_payload["rule"], "neighbor_only_horizontal_legality")
            self.assertEqual(legal_payload["source_item_id"], "Figure_7_adjacency")
            self.assertEqual(legal_payload["source_assumption_status_required"], "approved")
            self.assertEqual(legal_payload["node_order"], "1_to_20")
            self.assertTrue(legal_payload["no_self_offload"])
            self.assertFalse(legal_payload["non_neighbor_horizontal_offload_allowed"])
            self.assertTrue(legal_payload["vertical_cloud_offload_separate"])
            self.assertEqual(len(legal_payload["destinations"]), 20)
            self.assertEqual(legal_payload["destinations"]["1"], [6, 11, 16])
            self.assertEqual(legal_payload["destinations"]["20"], [5, 10, 15])
            private = next(item for item in payload["entries"] if item["item_id"] == "EA_private_cpu_capacity")
            self.assertEqual(private["assumption_status"], "approved")
            self.assertTrue(private["runtime_use_allowed"])
            self.assertFalse(private["approval_required"])
            self.assertEqual(private["approval_source"], "user_supplied_table4_ocr_extraction")
            private_payload = private["proposed_value"]
            self.assertEqual(private_payload["source"], "user_supplied_table4_ocr_extraction")
            self.assertEqual(private_payload["symbol"], "f_n^{EA,priv}")
            self.assertEqual(private_payload["frequency_ghz"], 5.0)
            self.assertEqual(private_payload["slot_duration_seconds"], 0.1)
            self.assertEqual(private_payload["derived_capacity_gcycles_per_slot"], 0.5)
            self.assertEqual(private_payload["previous_runtime_default_gcycles_per_slot"], 32.0)
            self.assertEqual(private_payload["previous_runtime_default_ratio_to_approved"], 64.0)
            self.assertFalse(private_payload["runtime_patch_applied"])
            self.assertFalse(private_payload["paper_recovery_claim"])

    def test_registry_json_parse_and_keys(self) -> None:
        payload = build_user_approved_assumption_registry()
        self.assertEqual(payload["feature_id"], "031-user-approved-assumption-patch-registry")
        self.assertEqual(payload["item_count"], 8)
        self.assertIn("entries", payload)
        self.assertEqual(len(payload["entries"]), 8)
        for entry in payload["entries"]:
            self.assertIn("no_paper_recovery_claim", entry)
            self.assertTrue(entry["no_paper_recovery_claim"])
            self.assertTrue(entry["rationale"])
            self.assertTrue(entry["scientific_risk"])
            self.assertTrue(entry["validation_plan"])
            self.assertIsInstance(entry["affected_runtime_components"], list)
            self.assertGreater(len(entry["affected_runtime_components"]), 0)
        figure = next(item for item in payload["entries"] if item["item_id"] == "Figure_7_adjacency")
        self.assertEqual(figure["assumption_status"], "approved")
        self.assertTrue(figure["runtime_use_allowed"])
        self.assertFalse(figure["approval_required"])
        self.assertEqual(figure["approval_source"], "user_supplied_manual_extraction")
        legal = next(item for item in payload["entries"] if item["item_id"] == "legal_horizontal_destinations")
        self.assertEqual(legal["assumption_status"], "approved")
        self.assertTrue(legal["runtime_use_allowed"])
        self.assertFalse(legal["approval_required"])
        self.assertEqual(legal["approval_source"], "derived_from_user_approved_adjacency_neighbor_rule")
        private = next(item for item in payload["entries"] if item["item_id"] == "EA_private_cpu_capacity")
        self.assertEqual(private["assumption_status"], "approved")
        self.assertTrue(private["runtime_use_allowed"])
        self.assertFalse(private["approval_required"])
        self.assertEqual(private["approval_source"], "user_supplied_table4_ocr_extraction")


if __name__ == "__main__":
    unittest.main()
