from __future__ import annotations

import unittest

from src.analysis.full_paper_default_training_campaign_gate import build_full_paper_default_training_campaign_gate_report
from src.analysis.full_paper_default_training_campaign_gate.config import FullPaperDefaultTrainingCampaignGateConfig
from src.analysis.full_paper_default_training_campaign_gate.model import FullPaperDefaultTrainingCampaignGateReport
from tests.unit.test_full_paper_default_training_campaign_gate_schema import _base_report_kwargs


class FullPaperDefaultTrainingCampaignGateBehaviorEquivalenceTests(unittest.TestCase):
    def test_behavior_equivalence_check_names_are_unique(self) -> None:
        payload = build_full_paper_default_training_campaign_gate_report().to_dict()
        names = [entry["name"] for entry in payload["prerequisite_tags_verified"]]
        self.assertEqual(len(names), len(set(names)))

    def test_safety_fields_cover_forbidden_feature_059_behaviors(self) -> None:
        payload = build_full_paper_default_training_campaign_gate_report().to_dict()
        for key in (
            "no_training_execution",
            "no_optimizer_execution",
            "no_replay_mutation",
            "no_checkpoint_binary_written",
            "no_full_campaign_execution",
            "no_paper_reproduction_claim",
            "no_performance_claim",
            "no_baseline_superiority_claim",
            "no_prior_artifact_rewrite",
        ):
            self.assertIn(key, payload["safety_summary"])
            self.assertIsInstance(payload["safety_summary"][key], bool)

    def test_forbidden_execution_flags_are_rejected_by_config(self) -> None:
        for kwargs in (
            {"full_campaign_executed_this_feature": True},
            {"training_executed_this_feature": True},
            {"optimizer_executed_this_feature": True},
            {"replay_mutated_this_feature": True},
            {"checkpoint_binary_written_this_feature": True},
            {"paper_reproduction_claim": True},
            {"performance_claim": True},
            {"baseline_superiority_claim": True},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    FullPaperDefaultTrainingCampaignGateConfig(**kwargs)

    def test_safety_false_cannot_claim_ready(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["safety_summary"]["no_training_execution"] = False
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignGateReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
