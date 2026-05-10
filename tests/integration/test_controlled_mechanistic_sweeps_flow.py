from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.controlled_mechanistic_sweeps.runner import ControlledMechanisticSweepRunner


class ControlledMechanisticSweepsFlowTests(unittest.TestCase):
    def test_tiny_sweeps_run_deterministically_and_write_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first_runner = ControlledMechanisticSweepRunner(output_dir=Path(first_dir))
            second_runner = ControlledMechanisticSweepRunner(output_dir=Path(second_dir))

            first_report = first_runner.run()
            second_report = second_runner.run()

            first_json = Path(first_dir) / "controlled-mechanistic-sweeps.json"
            first_md = Path(first_dir) / "controlled-mechanistic-sweeps.md"
            second_json = Path(second_dir) / "controlled-mechanistic-sweeps.json"
            second_md = Path(second_dir) / "controlled-mechanistic-sweeps.md"

            self.assertTrue(first_json.exists())
            self.assertTrue(first_md.exists())
            self.assertTrue(second_json.exists())
            self.assertTrue(second_md.exists())
            self.assertEqual(first_json.read_text(encoding="utf-8"), second_json.read_text(encoding="utf-8"))
            self.assertEqual(first_md.read_text(encoding="utf-8"), second_md.read_text(encoding="utf-8"))
            self.assertEqual(first_report.to_dict(), second_report.to_dict())
            self.assertEqual(first_report.overall_status, "instrumentation_gap")

            checks = {check["sweep_name"]: check for check in first_report.to_dict()["monotonic_checks"]}
            self.assertEqual(checks["arrival_probability"]["status"], "pass")
            self.assertEqual(checks["timeout"]["status"], "pass")
            self.assertEqual(checks["cpu_capacity"]["status"], "pass")
            self.assertEqual(checks["topology_density"]["status"], "pass")
            self.assertEqual(checks["link_rate"]["status"], "instrumentation_gap")

            observations = first_report.to_dict()["observations"]
            arrival_indicators = [
                observation["observed_pressure_indicator"]
                for observation in observations
                if observation["sweep_name"] == "arrival_probability"
            ]
            self.assertEqual(arrival_indicators, sorted(arrival_indicators))

    def test_unsupported_dimensions_remain_instrumentation_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as output_dir:
            report = ControlledMechanisticSweepRunner(output_dir=Path(output_dir)).run()

            link_rate_check = next(item for item in report.to_dict()["monotonic_checks"] if item["sweep_name"] == "link_rate")
            self.assertEqual(link_rate_check["status"], "instrumentation_gap")
            self.assertTrue(report.instrumentation_gaps)
            self.assertTrue(any("link rate" in gap.lower() for gap in report.instrumentation_gaps))


if __name__ == "__main__":
    unittest.main()
