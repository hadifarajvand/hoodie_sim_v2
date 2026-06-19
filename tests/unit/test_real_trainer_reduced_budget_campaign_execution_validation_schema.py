from __future__ import annotations

import unittest

from src.analysis.real_trainer_reduced_budget_campaign_execution_validation.model import RealTrainerReducedBudgetCampaignExecutionValidationReport


def _base_report_kwargs() -> dict[str, object]:
    return {
        "feature_id": "060a-real-trainer-reduced-budget-campaign-execution-validation",
        "prerequisite_tags_verified": [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "feature_059_report_valid", "verified": True, "details": "059"},
            {"name": "feature_058_report_valid", "verified": True, "details": "058"},
            {"name": "feature_057_report_valid", "verified": True, "details": "057"},
        ],
        "feature_059_gate_verified": True,
        "feature_058_harness_verified": True,
        "feature_057_pilot_verified": True,
        "real_trainer_binding_summary": {
            "torch_import_used": True,
            "real_trainer_import_used": True,
            "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
            "real_trainer_instantiated": True,
            "trainer_method_called": "DDQNTrainer.run_pilot",
            "real_trainer_update_or_train_called": True,
        },
        "reduced_budget_execution_summary": {
            "configured_full_campaign_budget": {"training_episode_count": 1000, "evaluation_episode_count": 100, "baseline_evaluation_episode_count": 100},
            "actual_reduced_budget": {"training_episode_count": 1, "evaluation_episode_count": 3, "baseline_evaluation_episode_count": 1, "actual_episode_length": 110},
            "actual_budget_is_reduced_for_validation": True,
            "full_campaign_executed": False,
            "real_trainer_used": True,
            "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
            "trainer_method_called": "DDQNTrainer.run_pilot",
            "optimizer_steps_executed": True,
            "replay_populated": True,
            "loss_finite": True,
            "evaluation_metrics_generated": True,
            "baseline_contract_checked": True,
            "checkpoint_metadata_written": True,
            "run_manifest_written": True,
        },
        "training_metrics_summary": {
            "optimizer_step_count": 1,
            "replay_size": 1,
            "loss_count": 1,
            "loss_finite": True,
            "action_distribution": {"local": 1, "horizontal": 0, "vertical": 0},
        },
        "evaluation_metrics_summary": {
            "evaluation_episode_count": 3,
            "trace_bank_disjoint": True,
            "trace_bank_ids": {"training": "t", "evaluation": "e"},
            "evaluation_on_training_traces": False,
        },
        "baseline_contract_summary": {
            "feature_058_harness_verified": True,
            "baseline_harness_ready": True,
            "baseline_registry_ready": True,
            "metric_schema_complete": True,
            "baseline_policy_count": 3,
            "baseline_policy_names": ["local-only", "random-legal", "fixed-horizontal"],
            "evaluation_trace_count": 12,
        },
        "checkpoint_metadata_summary": {
            "metadata_artifact_exists": True,
            "checkpoint_schema_valid": True,
            "target_update_metadata": {"target_update_unit": "optimizer_step"},
            "replay_metadata": {"replay_size": 1},
            "seed_bundle": {"training_trace_generation_seed": 41},
            "checkpoint_metadata": {"target_update_unit": "optimizer_step"},
        },
        "artifact_manifest_summary": {
            "real_campaign_json_report": "x",
            "real_campaign_markdown_report": "x",
            "training_metrics_json": "x",
            "evaluation_metrics_json": "x",
            "checkpoint_metadata_json": "x",
            "run_manifest_json": "x",
            "all_required_artifacts_exist": True,
        },
        "resource_control_summary": {
            "configured_full_campaign_budget": {"training_episode_count": 1000},
            "actual_reduced_budget": {"training_episode_count": 1},
            "actual_budget_is_reduced_for_validation": True,
            "resource_control_complete": True,
        },
        "safety_summary": {
            "no_full_campaign_execution": True,
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
        "recommended_next_feature": "Feature 060 — Full Paper-Default Training Campaign Execution",
        "final_verdict": "real_trainer_reduced_budget_campaign_validation_passed",
    }


class RealTrainerReducedBudgetCampaignExecutionValidationSchemaTests(unittest.TestCase):
    def test_report_round_trip_schema(self) -> None:
        report = RealTrainerReducedBudgetCampaignExecutionValidationReport(**_base_report_kwargs())
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "060a-real-trainer-reduced-budget-campaign-execution-validation")
        self.assertEqual(payload["final_verdict"], "real_trainer_reduced_budget_campaign_validation_passed")

    def test_report_rejects_pass_with_blockers(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["remaining_blockers"] = ["training_metrics_blocked"]
        with self.assertRaises(ValueError):
            RealTrainerReducedBudgetCampaignExecutionValidationReport(**kwargs)

    def test_prerequisite_tag_names_must_be_unique(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["prerequisite_tags_verified"] = [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "branch", "verified": True, "details": "dup"},
        ]
        with self.assertRaises(ValueError):
            RealTrainerReducedBudgetCampaignExecutionValidationReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
