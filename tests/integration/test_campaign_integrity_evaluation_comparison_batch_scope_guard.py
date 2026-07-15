from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.analysis.campaign_integrity_evaluation_comparison_batch import build_campaign_integrity_evaluation_comparison_batch_report


class CampaignIntegrityEvaluationComparisonBatchScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_061_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True, capture_output=True, text=True)
            approved = repo / "src/analysis/campaign_integrity_evaluation_comparison_batch/fixture.txt"
            approved.parent.mkdir(parents=True, exist_ok=True)
            approved.write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True, text=True)
            approved.write_text("dirty\n", encoding="utf-8")
            dirty = repo / "tests/integration/test_campaign_integrity_evaluation_comparison_batch_dirty.txt"
            dirty.parent.mkdir(parents=True, exist_ok=True)
            dirty.write_text("dirty\n", encoding="utf-8")
            status_output = subprocess.run(["git", "status", "--short"], cwd=repo, check=True, capture_output=True, text=True).stdout.splitlines()
            diff_output = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.splitlines()
            cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=repo, check=True, capture_output=True, text=True).stdout.splitlines()
            paths = [line[3:].strip() for line in status_output] + [line.strip() for line in diff_output + cached_output]
            forbidden_prefixes = (
                ".specify/feature.json",
                "AGENTS.md",
                ".gitignore",
                "src/environment/",
                "src/policies/",
                "artifacts/analysis/full-paper-default-training-campaign-execution/",
                "artifacts/analysis/bind-full-campaign-real-torch-trainer/",
                "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
                "requirements",
                "pyproject.toml",
                "poetry.lock",
                "uv.lock",
            )
            approved_prefixes = (
                "src/analysis/campaign_integrity_evaluation_comparison_batch/",
                "tests/",
                "tests/integration/test_campaign_integrity_evaluation_comparison_batch",
            )
            for path in paths:
                for forbidden in forbidden_prefixes:
                    self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")
                if path:
                    self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")

    def test_report_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.campaign_integrity_evaluation_comparison_batch.runner as runner

        passing_baseline = {
            "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
            "trace_ids": ["trace-1"],
            "policies": ["FLC"],
            "metric_schema": {"required_metric_fields": ["delay"]},
            "baseline_policy_metrics": {"local-only": {"delay": 1.0, "drop": 0.0, "timeout": 0.0, "reward": 1.0, "action_distribution": {"local": 1}, "local_action_count": 1, "horizontal_action_count": 0, "vertical_action_count": 0, "per_episode_summary": []}},
            "controlled_experiment_data": True,
        }
        passing_trained = {
            "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
            "trace_ids": ["trace-1"],
            "metric_schema": {"required_metric_fields": ["delay"]},
            "trained_policy_metrics": {"delay": 1.0, "drop": 0.0, "timeout": 0.0, "reward": 1.0, "action_distribution": {"local": 1}, "train_eval_separation": {"evaluation_on_training_traces": False}},
            "controlled_experiment_data": True,
        }
        passing_campaign = {
            "feature_060_report_exists": True,
            "feature_060_training_metrics_exist": True,
            "feature_060_evaluation_metrics_exist": True,
            "feature_060_checkpoint_metadata_exist": True,
            "feature_060_run_manifest_exist": True,
            "artifact_manifest_paths_agree": True,
            "trace_bank_ids_consistent": True,
            "seed_bundle_consistent": True,
            "real_trainer_binding_evidence_exists": True,
            "scalar_fallback_drives_campaign_claim": False,
            "feature_060_sources": {"feature_060_report": "a", "feature_060b_report": "b", "feature_058_report": "c"},
            "feature_060_artifacts_refreshed": True,
        }
        passing_readiness = {
            "same_evaluation_trace_bank": True,
            "identical_metric_schema": True,
            "identical_action_contract": True,
            "trace_ids_comparable": True,
            "no_training_traces_leak_into_evaluation": True,
            "no_paper_reproduction_claim": True,
            "no_unsupported_superiority_claim": True,
        }
        passing_comparison = {
            "delay": {}, "drop": {}, "timeout": {}, "reward": {}, "action_distribution": {},
            "local_action_count": {}, "horizontal_action_count": {}, "vertical_action_count": {},
            "per_episode_summary": {}, "train_eval_separation": {},
            "baseline_policy_metrics": {}, "trained_policy_metrics": {},
            "controlled_experiment_data": True, "paper_reproduction_claim": False, "superiority_claim": False, "single_run_limitation": True,
        }

        with mock.patch.object(runner, "_status_paths", return_value=["src/policies/example.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_paths", return_value=[]):
                    with mock.patch.object(runner, "_feature_060_local_validation_mode", return_value=False):
                        with mock.patch.object(runner, "_baseline_results", return_value=passing_baseline):
                            with mock.patch.object(runner, "_trained_policy_results", return_value=passing_trained):
                                with mock.patch.object(runner, "_campaign_integrity_summary", return_value=passing_campaign):
                                    with mock.patch.object(runner, "_comparison_readiness_summary", return_value=passing_readiness):
                                        with mock.patch.object(runner, "_comparison_report_summary", return_value=passing_comparison):
                                            payload = build_campaign_integrity_evaluation_comparison_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "behavior_drift_detected")
        self.assertIn("behavior_drift_detected", payload["remaining_blockers"])
        self.assertFalse(payload["safety_summary"]["no_policy_drift"])


if __name__ == "__main__":
    unittest.main()
