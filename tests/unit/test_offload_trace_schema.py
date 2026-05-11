from __future__ import annotations

import unittest

from src.environment.offload_trace_schema import OFFLOAD_LIFECYCLE_EVENTS


class OffloadTraceSchemaTest(unittest.TestCase):
    def test_event_sequence_is_stable_and_ordered(self) -> None:
        self.assertEqual(
            OFFLOAD_LIFECYCLE_EVENTS,
            (
                "selected_action",
                "queued_public",
                "offloaded_cloud",
                "transmission_started",
                "transmission_completed",
                "execution_started",
                "execution_completed",
                "dropped_timeout",
                "reward_emitted",
            ),
        )

