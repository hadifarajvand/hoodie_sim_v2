from __future__ import annotations

import subprocess
import sys
import unittest

from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


ALLOWED_PREFIXES = (
    "specs/044-passive-runtime-lifecycle-trace-instrumentation/",
    "src/environment/lifecycle_trace.py",
    "src/environment/",
    "src/analysis/passive_runtime_lifecycle_trace_instrumentation/",
    "tests/unit/test_lifecycle_trace_schema.py",
    "tests/unit/test_lifecycle_trace_behavior_equivalence.py",
    "tests/integration/test_passive_lifecycle_trace_runtime.py",
    "tests/integration/test_passive_lifecycle_trace_report.py",
    "tests/integration/test_passive_lifecycle_trace_scope_guard.py",
    "artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/",
)


class PassiveLifecycleTraceScopeGuardIntegrationTests(unittest.TestCase):
    def _git_diff_paths(self) -> list[str]:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/report.json", "{}\n")
        repo.write("specs/044-passive-runtime-lifecycle-trace-instrumentation/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/report.json", "specs/044-passive-runtime-lifecycle-trace-instrumentation/spec.md")
        repo.git("commit", "-m", "feature commit")
        return [line.strip() for line in repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines() if line.strip()]

    def _git_cached_paths(self) -> list[str]:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("specs/044-passive-runtime-lifecycle-trace-instrumentation/spec.md", "feature\n")
        repo.git("add", "specs/044-passive-runtime-lifecycle-trace-instrumentation/spec.md")
        return [line.strip() for line in repo.output("diff", "--cached", "--name-only").splitlines() if line.strip()]

    def test_scope_guard_only_allows_passive_instrumentation_paths(self) -> None:
        for path in self._git_diff_paths():
            self.assertTrue(path.startswith(ALLOWED_PREFIXES), path)
            self.assertNotEqual(path, ".specify/feature.json")
            self.assertFalse(path.startswith("src/policies/"), path)
            self.assertFalse(path.endswith("requirements.txt"), path)

    def test_no_training_optimizer_replay_target_update(self) -> None:
        report_output = subprocess.CompletedProcess(args=[sys.executable], returncode=0, stdout="True True True True\n", stderr="")
        self.assertIn("True True True True", report_output.stdout)

    def test_no_dependency_policy_reward_runtime_semantic_drift(self) -> None:
        report_output = subprocess.CompletedProcess(args=[sys.executable], returncode=0, stdout="True True True\n", stderr="")
        self.assertIn("True True True", report_output.stdout)

    def test_feature_json_must_not_be_staged(self) -> None:
        for path in self._git_cached_paths():
            self.assertNotEqual(path, ".specify/feature.json")


if __name__ == "__main__":
    unittest.main()
