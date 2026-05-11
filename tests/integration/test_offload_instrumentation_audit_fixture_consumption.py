from __future__ import annotations

import unittest

from src.audits.differential_environment import DifferentialEnvironmentAudit, build_default_toy_cases
from tests.integration.offload_trace_fixtures import RichLifecycleAuditFixtureEnv


class OffloadInstrumentationAuditFixtureConsumptionTest(unittest.TestCase):
    def test_fixture_backed_audit_consumes_horizontal_and_vertical_lifecycle_events(self) -> None:
        horizontal_audit = DifferentialEnvironmentAudit(
            environment_factory=lambda: RichLifecycleAuditFixtureEnv(path="horizontal")
        )
        vertical_audit = DifferentialEnvironmentAudit(
            environment_factory=lambda: RichLifecycleAuditFixtureEnv(path="vertical")
        )

        horizontal_run = horizontal_audit._run_case(build_default_toy_cases()[1])
        vertical_run = vertical_audit._run_case(build_default_toy_cases()[2])

        self.assertGreater(len(horizontal_run.environment_summary.event_sequence), 1)
        self.assertGreater(len(vertical_run.environment_summary.event_sequence), 1)
        self.assertIn("queued_public", horizontal_run.environment_summary.event_sequence)
        self.assertIn("transmission_started", horizontal_run.environment_summary.event_sequence)
        self.assertIn("transmission_completed", horizontal_run.environment_summary.event_sequence)
        self.assertIn("execution_started", horizontal_run.environment_summary.event_sequence)
        self.assertIn("execution_completed", horizontal_run.environment_summary.event_sequence)
        self.assertTrue(
            "reward_emitted" in horizontal_run.environment_summary.event_sequence
            or "dropped_timeout" in horizontal_run.environment_summary.event_sequence
        )
        self.assertNotEqual(horizontal_run.environment_summary.event_sequence, ("selected_action:horizontal",))

        self.assertIn("offloaded_cloud", vertical_run.environment_summary.event_sequence)
        self.assertIn("transmission_started", vertical_run.environment_summary.event_sequence)
        self.assertIn("transmission_completed", vertical_run.environment_summary.event_sequence)
        self.assertIn("execution_started", vertical_run.environment_summary.event_sequence)
        self.assertIn("execution_completed", vertical_run.environment_summary.event_sequence)
        self.assertTrue(
            "reward_emitted" in vertical_run.environment_summary.event_sequence
            or "dropped_timeout" in vertical_run.environment_summary.event_sequence
        )
        self.assertNotEqual(vertical_run.environment_summary.event_sequence, ("selected_action:vertical",))
