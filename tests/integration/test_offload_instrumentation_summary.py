from __future__ import annotations

from pathlib import Path
import unittest

from src.audits.differential_environment import DifferentialEnvironmentAudit
from src.audits.differential_environment.report import build_instrumentation_summary


class OffloadInstrumentationSummaryTest(unittest.TestCase):
    def test_summary_artifacts_are_produced_deterministically(self) -> None:
        report = DifferentialEnvironmentAudit(output_dir=Path("artifacts/analysis/differential-environment-audit")).run()
        summary = build_instrumentation_summary(report)
        out_dir = Path("artifacts/analysis/offload-lifecycle-instrumentation")
        json_path, md_path = summary.write(out_dir)
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json_path.read_text()
        self.assertIn("schema_supported_events", payload)
        self.assertIn("observed_default_audit_events", payload)
        self.assertIn("observed_synthetic_fixture_events", payload)
