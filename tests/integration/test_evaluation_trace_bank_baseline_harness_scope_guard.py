from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.evaluation_trace_bank_baseline_harness import build_evaluation_trace_bank_baseline_harness_report
from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


class EvaluationTraceBankBaselineHarnessScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_058_paths(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/evaluation-trace-bank-baseline-harness/report.json", "{}\n")
        repo.write("specs/058-evaluation-trace-bank-baseline-harness/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/evaluation-trace-bank-baseline-harness/report.json", "specs/058-evaluation-trace-bank-baseline-harness/spec.md")
        repo.git("commit", "-m", "feature commit")
        status_output = repo.output("status", "--short").splitlines()
        diff_output = repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines()
        cached_output = repo.output("diff", "--cached", "--name-only").splitlines()

        forbidden_prefixes = (
            ".specify/feature.json",
            "AGENTS.md",
            ".gitignore",
            "src/environment/",
            "src/policies/",
            "artifacts/analysis/paper-default-pilot-training-run/",
            "artifacts/analysis/target-update-replay-training-validation/",
            "artifacts/analysis/paper-default-training-smoke-run/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        paths = [line[3:].strip() for line in status_output] + [line.strip() for line in diff_output + cached_output]
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
            self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")
        self.assertEqual(cached_output, [])

    def test_report_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.evaluation_trace_bank_baseline_harness.runner as runner

        with mock.patch.object(runner, "_status_paths", return_value=["src/policies/example.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_names", return_value=[]):
                    payload = build_evaluation_trace_bank_baseline_harness_report().to_dict()
        self.assertEqual(payload["final_verdict"], "feature_057_prerequisite_blocked")
        self.assertFalse(payload["behavior_safety_summary"]["no_policy_drift"])


if __name__ == "__main__":
    unittest.main()
