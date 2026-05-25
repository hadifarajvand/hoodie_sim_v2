from __future__ import annotations

from pathlib import Path
import unittest

from src.analysis.paper_default_training_smoke_run import build_paper_default_training_smoke_report, generate_paper_default_training_smoke_artifacts


class PaperDefaultTrainingSmokeRunIntegrationTests(unittest.TestCase):
    def test_report_writes_expected_artifacts(self) -> None:
        report, json_path, md_path = generate_paper_default_training_smoke_artifacts()
        json_path = Path("artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json")
        md_path = Path("artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.md")
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = build_paper_default_training_smoke_report().to_dict()
        self.assertEqual(payload["feature_id"], report.feature_id)
        self.assertEqual(payload["final_verdict"], "paper_default_training_smoke_passed")


if __name__ == "__main__":
    unittest.main()
