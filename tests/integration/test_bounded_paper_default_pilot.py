from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.analysis.run_bounded_paper_default_pilot import run_bounded_pilot, write_artifacts


class BoundedPilotEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_bounded_pilot()
        cls.json_path, cls.md_path = write_artifacts(cls.report)

    def test_all_3_episodes_completed(self) -> None:
        self.assertEqual(self.report["metrics"]["episodes_completed"], 3)

    def test_transition_count_positive(self) -> None:
        self.assertGreater(self.report["metrics"]["total_transition_count"], 0)

    def test_loss_all_finite(self) -> None:
        self.assertTrue(self.report["metrics"]["loss_summary"]["all_finite"])

    def test_loss_no_nan(self) -> None:
        self.assertTrue(self.report["metrics"]["loss_summary"]["no_nan"])

    def test_loss_no_inf(self) -> None:
        self.assertTrue(self.report["metrics"]["loss_summary"]["no_inf"])

    def test_legal_action_only(self) -> None:
        self.assertTrue(self.report["metrics"]["legal_action_only"])

    def test_state_dim_74(self) -> None:
        self.assertEqual(self.report["config_summary"]["state_dim"], 74)

    def test_action_count_22(self) -> None:
        self.assertEqual(self.report["config_summary"]["action_count"], 22)

    def test_full_campaign_disabled(self) -> None:
        self.assertFalse(self.report["config_summary"]["full_campaign_enabled"])

    def test_verdict_is_pass(self) -> None:
        self.assertEqual(self.report["verdict"], "pass")

    def test_json_artifact_written(self) -> None:
        self.assertTrue(self.json_path.exists())
        self.assertGreater(self.json_path.stat().st_size, 0)

    def test_md_artifact_written(self) -> None:
        self.assertTrue(self.md_path.exists())
        self.assertGreater(self.md_path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
