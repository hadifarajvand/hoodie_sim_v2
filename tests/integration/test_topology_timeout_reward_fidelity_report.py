from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.analysis.topology_timeout_reward_fidelity.report import build_feature_070_report, render_feature_070_report, write_feature_070_report


class TopologyTimeoutRewardFidelityReportIntegrationTests(unittest.TestCase):
    def test_report_writes_markdown_and_json_to_requested_directory(self) -> None:
        report = build_feature_070_report(
            changed_files=(
                "specs/070-topology-timeout-reward-fidelity/tasks.md",
                "src/analysis/topology_timeout_reward_fidelity/report.py",
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            json_path, md_path = write_feature_070_report(report, Path(tmp))
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report.to_dict())
            markdown = md_path.read_text(encoding="utf-8")
            self.assertIn("Feature 070 Fidelity Report", markdown)
            self.assertIn("## Topology Evidence", markdown)
            self.assertIn("## Timeout/Drop Rule Evidence", markdown)
            self.assertIn("## Timeout/Drop Accounting Evidence", markdown)
            self.assertIn("## Reward Equation Evidence", markdown)

    def test_rendered_report_mentions_regression_status_and_scope_boundary(self) -> None:
        report = build_feature_070_report()
        self.assertTrue(report.passed)
        self.assertEqual(report.status, "blocker_resolution_readiness_with_runtime_divergence")
        markdown = render_feature_070_report(report)
        self.assertIn("Feature 068R", markdown)
        self.assertIn("Feature 069", markdown)
        self.assertIn("No full paper reproduction claim", markdown)
        self.assertIn("runtime_compatibility_divergence", markdown)
        self.assertIn("Recommended Next Feature", markdown)


if __name__ == "__main__":
    unittest.main()
