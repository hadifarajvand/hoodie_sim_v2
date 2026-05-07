from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.campaign_audit import CampaignAudit


class CampaignResultSanityAuditIntegrationTests(unittest.TestCase):
    def _campaign_dir(self) -> Path:
        return Path("artifacts/campaigns/baseline-sanity")

    def test_complete_audit_against_existing_campaign_artifacts(self) -> None:
        audit = CampaignAudit(self._campaign_dir())
        report = audit.run()

        self.assertEqual(report.accounting_consistency.expected_runs, 28)
        self.assertEqual(report.accounting_consistency.discovered_runs, 28)
        self.assertTrue(report.accounting_consistency.passed)
        self.assertTrue(report.passed)
        self.assertGreater(len(report.artifact_inventory.found_files), 0)

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = audit.write_outputs(Path(tmpdir), report)
            payload = json.loads(outputs["audit-report.json"].read_text(encoding="utf-8"))
            self.assertTrue(payload["passed"])
            self.assertIn("artifact_inventory", payload)

    def test_missing_finalization_or_reconciliation_mismatches_are_surface_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign_dir = Path(tmpdir) / "campaign"
            matrix_dir = campaign_dir / "matrix"
            bundle_dir = campaign_dir / "bundle"
            matrix_dir.mkdir(parents=True, exist_ok=True)
            bundle_dir.mkdir(parents=True, exist_ok=True)
            campaign_dir.joinpath("campaign-summary.json").write_text(
                "{\"result_count\": 1, \"mean_drop_ratio\": 0.0, \"total_tasks\": 4}",
                encoding="utf-8",
            )
            campaign_dir.joinpath("policy-summary.json").write_text(
                "[{\"policy_name\": \"FLC\", \"mean_average_delay\": 5.0, \"total_tasks\": 4}]",
                encoding="utf-8",
            )
            campaign_dir.joinpath("scenario-summary.json").write_text(
                "[{\"scenario_name\": \"paper_default\", \"mean_average_delay\": 5.0, \"total_tasks\": 4}]",
                encoding="utf-8",
            )
            campaign_dir.joinpath("determinism-check.json").write_text("{\"passed\": true}", encoding="utf-8")
            matrix_dir.joinpath("matrix-summary.csv").write_text(
                "policy_name,scenario_name,seed,trace_id,total_tasks\nFLC,paper_default,1,t1,5\n",
                encoding="utf-8",
            )
            matrix_dir.joinpath("FLC-paper_default-1.json").write_text(
                "{\"final_metrics\": {\"total_tasks\": 5}}",
                encoding="utf-8",
            )

            report = CampaignAudit(campaign_dir).run()

            self.assertFalse(report.accounting_consistency.passed)
            self.assertTrue(report.accounting_consistency.missing_finalization_detected)
            self.assertTrue(any(finding.category == "accounting_inconsistency" for finding in report.findings))


if __name__ == "__main__":
    unittest.main()

