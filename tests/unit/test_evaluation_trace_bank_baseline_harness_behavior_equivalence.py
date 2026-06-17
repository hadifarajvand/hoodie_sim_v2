from __future__ import annotations

import unittest

from src.analysis.evaluation_trace_bank_baseline_harness import build_evaluation_trace_bank_baseline_harness_report
from src.analysis.evaluation_trace_bank_baseline_harness.config import EvaluationTraceBankBaselineHarnessConfig
from src.analysis.evaluation_trace_bank_baseline_harness.model import EvaluationTraceBankBaselineHarnessReport
from tests.unit.test_evaluation_trace_bank_baseline_harness_schema import _base_report_kwargs


class EvaluationTraceBankBaselineHarnessBehaviorEquivalenceTests(unittest.TestCase):
    def test_behavior_equivalence_check_names_are_unique(self) -> None:
        payload = build_evaluation_trace_bank_baseline_harness_report().to_dict()
        names = [entry["name"] for entry in payload["prerequisite_tags_verified"]]
        self.assertEqual(len(names), len(set(names)))

    def test_behavior_safety_fields_cover_all_forbidden_behaviors(self) -> None:
        payload = build_evaluation_trace_bank_baseline_harness_report().to_dict()
        self.assertEqual(payload["final_verdict"], "behavior_drift_detected")
        self.assertFalse(payload["behavior_safety_summary"]["no_policy_drift"])
        self.assertFalse(payload["behavior_safety_summary"]["no_environment_contract_drift"])
        self.assertFalse(payload["behavior_safety_summary"]["no_reward_timing_change"])
        for key in (
            "no_training_execution",
            "no_optimizer_execution",
            "no_replay_mutation",
            "no_checkpoint_binary_written",
            "no_full_campaign",
            "no_paper_reproduction_claim",
            "no_performance_claim",
            "no_policy_drift",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_reward_timing_change",
            "no_prior_artifact_rewrite",
        ):
            self.assertIn(key, payload["behavior_safety_summary"])
            self.assertIsInstance(payload["behavior_safety_summary"][key], bool)

    def test_forbidden_execution_flags_are_rejected_by_config(self) -> None:
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessConfig(run_training=True)
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessConfig(run_optimizer=True)
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessConfig(mutate_replay=True)
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessConfig(write_checkpoint_binary=True)
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessConfig(run_full_campaign=True)
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessConfig(claim_paper_reproduction=True)
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessConfig(claim_performance=True)

    def test_behavior_safety_false_cannot_claim_ready(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["behavior_safety_summary"]["no_training_execution"] = False
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
