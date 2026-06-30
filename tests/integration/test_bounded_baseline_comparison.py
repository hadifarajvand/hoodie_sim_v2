from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.analysis.run_bounded_baseline_comparison import (
    run_bounded_baseline_comparison,
    write_artifacts,
)


class BoundedBaselineComparisonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_bounded_baseline_comparison()
        cls.json_path, cls.md_path = write_artifacts(cls.report)

    def test_both_paths_execute(self) -> None:
        legacy = self.report["legacy"]
        paper = self.report["paper_default"]
        self.assertEqual(legacy["metrics"]["episodes_completed"], 3)
        self.assertEqual(paper["metrics"]["episodes_completed"], 3)

    def test_transition_counts_positive(self) -> None:
        legacy = self.report["legacy"]
        paper = self.report["paper_default"]
        self.assertGreater(legacy["metrics"]["total_transition_count"], 0)
        self.assertGreater(paper["metrics"]["total_transition_count"], 0)

    def test_losses_all_finite(self) -> None:
        legacy = self.report["legacy"]
        paper = self.report["paper_default"]
        self.assertTrue(legacy["metrics"]["loss_summary"]["all_finite"])
        self.assertTrue(paper["metrics"]["loss_summary"]["all_finite"])

    def test_losses_no_nan(self) -> None:
        legacy = self.report["legacy"]
        paper = self.report["paper_default"]
        self.assertTrue(legacy["metrics"]["loss_summary"]["no_nan"])
        self.assertTrue(paper["metrics"]["loss_summary"]["no_nan"])

    def test_losses_no_inf(self) -> None:
        legacy = self.report["legacy"]
        paper = self.report["paper_default"]
        self.assertTrue(legacy["metrics"]["loss_summary"]["no_inf"])
        self.assertTrue(paper["metrics"]["loss_summary"]["no_inf"])

    def test_legal_action_only(self) -> None:
        legacy = self.report["legacy"]
        paper = self.report["paper_default"]
        self.assertTrue(legacy["metrics"]["legal_action_only"])
        self.assertTrue(paper["metrics"]["legal_action_only"])

    def test_illegal_action_count_zero(self) -> None:
        legacy = self.report["legacy"]
        paper = self.report["paper_default"]
        self.assertEqual(legacy["metrics"]["illegal_action_count"], 0)
        self.assertEqual(paper["metrics"]["illegal_action_count"], 0)

    def test_state_dimensions_correct(self) -> None:
        legacy = self.report["legacy"]
        paper = self.report["paper_default"]
        self.assertEqual(legacy["config_summary"]["state_dim"], 3)
        self.assertEqual(paper["config_summary"]["state_dim"], 74)

    def test_action_counts_correct(self) -> None:
        legacy = self.report["legacy"]
        paper = self.report["paper_default"]
        self.assertEqual(legacy["config_summary"]["action_count"], 3)
        self.assertEqual(paper["config_summary"]["action_count"], 22)

    def test_full_campaign_disabled(self) -> None:
        legacy = self.report["legacy"]
        paper = self.report["paper_default"]
        self.assertFalse(legacy["config_summary"]["full_campaign_enabled"])
        self.assertFalse(paper["config_summary"]["full_campaign_enabled"])

    def test_verdict_is_pass(self) -> None:
        self.assertEqual(self.report["verdict"], "pass")

    def test_json_artifact_written(self) -> None:
        self.assertTrue(self.json_path.exists())
        self.assertGreater(self.json_path.stat().st_size, 0)
        # Verify JSON is valid and contains expected structure
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        self.assertIn("legacy", data)
        self.assertIn("paper_default", data)
        self.assertEqual(data["verdict"], "pass")

    def test_md_artifact_written(self) -> None:
        self.assertTrue(self.md_path.exists())
        self.assertGreater(self.md_path.stat().st_size, 0)
        content = self.md_path.read_text(encoding="utf-8")
        self.assertIn("# Bounded Baseline Comparison Evidence", content)
        self.assertIn("## Legacy Path", content)
        self.assertIn("## Paper_default Path", content)


if __name__ == "__main__":
    unittest.main()