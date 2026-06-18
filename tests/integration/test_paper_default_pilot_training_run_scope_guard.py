from __future__ import annotations

import subprocess
import unittest


class PaperDefaultPilotTrainingRunScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_057_paths(self) -> None:
        status_output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines()
        diff_output = subprocess.run(["git", "diff", "--name-only", "057-paper-default-pilot-training-run...HEAD"], check=True, capture_output=True, text=True).stdout.splitlines()
        cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.splitlines()

        ignored_noise_prefixes = (
            ".personality_migration",
            ".venvmac",
            "auth.json",
            "cache/",
            "config.toml",
            "engine/",
            "goals_",
            "history.jsonl",
            "installation_id",
            "logs_",
            "memories_",
            "models_cache.json",
            "plugins/",
            "rules/",
            "scripts/run_hoodie_experiment_suite.py",
            "sessions/",
            "shell_snapshots/",
            "skills/",
            "state_",
            "tmp/",
            "version.json",
            "artifacts/figure10_validation/",
            "artifacts/runtime-audit-smoke/",
            "tests/test_model16_experimental_layers_contract.py",
            "tests/test_model17_euls_execution_engine.py",
        )
        forbidden_prefixes = (
            ".specify/feature.json",
            "AGENTS.md",
            ".gitignore",
            "src/environment/",
            "src/policies/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        ignored_noise_prefixes = (
            ".personality_migration",
            ".venvmac",
            "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
            "artifacts/figure10_validation/",
            "artifacts/runtime-audit-smoke/",
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
            "scripts/run_hoodie_experiment_suite.py",
            "sessions/",
            "shell_snapshots/",
            "skills/",
            "src/analysis/evaluation_trace_bank_baseline_harness/",
            "tests/unit/test_evaluation_trace_bank_baseline_harness",
            "tests/integration/test_evaluation_trace_bank_baseline_harness",
            "state_",
            "tests/test_model16_experimental_layers_contract.py",
            "tests/test_model17_euls_execution_engine.py",
            "tmp/",
            "version.json",
            "auth.json",
            "config.toml",
        )
        for line in status_output + diff_output + cached_output:
            path = line[3:].strip() if line.startswith(("??", " M", "M ", "A ", "D ", "R ", "C ", "UU")) else line.strip()
            if any(path.startswith(prefix) for prefix in ignored_noise_prefixes):
                continue
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")

        approved_prefixes = (
            "artifacts/analysis/paper-default-pilot-training-run/",
            "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
            "specs/057-paper-default-pilot-training-run/",
            "src/analysis/paper_default_pilot_training_run/",
            "src/analysis/paper_default_training_smoke_run/",
            "docs/architecture/euls_phase17_paper_default_pilot_training_run.md",
            "tests/unit/test_paper_default_pilot_training_run",
            "tests/integration/test_paper_default_pilot_training_run",
        )
        for path in status_output + diff_output + cached_output:
            cleaned = path[3:].strip() if path.startswith(("??", " M", "M ", "A ", "D ", "R ", "C ", "UU")) else path.strip()
            if cleaned.startswith("artifacts/analysis/evaluation-trace-bank-baseline-harness/"):
                continue
            if any(cleaned.startswith(prefix) for prefix in ignored_noise_prefixes):
                continue
            if not cleaned:
                continue
            if any(cleaned.startswith(prefix) for prefix in ignored_noise_prefixes):
                continue
            self.assertTrue(any(cleaned.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {cleaned}")

        self.assertEqual(cached_output, [])
