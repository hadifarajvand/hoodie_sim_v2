from __future__ import annotations

import unittest

from src.analysis.hoodie_runtime_evaluation_runner.report import build_feature_082_report, render_feature_082_report


class HoodieRuntimeEvaluationRunnerReportIntegrationTests(unittest.TestCase):
    def test_report_is_structured_and_rendered(self) -> None:
        report = build_feature_082_report()
        rendered = render_feature_082_report(report)

        self.assertEqual(report.status, "hoodie_runtime_evaluation_ready")
        self.assertTrue(report.passed)
        self.assertEqual(report.readiness_level, "fully_implemented")
        self.assertFalse(report.compatibility_mode_used)
        self.assertEqual(len(report.policy_coverage), 5)
        self.assertEqual(len(report.scenario_coverage), 7)
        self.assertEqual(len(report.metric_coverage), 10)
        self.assertEqual(len(report.ranking_tables), 10)
        self.assertIn("HOODIE_PROPOSED", rendered)
        self.assertIn("ORIGINAL_HOODIE_BASELINE", rendered)
        self.assertIn("identity proof", rendered.lower())
        self.assertIn("no compatibility-mode policies remain", rendered.lower())
        self.assertIn("HOODIE_PROPOSED differs from LOCAL_ONLY", rendered)
        self.assertIn("ORIGINAL_HOODIE_BASELINE differs from CLOUD_ONLY", rendered)
        self.assertIn("metric-by-metric", rendered.lower())
        self.assertIn("no dcq", rendered.lower())
        self.assertIn("no thesis method", rendered.lower())
        self.assertIn("no empirical full-paper reproduction", rendered.lower())
        self.assertIn("no statistical superiority", rendered.lower())
        self.assertFalse(report.remaining_gaps)


if __name__ == "__main__":
    unittest.main()
