from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.analysis.hoodie_evaluation_runner.runner import generate_hoodie_evaluation_runner_artifacts


class HoodieEvaluationRunnerArtifactTests(unittest.TestCase):
    def test_artifact_bundle_is_written_with_expected_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/feature_081_evaluation_baseline"
            report, paths, manifest = generate_hoodie_evaluation_runner_artifacts(output_dir)

            required_names = {
                "raw_rows.json",
                "raw_rows.csv",
                "aggregate_by_policy.json",
                "aggregate_by_policy.csv",
                "ranking_by_metric.json",
                "ranking_by_metric.csv",
                "feature_081_evaluation_report.md",
                "execution_manifest.json",
            }
            self.assertEqual(set(paths), required_names)
            for path in paths.values():
                self.assertTrue(path.exists(), path)

            raw_payload = json.loads(paths["raw_rows.json"].read_text(encoding="utf-8"))
            aggregate_payload = json.loads(paths["aggregate_by_policy.json"].read_text(encoding="utf-8"))
            ranking_payload = json.loads(paths["ranking_by_metric.json"].read_text(encoding="utf-8"))
            manifest_payload = json.loads(paths["execution_manifest.json"].read_text(encoding="utf-8"))

            self.assertEqual(raw_payload["count"], 2520)
            self.assertEqual(len(raw_payload["rows"]), 2520)
            self.assertEqual(len(aggregate_payload["rows"]), 5)
            self.assertEqual(set(ranking_payload["ranking_tables"]), {
                "completion_rate",
                "timeout_drop_rate",
                "unavailable_drop_rate",
                "deadline_violation_rate",
                "average_delay",
                "average_reward",
                "total_reward",
                "throughput",
                "queue_stability_score",
                "illegal_action_rejection_count",
            })
            self.assertEqual(manifest_payload["raw_row_count"], 2520)
            self.assertEqual(manifest_payload["report_status"], "hoodie_evaluation_runner_ready")
            self.assertTrue(manifest_payload["passed"])
            self.assertEqual(manifest_payload["compatibility_mode_policies"], ["HOODIE_PROPOSED", "ORIGINAL_HOODIE_BASELINE"])
            self.assertEqual(report.status, "hoodie_evaluation_runner_ready")
            self.assertTrue(report.passed)

            markdown = paths["feature_081_evaluation_report.md"].read_text(encoding="utf-8")
            self.assertIn("Feature 081 HOODIE Evaluation & Baseline Benchmarking Artifact Bundle", markdown)
            self.assertIn("raw_row_count: `2520`", markdown)
            self.assertIn("HOODIE_PROPOSED", markdown)
            self.assertIn("ORIGINAL_HOODIE_BASELINE", markdown)


if __name__ == "__main__":
    unittest.main()
