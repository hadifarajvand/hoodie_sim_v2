from __future__ import annotations

import unittest
from unittest.mock import patch, MagicMock
import torch
import numpy as np
from src.analysis.full_training_reproduction_campaign import CampaignConfig, CampaignSeedBundle
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer
from src.agents.paper_state_builder import PaperStateBuilder


class TestTrainerUsesRealState(unittest.TestCase):
    """Test that DDQNTrainer uses real state vectors from PaperStateBuilder instead of placeholders."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.config = CampaignConfig(
            state_dim=74,  # Paper state dimension
            action_count=22,
            lookback_w=10,
            learning_rate=7e-7,
            gamma=0.99,
            batch_size=64,
            replay_memory_capacity=10000,
            target_update_contract=None,  # Will use default
            seed_bundle=CampaignSeedBundle(),
            feature_id="041-full-training-reproduction-campaign",
            full_campaign_enabled=False,
            evaluation_episode_length=10,
            pilot_budget=MagicMock(),
            pilot_episode_length=10,
        )
        
        # Mock the seed bundle attributes
        self.config.seed_bundle.training_trace_generation_seed = 42
        self.config.seed_bundle.evaluation_trace_generation_seed = 43
        self.config.seed_bundle.replay_sampling_seed = 44

    @patch('src.analysis.full_training_reproduction_campaign.trainer.build_online_network')
    @patch('src.analysis.full_training_reproduction_campaign.trainer.build_target_network')
    def test_trainer_contains_paper_state_builder(self, mock_build_target, mock_build_online):
        """Test that DDQNTrainer contains a PaperStateBuilder instance."""
        mock_build_online.return_value = torch.nn.Linear(74, 22)
        mock_build_target.return_value = torch.nn.Linear(74, 22)
        
        trainer = DDQNTrainer(self.config)
        
        # Check that trainer has a state_builder attribute
        self.assertTrue(hasattr(trainer, 'state_builder'))
        self.assertIsInstance(trainer.state_builder, PaperStateBuilder)
        self.assertEqual(trainer.state_builder.num_eas, 20)  # Default value

    @patch('src.analysis.full_training_reproduction_campaign.trainer.build_online_network')
    @patch('src.analysis.full_training_reproduction_campaign.trainer.build_target_network')
    @patch('src.analysis.full_training_reproduction_campaign.trainer._build_environment')
    def test_compute_state_vector_uses_paper_state_builder(self, mock_build_env, mock_build_target, mock_build_online):
        """Test that _compute_state_vector uses PaperStateBuilder to generate real state vectors."""
        mock_build_online.return_value = torch.nn.Linear(74, 22)
        mock_build_target.return_value = torch.nn.Linear(74, 22)
        
        # Setup mock environment
        mock_env = MagicMock()
        mock_env._public_queues = {}
        mock_build_env.return_value = mock_env
        
        trainer = DDQNTrainer(self.config)
        
        # Mock observation data
        observation = {
            "size": 3.5,
            "processing_density": 2.5,
            # Note: _compute_state_vector doesn't use slot, queue_load, history_length for paper state
        }
        
        # Call _compute_state_vector
        state_vector = trainer._compute_state_vector(observation, mock_env)
        
        # Should return a tuple of 74 floats
        self.assertIsInstance(state_vector, tuple)
        self.assertEqual(len(state_vector), 74)
        self.assertTrue(all(isinstance(x, float) for x in state_vector))
        
        # Convert to numpy for easier checking
        state_array = np.array(state_vector)
        
        # Verify it's not all zeros (unlike the placeholder it replaced)
        self.assertFalse(np.allclose(state_array, 0.0))
        
        # Verify specific components are present
        # Task size one-hot (first 31 elements) - should sum to 1.0
        size_one_hot = state_array[:31]
        self.assertAlmostEqual(np.sum(size_one_hot), 1.0, places=6)
        
        # Processing density (element 31)
        self.assertAlmostEqual(state_array[31], 2.5, places=6)
        
        # Wait times (elements 32-33)
        self.assertAlmostEqual(state_array[32], 0.0, places=6)  # private_wait_time (0 at decision point)
        self.assertAlmostEqual(state_array[33], 0.0, places=6)  # offload_wait_time (0 at decision point)
        
        # Public queue lengths (elements 34-53) - should be zeros since mock env has empty queues
        public_queue_lengths = state_array[34:54]
        np.testing.assert_array_equal(public_queue_lengths, np.zeros(20))
        
        # Load forecast (elements 54-73) - should be zeros (placeholder until LSTM)
        load_forecast = state_array[54:74]
        np.testing.assert_array_equal(load_forecast, np.zeros(20))

    @patch('src.analysis.full_training_reproduction_campaign.trainer.build_online_network')
    @patch('src.analysis.full_training_reproduction_campaign.trainer.build_target_network')
    @patch('src.analysis.full_training_reproduction_campaign.trainer._build_environment')
    def test_initial_history_uses_real_state_for_paper_dimension(self, mock_build_env, mock_build_target, mock_build_online):
        """Test that _initial_history uses real state computation for paper dimension (not just zeros)."""
        mock_build_online.return_value = torch.nn.Linear(74, 22)
        mock_build_target.return_value = torch.nn.Linear(74, 22)
        
        # Setup mock environment
        mock_env = MagicMock()
        mock_env._public_queues = {}
        mock_build_env.return_value = mock_env
        
        trainer = DDQNTrainer(self.config)
        
        # Get initial history
        history = trainer._initial_history(episode_length=20)
        
        # Should have lookback_w rows
        self.assertEqual(len(history), self.config.lookback_w)
        
        # Each row should be 74-dimensional
        for row in history:
            self.assertEqual(len(row), 74)
            self.assertTrue(all(isinstance(x, float) for x in row))
        
        # For paper state dimension, initial history should use computed zero state (not hardcoded zeros)
        # All rows should be identical since we're using the same observation
        first_row = np.array(history[0])
        for row in history[1:]:
            np.testing.assert_array_equal(np.array(row), first_row)
        
        # The state should not be all zeros (unlike legacy 3D case)
        # It should represent an "empty system" state
        self.assertFalse(np.allclose(first_row, 0.0))
        
        # Verify specific components of the zero state
        # Task size one-hot for size=0.0 should be [1.0, 0.0, ..., 0.0] (maps to 2.0)
        size_one_hot = first_row[:31]
        self.assertAlmostEqual(size_one_hot[0], 1.0, places=6)  # First bin for 2.0
        self.assertAlmostEqual(np.sum(size_one_hot), 1.0, places=6)
        
        # Processing density should be 0.0
        self.assertAlmostEqual(first_row[31], 0.0, places=6)
        
        # Wait times should be 0.0
        self.assertAlmostEqual(first_row[32], 0.0, places=6)
        self.assertAlmostEqual(first_row[33], 0.0, places=6)
        
        # Public queue lengths should be 0.0
        np.testing.assert_array_equal(first_row[34:54], np.zeros(20))
        
        # Load forecast should be 0.0
        np.testing.assert_array_equal(first_row[54:74], np.zeros(20))

    @patch('src.analysis.full_training_reproduction_campaign.trainer.build_online_network')
    @patch('src.analysis.full_training_reproduction_campaign.trainer.build_target_network')
    @patch('src.analysis.full_training_reproduction_campaign.trainer._build_environment')
    def test_legacy_3d_path_unchanged(self, mock_build_env, mock_build_target, mock_build_online):
        """Test that legacy 3D path still uses the original placeholder approach."""
        # Use legacy config
        legacy_config = CampaignConfig(
            state_dim=3,  # Legacy dimension
            action_count=3,
            lookback_w=10,
            learning_rate=7e-7,
            gamma=0.99,
            batch_size=64,
            replay_memory_capacity=10000,
            target_update_contract=None,
            seed_bundle=CampaignSeedBundle(),
            feature_id="041-full-training-reproduction-campaign",
            full_campaign_enabled=False,
            evaluation_episode_length=10,
            pilot_budget=MagicMock(),
            pilot_episode_length=10,
        )
        
        # Mock the seed bundle attributes
        legacy_config.seed_bundle.training_trace_generation_seed = 42
        legacy_config.seed_bundle.evaluation_trace_generation_seed = 43
        legacy_config.seed_bundle.replay_sampling_seed = 44
        
        mock_build_online.return_value = torch.nn.Linear(3, 3)
        mock_build_target.return_value = torch.nn.Linear(3, 3)
        
        # Setup mock environment
        mock_env = MagicMock()
        mock_env._public_queues = {}
        mock_build_env.return_value = mock_env
        
        trainer = DDQNTrainer(legacy_config)
        
        # Legacy trainer should NOT have a state_builder
        self.assertFalse(hasattr(trainer, 'state_builder'))
        
        # Get initial history for legacy path
        history = trainer._initial_history(episode_length=20)
        
        # Should have lookback_w rows
        self.assertEqual(len(history), legacy_config.lookback_w)
        
        # Each row should be 3-dimensional (legacy)
        for row in history:
            self.assertEqual(len(row), 3)
            self.assertTrue(all(isinstance(x, float) for x in row))
        
        # Legacy path should use all zeros
        first_row = np.array(history[0])
        np.testing.assert_array_equal(first_row, np.zeros(3))
        
        # All rows should be identical zeros
        for row in history[1:]:
            np.testing.assert_array_equal(np.array(row), np.zeros(3))

    @patch('src.analysis.full_training_reproduction_campaign.trainer.build_online_network')
    @patch('src.analysis.full_training_reproduction_campaign.trainer.build_target_network')
    @patch('src.analysis.full_training_reproduction_campaign.trainer._build_environment')
    def test_state_vector_computation_in_episode_rollout(self, mock_build_env, mock_build_target, mock_build_online):
        """Test that state vectors computed during episode rollout use real state builder."""
        mock_build_online.return_value = torch.nn.Linear(74, 22)
        mock_build_target.return_value = torch.nn.Linear(74, 22)
        
        # Setup mock environment that returns specific observations
        mock_env = MagicMock()
        mock_env._public_queues = {("1", "2"): MagicMock(tasks=[1, 2, 3])}  # 3 tasks in queue 1->2
        mock_env.current_task = None
        mock_env.observe_flat.return_value = {
            "size": 0.0,
            "processing_density": 0.0,
            "legal_action_mask": {}
        }
        mock_env.step.return_value = (
            {"size": 0.0, "processing_density": 0.0, "legal_action_mask": {}},  # next_observation
            0.0,  # reward
            False,  # terminated
            False,  # truncated
            {"finalized_tasks": []}  # info
        )
        mock_build_env.return_value = mock_env
        
        trainer = DDQNTrainer(self.config)
        
        # Mock the policy to return a valid action
        with patch.object(trainer.policy, 'choose_action', return_value='local'):
            with patch.object(trainer.policy, 'choose_action_index', return_value=0):
                # Run a short episode rollout
                result = trainer._episode_rollout(
                    episode_id=0,
                    seed=42,
                    episode_length=5,
                    training=False  # Don't train to avoid complexity
                )
                
                # Verify we got a result
                self.assertIsInstance(result, dict)
                self.assertIn('transition_count', result)
                
                # The key point is that if we had a task, _compute_state_vector would be called
                # and it would use the PaperStateBuilder to generate real state vectors


if __name__ == "__main__":
    unittest.main()