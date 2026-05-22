from __future__ import annotations

import subprocess
import unittest

from src.analysis.completion_root_cause_diagnosis import run_completion_root_cause_diagnosis


ALLOWED_PREFIXES = (
    "specs/045-completion-root-cause-diagnosis/",
    "src/analysis/completion_root_cause_diagnosis/",
    "tests/unit/test_completion_root_cause_schema.py",
    "tests/unit/test_completion_root_cause_classifiers.py",
    "tests/integration/test_completion_root_cause_diagnosis.py",
    "tests/integration/test_completion_root_cause_report.py",
    "tests/integration/test_completion_root_cause_scope_guard.py",
    "artifacts/analysis/completion-root-cause-diagnosis/",
)


class CompletionRootCauseScopeGuardIntegrationTests(unittest.TestCase):
    def _git_diff_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def _git_cached_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def test_scope_guard_only_allows_feature_045_paths(self) -> None:
        for path in self._git_diff_paths():
            self.assertTrue(path.startswith(ALLOWED_PREFIXES), path)
            self.assertNotEqual(path, ".specify/feature.json")
            self.assertFalse(path.startswith("src/environment/"), path)
            self.assertFalse(path.startswith("src/policies/"), path)

    def test_feature_json_must_not_be_staged(self) -> None:
        for path in self._git_cached_paths():
            self.assertNotEqual(path, ".specify/feature.json")

    def test_no_runtime_training_policy_dependency_drift(self) -> None:
        report = run_completion_root_cause_diagnosis()
        payload = report.to_dict()
        self.assertTrue(payload["no_training_started"])
        self.assertTrue(payload["no_optimizer_step"])
        self.assertTrue(payload["no_replay_training"])
        self.assertTrue(payload["no_target_update_execution"])
        self.assertTrue(payload["no_dependency_drift"])
        self.assertTrue(payload["no_policy_drift"])
        self.assertTrue(payload["no_reward_timing_change"])
        self.assertTrue(payload["no_timeout_contract_drift"])
        self.assertTrue(payload["no_capacity_contract_drift"])
        self.assertTrue(payload["no_transmission_contract_drift"])
        self.assertTrue(payload["no_action_legality_drift"])


if __name__ == "__main__":
    unittest.main()
