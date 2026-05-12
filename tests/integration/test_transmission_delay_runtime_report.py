from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.transmission_delay_runtime_wiring import build_transmission_delay_runtime_wiring_report, write_transmission_delay_runtime_wiring_report


class TransmissionDelayRuntimeReportIntegrationTests(unittest.TestCase):
    def test_report_schema_and_contents(self) -> None:
        report = build_transmission_delay_runtime_wiring_report()

        self.assertEqual(report.feature_id, "034-transmission-delay-runtime-wiring")
        self.assertEqual(report.horizontal_rate_mbps, 30.0)
        self.assertEqual(report.vertical_rate_mbps, 10.0)
        self.assertEqual(report.slot_duration_seconds, 0.1)
        self.assertEqual(report.rounding_policy, "ceil")
        self.assertTrue(report.no_dependency_drift)
        self.assertTrue(report.no_training_or_policy_drift)
        self.assertTrue(report.no_reward_timing_change)
        self.assertTrue(report.no_execution_time_contract_drift)
        self.assertTrue(report.no_capacity_sharing_scope_creep)
        self.assertTrue(report.no_campaign_rerun)
        self.assertIn("src/environment/gym_adapter.py", report.wired_runtime_components)
        self.assertIn("src/environment/link_rate_config.py", report.validated_runtime_components)
        self.assertIn("transmission_rounding_policy", report.transmission_metadata_fields)
        self.assertIn("test_horizontal_transmission_delay_uses_task_size_and_RH", report.tests_added)
        self.assertIn("tests.integration.test_transmission_delay_runtime_wiring", report.tests_run)

    def test_report_writes_json_and_markdown(self) -> None:
        report = build_transmission_delay_runtime_wiring_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path, md_path = write_transmission_delay_runtime_wiring_report(report, Path(tmpdir) / "artifacts/analysis/transmission-delay-runtime-wiring")
            payload = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertEqual(payload["feature_id"], "034-transmission-delay-runtime-wiring")
            self.assertEqual(payload["final_verdict"], "transmission_delay_runtime_wired")
            self.assertEqual(payload["rounding_policy"], "ceil")
            self.assertEqual(payload["admission_boundary_contract"], report.admission_boundary_contract)
            self.assertEqual(payload["transmission_metadata_fields"], report.transmission_metadata_fields)


if __name__ == "__main__":
    unittest.main()

