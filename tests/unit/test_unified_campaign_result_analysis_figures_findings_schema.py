from __future__ import annotations

import unittest

from src.analysis.unified_campaign_result_analysis_figures_findings.model import UnifiedCampaignAnalysisReport


def _ready_payload() -> dict:
    return {
        "feature_id": "062-unified-campaign-result-analysis-figures-findings",
        "feature_060_prerequisite_verification": {"verified": True},
        "integrity_audit_result": {"passed": True},
        "training_metrics_summary": {"action_accounting_reconciled": True},
        "evaluation_metrics_summary": {},
        "baseline_evaluation_summary": {"baseline_metrics_real_execution": True},
        "comparison_readiness": {"comparison_ready": True, "performance_claim": False},
        "result_tables_summary": {"tables_generated": True},
        "figure_manifest": {
            "figures_generated": True,
            "figure_files": [
                "figure_01_training_action_distribution.png",
                "figure_02_training_reward_summary.png",
                "figure_03_baseline_policy_action_distribution.png",
                "figure_04_campaign_budget_integrity.png",
            ],
        },
        "claim_safety_review": {
            "claim_safety_passed": True,
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
        },
        "remaining_blockers": [],
        "recommended_next_step": "External review of unified campaign analysis artifacts",
        "final_verdict": "unified_campaign_result_analysis_ready",
    }


class UnifiedCampaignAnalysisSchemaTests(unittest.TestCase):
    def test_ready_report_round_trip(self) -> None:
        report = UnifiedCampaignAnalysisReport(**_ready_payload())
        self.assertEqual(report.to_dict()["final_verdict"], "unified_campaign_result_analysis_ready")

    def test_blocked_report_cannot_use_ready_verdict_with_blockers(self) -> None:
        payload = _ready_payload()
        payload["remaining_blockers"] = ["feature_060_prerequisite_blocked"]
        with self.assertRaises(ValueError):
            UnifiedCampaignAnalysisReport(**payload)

    def test_ready_report_requires_all_figures(self) -> None:
        payload = _ready_payload()
        payload["figure_manifest"]["figure_files"] = ["figure_01_training_action_distribution.png"]
        with self.assertRaises(ValueError):
            UnifiedCampaignAnalysisReport(**payload)

    def test_claim_safety_rejects_paper_reproduction_claim(self) -> None:
        payload = _ready_payload()
        payload["claim_safety_review"]["paper_reproduction_claim_made"] = True
        with self.assertRaises(ValueError):
            UnifiedCampaignAnalysisReport(**payload)


if __name__ == "__main__":
    unittest.main()
