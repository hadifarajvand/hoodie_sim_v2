from __future__ import annotations

import unittest

from src.analysis.evaluation_trace_bank_baseline_harness.model import EvaluationTraceBankBaselineHarnessReport


def _base_report_kwargs() -> dict[str, object]:
    trace_ids = [f"feature-058-evaluation-trace-bank-trace-{index:03d}" for index in range(3)]
    metric_shell = {
        "delay": {"value": None, "status": "schema_only_not_performance_claim"},
        "drop": {"value": None, "status": "schema_only_not_performance_claim"},
        "timeout": {"value": None, "status": "schema_only_not_performance_claim"},
        "reward": {"value": None, "status": "schema_only_not_performance_claim"},
        "action_distribution": {"local": 3, "horizontal": 0, "vertical": 0},
        "local_action_count": 3,
        "horizontal_action_count": 0,
        "vertical_action_count": 0,
        "per_episode_summary": [{"episode_id": 0, "metric_shell_only": True, "performance_claim": False}],
    }
    return {
        "feature_id": "058-evaluation-trace-bank-baseline-harness",
        "prerequisite_tags_verified": [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "feature_057_report_valid", "verified": True, "details": "057"},
        ],
        "feature_057_pilot_verified": True,
        "evaluation_trace_bank_summary": {
            "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
            "evaluation_trace_count": 3,
            "seed_bundle": {"evaluation_trace_generation_seed": 43, "baseline_policy_seed": 6101},
            "trace_identities": trace_ids,
            "trace_hashes": ["a" * 64, "b" * 64, "c" * 64],
            "trace_bank_signature": "d" * 64,
            "repeatability_evidence": {"same_seed_rebuild_signature": "d" * 64},
            "bank_generation_repeatable": True,
        },
        "train_eval_separation_summary": {
            "training_trace_bank_id": "full-training-train-bank",
            "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
            "training_trace_bank_exists": True,
            "evaluation_trace_bank_exists": True,
            "training_trace_ids": ["full-training-train-bank-trace-000"],
            "evaluation_trace_ids": trace_ids,
            "overlap_trace_ids": [],
            "train_eval_trace_banks_disjoint": True,
            "evaluation_on_training_traces": False,
        },
        "baseline_policy_registry_summary": {
            "registered_policy_names": ["local-only"],
            "baseline_policy_count": 1,
            "policies": [
                {
                    "name": "local-only",
                    "kind": "deterministic-fixed-action",
                    "selected_action": "local",
                    "action_contract_compatible": True,
                    "learned_policy_checkpoint_dependency": False,
                }
            ],
            "action_contract_compatible": True,
            "no_learned_policy_checkpoint_dependency": True,
        },
        "baseline_evaluation_harness_summary": {
            "registered_policy_count": 1,
            "evaluated_policy_count": 1,
            "evaluation_trace_count": 3,
            "per_policy_metric_shells": {"local-only": metric_shell},
            "no_optimizer_steps": True,
            "no_replay_mutation": True,
            "no_checkpoint_binary": True,
            "no_training_execution": True,
        },
        "metric_schema_summary": {
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
            ],
            "missing_metric_fields": [],
            "metric_schema_complete": True,
        },
        "determinism_summary": {
            "trace_bank_repeatable": True,
            "harness_outputs_repeatable": True,
            "first_run_signature": "e" * 64,
            "second_run_signature": "e" * 64,
            "repeatability_proven": True,
        },
        "behavior_safety_summary": {
            "no_training_execution": True,
            "no_optimizer_execution": True,
            "no_replay_mutation": True,
            "no_checkpoint_binary_written": True,
            "no_full_campaign": True,
            "no_paper_reproduction_claim": True,
            "no_performance_claim": True,
            "no_policy_drift": True,
            "no_dependency_drift": True,
            "no_environment_contract_drift": True,
            "no_reward_timing_change": True,
            "no_prior_artifact_rewrite": True,
        },
        "remaining_blockers": [],
        "recommended_next_feature": "Feature 059 — Full Paper-Default Training Campaign Gate",
        "final_verdict": "evaluation_trace_bank_baseline_harness_ready",
    }


class EvaluationTraceBankBaselineHarnessSchemaTests(unittest.TestCase):
    def test_report_round_trip_schema(self) -> None:
        report = EvaluationTraceBankBaselineHarnessReport(**_base_report_kwargs())
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "058-evaluation-trace-bank-baseline-harness")
        self.assertEqual(payload["final_verdict"], "evaluation_trace_bank_baseline_harness_ready")
        self.assertEqual(payload["recommended_next_feature"], "Feature 059 — Full Paper-Default Training Campaign Gate")

    def test_report_rejects_pass_with_blockers(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["remaining_blockers"] = ["metric_schema_blocked"]
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessReport(**kwargs)

    def test_report_rejects_duplicate_prerequisite_names(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["prerequisite_tags_verified"] = [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "branch", "verified": True, "details": "duplicate"},
        ]
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessReport(**kwargs)

    def test_report_rejects_pass_routing_when_feature_057_gate_fails(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["feature_057_pilot_verified"] = False
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
