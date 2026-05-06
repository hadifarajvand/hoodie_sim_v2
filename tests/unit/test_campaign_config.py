from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.evaluation.campaign_config import CampaignConfig


class CampaignConfigTests(unittest.TestCase):
    def test_campaign_name_and_path_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = CampaignConfig(
                campaign_name="  baseline  ",
                policy_names=("FLC",),
                scenario_names=("paper_default",),
                seeds=(1,),
                output_dir=Path(tmpdir) / ".",
            )
            self.assertEqual(config.campaign_name, "baseline")
            self.assertEqual(config.output_dir, Path(tmpdir))

    def test_non_empty_policy_scenario_and_seed_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                CampaignConfig("", ("FLC",), ("paper_default",), (1,), Path(tmpdir))
            with self.assertRaises(ValueError):
                CampaignConfig("c", tuple(), ("paper_default",), (1,), Path(tmpdir))
            with self.assertRaises(ValueError):
                CampaignConfig("c", ("FLC",), tuple(), (1,), Path(tmpdir))
            with self.assertRaises(ValueError):
                CampaignConfig("c", ("FLC",), ("paper_default",), tuple(), Path(tmpdir))

    def test_seed_validation_requires_integers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(TypeError):
                CampaignConfig("c", ("FLC",), ("paper_default",), (1, "2"), Path(tmpdir))

    def test_episode_length_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                CampaignConfig("c", ("FLC",), ("paper_default",), (1,), Path(tmpdir), episode_length=0)

    def test_created_at_override_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = CampaignConfig(
                campaign_name="c",
                policy_names=("FLC",),
                scenario_names=("paper_default",),
                seeds=(1,),
                output_dir=Path(tmpdir),
                created_at_override="2026-05-06T00:00:00+00:00",
            )
            self.assertEqual(config.created_at_override, "2026-05-06T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()

