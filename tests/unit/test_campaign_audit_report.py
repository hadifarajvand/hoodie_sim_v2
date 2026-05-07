from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.campaign_audit import CampaignAudit


class CampaignAuditReportTests(unittest.TestCase):
    def _audit(self, campaign_dir: Path) -> CampaignAudit:
        return CampaignAudit(campaign_dir)

    def test_inventory_output_and_stable_ordering(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign_dir = Path(tmpdir) / "campaign"
            matrix_dir = campaign_dir / "matrix"
            bundle_dir = campaign_dir / "bundle"
            trace_dir = matrix_dir / "traces"
            trace_dir.mkdir(parents=True, exist_ok=True)
            bundle_dir.mkdir(parents=True, exist_ok=True)
            (matrix_dir / "matrix-summary.csv").write_text("policy_name,scenario_name,seed,trace_id\n", encoding="utf-8")
            (campaign_dir / "campaign-summary.json").write_text("{\"result_count\": 0, \"total_tasks\": 0}", encoding="utf-8")
            (campaign_dir / "determinism-check.json").write_text("{\"passed\": true}", encoding="utf-8")
            (bundle_dir / "manifest.json").write_text("{}", encoding="utf-8")
            (bundle_dir / "validation-summary.json").write_text("{}", encoding="utf-8")
            (matrix_dir / "b.json").write_text("{}", encoding="utf-8")
            (matrix_dir / "a.json").write_text("{}", encoding="utf-8")

            report = self._audit(campaign_dir).run()

            self.assertEqual(report.artifact_inventory.found_files, sorted(report.artifact_inventory.found_files))
            self.assertIn("matrix/matrix-summary.csv", report.artifact_inventory.found_files)
            self.assertIn("bundle/manifest.json", report.artifact_inventory.found_files)

    def test_anomaly_categorization_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign_dir = Path(tmpdir) / "campaign"
            matrix_dir = campaign_dir / "matrix"
            bundle_dir = campaign_dir / "bundle"
            matrix_dir.mkdir(parents=True, exist_ok=True)
            bundle_dir.mkdir(parents=True, exist_ok=True)

            campaign_dir.joinpath("campaign-summary.json").write_text(
                "{\"result_count\": 2, \"mean_drop_ratio\": 0.808, \"total_tasks\": 10}",
                encoding="utf-8",
            )
            campaign_dir.joinpath("policy-summary.json").write_text(
                "[{\"policy_name\": \"FLC\", \"mean_average_delay\": 5.0, \"total_tasks\": 5}, {\"policy_name\": \"VO\", \"mean_average_delay\": 5.0, \"total_tasks\": 5}]",
                encoding="utf-8",
            )
            campaign_dir.joinpath("scenario-summary.json").write_text(
                "[{\"scenario_name\": \"paper_default\", \"mean_average_delay\": 5.0, \"total_tasks\": 5}, {\"scenario_name\": \"moderate\", \"mean_average_delay\": 5.0, \"total_tasks\": 5}]",
                encoding="utf-8",
            )
            campaign_dir.joinpath("determinism-check.json").write_text("{\"passed\": true}", encoding="utf-8")
            matrix_dir.joinpath("matrix-summary.csv").write_text("policy_name,scenario_name,seed,trace_id,total_tasks\nFLC,paper_default,1,t1,5\nVO,moderate,1,t2,5\n", encoding="utf-8")
            matrix_dir.joinpath("FLC-paper_default-1.json").write_text(
                "{\"final_metrics\": {\"total_tasks\": 5}}",
                encoding="utf-8",
            )
            matrix_dir.joinpath("VO-moderate-1.json").write_text(
                "{\"final_metrics\": {\"total_tasks\": 5}}",
                encoding="utf-8",
            )

            report = self._audit(campaign_dir).run()

            categories = [finding.category for finding in report.findings]
            self.assertIn("high_drop_ratio", categories)
            self.assertIn("weak_policy_differentiation", categories)
            self.assertIn("weak_scenario_differentiation", categories)
            self.assertTrue(report.passed)

    def test_rendered_text_contains_machine_and_human_readable_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign_dir = Path(tmpdir) / "campaign"
            matrix_dir = campaign_dir / "matrix"
            bundle_dir = campaign_dir / "bundle"
            matrix_dir.mkdir(parents=True, exist_ok=True)
            bundle_dir.mkdir(parents=True, exist_ok=True)
            campaign_dir.joinpath("campaign-summary.json").write_text(
                "{\"result_count\": 1, \"mean_drop_ratio\": 0.0, \"total_tasks\": 5}",
                encoding="utf-8",
            )
            campaign_dir.joinpath("policy-summary.json").write_text(
                "[{\"policy_name\": \"FLC\", \"mean_average_delay\": 5.0, \"total_tasks\": 5}]",
                encoding="utf-8",
            )
            campaign_dir.joinpath("scenario-summary.json").write_text(
                "[{\"scenario_name\": \"paper_default\", \"mean_average_delay\": 5.0, \"total_tasks\": 5}]",
                encoding="utf-8",
            )
            campaign_dir.joinpath("determinism-check.json").write_text("{\"passed\": true}", encoding="utf-8")
            matrix_dir.joinpath("matrix-summary.csv").write_text("policy_name,scenario_name,seed,trace_id,total_tasks\nFLC,paper_default,1,t1,5\n", encoding="utf-8")
            matrix_dir.joinpath("FLC-paper_default-1.json").write_text(
                "{\"final_metrics\": {\"total_tasks\": 5}}",
                encoding="utf-8",
            )

            audit = self._audit(campaign_dir)
            report = audit.run()
            text = audit.render_text(report)

            self.assertIn("# Campaign Result Sanity Audit", text)
            self.assertIn("## Accounting Consistency", text)
            self.assertIn("Passed: true", text)


if __name__ == "__main__":
    unittest.main()
