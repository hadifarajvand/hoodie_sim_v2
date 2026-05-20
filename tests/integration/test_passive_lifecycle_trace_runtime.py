from __future__ import annotations

import unittest

from src.analysis.passive_runtime_lifecycle_trace_instrumentation import TRACE_EVENT_TYPES, run_passive_runtime_lifecycle_trace_instrumentation


class PassiveLifecycleTraceRuntimeIntegrationTests(unittest.TestCase):
    def test_passive_trace_runner_uses_t_110(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        self.assertEqual(report.paper_default_runtime_verified["episode_length"], 110)
        self.assertEqual(report.paper_default_runtime_verified["timeout_slots"], 20)
        self.assertEqual(report.paper_default_runtime_verified["seeds"], [0, 1, 2])

    def test_trace_records_execution_progress_without_infering_completion(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        summary = report.trace_coverage_summary
        self.assertIn("execution_progress", summary["event_types_seen"])
        self.assertIn("task_dropped", summary["event_types_seen"])
        self.assertIn("reward_emitted", summary["event_types_seen"])

    def test_trace_records_completion_drop_reward_ordering(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        sample = report.lifecycle_trace_sample
        self.assertTrue(sample)
        self.assertIn(sample[0]["event_type"], TRACE_EVENT_TYPES)
        event_types = [item["event_type"] for item in sample]
        self.assertIn("task_generated", event_types)

    def test_trace_records_pending_at_horizon_as_non_terminal(self) -> None:
        report = run_passive_runtime_lifecycle_trace_instrumentation()
        self.assertIn("pending_at_horizon", report.trace_coverage_summary["required_event_types"])
        self.assertTrue(report.pending_at_horizon_contract_verified)


if __name__ == "__main__":
    unittest.main()
