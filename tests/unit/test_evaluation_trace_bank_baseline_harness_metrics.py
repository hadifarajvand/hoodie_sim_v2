from __future__ import annotations

import unittest

from src.analysis.evaluation_trace_bank_baseline_harness import (
    build_baseline_policy_registry,
    build_evaluation_trace_bank_baseline_harness_report,
    build_evaluation_trace_bank_summary,
)
from src.analysis.evaluation_trace_bank_baseline_harness.config import METRIC_SCHEMA_FIELDS
from src.analysis.evaluation_trace_bank_baseline_harness.model import EvaluationTraceBankBaselineHarnessReport
from tests.unit.test_evaluation_trace_bank_baseline_harness_schema import _base_report_kwargs


class EvaluationTraceBankBaselineHarnessMetricsTests(unittest.TestCase):
    def test_generated_report_has_complete_metric_schema(self) -> None:
        payload = build_evaluation_trace_bank_baseline_harness_report().to_dict()
        self.assertEqual(payload["final_verdict"], "evaluation_trace_bank_baseline_harness_ready")
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertEqual(payload["metric_schema_summary"]["missing_metric_fields"], [])
        self.assertEqual(tuple(payload["metric_schema_summary"]["required_metric_fields"]), METRIC_SCHEMA_FIELDS)
        self.assertTrue(payload["metric_schema_summary"]["metric_schema_complete"])
        for field in METRIC_SCHEMA_FIELDS:
            self.assertIn(field, payload["metric_schema_summary"]["required_metric_fields"])

    def test_metric_schema_cannot_omit_required_fields_on_pass_path(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["metric_schema_summary"]["missing_metric_fields"] = ["reward"]
        kwargs["metric_schema_summary"]["metric_schema_complete"] = False
        kwargs["metric_schema_summary"]["present_metric_fields"].remove("reward")
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessReport(**kwargs)

    def test_baseline_registry_is_non_empty_and_checkpoint_free(self) -> None:
        trace_bank = build_evaluation_trace_bank_summary()
        registry = build_baseline_policy_registry(trace_bank)
        self.assertGreater(registry["baseline_policy_count"], 0)
        self.assertIn("local-only", registry["registered_policy_names"])
        self.assertIn("random-legal", registry["registered_policy_names"])
        self.assertTrue(registry["action_contract_compatible"])
        self.assertTrue(registry["no_learned_policy_checkpoint_dependency"])

    def test_empty_baseline_registry_cannot_claim_ready(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["baseline_policy_registry_summary"]["registered_policy_names"] = []
        kwargs["baseline_policy_registry_summary"]["baseline_policy_count"] = 0
        kwargs["baseline_policy_registry_summary"]["policies"] = []
        kwargs["baseline_evaluation_harness_summary"]["registered_policy_count"] = 0
        kwargs["baseline_evaluation_harness_summary"]["evaluated_policy_count"] = 0
        kwargs["baseline_evaluation_harness_summary"]["per_policy_metric_shells"] = {}
        with self.assertRaises(ValueError):
            EvaluationTraceBankBaselineHarnessReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
