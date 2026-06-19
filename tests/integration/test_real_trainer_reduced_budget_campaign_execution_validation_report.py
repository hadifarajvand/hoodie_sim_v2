from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.real_trainer_reduced_budget_campaign_execution_validation import generate_real_trainer_reduced_budget_campaign_execution_validation_artifacts


class RealTrainerReducedBudgetCampaignExecutionValidationReportIntegrationTests(unittest.TestCase):
    def test_report_artifacts_are_generated(self) -> None:
        report, json_path, md_path = generate_real_trainer_reduced_budget_campaign_execution_validation_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], report.feature_id)
        self.assertEqual(payload["final_verdict"], "real_trainer_reduced_budget_campaign_validation_passed")
        self.assertEqual(payload["remaining_blockers"], [])

    def test_markdown_report_mentions_required_sections(self) -> None:
        generate_real_trainer_reduced_budget_campaign_execution_validation_artifacts()
        markdown = Path("artifacts/analysis/real-trainer-reduced-budget-campaign-execution-validation/real-trainer-reduced-budget-campaign-validation-report.md").read_text(encoding="utf-8")
        self.assertIn("Real Trainer Reduced-Budget Campaign Execution Validation Report", markdown)
        self.assertIn("## Reduced Budget Execution Summary", markdown)
        self.assertIn("## Training Metrics Summary", markdown)
        self.assertIn("## Artifact Manifest Summary", markdown)


if __name__ == "__main__":
    unittest.main()
