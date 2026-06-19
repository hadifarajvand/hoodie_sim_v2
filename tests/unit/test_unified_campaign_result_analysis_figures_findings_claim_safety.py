from __future__ import annotations

import unittest

from src.analysis.unified_campaign_result_analysis_figures_findings.runner import build_unified_campaign_analysis_report


class UnifiedCampaignAnalysisClaimSafetyTests(unittest.TestCase):
    def test_claim_safety_does_not_claim_superiority_or_reproduction(self) -> None:
        payload = build_unified_campaign_analysis_report().to_dict()
        safety = payload["claim_safety_review"]
        self.assertFalse(safety["paper_reproduction_claim_made"])
        self.assertFalse(safety["performance_superiority_claim_made"])
        self.assertFalse(safety["baseline_superiority_claim_made"])
        self.assertIn("performance superiority not claimed", safety["allowed_claim"])


if __name__ == "__main__":
    unittest.main()
