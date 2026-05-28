from __future__ import annotations

import unittest

from src.analysis.paper_faithful_state_action_space_batch import generate_paper_faithful_state_action_space_batch_artifacts
from src.analysis.paper_faithful_state_action_space_batch.config import REPORT_JSON, REPORT_MD


class PaperFaithfulStateActionSpaceBatchReportTests(unittest.TestCase):
    def test_markdown_and_json_reports_are_generated(self) -> None:
        generate_paper_faithful_state_action_space_batch_artifacts()
        self.assertTrue(REPORT_JSON.exists())
        self.assertTrue(REPORT_MD.exists())
        self.assertIn("paper_faithful_state_action_space_batch_passed", REPORT_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
