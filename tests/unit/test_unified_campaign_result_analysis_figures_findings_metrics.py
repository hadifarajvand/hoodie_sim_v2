from __future__ import annotations

import json
import unittest

from src.analysis.unified_campaign_result_analysis_figures_findings.runner import build_unified_campaign_analysis_report


class UnifiedCampaignAnalysisMetricsTests(unittest.TestCase):
    def test_feature_060_artifacts_drive_ready_report(self) -> None:
        payload = build_unified_campaign_analysis_report().to_dict()
        self.assertEqual(payload["final_verdict"], "unified_campaign_result_analysis_ready")
        self.assertTrue(payload["feature_060_prerequisite_verification"]["verified"])
        self.assertTrue(payload["integrity_audit_result"]["passed"])
        self.assertTrue(payload["training_metrics_summary"]["action_accounting_reconciled"])
        self.assertTrue(payload["baseline_evaluation_summary"]["baseline_metrics_real_execution"])
        self.assertFalse(payload["comparison_readiness"]["performance_claim"])

    def test_baseline_shell_metrics_are_absent_from_source_summary(self) -> None:
        payload = build_unified_campaign_analysis_report().to_dict()
        self.assertNotIn("metric_shell_only", json.dumps(payload["baseline_evaluation_summary"]))


if __name__ == "__main__":
    unittest.main()
