from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import unittest

from src.analysis.end_to_end_hoodie_golden_trace_validation.report import build_feature_072_report, render_feature_072_report, write_feature_072_report


class EndToEndHoodieGoldenTraceValidationReportIntegrationTests(unittest.TestCase):
    def test_write_report_and_render_trace_sections(self) -> None:
        report = build_feature_072_report()
        self.assertTrue(report.passed)
        self.assertEqual(report.status, "end_to_end_golden_trace_validation_ready")
        with tempfile.TemporaryDirectory() as tmp:
            json_path, md_path = write_feature_072_report(report, Path(tmp))
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_name"], report.feature_name)
            self.assertEqual(len(payload["scenarios"]), 11)
            self.assertTrue(math.isnan(payload["scenarios"][8]["actual_outputs"]["reward"]["reward_value"]))
            markdown = md_path.read_text(encoding="utf-8")
            self.assertIn("Feature 072 End-to-End HOODIE Golden Trace Validation Report", markdown)
            self.assertIn("local_success_before_deadline", markdown)
            self.assertIn("compatibility_mode_not_default", markdown)
            self.assertIn("Feature 073", markdown)
            self.assertIn("Feature 071 Regression Status", markdown)

    def test_render_report_mentions_feature_070_and_feature_071_consumption(self) -> None:
        report = build_feature_072_report()
        markdown = render_feature_072_report(report)
        self.assertIn("figure-7-topology-extraction.md", markdown)
        self.assertIn("is_success_before_deadline", markdown)
        self.assertIn("reward_for_terminal_task", markdown)


if __name__ == "__main__":
    unittest.main()
