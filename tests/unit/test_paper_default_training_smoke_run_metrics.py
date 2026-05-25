from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import unittest

from src.analysis.paper_default_training_smoke_run import PaperDefaultTrainingSmokeReport, build_paper_default_training_smoke_report
from src.analysis.paper_default_training_smoke_run.runner import _feature_054_readiness_verified


class PaperDefaultTrainingSmokeRunMetricsTests(unittest.TestCase):
    def test_feature_054_readiness_gate_requires_declared_fields(self) -> None:
        payload = json.loads(
            Path("artifacts/analysis/training-readiness-contract/training-readiness-contract-report.json").read_text(encoding="utf-8")
        )
        self.assertTrue(_feature_054_readiness_verified(payload))
        cases = [
            ("feature_id", "not-054"),
            ("feature_053_readiness_verified", False),
            ("evidence_chain_ready_for_training_contract", False),
            ("training_execution_allowed_next", False),
            ("remaining_blockers", ["unexpected"]),
            ("final_verdict", "not-ready"),
            ("recommended_next_feature", "Feature 999 — Wrong"),
        ]
        for field_name, bad_value in cases:
            mutated = deepcopy(payload)
            mutated[field_name] = bad_value
            self.assertFalse(_feature_054_readiness_verified(mutated), msg=field_name)

    def test_smoke_run_contracts_are_true_on_the_passing_path(self) -> None:
        payload = build_paper_default_training_smoke_report().to_dict()
        self.assertTrue(payload["feature_054_readiness_verified"])
        self.assertTrue(payload["live_environment_training_used"])
        self.assertFalse(payload["fixture_training_used"])
        self.assertGreater(payload["replay_summary"]["replay_size"], 0)
        self.assertTrue(payload["replay_summary"]["replay_inserted"])
        self.assertGreater(payload["optimizer_step_summary"]["optimizer_step_count"], 0)
        self.assertTrue(payload["optimizer_step_summary"]["optimizer_steps_executed"])
        self.assertTrue(payload["loss_summary"]["loss_is_finite"])
        self.assertTrue(payload["legal_action_summary"]["legal_action_only"])
        self.assertTrue(payload["delayed_reward_contract_verified"]["delayed_reward_contract_preserved"])
        self.assertTrue(payload["train_eval_contract_verified"]["train_eval_trace_banks_disjoint"])
        self.assertTrue(payload["checkpoint_summary"]["checkpoint_schema_valid"])
        self.assertFalse(payload["checkpoint_summary"]["model_checkpoint_written"])
        self.assertTrue(payload["behavior_safety_summary"]["no_full_campaign"])
        self.assertTrue(payload["behavior_safety_summary"]["no_baseline_comparison"])
        self.assertTrue(payload["behavior_safety_summary"]["no_paper_reproduction_claim"])
        self.assertTrue(payload["behavior_safety_summary"]["no_policy_drift"])
        self.assertTrue(payload["behavior_safety_summary"]["no_dependency_drift"])
        self.assertTrue(payload["behavior_safety_summary"]["no_environment_contract_drift"])
        self.assertEqual(payload["final_verdict"], "paper_default_training_smoke_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 056 — Target Update and Replay Training Validation")
        self.assertFalse(payload["remaining_blockers"])

    def test_blocked_reports_cannot_claim_pass_or_route_to_feature_056(self) -> None:
        payload = build_paper_default_training_smoke_report().to_dict()
        payload["remaining_blockers"] = ["replay_empty"]
        payload["final_verdict"] = "paper_default_training_smoke_passed"
        with self.assertRaises(ValueError):
            PaperDefaultTrainingSmokeReport(**payload)

        payload = build_paper_default_training_smoke_report().to_dict()
        payload["remaining_blockers"] = ["replay_empty"]
        payload["final_verdict"] = "paper_default_training_smoke_blocked"
        payload["recommended_next_feature"] = "Feature 056 — Target Update and Replay Training Validation"
        with self.assertRaises(ValueError):
            PaperDefaultTrainingSmokeReport(**payload)


if __name__ == "__main__":
    unittest.main()
