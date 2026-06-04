from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.analysis.hoodie_system_model_fidelity_gate.config import (
    ACTIVE_POLICIES,
    FEATURE_085_AUDIT_DIR,
    INVALID_LABELS,
    READY_STATUS,
    REQUIRED_MECHANISM_IDS,
    REQUIRED_METRICS,
)
from src.analysis.hoodie_system_model_fidelity_gate.report import build_feature_086_report
from src.analysis.hoodie_system_model_fidelity_gate.runner import generate_feature_086_artifacts, validate_feature_086_artifacts


class HoodieSystemModelFidelityGateTests(unittest.TestCase):
    def test_report_uses_required_policy_set_and_no_legacy_labels(self) -> None:
        report = build_feature_086_report()
        self.assertEqual(report.status, READY_STATUS)
        self.assertEqual(report.verdict, READY_STATUS)
        self.assertEqual(report.active_policies, ACTIVE_POLICIES)
        invalid_joined = " ".join(report.invalid_label_check)
        for label in INVALID_LABELS:
            self.assertNotIn(label, invalid_joined)
        self.assertEqual(report.blocked_mechanisms, ())
        self.assertTrue(report.output_comparison_ready)

    def test_report_covers_required_mechanisms_and_metrics(self) -> None:
        report = build_feature_086_report()
        self.assertEqual({row.mechanism_id for row in report.mechanism_coverage}, set(REQUIRED_MECHANISM_IDS))
        self.assertTrue(all(row.status in {"exact", "approximate_documented"} for row in report.mechanism_coverage))
        self.assertEqual({row.metric for row in report.metric_readiness_matrix}, set(REQUIRED_METRICS))
        classifications = {row.metric: row.classification for row in report.metric_readiness_matrix}
        self.assertEqual(classifications["task_completion_delay"], "paper_primary_metric")
        self.assertEqual(classifications["task_drop_ratio"], "paper_primary_metric")
        self.assertEqual(classifications["queue_stability_score"], "repository_diagnostic_metric")
        self.assertEqual(classifications["illegal_action_rejection_count"], "repository_diagnostic_metric")
        self.assertTrue(any("no full empirical hoodie reproduction" in item.lower() for item in report.claim_boundary))

    def test_hoodie_mleo_tie_evidence_is_loaded_from_feature_085_bundle(self) -> None:
        report = build_feature_086_report()
        tie = report.hoodie_mleo_tie_evidence
        self.assertEqual(tie.source_artifact_dir, str(FEATURE_085_AUDIT_DIR))
        self.assertEqual(tie.matching_rows, 1080)
        self.assertEqual(tie.differing_rows, 432)
        self.assertEqual(
            tie.identical_scenarios,
            (
                "cloud_vertical_fallback",
                "illegal_horizontal_destination_attempt",
                "legal_horizontal_offload",
                "light_load_no_deadline_pressure",
                "mixed_local_horizontal_cloud_candidates",
            ),
        )
        self.assertEqual(tie.divergent_scenarios, ("tight_deadline_pressure", "timeout_drop_case"))
        self.assertEqual(tie.divergent_action_counts["tight_deadline_pressure"], {"vertical->local": 216})
        self.assertEqual(tie.divergent_action_counts["timeout_drop_case"], {"vertical->local": 216})

    def test_artifact_bundle_can_be_generated_and_validated(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "feature_086"
            payload, paths = generate_feature_086_artifacts(output_dir)
            self.assertEqual(payload["verdict"], READY_STATUS)
            expected = {
                "mechanism_coverage.json",
                "mechanism_coverage.csv",
                "system_model_gap_matrix.json",
                "system_model_gap_matrix.md",
                "metric_readiness_matrix.json",
                "metric_readiness_matrix.md",
                "scenario_mechanism_coverage.json",
                "hoodie_mleo_tie_evidence.json",
                "feature_086_system_model_fidelity_report.json",
                "feature_086_system_model_fidelity_report.md",
            }
            self.assertEqual(set(paths), expected)
            for path in paths.values():
                self.assertTrue(path.exists())
            validated = validate_feature_086_artifacts(output_dir)
            self.assertTrue(validated["validated"])
            report_payload = json.loads(paths["feature_086_system_model_fidelity_report.json"].read_text(encoding="utf-8"))
            self.assertEqual(report_payload["verdict"], READY_STATUS)
            self.assertEqual(report_payload["active_policies"], list(ACTIVE_POLICIES))
            self.assertIn("Feature 086 HOODIE System-Model Fidelity Gate Report", paths["feature_086_system_model_fidelity_report.md"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
