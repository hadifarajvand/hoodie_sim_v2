from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.public_cloud_queue_capacity_sharing import build_public_cloud_queue_capacity_sharing_report, write_public_cloud_queue_capacity_sharing_report


class PublicCloudCapacitySharingReportIntegrationTests(unittest.TestCase):
    def test_report_schema_and_contents(self) -> None:
        report = build_public_cloud_queue_capacity_sharing_report()

        self.assertEqual(report.feature_id, "035-public-cloud-queue-capacity-sharing-contract")
        self.assertEqual(report.sharing_rule, "deterministic_equal_share_at_slot_start")
        self.assertEqual(report.redistribution_policy, "no_same_slot_redistribution")
        self.assertTrue(report.no_paper_recovery_claims)
        self.assertTrue(report.no_dependency_drift)
        self.assertTrue(report.no_training_or_policy_drift)
        self.assertTrue(report.no_reward_timing_change)
        self.assertTrue(report.no_execution_time_contract_drift)
        self.assertTrue(report.no_transmission_delay_contract_drift)
        self.assertTrue(report.no_campaign_rerun)
        self.assertIn("src/environment/gym_adapter.py", report.wired_runtime_components)
        self.assertIn("src/environment/public_queue.py", report.validated_runtime_components)
        self.assertIn("public", report.destination_kinds_validated)
        self.assertIn("cloud", report.destination_kinds_validated)
        self.assertIn("test_single_public_queue_gets_full_edge_capacity", report.tests_added)
        self.assertIn("tests.unit.test_public_cloud_capacity_sharing", report.tests_run)
        self.assertIn("tests.integration.test_public_cloud_capacity_sharing_flow", report.tests_run)

    def test_report_writes_json_and_markdown(self) -> None:
        report = build_public_cloud_queue_capacity_sharing_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path, md_path = write_public_cloud_queue_capacity_sharing_report(report, Path(tmpdir) / "artifacts/analysis/public-cloud-queue-capacity-sharing")
            payload = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertEqual(payload["feature_id"], "035-public-cloud-queue-capacity-sharing-contract")
            self.assertEqual(payload["sharing_rule"], "deterministic_equal_share_at_slot_start")
            self.assertEqual(payload["redistribution_policy"], "no_same_slot_redistribution")
            self.assertTrue(payload["no_paper_recovery_claims"])
            self.assertEqual(payload["final_verdict"], "public_cloud_capacity_sharing_wired")


if __name__ == "__main__":
    unittest.main()
