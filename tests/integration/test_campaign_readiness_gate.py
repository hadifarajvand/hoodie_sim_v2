from __future__ import annotations

import unittest

from src.analysis.full_training_reproduction_campaign import CampaignConfig, run_campaign_readiness_probe


class CampaignReadinessGateIntegrationTests(unittest.TestCase):
    def test_readiness_probe_report_has_exact_counter_schema(self) -> None:
        config = CampaignConfig(readiness_manual_approval_status="not_approved", readiness_probe_episode_count=1, readiness_probe_episode_length=5)
        report = run_campaign_readiness_probe(config)
        payload = report.to_dict()
        expected_keys = {
            "probe_episode_count",
            "probe_step_count",
            "generated_task_count",
            "transition_count",
            "completed_task_count",
            "dropped_task_count",
            "pending_at_horizon_count",
            "terminal_transition_count",
            "reward_bearing_transition_count",
            "non_terminal_transition_count",
            "terminal_transition_ratio",
            "reward_bearing_transition_ratio",
            "pending_at_horizon_ratio",
            "illegal_action_count",
            "illegal_action_ratio",
            "action_count_by_type",
            "local_action_count",
            "horizontal_action_count",
            "vertical_action_count",
            "readiness_manual_approval_required",
            "readiness_manual_approval_status",
            "readiness_block_reason",
        }
        self.assertEqual(set(payload), expected_keys)
        self.assertEqual(payload["readiness_manual_approval_status"], "not_approved")
        self.assertTrue(payload["readiness_manual_approval_required"])

    def test_readiness_probe_blocks_when_manual_approval_missing(self) -> None:
        config = CampaignConfig(readiness_manual_approval_status="not_approved", readiness_probe_episode_count=1, readiness_probe_episode_length=5)
        report = run_campaign_readiness_probe(config)
        self.assertEqual(report.gate_status, "blocked")
        self.assertTrue(report.readiness_manual_approval_required)
        self.assertEqual(report.readiness_manual_approval_status, "not_approved")
        self.assertIsNotNone(report.readiness_block_reason)

    def test_readiness_probe_rejects_approved_status_without_explicit_marker(self) -> None:
        with self.assertRaises(ValueError):
            CampaignConfig(readiness_manual_approval_status="approved", readiness_probe_episode_count=1, readiness_probe_episode_length=5)


if __name__ == "__main__":
    unittest.main()
