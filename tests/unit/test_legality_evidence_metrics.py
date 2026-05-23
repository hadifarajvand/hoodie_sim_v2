from __future__ import annotations

import unittest

from src.analysis.legality_evidence_expansion import LegalityEvidenceReport


class LegalityEvidenceMetricsUnitTests(unittest.TestCase):
    def test_missing_legality_evidence_uses_null_not_fake_zero(self) -> None:
        report = LegalityEvidenceReport(
            feature_id="048-legality-evidence-expansion",
            prerequisite_tags_verified=[{"name": "branch", "verified": True, "details": ""}],
            prior_feature_gates_verified=[],
            paper_default_runtime_verified={},
            legality_evidence_source="unavailable",
            legality_snapshot_schema={"fields": [], "schema_version": 1},
            legal_evidence_coverage_ratio=0.0,
            legality_evidence_coverage_summary={
                "decision_opportunity_count": 10,
                "legality_snapshot_count": 0,
                "legal_evidence_coverage_ratio": 0.0,
                "evidence_status": "unavailable",
                "reason": "no snapshots",
            },
            per_strategy_seed_legality_coverage=[],
            action_mask_summary={},
            selected_illegal_action_summary={},
            selected_illegal_action_count=None,
            selected_illegal_local_count=None,
            selected_illegal_horizontal_count=None,
            selected_illegal_vertical_count=None,
            selected_illegal_action_rate=None,
            selected_illegal_action_examples=[],
            selected_illegal_action_evidence_status="unavailable",
            behavior_equivalence_summary={"passed": True, "checks": []},
            exposure_matrix_unblocked=False,
            recommended_next_feature="public legality helper feature before exposure-matrix rerun",
            final_verdict="legality_evidence_unavailable_requires_runtime_public_helper",
        )
        payload = report.to_dict()
        self.assertIsNone(payload["selected_illegal_action_count"])
        self.assertEqual(payload["selected_illegal_action_examples"], [])

    def test_selected_illegal_action_rate_uses_selected_action_count_denominator(self) -> None:
        report = LegalityEvidenceReport(
            feature_id="048-legality-evidence-expansion",
            prerequisite_tags_verified=[{"name": "branch", "verified": True, "details": ""}],
            prior_feature_gates_verified=[],
            paper_default_runtime_verified={},
            legality_evidence_source="available",
            legality_snapshot_schema={"fields": [], "schema_version": 1},
            legal_evidence_coverage_ratio=1.0,
            legality_evidence_coverage_summary={
                "decision_opportunity_count": 2,
                "legality_snapshot_count": 2,
                "legal_evidence_coverage_ratio": 1.0,
                "evidence_status": "available",
                "reason": "captured",
            },
            per_strategy_seed_legality_coverage=[],
            action_mask_summary={},
            selected_illegal_action_summary={},
            selected_illegal_action_count=1,
            selected_illegal_local_count=1,
            selected_illegal_horizontal_count=0,
            selected_illegal_vertical_count=0,
            selected_illegal_action_rate=0.5,
            selected_illegal_action_examples=[],
            selected_illegal_action_evidence_status="available",
            behavior_equivalence_summary={"passed": True, "checks": []},
            exposure_matrix_unblocked=True,
            recommended_next_feature="Feature 049 - Exposure-Matrix Rerun with Legality Evidence",
            final_verdict="legality_evidence_ready_for_exposure_matrix_rerun",
        )
        self.assertEqual(report.to_dict()["selected_illegal_action_rate"], 0.5)

    def test_selected_illegal_action_count_computed_when_evidence_exists(self) -> None:
        report = LegalityEvidenceReport(
            feature_id="048-legality-evidence-expansion",
            prerequisite_tags_verified=[{"name": "branch", "verified": True, "details": ""}],
            prior_feature_gates_verified=[],
            paper_default_runtime_verified={},
            legality_evidence_source="available",
            legality_snapshot_schema={"fields": [], "schema_version": 1},
            legal_evidence_coverage_ratio=1.0,
            legality_evidence_coverage_summary={
                "decision_opportunity_count": 2,
                "legality_snapshot_count": 2,
                "legal_evidence_coverage_ratio": 1.0,
                "evidence_status": "available",
                "reason": "captured",
            },
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
        self.assertEqual(report.selected_illegal_action_count, 0)

    def test_selected_illegal_action_count_null_when_evidence_unavailable(self) -> None:
        report = LegalityEvidenceReport(
            feature_id="048-legality-evidence-expansion",
            prerequisite_tags_verified=[{"name": "branch", "verified": True, "details": ""}],
            prior_feature_gates_verified=[],
            paper_default_runtime_verified={},
            legality_evidence_source="unavailable",
            legality_snapshot_schema={"fields": [], "schema_version": 1},
            legal_evidence_coverage_ratio=None,
            legality_evidence_coverage_summary={
                "decision_opportunity_count": 0,
                "legality_snapshot_count": 0,
                "legal_evidence_coverage_ratio": None,
                "evidence_status": "unavailable",
                "reason": "no opportunities",
            },
            per_strategy_seed_legality_coverage=[],
            action_mask_summary={},
            selected_illegal_action_summary={},
            selected_illegal_action_count=None,
            selected_illegal_local_count=None,
            selected_illegal_horizontal_count=None,
            selected_illegal_vertical_count=None,
            selected_illegal_action_rate=None,
            selected_illegal_action_examples=[],
            selected_illegal_action_evidence_status="unavailable",
            behavior_equivalence_summary={"passed": True, "checks": []},
            exposure_matrix_unblocked=False,
            recommended_next_feature="public legality helper feature before exposure-matrix rerun",
            final_verdict="legality_evidence_unavailable_requires_runtime_public_helper",
        )
        self.assertIsNone(report.selected_illegal_action_count)

    def test_feature_049_not_recommended_when_coverage_ratio_zero(self) -> None:
        report = LegalityEvidenceReport(
            feature_id="048-legality-evidence-expansion",
            prerequisite_tags_verified=[{"name": "branch", "verified": True, "details": ""}],
            prior_feature_gates_verified=[],
            paper_default_runtime_verified={},
            legality_evidence_source="available",
            legality_snapshot_schema={"fields": [], "schema_version": 1},
            legal_evidence_coverage_ratio=0.0,
            legality_evidence_coverage_summary={
                "decision_opportunity_count": 10,
                "legality_snapshot_count": 0,
                "legal_evidence_coverage_ratio": 0.0,
                "evidence_status": "unavailable",
                "reason": "known opportunities, no snapshots",
            },
            per_strategy_seed_legality_coverage=[],
            action_mask_summary={},
            selected_illegal_action_summary={},
            selected_illegal_action_count=None,
            selected_illegal_local_count=None,
            selected_illegal_horizontal_count=None,
            selected_illegal_vertical_count=None,
            selected_illegal_action_rate=None,
            selected_illegal_action_examples=[],
            selected_illegal_action_evidence_status="unavailable",
            behavior_equivalence_summary={"passed": True, "checks": []},
            exposure_matrix_unblocked=False,
            recommended_next_feature="public legality helper feature before exposure-matrix rerun",
            final_verdict="legality_evidence_unavailable_requires_runtime_public_helper",
        )
        payload = report.to_dict()
        self.assertEqual(payload["final_verdict"], "legality_evidence_unavailable_requires_runtime_public_helper")
        self.assertNotEqual(payload["recommended_next_feature"], "Feature 049 - Exposure-Matrix Rerun with Legality Evidence")

    def test_feature_049_not_recommended_when_coverage_ratio_null(self) -> None:
        report = LegalityEvidenceReport(
            feature_id="048-legality-evidence-expansion",
            prerequisite_tags_verified=[{"name": "branch", "verified": True, "details": ""}],
            prior_feature_gates_verified=[],
            paper_default_runtime_verified={},
            legality_evidence_source="available",
            legality_snapshot_schema={"fields": [], "schema_version": 1},
            legal_evidence_coverage_ratio=None,
            legality_evidence_coverage_summary={
                "decision_opportunity_count": 0,
                "legality_snapshot_count": 0,
                "legal_evidence_coverage_ratio": None,
                "evidence_status": "unavailable",
                "reason": "no decision opportunities",
            },
            per_strategy_seed_legality_coverage=[],
            action_mask_summary={},
            selected_illegal_action_summary={},
            selected_illegal_action_count=None,
            selected_illegal_local_count=None,
            selected_illegal_horizontal_count=None,
            selected_illegal_vertical_count=None,
            selected_illegal_action_rate=None,
            selected_illegal_action_examples=[],
            selected_illegal_action_evidence_status="unavailable",
            behavior_equivalence_summary={"passed": True, "checks": []},
            exposure_matrix_unblocked=False,
            recommended_next_feature="public legality helper feature before exposure-matrix rerun",
            final_verdict="legality_evidence_unavailable_requires_runtime_public_helper",
        )
        payload = report.to_dict()
        self.assertIsNone(payload["legal_evidence_coverage_ratio"])
        self.assertNotEqual(payload["recommended_next_feature"], "Feature 049 - Exposure-Matrix Rerun with Legality Evidence")


if __name__ == "__main__":
    unittest.main()
