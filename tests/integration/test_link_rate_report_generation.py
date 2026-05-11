from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.link_rate_transmission_delay_contract.runner import run_link_rate_transmission_delay_contract
from src.analysis.link_rate_transmission_delay_contract.report import build_link_rate_contract_report, write_link_rate_contract_report


class LinkRateReportGenerationTest(unittest.TestCase):
    def test_report_artifacts_are_generated_with_required_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_path, md_path = write_link_rate_contract_report(build_link_rate_contract_report(), Path(tmp))
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(
                set(payload.keys()),
                {
                    "schema_version",
                    "feature_id",
                    "source_gates",
                    "paper_backed_defaults",
                    "link_rate_controls",
                    "transmission_delay_contract",
                    "unit_conversions",
                    "monotonicity_checks",
                    "unsupported_controls",
                    "remaining_blockers",
                    "topology_boundaries",
                    "no_curve_fitting",
                    "no_topology_fabrication",
                    "no_policy_or_metric_redesign",
                    "no_training_or_dependency_drift",
                    "generated_artifacts",
                    "validation_summary",
                },
            )
            self.assertTrue(md_path.exists())
            self.assertIn("horizontal_data_rate_mbps", md_path.read_text(encoding="utf-8"))

    def test_runner_writes_report_to_default_artifacts_directory(self) -> None:
        outputs = run_link_rate_transmission_delay_contract()
        self.assertIn("json", outputs)
        self.assertIn("markdown", outputs)
        self.assertTrue(outputs["json"].exists())
        self.assertTrue(outputs["markdown"].exists())


if __name__ == "__main__":
    unittest.main()
