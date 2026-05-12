from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.analysis.runtime_adoption_approved_assumption_registry import build_runtime_adoption_report, write_runtime_adoption_report
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.traffic_config import TrafficScenarioPreset
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class RuntimeAdoptionReportIntegrationTests(unittest.TestCase):
    def test_report_schema_and_contents(self) -> None:
        report = build_runtime_adoption_report()

        self.assertEqual(report.feature_id, "032-runtime-adoption-approved-assumption-registry")
        self.assertTrue(report.no_paper_recovery_claims)
        self.assertTrue(report.no_dependency_drift)
        self.assertTrue(report.no_training_or_policy_drift)
        self.assertTrue(report.no_reward_timing_change)
        self.assertTrue(report.no_campaign_rerun)
        self.assertIn("Figure_7_adjacency", report.consumed_assumption_ids)
        self.assertIn("src/environment/compute_config.py", report.runtime_components_changed)
        self.assertIn("test_timeout_drop_behavior_consumes_runtime_contract", report.tests_added)
        self.assertIn("ComputeConfig defaults 32.0/64.0/128.0 replaced with 0.5/0.5/3.0", report.old_stale_values_detected_or_replaced)

    def test_report_writes_json_and_markdown(self) -> None:
        report = build_runtime_adoption_report()

        with tempfile.TemporaryDirectory() as tmp:
            json_path, md_path = write_runtime_adoption_report(report, Path(tmp) / "artifacts/analysis/runtime-adoption-approved-assumption-registry")
            payload = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertEqual(payload["feature_id"], "032-runtime-adoption-approved-assumption-registry")
            self.assertEqual(payload["final_verdict"], "runtime_adoption_completed_with_user_approved_assumptions")
            self.assertTrue(payload["no_paper_recovery_claims"])
            self.assertEqual(len(payload["consumed_assumption_ids"]), 8)
            self.assertEqual(payload["runtime_components_validated"][0], "Figure_7_adjacency")

    def test_timeout_drop_behavior_consumes_runtime_contract(self) -> None:
        traffic = TrafficScenarioPreset.paper_default()
        env = HoodieGymEnvironment(
            episode_length=2,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            policy_name="FLC",
        )
        trace = EvaluationTrace(
            trace_id="timeout-drop",
            seed=1,
            tasks=(
                TraceTaskBlueprint(
                    task_id=1,
                    source_agent_id=1,
                    arrival_slot=0,
                    size=32.0,
                    processing_density=1.0,
                    timeout_length=traffic.timeout_slots,
                    absolute_deadline_slot=traffic.timeout_slots,
                ),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": "timeout-drop", "seed": "1"},
        )
        env.reset(seed=1)
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = traffic.timeout_slots + 1
        env._current_task = env._load_current_task()

        _obs, _reward, _terminated, _truncated, info = env.step("local")

        self.assertEqual(traffic.timeout_slots * traffic.slot_duration_seconds, 2.0)
        self.assertEqual(info["finalized_tasks"][0]["terminal_outcome"], "dropped")
        self.assertTrue(info["finalized_tasks"][0]["offload_lifecycle_events"])


if __name__ == "__main__":
    unittest.main()
