from __future__ import annotations

import unittest

from src.analysis.legality_evidence_expansion import LegalityEvidenceConfig, LegalitySnapshot, LegalityEvidenceReport, build_legality_evidence_report


class LegalityEvidenceSchemaUnitTests(unittest.TestCase):
    def test_config_uses_paper_default_grid(self) -> None:
        config = LegalityEvidenceConfig()
        self.assertEqual(config.feature_id, "048-legality-evidence-expansion")
        self.assertEqual(config.episode_length, 110)
        self.assertEqual(config.timeout_slots, 20)
        self.assertEqual(config.node_count, 20)
        self.assertEqual(config.arrival_probability, 0.5)
        self.assertEqual(list(config.seeds), [0, 1, 2])
        self.assertEqual(
            config.strategies,
            (
                "environment_default_policy_probe",
                "force_local_legal_probe",
                "force_horizontal_legal_probe",
                "force_vertical_legal_probe",
                "mixed_legal_round_robin_probe",
            ),
        )
        self.assertTrue(config.no_runtime_repair)
        self.assertTrue(config.no_training)
        self.assertTrue(config.passive_legality_capture)

    def test_legality_snapshot_schema(self) -> None:
        snapshot = LegalitySnapshot(
            strategy="environment_default_policy_probe",
            seed=0,
            slot=1,
            agent_id="1",
            task_id="task-1",
            selected_action="local",
            action_index=0,
            legal_local=True,
            legal_horizontal=False,
            legal_vertical=False,
            legal_action_mask={"local": True, "horizontal": False, "vertical": False},
            selected_was_legal=True,
            selected_illegal_reason=None,
            legal_horizontal_neighbors=["2"],
            horizontal_neighbor_count=1,
            vertical_available=True,
            cloud_available=True,
            private_queue_available=True,
            public_queue_available=False,
            legality_evidence_source="trace",
        )
        payload = snapshot.to_dict()
        for field in (
            "strategy",
            "seed",
            "slot",
            "agent_id",
            "task_id",
            "selected_action",
            "action_index",
            "legal_local",
            "legal_horizontal",
            "legal_vertical",
            "legal_action_mask",
            "selected_was_legal",
            "selected_illegal_reason",
            "legal_horizontal_neighbors",
            "horizontal_neighbor_count",
            "vertical_available",
            "cloud_available",
            "private_queue_available",
            "public_queue_available",
            "legality_evidence_source",
            "legality_snapshot_schema_version",
        ):
            self.assertIn(field, payload)

    def test_report_schema_exact_fields(self) -> None:
        report = build_legality_evidence_report()
        payload = report.to_dict()
        self.assertIn("legal_evidence_coverage_ratio", payload)
        self.assertIn("legality_evidence_coverage_summary", payload)
        self.assertIn("legal_evidence_coverage_ratio", payload["legality_evidence_coverage_summary"])
        self.assertIn("selected_illegal_action_count", payload)
        self.assertIn("selected_illegal_local_count", payload)
        self.assertIn("selected_illegal_horizontal_count", payload)
        self.assertIn("selected_illegal_vertical_count", payload)
        self.assertIn("selected_illegal_action_rate", payload)
        self.assertIn("selected_illegal_action_examples", payload)
        self.assertIn("selected_illegal_action_evidence_status", payload)
        self.assertEqual(payload["legal_evidence_coverage_ratio"], payload["legality_evidence_coverage_summary"]["legal_evidence_coverage_ratio"])

    def test_report_rejects_missing_nested_coverage_ratio(self) -> None:
        with self.assertRaises(ValueError):
            LegalityEvidenceReport(
                feature_id="048-legality-evidence-expansion",
                prerequisite_tags_verified=[],
                prior_feature_gates_verified=[],
                paper_default_runtime_verified={},
                legality_evidence_source="available",
                legality_snapshot_schema={"fields": [], "schema_version": 1},
                legal_evidence_coverage_ratio=1.0,
                legality_evidence_coverage_summary={"decision_opportunity_count": 1, "legality_snapshot_count": 1},
                per_strategy_seed_legality_coverage=[],
                action_mask_summary={},
                selected_illegal_action_summary={},
                selected_illegal_action_count=0,
                selected_illegal_local_count=0,
                selected_illegal_horizontal_count=0,
                selected_illegal_vertical_count=0,
                selected_illegal_action_rate=0.0,
                selected_illegal_action_examples=[],
                selected_illegal_action_evidence_status="available",
                behavior_equivalence_summary={"passed": True, "checks": []},
                exposure_matrix_unblocked=True,
                recommended_next_feature="Feature 049 - Exposure-Matrix Rerun with Legality Evidence",
                final_verdict="legality_evidence_ready_for_exposure_matrix_rerun",
            )

    def test_report_rejects_top_level_and_summary_ratio_contradiction(self) -> None:
        with self.assertRaises(ValueError):
            LegalityEvidenceReport(
                feature_id="048-legality-evidence-expansion",
                prerequisite_tags_verified=[],
                prior_feature_gates_verified=[],
                paper_default_runtime_verified={},
                legality_evidence_source="available",
                legality_snapshot_schema={"fields": [], "schema_version": 1},
                legal_evidence_coverage_ratio=1.0,
                legality_evidence_coverage_summary={"decision_opportunity_count": 1, "legality_snapshot_count": 1, "legal_evidence_coverage_ratio": 0.5},
                per_strategy_seed_legality_coverage=[],
                action_mask_summary={},
                selected_illegal_action_summary={},
                selected_illegal_action_count=0,
                selected_illegal_local_count=0,
                selected_illegal_horizontal_count=0,
                selected_illegal_vertical_count=0,
                selected_illegal_action_rate=0.0,
                selected_illegal_action_examples=[],
                selected_illegal_action_evidence_status="available",
                behavior_equivalence_summary={"passed": True, "checks": []},
                exposure_matrix_unblocked=True,
                recommended_next_feature="Feature 049 - Exposure-Matrix Rerun with Legality Evidence",
                final_verdict="legality_evidence_ready_for_exposure_matrix_rerun",
            )


if __name__ == "__main__":
    unittest.main()
