from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.analysis.runtime_paper_faithful_semantics_alignment.report import build_feature_071_report, render_feature_071_report, write_feature_071_report


class RuntimePaperFaithfulSemanticsAlignmentReportIntegrationTests(unittest.TestCase):
    def test_report_writes_markdown_and_json_and_mentions_feature_072(self) -> None:
        report = build_feature_071_report()
        self.assertTrue(report.passed)
        self.assertEqual(report.status, "runtime_paper_faithful_semantics_alignment_ready")
        with tempfile.TemporaryDirectory() as tmp:
            json_path, md_path = write_feature_071_report(report, Path(tmp))
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report.to_dict())
            markdown = md_path.read_text(encoding="utf-8")
            self.assertIn("Feature 071 Runtime Paper-Faithful Semantics Alignment Report", markdown)
            self.assertIn("Deadline Evidence", markdown)
            self.assertIn("Terminal State Evidence", markdown)
        self.assertIn("Reward Runtime Evidence", markdown)
        self.assertIn("Compatibility Evidence", markdown)
        self.assertIn("Feature 072", markdown)
        self.assertIn("build_timeout_contract_default_is_paper", markdown)
        self.assertIn("reward_for_terminal_task_default_uses_plus_one", markdown)
        self.assertIn("no_call_stack_compatibility_bypass", markdown)

    def test_rendered_report_mentions_paper_and_compatibility_modes(self) -> None:
        report = build_feature_071_report()
        markdown = render_feature_071_report(report)
        self.assertIn("paper mode", markdown.lower())
        self.assertIn("compatibility", markdown.lower())
        self.assertIn("reward_slot_for_terminal", markdown)
        self.assertIn("call-stack-based bypass", markdown)


if __name__ == "__main__":
    unittest.main()
