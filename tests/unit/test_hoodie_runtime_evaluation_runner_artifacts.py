from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.analysis.hoodie_runtime_evaluation_runner.config import REQUIRED_POLICIES
from src.analysis.hoodie_runtime_evaluation_runner.runner import (
    generate_hoodie_runtime_evaluation_artifacts,
    validate_hoodie_runtime_evaluation_artifacts,
)


class HoodieRuntimeEvaluationRunnerArtifactTests(unittest.TestCase):
    def test_artifact_bundle_is_written_with_expected_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/feature_085_full_audit"
            report, paths, manifest = generate_hoodie_runtime_evaluation_artifacts(output_dir)

            required_names = {
                "raw_rows.json",
                "raw_rows.csv",
                "aggregate_by_policy.json",
                "aggregate_by_policy.csv",
                "ranking_by_metric.json",
                "ranking_by_metric.csv",
                "feature_085_audit_report.json",
                "feature_085_audit_report.md",
                "execution_manifest.json",
            }
            self.assertEqual(set(paths), required_names)
            for path in paths.values():
                self.assertTrue(path.exists(), path)

            raw_payload = json.loads(paths["raw_rows.json"].read_text(encoding="utf-8"))
            aggregate_payload = json.loads(paths["aggregate_by_policy.json"].read_text(encoding="utf-8"))
            ranking_payload = json.loads(paths["ranking_by_metric.json"].read_text(encoding="utf-8"))
            report_payload = json.loads(paths["feature_085_audit_report.json"].read_text(encoding="utf-8"))
            manifest_payload = json.loads(paths["execution_manifest.json"].read_text(encoding="utf-8"))

            self.assertEqual(raw_payload["count"], 10584)
            self.assertEqual(len(raw_payload["rows"]), 10584)
            self.assertEqual(len(aggregate_payload["rows"]), 7)
            self.assertEqual(set(ranking_payload["ranking_tables"]), {
                "task_completion_delay",
                "task_drop_ratio",
                "completion_rate",
                "timeout_drop_rate",
                "unavailable_drop_rate",
                "deadline_violation_rate",
                "average_reward",
                "total_reward",
                "throughput",
                "queue_stability_score",
                "illegal_action_rejection_count",
            })
            self.assertEqual(manifest_payload["raw_row_count"], 10584)
            self.assertEqual(manifest_payload["feature"], "085")
            self.assertEqual(manifest_payload["policy_count"], 7)
            self.assertEqual(manifest_payload["scenario_count"], 7)
            self.assertEqual(manifest_payload["metric_count"], 11)
            self.assertEqual(manifest_payload["compatibility_mode_policies"], [])
            self.assertEqual(set(row["policy"] for row in manifest_payload["policy_coverage"]), set(REQUIRED_POLICIES))
            for key, proof in manifest_payload["identity_proof"].items():
                if key == "hoodie_vs_mleo":
                    self.assertFalse(proof["different"], key)
                    self.assertEqual(proof["metrics"], [], key)
                else:
                    self.assertTrue(proof["different"], key)
                    self.assertTrue(proof["metrics"], key)
            aggregate_rows = {row["policy"]: row for row in aggregate_payload["rows"]}
            self.assertNotEqual(aggregate_rows["HOODIE"]["total_reward"], aggregate_rows["RO"]["total_reward"])
            self.assertNotEqual(aggregate_rows["HOODIE"]["total_reward"], aggregate_rows["FLC"]["total_reward"])
            self.assertNotEqual(aggregate_rows["HOODIE"]["total_reward"], aggregate_rows["VO"]["total_reward"])
            self.assertNotEqual(aggregate_rows["HOODIE"]["total_reward"], aggregate_rows["HO"]["total_reward"])
            self.assertNotEqual(aggregate_rows["HOODIE"]["total_reward"], aggregate_rows["BCO"]["total_reward"])
            self.assertEqual(aggregate_rows["HOODIE"]["total_reward"], aggregate_rows["MLEO"]["total_reward"])
            self.assertEqual(report_payload["feature_id"], "085-hoodie-paper-baseline-fidelity-audit")
            self.assertEqual(report_payload["status"], "hoodie_paper_baseline_fidelity_audit_ready")
            self.assertTrue(report_payload["passed"])
            self.assertEqual(report_payload["readiness_level"], "fully_implemented")
            self.assertFalse(report_payload["compatibility_mode_used"])
            self.assertEqual(report.status, "hoodie_paper_baseline_fidelity_audit_ready")
            self.assertTrue(report.passed)

            markdown = paths["feature_085_audit_report.md"].read_text(encoding="utf-8")
            self.assertIn("Feature 085 HOODIE Baseline Fidelity Audit Artifact Bundle", markdown)
            self.assertIn("raw_row_count: `10584`", markdown)
            self.assertIn("HOODIE", markdown)
            self.assertIn("RO", markdown)
            self.assertIn("MLEO", markdown)
            self.assertNotIn("ORIGINAL_HOODIE_BASELINE: implemented", markdown)

    def test_artifact_validation_rejects_hoodie_baseline_equality(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/feature_085_full_audit"
            generate_hoodie_runtime_evaluation_artifacts(output_dir)
            aggregate_path = output_dir / "aggregate_by_policy.json"
            payload = json.loads(aggregate_path.read_text(encoding="utf-8"))
            rows = {row["policy"]: row for row in payload["rows"]}
            rows["RO"] = dict(rows["HOODIE"])
            payload["rows"] = list(rows.values())
            aggregate_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                validate_hoodie_runtime_evaluation_artifacts(output_dir)


if __name__ == "__main__":
    unittest.main()
