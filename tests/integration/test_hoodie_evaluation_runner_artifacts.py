from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.analysis.hoodie_evaluation_runner.runner import main


class HoodieEvaluationRunnerArtifactIntegrationTests(unittest.TestCase):
    def test_cli_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/feature_081_evaluation_baseline"
            main(["--output-dir", str(output_dir)])

            expected = {
                "raw_rows.json",
                "raw_rows.csv",
                "aggregate_by_policy.json",
                "aggregate_by_policy.csv",
                "ranking_by_metric.json",
                "ranking_by_metric.csv",
                "feature_081_evaluation_report.md",
                "execution_manifest.json",
            }
            self.assertTrue(output_dir.exists())
            self.assertTrue(expected.issubset({path.name for path in output_dir.iterdir()}))
            self.assertIn("feature_081_evaluation_report.md", {path.name for path in output_dir.iterdir()})
            self.assertIn("execution_manifest.json", {path.name for path in output_dir.iterdir()})


if __name__ == "__main__":
    unittest.main()
