#!/usr/bin/env python3
"""
Test for post-repair phase 1 readiness diagnostic helper.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.analysis.post_repair_phase1_readiness import ConfigFactory


class TestPostRepairPhase1Readiness(unittest.TestCase):
    """Test the post-repair phase 1 readiness diagnostic helper."""

    def test_config_factory_returns_paper_default(self):
        """Test that ConfigFactory returns a valid paper_default config."""
        config = ConfigFactory.paper_default()
        
        # Check that we got a CampaignConfig instance
        from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
        self.assertIsInstance(config, CampaignConfig)
        
        # Check paper_default specific values
        self.assertEqual(config.state_dim, 74)
        self.assertEqual(config.action_count, 22)
        self.assertEqual(config.learning_rate, 7e-7)
        self.assertEqual(config.gamma, 0.99)
        self.assertEqual(config.batch_size, 64)
        self.assertEqual(config.replay_memory_capacity, 10_000)
        self.assertEqual(config.readiness_probe_episode_count, 3)
        self.assertEqual(config.readiness_probe_episode_length, 50)
        self.assertEqual(config.pilot_episode_length, 50)
        self.assertEqual(config.evaluation_episode_length, 50)
        self.assertEqual(config.full_campaign_episode_length, 110)
        self.assertEqual(config.full_campaign_budget, 5_000)
        self.assertEqual(config.readiness_manual_approval_status, "approved")
        self.assertEqual(config.readiness_manual_approval_reference, "paper-default-smoke-campaign-approved")


if __name__ == "__main__":
    unittest.main()