from __future__ import annotations

import unittest

from src.analysis.full_paper_default_training_campaign_gate.model import FullPaperDefaultTrainingCampaignGateReport


def _base_report_kwargs() -> dict[str, object]:
    return {
        "feature_id": "059-full-paper-default-training-campaign-gate",
        "prerequisite_tags_verified": [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "feature_058_report_valid", "verified": True, "details": "058"},
        ],
        "feature_058_harness_verified": True,
        "campaign_scope_summary": {
            "full_campaign_allowed_next_feature": True,
            "full_campaign_executed_this_feature": False,
            "paper_default_training_campaign": True,
            "training_trace_bank_id": "full-training-train-bank",
            "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
            "baseline_harness_id": "feature-058-baseline-evaluation-harness",
            "seed_bundle": {"training_trace_generation_seed": 41, "evaluation_trace_generation_seed": 43},
            "run_count_or_episode_budget": {"training_episode_count": 1000, "evaluation_episode_count": 100},
            "campaign_scale_is_explicit": True,
        },
        "training_execution_gate_summary": {
            "training_execution_allowed_next_feature": True,
            "training_executed_this_feature": False,
            "optimizer_executed_this_feature": False,
            "replay_mutated_this_feature": False,
            "checkpoint_binary_written_this_feature": False,
        },
        "evaluation_harness_gate_summary": {
            "evaluation_trace_bank_ready": True,
            "train_eval_trace_banks_disjoint": True,
            "baseline_policy_registry_ready": True,
            "baseline_harness_ready": True,
            "metric_schema_complete": True,
            "determinism_ready": True,
        },
        "artifact_output_contract_summary": {
            "full_campaign_json_report": "artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json",
            "full_campaign_markdown_report": "artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md",
            "training_metrics_artifact": "artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json",
            "evaluation_metrics_artifact": "artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json",
            "checkpoint_metadata_artifact": "artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json",
            "run_manifest_artifact": "artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json",
            "artifact_output_contract_complete": True,
        },
        "resource_control_summary": {
            "deterministic_seeds": {"training_trace_generation_seed": 41, "evaluation_trace_generation_seed": 43},
            "max_episode_or_run_budget": {"training_episode_count": 1000, "evaluation_episode_count": 100},
            "timeout_runtime_budget": {"max_wall_clock_minutes": 240, "per_episode_timeout_seconds": 120},
            "controlled_output_directory": "artifacts/analysis/full-paper-default-training-campaign-execution/",
            "no_uncontrolled_loop": True,
            "resource_control_complete": True,
        },
        "checkpoint_contract_summary": {
            "metadata_required": True,
            "checkpoint_binary_policy": "Feature 060 may write checkpoint binaries only under its controlled output directory with metadata; Feature 059 writes none.",
            "target_update_metadata_required": True,
            "replay_metadata_required": True,
            "seed_bundle_required": True,
            "trace_bank_ids_required": True,
            "checkpoint_contract_complete": True,
        },
        "metric_collection_contract_summary": {
            "required_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics",
            ],
            "present_metric_fields": [
                "delay",
                "drop",
                "timeout",
                "reward",
                "action_distribution",
                "local_action_count",
                "horizontal_action_count",
                "vertical_action_count",
                "per_episode_summary",
                "train_eval_separation",
                "baseline_policy_metrics",
            ],
            "missing_metric_fields": [],
            "metric_collection_contract_complete": True,
        },
        "safety_summary": {
            "no_training_execution": True,
            "no_optimizer_execution": True,
            "no_replay_mutation": True,
            "no_checkpoint_binary_written": True,
            "no_full_campaign_execution": True,
            "no_paper_reproduction_claim": True,
            "no_performance_claim": True,
            "no_baseline_superiority_claim": True,
            "no_policy_drift": True,
            "no_dependency_drift": True,
            "no_environment_contract_drift": True,
            "no_reward_timing_change": True,
            "no_prior_artifact_rewrite": True,
        },
        "remaining_blockers": [],
        "recommended_next_feature": "Feature 060 — Full Paper-Default Training Campaign Execution",
        "final_verdict": "full_paper_default_training_campaign_gate_ready",
    }


class FullPaperDefaultTrainingCampaignGateSchemaTests(unittest.TestCase):
    def test_report_round_trip_schema(self) -> None:
        report = FullPaperDefaultTrainingCampaignGateReport(**_base_report_kwargs())
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "059-full-paper-default-training-campaign-gate")
        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_gate_ready")
        self.assertEqual(payload["recommended_next_feature"], "Feature 060 — Full Paper-Default Training Campaign Execution")

    def test_report_rejects_pass_with_blockers(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["remaining_blockers"] = ["campaign_scope_blocked"]
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignGateReport(**kwargs)

    def test_report_rejects_feature_060_route_when_blocked(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["feature_058_harness_verified"] = False
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignGateReport(**kwargs)

    def test_report_rejects_ready_when_any_prerequisite_tag_is_false(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["prerequisite_tags_verified"][1]["verified"] = False
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignGateReport(**kwargs)

    def test_prerequisite_tag_names_must_be_unique(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["prerequisite_tags_verified"] = [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "branch", "verified": True, "details": "duplicate"},
        ]
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignGateReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
