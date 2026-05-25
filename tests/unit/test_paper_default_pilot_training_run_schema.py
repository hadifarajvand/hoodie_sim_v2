from __future__ import annotations

import unittest

from src.analysis.paper_default_pilot_training_run.model import PaperDefaultPilotTrainingRunReport


def _base_report_kwargs() -> dict[str, object]:
    return {
        "feature_id": "057-paper-default-pilot-training-run",
        "prerequisite_tags_verified": [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "not_main", "verified": True, "details": "not main"},
        ],
        "feature_056_validation_verified": True,
        "pilot_scope": {
            "pilot_episodes": 3,
            "pilot_episode_length": 110,
            "full_campaign": False,
            "baseline_comparison": False,
            "paper_reproduction_claim": False,
        },
        "live_environment_training_used": True,
        "fixture_training_used": False,
        "episode_summary": {
            "pilot_episodes": 3,
            "pilot_episode_length": 110,
            "episodes_requested": 3,
            "episodes_completed": 3,
            "completed_all_episodes": True,
        },
        "replay_summary": {
            "feature_055_smoke_replay_size": 110,
            "replay_size": 330,
            "replay_growth_count": 220,
            "replay_growth_validated": True,
            "sampled_batch_size": 16,
            "sampled_transition_count": 16,
            "replay_inserted": True,
            "sampled_field_coverage": {
                "state": True,
                "action": True,
                "legal_action_mask": True,
                "next_state": True,
                "reward": True,
                "terminal": True,
                "reward_available": True,
                "pending_at_horizon": True,
            },
            "delayed_reward_semantics_preserved": True,
            "pending_at_horizon_preserved": True,
            "reward_available_count": 5,
            "sample_transitions": [],
        },
        "optimizer_summary": {
            "feature_055_smoke_optimizer_step_count": 47,
            "optimizer_step_count": 141,
            "optimizer_step_growth_count": 94,
            "optimizer_progress_validated": True,
            "optimizer_steps_executed": True,
            "optimizer_step_monotonic": True,
            "target_sync_count": 0,
        },
        "target_update_summary": {
            "target_update_unit": "optimizer_step",
            "target_update_frequency": 2000,
            "target_sync_count": 0,
            "target_sync_before_threshold_blocked": True,
            "target_sync_at_threshold_validated": False,
            "target_update_contract_validated": True,
            "target_update_schedule_within_pilot": True,
        },
        "loss_summary": {
            "loss_count": 3,
            "all_losses_finite": True,
            "min_loss": 0.1,
            "max_loss": 0.4,
            "mean_loss": 0.2,
            "loss_values": [0.1, 0.2, 0.4],
        },
        "reward_summary": {
            "reward_count": 5,
            "reward_available_count": 5,
            "delayed_reward_contract_preserved": True,
            "pending_at_horizon_preserved": True,
            "total_reward": 2.5,
            "mean_reward": 0.5,
        },
        "legal_action_summary": {
            "legal_action_only": True,
            "illegal_action_count": 0,
        },
        "checkpoint_summary": {
            "checkpoint_schema_valid": True,
            "metadata_only": True,
            "model_checkpoint_written": False,
            "keys_present": {
                "target_update_unit": True,
                "optimizer_step_count": True,
                "replay_size": True,
                "config_hash": True,
                "train_trace_bank_id": True,
                "eval_trace_bank_id": True,
                "seed_bundle": True,
            },
            "checkpoint_metadata": {
                "target_update_unit": "optimizer_step",
                "optimizer_step_count": 141,
                "replay_size": 330,
                "config_hash": "abc123",
                "train_trace_bank_id": "full-training-train-bank",
                "eval_trace_bank_id": "full-training-eval-bank",
                "seed_bundle": {"training_trace_generation_seed": 41},
            },
        },
        "train_eval_contract_verified": {
            "train_eval_trace_banks_disjoint": True,
            "trace_bank_ids": {
                "training": "full-training-train-bank",
                "evaluation": "full-training-eval-bank",
            },
            "evaluation_on_training_traces": False,
            "candidate_reproduction_supported": False,
        },
        "behavior_safety_summary": {
            "no_full_campaign": True,
            "no_baseline_comparison": True,
            "no_paper_reproduction_claim": True,
            "no_performance_claim": True,
            "no_policy_drift": True,
            "no_dependency_drift": True,
            "no_environment_contract_drift": True,
            "no_reward_timing_change": True,
            "no_prior_artifact_rewrite": True,
        },
        "remaining_blockers": [],
        "recommended_next_feature": "Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness",
        "final_verdict": "paper_default_pilot_training_passed",
    }


class PaperDefaultPilotTrainingRunSchemaTests(unittest.TestCase):
    def test_report_round_trip_schema(self) -> None:
        report = PaperDefaultPilotTrainingRunReport(**_base_report_kwargs())
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "057-paper-default-pilot-training-run")
        self.assertEqual(payload["final_verdict"], "paper_default_pilot_training_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness")
        self.assertEqual(payload["pilot_scope"]["pilot_episodes"], 3)

    def test_report_rejects_pass_with_blockers(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["remaining_blockers"] = ["replay_growth_not_validated"]
        with self.assertRaises(ValueError):
            PaperDefaultPilotTrainingRunReport(**kwargs)

    def test_prerequisite_tag_names_must_be_unique(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["prerequisite_tags_verified"] = [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "branch", "verified": True, "details": "duplicate"},
        ]
        with self.assertRaises(ValueError):
            PaperDefaultPilotTrainingRunReport(**kwargs)
