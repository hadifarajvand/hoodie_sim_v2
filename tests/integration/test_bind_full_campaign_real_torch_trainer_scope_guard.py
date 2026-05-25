from __future__ import annotations

import subprocess
import unittest


class BindFullCampaignRealTorchTrainerScopeGuardTests(unittest.TestCase):
    def test_dirty_and_staged_paths_are_only_feature_060b_paths(self) -> None:
        status_output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines()
        cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.splitlines()
        paths = [line[3:].strip() for line in status_output] + [line.strip() for line in cached_output]
        approved = (
            "artifacts/analysis/bind-full-campaign-real-torch-trainer/",
            "artifacts/analysis/full-paper-default-training-campaign-execution/",
            "specs/060b-bind-full-campaign-real-torch-trainer/",
            "src/analysis/bind_full_campaign_real_torch_trainer/",
            "src/analysis/full_paper_default_training_campaign_execution/",
            "tests/unit/test_bind_full_campaign_real_torch_trainer",
            "tests/integration/test_bind_full_campaign_real_torch_trainer",
        )
        forbidden = (".specify/feature.json", "AGENTS.md", ".gitignore", "src/environment/", "src/policies/", "requirements", "pyproject.toml", "poetry.lock", "uv.lock")
        for path in paths:
            self.assertFalse(any(path.startswith(prefix) for prefix in forbidden), msg=f"forbidden path present: {path}")
            self.assertTrue(any(path.startswith(prefix) for prefix in approved), msg=f"unexpected dirty/staged path: {path}")
        self.assertEqual(cached_output, [])


if __name__ == "__main__":
    unittest.main()
