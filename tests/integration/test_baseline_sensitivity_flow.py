from __future__ import annotations

import json
from hashlib import sha256
import tempfile
import unittest
from pathlib import Path

from src.analysis.baseline_sensitivity import BaselineSensitivityAnalyzer


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


class BaselineSensitivityFlowTests(unittest.TestCase):
    def test_analysis_against_paper_baseline_reproduction_is_deterministic_and_read_only(self) -> None:
        campaign_root = Path("artifacts/campaigns/paper-baseline-reproduction")
        watched_files = [
            campaign_root / "campaign" / "campaign-summary.json",
            campaign_root / "campaign" / "policy-summary.json",
            campaign_root / "campaign" / "scenario-summary.json",
            campaign_root / "campaign" / "determinism-check.json",
            campaign_root / "matrix" / "matrix-summary.csv",
        ]
        before = {path: _file_digest(path) for path in watched_files}

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "analysis"
            analyzer = BaselineSensitivityAnalyzer(campaign_root, output_dir)
            first = analyzer.write_outputs()
            second = analyzer.write_outputs()

            report_json = json.loads(first["sensitivity-report.json"].read_text(encoding="utf-8"))
            report_json_repeat = json.loads(second["sensitivity-report.json"].read_text(encoding="utf-8"))
            self.assertEqual(report_json, report_json_repeat)
            self.assertTrue(report_json["passed"])
            self.assertEqual(report_json["campaign_root"], campaign_root.as_posix())
            self.assertEqual(report_json["analysis_output_dir"], output_dir.as_posix())
            self.assertTrue(any(item["comparison"] == "identical" for item in report_json["trace_comparisons"]) or any(item["comparison"] == "same_count_but_different_slots" for item in report_json["trace_comparisons"]))
            self.assertTrue(any(item["policy_name"] in {"BCO", "FLC", "MLEO"} for item in report_json["policy_comparisons"]))
            self.assertIn("accounting_clean", report_json["classifications"])
            self.assertIn("saturation_dominant", report_json["classifications"])
            self.assertTrue((output_dir / "sensitivity-report.json").exists())
            self.assertTrue((output_dir / "sensitivity-report.md").exists())

        after = {path: _file_digest(path) for path in watched_files}
        self.assertEqual(before, after)

    def test_missing_artifacts_are_reported_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "campaign-root"
            (root / "campaign").mkdir(parents=True, exist_ok=True)
            (root / "matrix").mkdir(parents=True, exist_ok=True)
            (root / "bundle").mkdir(parents=True, exist_ok=True)
            analyzer = BaselineSensitivityAnalyzer(root, Path(tmpdir) / "analysis")
            report = analyzer.analyze()

            self.assertFalse(report.passed)
            self.assertTrue(report.missing_artifacts)
            self.assertTrue(any(item["category"] == "missing_artifacts" for item in report.findings))


if __name__ == "__main__":
    unittest.main()
