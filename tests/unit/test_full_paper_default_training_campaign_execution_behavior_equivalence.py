from __future__ import annotations

import unittest

from src.analysis.full_paper_default_training_campaign_execution import build_full_paper_default_training_campaign_execution_report
from src.analysis.full_paper_default_training_campaign_execution.config import FullPaperDefaultTrainingCampaignExecutionConfig
from src.analysis.full_paper_default_training_campaign_execution.model import FullPaperDefaultTrainingCampaignExecutionReport
from tests.unit.test_full_paper_default_training_campaign_execution_schema import _base_report_kwargs


class FullPaperDefaultTrainingCampaignExecutionBehaviorEquivalenceTests(unittest.TestCase):
    def test_behavior_equivalence_check_names_are_unique(self) -> None:
        payload = build_full_paper_default_training_campaign_execution_report().to_dict()
        names = [entry["name"] for entry in payload["prerequisite_tags_verified"]]
        self.assertEqual(len(names), len(set(names)))

    def test_safety_fields_cover_no_claim_and_no_drift_guards(self) -> None:
        payload = build_full_paper_default_training_campaign_execution_report().to_dict()
        for key in (
            "no_paper_reproduction_claim",
            "no_performance_superiority_claim",
            "no_baseline_superiority_claim",
            "no_uncontrolled_campaign_loop",
            "no_policy_drift",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_reward_timing_change",
            "no_prior_artifact_rewrite",
        ):
            self.assertIn(key, payload["safety_summary"])
            if key in {"no_policy_drift", "no_environment_contract_drift", "no_reward_timing_change"}:
                self.assertFalse(payload["safety_summary"][key])
            else:
                self.assertTrue(payload["safety_summary"][key])

    def test_forbidden_claim_flags_are_rejected_by_config(self) -> None:
        for kwargs in (
            {"paper_reproduction_claim": True},
            {"performance_superiority_claim": True},
            {"baseline_superiority_claim": True},
            {"uncontrolled_campaign_loop": True},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    FullPaperDefaultTrainingCampaignExecutionConfig(**kwargs)

    def test_safety_false_cannot_claim_pass(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["safety_summary"]["no_paper_reproduction_claim"] = False
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
