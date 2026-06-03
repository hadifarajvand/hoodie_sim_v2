from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from src.analysis.hoodie_proposed_method.report import build_feature_080_report, render_feature_080_report, write_feature_080_report
from src.analysis.hoodie_proposed_method.runner import main as hoodie_proposed_method_main


class HoodieProposedMethodReportIntegrationTests(unittest.TestCase):
    def _changed_files(self) -> tuple[str, ...]:
        return (
            "specs/080-evaluation-ranking/plan.md",
            "specs/080-evaluation-ranking/checklists/requirements.md",
            "src/analysis/hoodie_proposed_method/report.py",
            "tests/integration/test_hoodie_proposed_method_report.py",
        )

    def test_report_renders_honestly_without_ranking_or_baselines(self) -> None:
        report = build_feature_080_report(changed_files=self._changed_files())
        rendered = render_feature_080_report(report).lower()
        self.assertFalse(report.passed)
        self.assertEqual(report.status, "hoodie_proposed_method_blocked")
        self.assertEqual(report.readiness_level, "mostly_implemented")
        self.assertEqual(report.component_count, 14)
        self.assertEqual(report.implemented_count, 11)
        self.assertEqual(report.partial_count, 3)
        self.assertEqual(report.missing_count, 0)
        self.assertTrue(report.validation_summary)
        self.assertIn("hoodie_proposed", rendered)
        self.assertIn("validation summary", rendered)
        self.assertIn("remaining partial components are learning internals expected to be implemented later.", rendered)
        self.assertIn("next partial targets", rendered)
        self.assertIn("double_dqn_target_rule", rendered)
        self.assertIn("claim boundary", rendered)
        self.assertIn("scope evidence", rendered)
        self.assertIn("no ranking is performed.", rendered)
        self.assertIn("no baseline evaluation is performed.", rendered)
        self.assertNotIn("ranking table", rendered)
        self.assertIn("no thesis/dcq extension is introduced.", rendered)
        self.assertNotIn("proposed_dcq", rendered)
        self.assertIn("dqn interface", rendered)
        self.assertIn("deterministic q-values", rendered)
        self.assertIn("epsilon-greedy training schedule", rendered)
        self.assertIn("decays from 1 to 0 across the first half of episodes", rendered)
        self.assertIn("replay memory interface", rendered)
        self.assertIn("bounded fifo replay memory", rendered)
        self.assertIn("distributed edge-agent decision model", rendered)
        self.assertIn("scores legal local/horizontal/vertical actions", rendered)

    def test_report_writer_and_cli_entrypoint_remain_callable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = write_feature_080_report(Path(tmpdir))
            self.assertTrue(output_path.exists())
            self.assertTrue((Path(tmpdir) / "feature-080-hoodie-proposed-method-report.json").exists())

        buffer = io.StringIO()
        with patch("src.analysis.hoodie_proposed_method.runner.write_feature_080_report", return_value=Path("/tmp/fake-report.md")):
            with redirect_stdout(buffer):
                exit_code = hoodie_proposed_method_main(["--output-dir", str(Path(tempfile.gettempdir()) / "hoodie-proposed-method-test")])
        self.assertEqual(exit_code, 0)
        self.assertEqual(buffer.getvalue().strip(), "/tmp/fake-report.md")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
