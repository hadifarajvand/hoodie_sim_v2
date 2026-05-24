from __future__ import annotations

import unittest

from src.analysis.passive_selected_action_trace_repair import build_passive_selected_action_trace_repair_report
from src.environment.lifecycle_trace import LifecycleTraceEvent


class PassiveSelectedActionTraceSchemaTests(unittest.TestCase):
    def test_lifecycle_trace_event_includes_selected_action_repair_fields(self) -> None:
        event = LifecycleTraceEvent(
            event_type="task_admitted",
            slot=1,
            selected_action="horizontal",
            selected_action_family="horizontal",
            selected_action_trace_source="decision_point",
            action_index=1,
            decision_event_id="trace:1:7",
            selected_action_to_task_join_key="trace:7",
            terminal_outcome_join_key="trace:7:terminal_outcome",
            strategy="HOODIE",
            seed=13,
            agent_id=3,
            task_id=7,
            trace_source_component="environment",
        )
        payload = event.to_dict()
        for key in [
            "selected_action",
            "action_index",
            "selected_action_family",
            "selected_action_trace_source",
            "decision_event_id",
            "selected_action_to_task_join_key",
            "terminal_outcome_join_key",
        ]:
            self.assertIn(key, payload)

    def test_report_schema_lists_selected_action_repair_fields(self) -> None:
        payload = build_passive_selected_action_trace_repair_report().to_dict()
        schema = payload["selected_action_trace_schema"]
        self.assertIn("selected_action", schema["required_fields"])
        self.assertIn("action_index", schema["required_fields"])
        self.assertIn("selected_action_family", schema["required_fields"])
        self.assertIn("decision_event_id", schema["required_fields"])
        self.assertIn("selected_action_to_task_join_key", schema["join_key_fields"])
        self.assertIn("terminal_outcome_join_key", schema["join_key_fields"])


if __name__ == "__main__":
    unittest.main()
