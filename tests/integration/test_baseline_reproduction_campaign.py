from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.evaluation.campaign_config import CampaignConfig
from src.evaluation.campaign_runner import CampaignRunner


class BaselineReproductionCampaignTests(unittest.TestCase):
    def _config(self, output_dir: Path) -> CampaignConfig:
        return CampaignConfig(
            campaign_name="baseline-reproduction",
            policy_names=("FLC", "ADAPTIVE"),
            scenario_names=("paper_default", "moderate"),
            seeds=(1,),
            output_dir=output_dir,
            episode_length=3,
            created_at_override="2026-05-06T00:00:00+00:00",
        )

    def _artifact_snapshot(self, output_dir: Path) -> dict[str, str]:
        campaign_dir = output_dir / "campaign"
        return {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(campaign_dir.iterdir())
            if path.is_file()
        }

    def test_campaign_flow_writes_required_artifacts_and_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "campaign-run"

            first_result = CampaignRunner(self._config(output_dir)).run()
            first_snapshot = self._artifact_snapshot(output_dir)
            second_result = CampaignRunner(self._config(output_dir)).run()
            second_snapshot = self._artifact_snapshot(output_dir)

            matrix_dir = output_dir / "matrix"
            bundle_dir = output_dir / "bundle"
            campaign_dir = output_dir / "campaign"
            self.assertTrue((matrix_dir / "matrix-summary.csv").exists())
            self.assertTrue(any(path.suffix == ".json" for path in matrix_dir.iterdir() if path.is_file()))
            self.assertTrue((bundle_dir / "manifest.json").exists())
            self.assertTrue((bundle_dir / "run-config.json").exists())
            self.assertTrue((bundle_dir / "artifact-index.json").exists())
            self.assertTrue((bundle_dir / "validation-summary.json").exists())
            self.assertTrue((bundle_dir / "README.md").exists())
            self.assertTrue((campaign_dir / "campaign-manifest.json").exists())
            self.assertTrue((campaign_dir / "campaign-summary.json").exists())
            self.assertTrue((campaign_dir / "policy-summary.json").exists())
            self.assertTrue((campaign_dir / "scenario-summary.json").exists())
            self.assertTrue((campaign_dir / "determinism-check.json").exists())
            self.assertTrue((campaign_dir / "README.md").exists())

            self.assertEqual(first_snapshot, second_snapshot)
            self.assertEqual(first_result["matrix_result_count"], 4)
            self.assertEqual(second_result["matrix_result_count"], 4)

            determinism = json.loads((campaign_dir / "determinism-check.json").read_text(encoding="utf-8"))
            self.assertTrue(determinism["passed"])
            self.assertEqual(determinism["expected_runs"], 4)
            self.assertEqual(determinism["discovered_runs"], 4)
            self.assertTrue(determinism["deterministic_timestamp_used"])

            manifest = json.loads((campaign_dir / "campaign-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["bundle_output_dir"], str(output_dir / "bundle"))
            self.assertEqual(manifest["matrix_result_count"], 4)


if __name__ == "__main__":
    unittest.main()
