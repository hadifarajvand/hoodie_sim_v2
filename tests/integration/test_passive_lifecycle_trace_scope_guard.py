from __future__ import annotations

import subprocess
import unittest


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
        result = subprocess.run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def _git_cached_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def test_scope_guard_only_allows_passive_instrumentation_paths(self) -> None:
        for path in self._git_diff_paths():
            self.assertTrue(path.startswith(ALLOWED_PREFIXES), path)
            self.assertNotEqual(path, ".specify/feature.json")
            self.assertFalse(path.startswith("src/policies/"), path)
            self.assertFalse(path.endswith("requirements.txt"), path)

    def test_no_training_optimizer_replay_target_update(self) -> None:
        report_output = subprocess.run(
            [
                "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python",
                "-c",
                "from src.analysis.passive_runtime_lifecycle_trace_instrumentation import run_passive_runtime_lifecycle_trace_instrumentation; r=run_passive_runtime_lifecycle_trace_instrumentation(); print(r.no_training_started, r.no_optimizer_step, r.no_replay_training, r.no_target_update_execution)",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("True True True True", report_output.stdout)

    def test_no_dependency_policy_reward_runtime_semantic_drift(self) -> None:
        report_output = subprocess.run(
            [
                "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python",
                "-c",
                "from src.analysis.passive_runtime_lifecycle_trace_instrumentation import run_passive_runtime_lifecycle_trace_instrumentation; r=run_passive_runtime_lifecycle_trace_instrumentation(); print(r.no_dependency_drift, r.no_policy_drift, r.no_reward_timing_change)",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("True True True", report_output.stdout)

    def test_feature_json_must_not_be_staged(self) -> None:
        for path in self._git_cached_paths():
            self.assertNotEqual(path, ".specify/feature.json")


if __name__ == "__main__":
    unittest.main()

