from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.analysis.full_hoodie_mechanism_fidelity_batch.report import build_feature_069_report, render_feature_069_report, write_feature_069_report


class FullHoodieMechanismFidelityBatchReportIntegrationTests(unittest.TestCase):
    def test_report_writes_markdown_and_json_to_requested_directory(self) -> None:
        report = build_feature_069_report(
            changed_files=(
                "specs/069-full-hoodie-mechanism-fidelity-batch/spec.md",
                "src/analysis/full_hoodie_mechanism_fidelity_batch/report.py",
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            json_path, md_path = write_feature_069_report(report, Path(tmp))
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report.to_dict())
            markdown = md_path.read_text(encoding="utf-8")
            self.assertIn("Full HOODIE Mechanism Fidelity Batch Report", markdown)
            self.assertIn("## Coordination Graph Contract", markdown)
            self.assertIn("## Synchronization Contract", markdown)
            self.assertIn("## Validation Commands", markdown)

    def test_rendered_report_mentions_blockers_and_boundary(self) -> None:
        report = build_feature_069_report()
        markdown = render_feature_069_report(report)
        self.assertIn("Mechanism-fidelity readiness only", markdown)
        self.assertIn("## Blockers", markdown)
        self.assertIn("## Reward Pipeline Evidence", markdown)


if __name__ == "__main__":
    unittest.main()
