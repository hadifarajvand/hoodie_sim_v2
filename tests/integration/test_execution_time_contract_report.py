from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.execution_time_contract_repair import build_execution_time_contract_report, write_execution_time_contract_report


class ExecutionTimeContractReportIntegrationTests(unittest.TestCase):
    def test_report_schema_and_write(self) -> None:
        report = build_execution_time_contract_report()

        self.assertEqual(report.feature_id, "033-execution-time-contract-repair")
        self.assertTrue(report.no_dependency_drift)
        self.assertTrue(report.no_training_or_policy_drift)
        self.assertTrue(report.no_reward_timing_change)
        self.assertTrue(report.no_transmission_delay_scope_creep)
        self.assertTrue(report.no_capacity_sharing_scope_creep)
        self.assertIn("src/environment/execution_helper.py", report.repaired_runtime_components)
        self.assertIn("test_local_execution_no_single_slot_shortcut_when_cycles_exceed_capacity", report.tests_added)

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path, md_path = write_execution_time_contract_report(report, Path(tmpdir) / "artifacts/analysis/execution-time-contract-repair")
            payload = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertEqual(payload["feature_id"], "033-execution-time-contract-repair")
            self.assertEqual(payload["final_verdict"], "execution_time_contract_repaired")
            self.assertEqual(payload["destination_kinds_validated"], ["local/private/self", "public/edge/horizontal", "cloud/vertical"])


if __name__ == "__main__":
    unittest.main()
