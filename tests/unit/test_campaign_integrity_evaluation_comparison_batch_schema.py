from __future__ import annotations

import unittest

from src.analysis.campaign_integrity_evaluation_comparison_batch.model import CampaignIntegrityEvaluationComparisonBatchReport


def _base_report_kwargs() -> dict[str, object]:
    return {
        "feature_id": "061-campaign-integrity-evaluation-comparison-batch",
        "batch_items_covered": [
            "Campaign Result Integrity and Comparison Readiness Audit",
            "Baseline Evaluation Execution",
            "Trained Policy Evaluation Execution",
            "Baseline vs Trained Policy Comparison Readiness Audit",
            "Baseline vs Trained Policy Comparison Report",
        ],
        "prerequisite_tags_verified": [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "not_main", "verified": True, "details": "not main"},
        ],
        "feature_060_verified": True,
        "campaign_integrity_summary": {
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
        },
        "baseline_evaluation_summary": {
            "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
            "trace_ids": ["trace-1", "trace-2"],
            "policies": [{"name": "local-only"}],
            "metric_schema": {"required_metric_fields": ["delay", "drop"]},
            "baseline_policy_metrics": {"local-only": {"delay": {}, "drop": {}, "timeout": {}, "reward": {}, "action_distribution": {}, "local_action_count": 1, "horizontal_action_count": 0, "vertical_action_count": 0, "per_episode_summary": []}},
            "controlled_experiment_data": True,
        },
        "trained_policy_evaluation_summary": {
            "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
            "trace_ids": ["trace-1", "trace-2"],
            "metric_schema": {"required_metric_fields": ["delay", "drop"]},
            "trained_policy_metrics": {"delay": {}, "drop": {}, "timeout": {}, "reward": {}, "action_distribution": {}, "train_eval_separation": {}},
            "controlled_experiment_data": True,
        },
        "comparison_readiness_summary": {
            "same_evaluation_trace_bank": True,
            "identical_metric_schema": True,
            "identical_action_contract": True,
            "trace_ids_comparable": True,
            "no_training_traces_leak_into_evaluation": True,
            "no_paper_reproduction_claim": True,
            "no_unsupported_superiority_claim": True,
        },
        "comparison_report_summary": {
            "delay": {},
            "drop": {},
            "timeout": {},
            "reward": {},
            "action_distribution": {},
            "local_action_count": {},
            "horizontal_action_count": {},
            "vertical_action_count": {},
            "per_episode_summary": {},
            "train_eval_separation": {},
            "baseline_policy_metrics": {},
            "trained_policy_metrics": {},
            "controlled_experiment_data": True,
            "paper_reproduction_claim": False,
            "superiority_claim": False,
            "single_run_limitation": True,
        },
        "artifact_manifest_summary": {"artifact_exists": {}, "all_required_artifacts_exist": True},
        "safety_summary": {
            "no_dependency_drift": True,
            "no_policy_drift": True,
            "no_environment_contract_drift": True,
            "no_reward_timing_change": True,
            "no_prior_feature_artifact_rewrite": True,
            "no_paper_reproduction_claim": True,
            "no_unsupported_superiority_claim": True,
            "no_uncontrolled_campaign_loop": True,
        },
        "remaining_blockers": [],
        "recommended_next_feature": "Feature 062 — Multi-Seed Campaign and Ablation Batch",
        "final_verdict": "campaign_integrity_evaluation_comparison_batch_passed",
    }


class CampaignIntegrityEvaluationComparisonBatchSchemaTests(unittest.TestCase):
    def test_report_round_trip_schema(self) -> None:
        report = CampaignIntegrityEvaluationComparisonBatchReport(**_base_report_kwargs())
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "061-campaign-integrity-evaluation-comparison-batch")
        self.assertEqual(payload["final_verdict"], "campaign_integrity_evaluation_comparison_batch_passed")

    def test_report_rejects_pass_with_blockers(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["remaining_blockers"] = ["comparison_readiness_blocked"]
        with self.assertRaises(ValueError):
            CampaignIntegrityEvaluationComparisonBatchReport(**kwargs)

    def test_report_rejects_duplicate_prerequisite_names(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["prerequisite_tags_verified"] = [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "branch", "verified": True, "details": "duplicate"},
        ]
        with self.assertRaises(ValueError):
            CampaignIntegrityEvaluationComparisonBatchReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
