from __future__ import annotations

import unittest

from src.analysis.full_paper_default_training_campaign_gate import build_full_paper_default_training_campaign_gate_report
from src.analysis.full_paper_default_training_campaign_gate.config import METRIC_COLLECTION_FIELDS
from src.analysis.full_paper_default_training_campaign_gate.model import FullPaperDefaultTrainingCampaignGateReport
from tests.unit.test_full_paper_default_training_campaign_gate_schema import _base_report_kwargs


class FullPaperDefaultTrainingCampaignGateMetricsTests(unittest.TestCase):
    def test_generated_report_has_complete_metric_collection_contract(self) -> None:
        payload = build_full_paper_default_training_campaign_gate_report().to_dict()
        metrics = payload["metric_collection_contract_summary"]
        self.assertEqual(tuple(metrics["required_metric_fields"]), METRIC_COLLECTION_FIELDS)
        self.assertEqual(metrics["missing_metric_fields"], [])
        self.assertTrue(metrics["metric_collection_contract_complete"])

    def test_metric_collection_contract_cannot_omit_required_fields_on_pass_path(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["metric_collection_contract_summary"]["present_metric_fields"].remove("baseline_policy_metrics")
        kwargs["metric_collection_contract_summary"]["missing_metric_fields"] = ["baseline_policy_metrics"]
        kwargs["metric_collection_contract_summary"]["metric_collection_contract_complete"] = False
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignGateReport(**kwargs)

    def test_campaign_scope_and_resource_controls_are_present(self) -> None:
        payload = build_full_paper_default_training_campaign_gate_report().to_dict()
        self.assertTrue(payload["campaign_scope_summary"]["campaign_scale_is_explicit"])
        self.assertTrue(payload["resource_control_summary"]["resource_control_complete"])
        self.assertTrue(payload["resource_control_summary"]["no_uncontrolled_loop"])
        self.assertIn("training_episode_count", payload["resource_control_summary"]["max_episode_or_run_budget"])

    def test_artifact_and_checkpoint_contracts_are_present(self) -> None:
        payload = build_full_paper_default_training_campaign_gate_report().to_dict()
        self.assertTrue(payload["artifact_output_contract_summary"]["artifact_output_contract_complete"])
        self.assertTrue(payload["checkpoint_contract_summary"]["checkpoint_contract_complete"])
        self.assertTrue(payload["checkpoint_contract_summary"]["metadata_required"])
        self.assertTrue(payload["checkpoint_contract_summary"]["trace_bank_ids_required"])


if __name__ == "__main__":
    unittest.main()
