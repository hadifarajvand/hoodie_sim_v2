from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.computation_delay_cpu_unit_validation.report import build_unit_validation_report, write_unit_validation_report


class ComputationDelayReportGenerationTests(unittest.TestCase):
    def test_report_artifacts_are_generated_with_required_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_path, md_path = write_unit_validation_report(build_unit_validation_report(), Path(tmp))
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(
                set(payload.keys()),
                {
                    "schema_version",
                    "feature_id",
                    "source_gates",
                    "paper_unit_evidence",
                    "runtime_unit_contract",
                    "slot_duration_audit",
                    "computation_delay_contract",
                    "cpu_capacity_contract",
                    "completion_slot_contract",
                    "mismatch_findings",
                    "repaired_items",
                    "unrecoverable_items",
                    "regression_checks",
                    "no_curve_fitting",
                    "no_policy_or_training_drift",
                    "generated_artifacts",
                    "validation_summary",
                },
            )
            self.assertEqual(payload["runtime_unit_contract"]["compute_config_path"], "src/environment/compute_config.py")
            self.assertEqual(payload["runtime_unit_contract"]["traffic_config_path"], "src/environment/traffic_config.py")
            self.assertEqual(payload["runtime_unit_contract"]["link_rate_config_path"], "src/environment/link_rate_config.py")
            self.assertEqual(payload["slot_duration_audit"]["paper_delta_seconds"], 0.1)
            self.assertEqual(payload["slot_duration_audit"]["runtime_delta_seconds"], 0.1)
            self.assertEqual(payload["slot_duration_audit"]["feature_027_reported_slot_duration_seconds"], 0.1)
            self.assertEqual(payload["slot_duration_audit"]["mismatch_status"], "matched")
            self.assertEqual(payload["slot_duration_audit"]["required_action"], "none")
            self.assertTrue(md_path.exists())


if __name__ == "__main__":
    unittest.main()
