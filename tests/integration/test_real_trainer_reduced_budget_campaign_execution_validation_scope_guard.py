from __future__ import annotations

import subprocess
import unittest


class RealTrainerReducedBudgetCampaignExecutionValidationScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_060a_paths(self) -> None:
        status_output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines()
        diff_output = subprocess.run(["git", "diff", "--name-only", "059-full-paper-default-training-campaign-gate...HEAD"], check=True, capture_output=True, text=True).stdout.splitlines()
        cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.splitlines()

        ignored_noise_prefixes = (
            ".personality_migration",
            ".venvmac",
            "artifacts/figure10_validation/",
            "artifacts/runtime-audit-smoke/",
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
            "tests/test_model16_experimental_layers_contract.py",
            "tests/test_model17_euls_execution_engine.py",
            "tmp/",
            "version.json",
        )
        forbidden_prefixes = (
            ".specify/feature.json",
            "AGENTS.md",
            ".gitignore",
            "src/environment/",
            "src/policies/",
            "src/analysis/full_paper_default_training_campaign_execution/",
            "src/analysis/full_paper_default_training_campaign_gate/",
            "src/analysis/evaluation_trace_bank_baseline_harness/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        approved_prefixes = (
            "artifacts/analysis/real-trainer-reduced-budget-campaign-execution-validation/",
            "docs/architecture/euls_phase20a_real_trainer_reduced_budget_campaign_execution_validation.md",
            "specs/060a-real-trainer-reduced-budget-campaign-execution-validation/",
            "src/analysis/real_trainer_reduced_budget_campaign_execution_validation/",
            "tests/unit/test_real_trainer_reduced_budget_campaign_execution_validation",
            "tests/integration/test_real_trainer_reduced_budget_campaign_execution_validation",
        )
        for line in status_output + diff_output + cached_output:
            path = line[3:].strip() if line.startswith(("??", " M", "M ", "A ", "D ", "R ", "C ", "UU")) else line.strip()
            if not path or any(path.startswith(prefix) for prefix in ignored_noise_prefixes):
                continue
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")
            self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")

        self.assertEqual(cached_output, [])


if __name__ == "__main__":
    unittest.main()
