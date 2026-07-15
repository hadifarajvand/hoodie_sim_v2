from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest import mock

from src.analysis.completion_root_cause_diagnosis import run_completion_root_cause_diagnosis
from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


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
    def test_scope_guard_only_allows_feature_045_paths(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json", "{}\n")
        repo.write("specs/045-completion-root-cause-diagnosis/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json", "specs/045-completion-root-cause-diagnosis/spec.md")
        repo.git("commit", "-m", "feature commit")
        for path in repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines():
            self.assertTrue(path.startswith(ALLOWED_PREFIXES), path)
            self.assertNotEqual(path, ".specify/feature.json")
            self.assertFalse(path.startswith("src/environment/"), path)
            self.assertFalse(path.startswith("src/policies/"), path)

    def test_feature_json_must_not_be_staged(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("specs/045-completion-root-cause-diagnosis/spec.md", "feature\n")
        repo.git("add", "specs/045-completion-root-cause-diagnosis/spec.md")
        for path in repo.output("diff", "--cached", "--name-only").splitlines():
            self.assertNotEqual(path, ".specify/feature.json")

    def test_no_runtime_training_policy_dependency_drift(self) -> None:
        stub_report = SimpleNamespace(
            no_training_started=True,
            no_optimizer_step=True,
            no_replay_training=True,
            no_target_update_execution=True,
            no_dependency_drift=True,
            no_policy_drift=True,
            no_reward_timing_change=True,
            no_timeout_contract_drift=True,
            no_capacity_contract_drift=True,
            no_transmission_contract_drift=True,
            no_action_legality_drift=True,
            to_dict=lambda: {
                "no_training_started": True,
                "no_optimizer_step": True,
                "no_replay_training": True,
                "no_target_update_execution": True,
                "no_dependency_drift": True,
                "no_policy_drift": True,
                "no_reward_timing_change": True,
                "no_timeout_contract_drift": True,
                "no_capacity_contract_drift": True,
                "no_transmission_contract_drift": True,
                "no_action_legality_drift": True,
            },
        )
        with mock.patch("src.analysis.completion_root_cause_diagnosis.runner.build_completion_root_cause_report", return_value=stub_report):
            with mock.patch("src.analysis.completion_root_cause_diagnosis.runner.write_completion_root_cause_report", return_value=None):
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
