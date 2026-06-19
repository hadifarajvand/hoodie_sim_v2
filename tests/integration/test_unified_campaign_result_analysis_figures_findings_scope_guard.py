from __future__ import annotations

import subprocess
import unittest


class UnifiedCampaignAnalysisScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_062_paths(self) -> None:
        status_output = subprocess.run(["git", "status", "--short", "--untracked-files=no"], check=True, capture_output=True, text=True).stdout.splitlines()
        diff_output = subprocess.run(["git", "diff", "--name-only", "060-full-paper-default-training-campaign-execution-v2...HEAD"], check=True, capture_output=True, text=True).stdout.splitlines()
        cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.splitlines()
        paths = [line[3:].strip() for line in status_output] + [line.strip() for line in diff_output + cached_output]
        forbidden_prefixes = (
            "src/environment/",
            "src/dal/",
            "src/policies/",
            "src/environment/replay_hash.py",
            "src/analysis/full_training_reproduction_campaign/",
            "src/analysis/full_paper_default_training_campaign_execution/",
            "src/analysis/evaluation_trace_bank_baseline_harness/",
            "requirements",
            "pyproject.toml",
            "AGENTS.md",
            ".specify/feature.json",
        )
        for path in paths:
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")
        approved_prefixes = (
            "artifacts/analysis/unified-campaign-result-analysis-figures-findings/",
            "docs/architecture/euls_phase21_unified_campaign_result_analysis_figures_findings.md",
            "specs/062-unified-campaign-result-analysis-figures-findings/",
            "src/analysis/unified_campaign_result_analysis_figures_findings/",
            "tests/unit/test_unified_campaign_result_analysis_figures_findings",
            "tests/integration/test_unified_campaign_result_analysis_figures_findings",
        )
        for path in paths:
            if path:
                self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")
        self.assertEqual(cached_output, [])


if __name__ == "__main__":
    unittest.main()
