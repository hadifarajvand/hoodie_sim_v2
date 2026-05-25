from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.full_paper_default_training_campaign_execution import build_full_paper_default_training_campaign_execution_report
from src.analysis.full_paper_default_training_campaign_execution.config import FullPaperDefaultTrainingCampaignExecutionConfig


class FullPaperDefaultTrainingCampaignExecutionIntegrationTests(unittest.TestCase):
    def test_generated_report_reaches_passed_verdict(self) -> None:
        payload = build_full_paper_default_training_campaign_execution_report().to_dict()
        self.assertTrue(payload["feature_059_gate_verified"])
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_execution_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit")

    def test_feature_059_gate_blocks_bad_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_report = Path(tmp) / "bad-059.json"
            bad_report.write_text(
                json.dumps(
                    {
                        "feature_id": "059-full-paper-default-training-campaign-gate",
                        "feature_058_harness_verified": True,
                        "final_verdict": "resource_control_blocked",
                        "remaining_blockers": ["resource_control_blocked"],
                        "campaign_scope_summary": {
                            "full_campaign_allowed_next_feature": True,
                            "full_campaign_executed_this_feature": False,
                        },
                        "resource_control_summary": {"resource_control_complete": False},
                        "checkpoint_contract_summary": {"checkpoint_contract_complete": True},
                        "metric_collection_contract_summary": {"metric_collection_contract_complete": True},
                        "training_execution_gate_summary": {"training_execution_allowed_next_feature": True},
                    }
                ),
                encoding="utf-8",
            )
            config = FullPaperDefaultTrainingCampaignExecutionConfig(feature_059_report_path=bad_report)
            payload = build_full_paper_default_training_campaign_execution_report(config).to_dict()
        self.assertFalse(payload["feature_059_gate_verified"])
        self.assertEqual(payload["final_verdict"], "feature_059_prerequisite_blocked")
        self.assertIn("feature_059_report_valid", payload["remaining_blockers"])
        self.assertNotEqual(payload["recommended_next_feature"], "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit")

    def test_required_artifacts_are_written(self) -> None:
        payload = build_full_paper_default_training_campaign_execution_report().to_dict()
        manifest = payload["artifact_manifest_summary"]
        self.assertTrue(manifest["all_required_artifacts_exist"])
        for exists in manifest["artifact_exists"].values():
            self.assertTrue(exists)

    def test_checkpoint_metadata_is_complete(self) -> None:
        payload = build_full_paper_default_training_campaign_execution_report().to_dict()
        checkpoint = payload["checkpoint_metadata_summary"]
        self.assertTrue(checkpoint["metadata_artifact_exists"])
        self.assertEqual(checkpoint["target_update_metadata"]["target_update_unit"], "optimizer_step")
        self.assertGreater(checkpoint["replay_metadata"]["replay_size"], 0)
        self.assertIn("training", checkpoint["trace_bank_ids"])
        self.assertIn("evaluation", checkpoint["trace_bank_ids"])


if __name__ == "__main__":
    unittest.main()
