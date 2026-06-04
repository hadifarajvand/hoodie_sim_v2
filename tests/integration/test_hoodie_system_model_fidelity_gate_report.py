from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.hoodie_system_model_fidelity_gate.config import READY_STATUS
from src.analysis.hoodie_system_model_fidelity_gate.runner import generate_feature_086_artifacts, validate_feature_086_artifacts


class HoodieSystemModelFidelityGateReportIntegrationTests(unittest.TestCase):
    def test_report_and_artifacts_render_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "feature_086_system_model_fidelity"
            payload, paths = generate_feature_086_artifacts(output_dir)
            self.assertEqual(payload["verdict"], READY_STATUS)
            validated = validate_feature_086_artifacts(output_dir)
            self.assertTrue(validated["validated"])

            report_json = json.loads(paths["feature_086_system_model_fidelity_report.json"].read_text(encoding="utf-8"))
            self.assertEqual(report_json["verdict"], READY_STATUS)
            self.assertEqual(report_json["active_policies"], ["HOODIE", "RO", "FLC", "VO", "HO", "BCO", "MLEO"])
            self.assertIn("system_model_fidelity_ready_for_output_comparison", report_json["verdict"])

            report_md = paths["feature_086_system_model_fidelity_report.md"].read_text(encoding="utf-8")
            for needle in (
                "Active Policies",
                "Invalid-Label Check",
                "Mechanism Coverage Summary",
                "Metric Readiness Summary",
                "HOODIE / MLEO Tie Evidence",
                "Remaining Approximations",
                "Claim Boundary",
            ):
                self.assertIn(needle, report_md)


if __name__ == "__main__":
    unittest.main()

