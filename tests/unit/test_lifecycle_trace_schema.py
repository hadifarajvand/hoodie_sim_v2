from __future__ import annotations

import json
import unittest

from src.environment.lifecycle_trace import LifecycleTraceConfig, LifecycleTraceEvent, LifecycleTraceRecorder


class LifecycleTraceSchemaTests(unittest.TestCase):
    def test_lifecycle_trace_event_schema_exact(self) -> None:
        event = LifecycleTraceEvent(
            event_type="execution_progress",
            slot=1,
            task_id=7,
            source_agent_id=3,
            selected_action="local",
            destination="self",
            queue_type="private",
            host_node_id="3",
            arrival_slot=0,
            absolute_deadline_slot=20,
            task_age_slots=1,
            size_mbits=2.0,
            processing_density_gcycles_per_mbit=0.297,
            cycles_required_gcycles=0.594,
            cycles_before_gcycles=0.594,
            cycles_consumed_gcycles=0.5,
            cycles_after_gcycles=0.094,
            compute_capacity_gcycles_per_slot=0.5,
            transmission_started_at=None,
            transmission_completed_at=None,
            transmission_delay_slots=None,
            terminal_outcome=None,
            reward=None,
            reward_available=False,
            pending_at_horizon=False,
            legality_snapshot={"local": True},
            trace_source_component="environment",
        )
        payload = event.to_dict()
        expected_keys = {
            "event_type",
            "slot",
            "task_id",
            "source_agent_id",
            "selected_action",
            "destination",
            "queue_type",
            "host_node_id",
            "arrival_slot",
            "absolute_deadline_slot",
            "task_age_slots",
            "size_mbits",
            "processing_density_gcycles_per_mbit",
            "cycles_required_gcycles",
            "cycles_before_gcycles",
            "cycles_consumed_gcycles",
            "cycles_after_gcycles",
            "compute_capacity_gcycles_per_slot",
            "reward_available",
            "pending_at_horizon",
            "legality_snapshot",
            "trace_source_component",
        }
        self.assertTrue(expected_keys.issubset(payload))
        json.dumps(payload)

    def test_trace_recorder_disabled_by_default(self) -> None:
        recorder = LifecycleTraceRecorder()
        recorder.emit("task_generated", slot=0, trace_source_component="traffic_generator", task_id=1)
        self.assertEqual(recorder.snapshot(), [])

    def test_trace_recorder_serializes_json_safe_events(self) -> None:
        recorder = LifecycleTraceRecorder(enabled=True)
        recorder.emit("task_generated", slot=0, trace_source_component="traffic_generator", task_id=1, legality_snapshot={"local": True})
        payload = recorder.snapshot()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["event_type"], "task_generated")
        json.dumps(payload)


if __name__ == "__main__":
    unittest.main()

