from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.unified_campaign_result_analysis_figures_findings import run_unified_campaign_analysis
from src.analysis.unified_campaign_result_analysis_figures_findings.config import OUTPUT_DIR, REQUIRED_FIGURES


class UnifiedCampaignAnalysisReportTests(unittest.TestCase):
    def test_report_artifacts_and_figures_exist(self) -> None:
        run_unified_campaign_analysis()
        required = [
            "unified-campaign-result-analysis-report.json",
            "unified-campaign-result-analysis-report.md",
            "integrity-audit.json",
            "comparison-readiness.json",
            "comparative-metrics-table.json",
            "thesis-result-tables.md",
            "final-experimental-findings.md",
            "figure-manifest.json",
        ]
        for name in required:
            self.assertTrue((OUTPUT_DIR / name).exists(), msg=name)
        for figure in REQUIRED_FIGURES:
            self.assertTrue((OUTPUT_DIR / "figures" / figure).exists(), msg=figure)

    def test_report_does_not_claim_paper_reproduction_or_superiority(self) -> None:
        run_unified_campaign_analysis()
        payload = json.loads((OUTPUT_DIR / "unified-campaign-result-analysis-report.json").read_text())
        rendered = json.dumps(payload)
        self.assertIn("comparison readiness only", rendered)
        self.assertFalse(payload["claim_safety_review"]["paper_reproduction_claim_made"])
        self.assertFalse(payload["claim_safety_review"]["performance_superiority_claim_made"])
        self.assertFalse(payload["claim_safety_review"]["baseline_superiority_claim_made"])


if __name__ == "__main__":
    unittest.main()
