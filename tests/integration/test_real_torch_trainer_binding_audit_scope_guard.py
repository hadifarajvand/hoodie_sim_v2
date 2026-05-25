from __future__ import annotations

import subprocess
import unittest


class RealTorchTrainerBindingAuditScopeGuardTests(unittest.TestCase):
    def test_git_status_and_feature_diff_only_show_feature_060a_paths(self) -> None:
        status_output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines()
        diff_output = subprocess.run(
            ["git", "diff", "--name-only", "060-full-paper-default-training-campaign-execution...HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.splitlines()

        paths = [line[3:].strip() for line in status_output] + [line.strip() for line in diff_output + cached_output]
        forbidden_prefixes = (
            ".specify/feature.json",
            "AGENTS.md",
            ".gitignore",
            "src/environment/",
            "src/policies/",
            "src/analysis/full_paper_default_training_campaign_execution/",
            "artifacts/analysis/full-paper-default-training-campaign-execution/",
            "artifacts/analysis/full-paper-default-training-campaign-gate/",
            "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
            "artifacts/analysis/paper-default-pilot-training-run/",
            "artifacts/analysis/target-update-replay-training-validation/",
            "artifacts/analysis/paper-default-training-smoke-run/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        for path in paths:
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")

        approved_prefixes = (
            "artifacts/analysis/real-torch-trainer-binding-audit/",
            "specs/060a-real-torch-trainer-binding-audit/",
            "src/analysis/real_torch_trainer_binding_audit/",
            "tests/unit/test_real_torch_trainer_binding_audit",
            "tests/integration/test_real_torch_trainer_binding_audit",
        )
        for path in paths:
            if not path:
                continue
            self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")
        self.assertEqual(cached_output, [])


if __name__ == "__main__":
    unittest.main()
