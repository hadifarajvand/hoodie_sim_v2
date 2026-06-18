from __future__ import annotations

import subprocess
import unittest
from unittest import mock

from src.analysis.evaluation_trace_bank_baseline_harness import build_evaluation_trace_bank_baseline_harness_report


class EvaluationTraceBankBaselineHarnessScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_058_paths(self) -> None:
        status_output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines()
        diff_output = subprocess.run(["git", "diff", "--name-only", "057-paper-default-pilot-training-run...HEAD"], check=True, capture_output=True, text=True).stdout.splitlines()
        cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.splitlines()

        forbidden_prefixes = (
            ".specify/feature.json",
            "AGENTS.md",
            ".gitignore",
            "src/environment/",
            "src/policies/",
            "artifacts/analysis/target-update-replay-training-validation/",
            "artifacts/analysis/paper-default-training-smoke-run/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        ignored_noise_prefixes = (
            ".personality_migration",
            ".venvmac",
            "artifacts/analysis/paper-default-pilot-training-run/",
            "artifacts/figure10_validation/",
            "artifacts/runtime-audit-smoke/",
            "docs/architecture/",
            "docs/architecture/euls_phase18_evaluation_trace_bank_baseline_harness.md",
            "cache/",
            "engine/",
            "goals_",
            "history.jsonl",
            "installation_id",
            "logs_",
            "memories_",
            "models_cache.json",
            "plugins/",
            "rules/",
            "sessions/",
            "shell_snapshots/",
            "skills/",
            "scripts/",
            "state_",
            "tests/test_model16_experimental_layers_contract.py",
            "tests/test_model17_euls_execution_engine.py",
            "tmp/",
            "version.json",
            "auth.json",
            "config.toml",
        )
        paths = [line[3:].strip() for line in status_output if not any(line[3:].strip().startswith(prefix) for prefix in ignored_noise_prefixes)]
        paths += [line.strip() for line in diff_output + cached_output if not any(line.strip().startswith(prefix) for prefix in ignored_noise_prefixes)]
        for path in paths:
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")

        approved_prefixes = (
            "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
            "specs/058-evaluation-trace-bank-baseline-harness/",
            "src/analysis/evaluation_trace_bank_baseline_harness/",
            "tests/unit/test_evaluation_trace_bank_baseline_harness",
            "tests/integration/test_evaluation_trace_bank_baseline_harness",
        )
        for path in paths:
            if not path:
                continue
            if path.startswith("tests/integration/test_paper_default_pilot_training_run_scope_guard.py"):
                continue
            self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")
        self.assertEqual(cached_output, [])

    def test_report_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.evaluation_trace_bank_baseline_harness.runner as runner

        with mock.patch.object(runner, "_status_paths", return_value=["src/policies/example.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_names", return_value=[]):
                    payload = build_evaluation_trace_bank_baseline_harness_report().to_dict()
        self.assertEqual(payload["final_verdict"], "behavior_drift_detected")
        self.assertIn("working_tree_paths_approved", payload["remaining_blockers"])
        self.assertFalse(payload["behavior_safety_summary"]["no_policy_drift"])


if __name__ == "__main__":
    unittest.main()
