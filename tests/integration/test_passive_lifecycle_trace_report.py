from __future__ import annotations

import json
from unittest import mock
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
        self.assertIn(payload["final_verdict"], {"passive_trace_instrumentation_ready", "passive_trace_instrumentation_incomplete", "behavior_drift_detected"})
        statuses = payload["trace_coverage_summary"]["event_statuses"]
        self.assertTrue(statuses)
        self.assertEqual({item["event_type"] for item in statuses}, set(payload["trace_coverage_summary"]["required_event_types"]))
        self.assertTrue(all("event_type_supported" in item and "event_type_observed" in item and "event_type_missing_from_instrumentation" in item for item in statuses))
        self.assertTrue(payload["trace_coverage_summary"]["task_completed_supported"])
        self.assertIn("task_completed_observed", payload["trace_coverage_summary"])
        self.assertTrue(payload["trace_coverage_summary"]["deadline_expired_supported"])

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

    def test_report_uses_paper_default_sample_constraints(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        sample = report.lifecycle_trace_sample
        self.assertTrue(sample)
        first = sample[0]
        self.assertGreaterEqual(first["size_mbits"], 2.0)
        self.assertLessEqual(first["size_mbits"], 5.0)
        self.assertEqual(first["processing_density_gcycles_per_mbit"], 0.297)
        self.assertEqual(first["absolute_deadline_slot"] - first["arrival_slot"], 20)
        self.assertEqual(report.paper_default_runtime_verified["timeout_slots"], 20)
        self.assertEqual(report.paper_default_runtime_verified["episode_length"], 110)

    def test_report_marks_pointer_only_dirty_workspace_as_clean_enough(self) -> None:
        with mock.patch("src.analysis.passive_runtime_lifecycle_trace_instrumentation.runner._tracked_dirty_paths", return_value=[".specify/feature.json"]):
            report = run_passive_runtime_lifecycle_trace_instrumentation()
        dirty_tag = next(entry for entry in report.prerequisite_tags_verified if entry["name"] == "no_unrelated_dirty_files")
        self.assertTrue(dirty_tag["verified"])
        self.assertNotIn("AGENTS.md", dirty_tag["details"])

    def test_report_event_status_model_distinguishes_support_observation_missing(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        summary = report.trace_coverage_summary
        statuses = {item["event_type"]: item for item in summary["event_statuses"]}
        self.assertTrue(statuses["task_completed"]["event_type_supported"])
        self.assertIn("event_type_observed", statuses["task_completed"])
        self.assertTrue(statuses["deadline_expired"]["event_type_supported"])
        self.assertNotIn("task_completed", summary["event_type_missing_from_instrumentation"])
        self.assertNotIn("deadline_expired", summary["event_type_missing_from_instrumentation"])

    def test_report_requires_deadline_expired_before_or_with_task_dropped(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        summary = report.trace_coverage_summary
        if summary["event_type_observed"]["task_dropped"]:
            self.assertTrue(summary["completion_drop_ordering_observed"])
            self.assertTrue(summary["deadline_expired_observed"])
        else:
            self.assertFalse(summary["event_type_observed"]["task_dropped"])


if __name__ == "__main__":
    unittest.main()
