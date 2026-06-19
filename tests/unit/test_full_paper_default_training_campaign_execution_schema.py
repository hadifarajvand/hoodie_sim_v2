from __future__ import annotations

import unittest

from src.analysis.full_paper_default_training_campaign_execution.model import FullPaperDefaultTrainingCampaignExecutionReport


def _baseline_metrics() -> dict[str, object]:
    return {
        name: {
            "episode_count": 100,
            "metric_shell_only": False,
            "performance_claim": False,
            "action_distribution": {"local": 100, "horizontal": 0, "vertical": 0},
            "local_action_count": 100,
            "horizontal_action_count": 0,
            "vertical_action_count": 0,
            "reward_summary": {"reward_count": 100, "total_reward": -100.0, "mean_reward": -1.0},
            "completed_task_count": 1,
            "dropped_task_count": 2,
            "terminal_transition_count": 3,
            "reward_bearing_transition_count": 3,
            "illegal_action_count": 0,
            "fallback_action_count": 0,
            "trace_ids": [f"eval-{index:03d}" for index in range(100)],
            "per_episode_summary": [
                {"episode_id": index, "metric_shell_only": False, "performance_claim": False}
                for index in range(100)
            ],
            "no_baseline_superiority_claim": True,
        }
        for name in ("local-only", "random-legal", "fixed-horizontal")
    }


def _base_report_kwargs() -> dict[str, object]:
    baseline_metrics = _baseline_metrics()
    return {
        "feature_id": "060-full-paper-default-training-campaign-execution",
        "prerequisite_tags_verified": [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "feature_059_report_valid", "verified": True, "details": "059"},
            {"name": "feature_060a_report_valid", "verified": True, "details": "060a"},
            {"name": "feature_058_report_present", "verified": True, "details": "058"},
            {"name": "feature_057_report_present", "verified": True, "details": "057"},
        ],
        "feature_059_gate_verified": True,
        "feature_060a_validation_verified": True,
        "feature_058_harness_verified": True,
        "campaign_execution_summary": {
            "configured_budget": {
                "training_episode_count": 1000,
                "evaluation_episode_count": 100,
                "baseline_evaluation_episode_count": 100,
                "episode_length": 110,
            },
            "actual_training_episode_count": 1000,
            "actual_evaluation_episode_count": 100,
            "actual_baseline_evaluation_episode_count": 100,
            "training_trace_bank_id": "full-training-train-bank",
            "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
            "baseline_harness_id": "feature-058-baseline-evaluation-harness",
            "seed_bundle": {"training_trace_generation_seed": 41},
            "execution_completed": True,
            "controlled_output_directory": "artifacts/analysis/full-paper-default-training-campaign-execution",
            "actual_budget_is_full_campaign": True,
            "actual_budget_is_reduced_for_local_validation": False,
            "real_trainer_used": True,
            "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
            "trainer_method_called": "DDQNTrainer.run_full_candidate",
            "full_campaign_executed": True,
        },
        "training_metrics_summary": {
            "optimizer_step_count": 47,
            "replay_size": 110,
            "loss_count": 47,
            "loss_finite": True,
            "reward_summary": {"reward_count": 10},
            "target_update_summary": {"target_update_unit": "optimizer_step"},
            "action_distribution": {"local": 37, "horizontal": 37, "vertical": 36, "invalid_or_noop_action_count": 0},
            "local_action_count": 37,
            "horizontal_action_count": 37,
            "vertical_action_count": 36,
            "invalid_or_noop_action_count": 0,
            "action_count_total": 110,
            "action_accounting_reconciled": True,
        },
        "evaluation_metrics_summary": {
            "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
            "evaluation_episode_count": 100,
            "metric_schema_coverage": {"metric_schema_complete": True},
            "delay": {"value": None, "status": "not_claimed_in_feature_060"},
            "drop": {"count": 1},
            "timeout": {"value": None, "status": "not_claimed_in_feature_060"},
            "reward": {"mean_reward": 0.1, "reward_bearing_transition_count": 1},
            "action_distribution": {"local": None, "horizontal": None, "vertical": None},
            "no_paper_reproduction_claim": True,
            "no_performance_superiority_claim": True,
        },
        "baseline_evaluation_summary": {
            "baseline_policy_names": ["local-only", "random-legal", "fixed-horizontal"],
            "evaluated_policy_count": 3,
            "actual_baseline_evaluation_episode_count": 100,
            "per_policy_metrics": baseline_metrics,
            "baseline_metric_shells": baseline_metrics,
            "baseline_metrics_real_execution": True,
            "no_baseline_superiority_claim": True,
        },
        "checkpoint_metadata_summary": {
            "metadata_artifact_exists": True,
            "target_update_metadata": {"target_update_unit": "optimizer_step"},
            "replay_metadata": {"replay_size": 110},
            "seed_bundle": {"training_trace_generation_seed": 41},
            "trace_bank_ids": {"training": "full-training-train-bank", "evaluation": "feature-058-evaluation-trace-bank"},
            "checkpoint_binary_policy": "metadata-only",
        },
        "artifact_manifest_summary": {
            "full_campaign_json_report": "report.json",
            "full_campaign_markdown_report": "report.md",
            "training_metrics_json": "training-metrics.json",
            "evaluation_metrics_json": "evaluation-metrics.json",
            "baseline_evaluation_metrics_json": "baseline-evaluation-metrics.json",
            "checkpoint_metadata_json": "checkpoint-metadata.json",
            "run_manifest_json": "run-manifest.json",
            "all_required_artifacts_exist": True,
        },
        "resource_control_summary": {
            "configured_budget": {
                "training_episode_count": 1000,
                "evaluation_episode_count": 100,
                "baseline_evaluation_episode_count": 100,
                "episode_length": 110,
            },
            "actual_executed_budget": {
                "training_episode_count": 1000,
                "evaluation_episode_count": 100,
                "baseline_evaluation_episode_count": 100,
            },
            "controlled_output_directory": "artifacts/analysis/full-paper-default-training-campaign-execution",
            "timeout_runtime_budget": {"max_wall_clock_minutes": 240},
            "no_uncontrolled_campaign_loop": True,
            "resource_control_observed": True,
        },
        "safety_summary": {
            "no_paper_reproduction_claim": True,
            "no_performance_superiority_claim": True,
            "no_baseline_superiority_claim": True,
            "no_uncontrolled_campaign_loop": True,
            "no_policy_drift": True,
            "no_dependency_drift": True,
            "no_environment_contract_drift": True,
            "no_reward_timing_change": True,
            "no_prior_artifact_rewrite": True,
        },
        "remaining_blockers": [],
        "recommended_next_feature": "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit",
        "final_verdict": "full_paper_default_training_campaign_execution_passed",
    }


class FullPaperDefaultTrainingCampaignExecutionSchemaTests(unittest.TestCase):
    def test_report_round_trip_schema(self) -> None:
        report = FullPaperDefaultTrainingCampaignExecutionReport(**_base_report_kwargs())
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "060-full-paper-default-training-campaign-execution")
        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_execution_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit")

    def test_report_rejects_pass_with_blockers(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["remaining_blockers"] = ["training_metrics_blocked"]
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)

    def test_report_rejects_feature_061_route_when_gate_fails(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["feature_059_gate_verified"] = False
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)

    def test_report_rejects_ready_when_any_prerequisite_tag_is_false(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["prerequisite_tags_verified"][1]["verified"] = False
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)

    def test_prerequisite_tag_names_must_be_unique(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["prerequisite_tags_verified"] = [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "branch", "verified": True, "details": "duplicate"},
        ]
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
