from __future__ import annotations

import unittest

from src.analysis.hoodie_runtime_evaluation_runner.report import build_feature_083_report, render_feature_083_report


class HoodieRuntimeEvaluationRunnerReportIntegrationTests(unittest.TestCase):
    def test_report_is_structured_and_rendered(self) -> None:
        report = build_feature_083_report()
        rendered = render_feature_083_report(report)

        self.assertEqual(report.status, "hoodie_paper_baseline_fidelity_ready")
        self.assertTrue(report.passed)
        self.assertEqual(report.readiness_level, "fully_implemented")
        self.assertFalse(report.compatibility_mode_used)
        self.assertEqual(len(report.policy_coverage), 7)
        self.assertEqual(len(report.scenario_coverage), 7)
        self.assertEqual(len(report.metric_coverage), 11)
        self.assertEqual(len(report.ranking_tables), 11)
        self.assertIn("HOODIE", rendered)
        self.assertIn("RO", rendered)
        self.assertIn("FLC", rendered)
        self.assertIn("VO", rendered)
        self.assertIn("HO", rendered)
        self.assertIn("BCO", rendered)
        self.assertIn("MQO", rendered)
        self.assertEqual({row.policy for row in report.policy_coverage}, {"HOODIE", "RO", "FLC", "VO", "HO", "BCO", "MQO"})
        self.assertIn("identity proof", rendered.lower())
        self.assertIn("no compatibility-mode policies remain", rendered.lower())
        self.assertIn("task_completion_delay", rendered)
        self.assertIn("task_drop_ratio", rendered)
        self.assertIn("primary paper metrics", rendered.lower())
        self.assertIn("secondary repository metrics", rendered.lower())
        self.assertIn("no dcq", rendered.lower())
        self.assertIn("no thesis method", rendered.lower())
        self.assertIn("no empirical full-paper reproduction", rendered.lower())
        self.assertIn("no statistical superiority", rendered.lower())
        self.assertNotIn("ORIGINAL_HOODIE_BASELINE: implemented", rendered)
        self.assertFalse(report.remaining_gaps)


if __name__ == "__main__":
    unittest.main()
