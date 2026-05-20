from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.passive_runtime_lifecycle_trace_instrumentation import run_passive_runtime_lifecycle_trace_instrumentation


class PassiveLifecycleTraceReportIntegrationTests(unittest.TestCase):
    def test_passive_trace_report_schema(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        payload = report.to_dict()
        required = {
            "feature_id",
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
            "instrumentation_scope",
            "trace_event_schema",
            "trace_sources",
            "paper_default_runtime_verified",
            "behavior_equivalence_checks",
            "trace_coverage_summary",
            "lifecycle_trace_sample",
            "completion_diagnosis_readiness",
            "runtime_contracts_verified",
            "reward_timing_contract_verified",
            "pending_at_horizon_contract_verified",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_timeout_contract_drift",
            "no_capacity_contract_drift",
            "no_transmission_contract_drift",
            "no_action_legality_drift",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
            "final_verdict",
        }
        self.assertTrue(required.issubset(payload))
        self.assertEqual(payload["feature_id"], "044-passive-runtime-lifecycle-trace-instrumentation")
        self.assertIn(payload["final_verdict"], {"passive_trace_instrumentation_ready", "passive_trace_instrumentation_incomplete"})

    def test_report_writes_json_and_markdown_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation"
            report = run_passive_runtime_lifecycle_trace_instrumentation(output_dir=output_dir)
            json_path = output_dir / "lifecycle-trace-instrumentation-report.json"
            md_path = output_dir / "lifecycle-trace-instrumentation-report.md"
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], report.feature_id)
            self.assertTrue(payload["no_paper_reproduction_claim"])


if __name__ == "__main__":
    unittest.main()

