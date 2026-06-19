from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest import mock

from src.analysis.full_paper_default_training_campaign_execution import generate_full_paper_default_training_campaign_execution_artifacts
from tests.unit.test_full_paper_default_training_campaign_execution_schema import _baseline_metrics


def _mock_execution() -> dict[str, object]:
    return {
        "training_trace_bank_id": "full-training-train-bank",
        "evaluation_trace_bank_id": "full-training-eval-bank",
        "baseline_harness_id": "feature-058-baseline-evaluation-harness",
        "seed_bundle": {"training_trace_generation_seed": 41},
        "replay": [],
        "replay_size": 110000,
        "optimizer_step_count": 2670,
        "target_sync_count": 1,
        "loss_values": [24.95241355895996],
        "loss_is_finite": True,
        "action_distribution": {"local": 33000, "horizontal": 38000, "vertical": 39000, "invalid_or_noop_action_count": 0},
        "reward_summary": {"reward_count": 1000, "reward_available_count": 1000, "total_reward": -2000.0, "mean_reward": -2.0, "pending_at_horizon_count": 0},
        "evaluation": {
            "evaluation_episode_count": 100,
            "mean_reward": -40.0,
            "completed_task_count": 0,
            "dropped_task_count": 0,
            "terminal_transition_count": 0,
            "reward_bearing_transition_count": 0,
            "trace_bank_disjoint": True,
            "trace_bank_ids": {"training": "full-training-train-bank", "evaluation": "full-training-eval-bank"},
            "trace_ids": [f"eval-{index:03d}" for index in range(100)],
            "evaluation_on_training_traces": False,
            "candidate_reproduction_supported": False,
        },
        "baseline_evaluation_summary": {
            "baseline_policy_names": ["local-only", "random-legal", "fixed-horizontal"],
            "evaluated_policy_count": 3,
            "actual_baseline_evaluation_episode_count": 100,
            "per_policy_metrics": _baseline_metrics(),
            "baseline_metric_shells": _baseline_metrics(),
            "baseline_metrics_real_execution": True,
            "no_baseline_superiority_claim": True,
        },
        "evaluation_trace_bank_summary": {"evaluation_trace_bank_id": "feature-058-evaluation-trace-bank"},
        "checkpoint_metadata": {
            "stage": "full_training_candidate",
            "feature_id": "041-full-training-reproduction-campaign",
            "seed_bundle": {"training_trace_generation_seed": 41},
            "target_update_unit": "optimizer_step",
            "config_hash": "abc123",
            "train_trace_bank_id": "full-training-train-bank",
            "eval_trace_bank_id": "full-training-eval-bank",
            "optimizer_step_count": 2670,
            "replay_size": 110000,
            "full_campaign_enabled": True,
        },
        "binding_evidence": {
            "torch_import_used": True,
            "real_trainer_import_used": True,
            "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
            "real_trainer_instantiated": True,
            "real_trainer_method_called": "DDQNTrainer.run_full_candidate",
            "full_campaign_executed": True,
            "full_campaign_block_reason": None,
        },
        "full_result": type("FullResult", (), {"full_campaign_executed": True})(),
    }


class FullPaperDefaultTrainingCampaignExecutionReportIntegrationTests(unittest.TestCase):
    def test_report_artifacts_are_generated(self) -> None:
        with mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._status_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._staged_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._diff_names", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._run_controlled_campaign", return_value=_mock_execution()):
            report, json_path, md_path = generate_full_paper_default_training_campaign_execution_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], report.feature_id)
        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_execution_passed")
        self.assertEqual(payload["remaining_blockers"], [])
        baseline_payload = json.loads(Path("artifacts/analysis/full-paper-default-training-campaign-execution/baseline-evaluation-metrics.json").read_text(encoding="utf-8"))
        self.assertTrue(baseline_payload["baseline_metrics_real_execution"])
        for metrics in baseline_payload["per_policy_metrics"].values():
            self.assertEqual(metrics["episode_count"], 100)
        self.assertNotIn("metric_shell_only", json.dumps(baseline_payload))

    def test_markdown_report_mentions_required_sections(self) -> None:
        with mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._status_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._staged_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._diff_names", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._run_controlled_campaign", return_value=_mock_execution()):
            generate_full_paper_default_training_campaign_execution_artifacts()
        markdown = Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md").read_text(encoding="utf-8")
        self.assertIn("Full Paper-Default Training Campaign Execution Report", markdown)
        self.assertIn("## Campaign Execution Summary", markdown)
        self.assertIn("## Training Metrics Summary", markdown)
        self.assertIn("## Artifact Manifest Summary", markdown)

    def test_report_does_not_claim_reproduction_or_superiority(self) -> None:
        with mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._status_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._staged_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._diff_names", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._run_controlled_campaign", return_value=_mock_execution()):
            payload = generate_full_paper_default_training_campaign_execution_artifacts()[0].to_dict()
        self.assertTrue(payload["safety_summary"]["no_paper_reproduction_claim"])
        self.assertTrue(payload["safety_summary"]["no_performance_superiority_claim"])
        self.assertTrue(payload["safety_summary"]["no_baseline_superiority_claim"])
        self.assertTrue(payload["safety_summary"]["no_uncontrolled_campaign_loop"])


if __name__ == "__main__":
    unittest.main()
