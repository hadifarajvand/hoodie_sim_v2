from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.analysis.hoodie_runtime_evaluation_runner.runner import generate_hoodie_runtime_evaluation_artifacts, main


class HoodieRuntimeEvaluationRunnerArtifactIntegrationTests(unittest.TestCase):
    def test_cli_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/feature_082_full_runtime_eval"
            main(["--write-artifacts", str(output_dir)])
            expected = {
                "raw_rows.json",
                "raw_rows.csv",
                "aggregate_by_policy.json",
                "aggregate_by_policy.csv",
                "ranking_by_metric.json",
                "ranking_by_metric.csv",
                "feature_082_runtime_evaluation_report.json",
                "feature_082_runtime_evaluation_report.md",
                "execution_manifest.json",
            }
            self.assertTrue(output_dir.exists())
            self.assertTrue(expected.issubset({path.name for path in output_dir.iterdir()}))

    def test_validate_artifacts_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/feature_082_full_runtime_eval"
            generate_hoodie_runtime_evaluation_artifacts(output_dir)
            main(["--validate-artifacts", "--artifact-dir", str(output_dir)])


if __name__ == "__main__":
    unittest.main()
