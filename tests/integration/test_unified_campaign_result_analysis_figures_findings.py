from __future__ import annotations

import unittest

from src.analysis.unified_campaign_result_analysis_figures_findings import run_unified_campaign_analysis


class UnifiedCampaignAnalysisIntegrationTests(unittest.TestCase):
    def test_runner_generates_ready_report(self) -> None:
        report = run_unified_campaign_analysis().to_dict()
        self.assertEqual(report["final_verdict"], "unified_campaign_result_analysis_ready")
        self.assertEqual(report["remaining_blockers"], [])
        self.assertTrue(report["comparison_readiness"]["comparison_ready"])
        self.assertTrue(report["figure_manifest"]["figures_generated"])


if __name__ == "__main__":
    unittest.main()
