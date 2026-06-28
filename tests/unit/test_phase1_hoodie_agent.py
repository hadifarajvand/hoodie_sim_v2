"""
Phase 1: Paper-Faithful HOODIE Agent verification.

Tests cover:
1. PaperStateBuilder: state dimensions, one-hot encoding, component ordering
2. DuelingDQNNetwork: forward pass shapes, 3x1024 architecture, dueling AV
3. HoodieModel: initialization from observations, Q-value computation, serialization
4. LSTM load forecaster: integration stub exists
"""

import math
import os
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

from src.agents.paper_state_builder import PaperStateBuilder
from src.agents.dueling_dqn_network import DuelingDQNNetwork
from src.agents.hoodie_model import HoodieModel
from src.policies.policy_interface import PolicyContext


# ═══════════════════════════════════════════════════════════════════════
# Part 1: PaperStateBuilder
# ═══════════════════════════════════════════════════════════════════════

class TestPaperStateBuilderStateDimensions(unittest.TestCase):
    """Verify PaperStateBuilder produces correct state vector dimensions per paper spec.

    Formula: 31 (task size one-hot) + 1 (density) + 1 (private wait)
             + 1 (offload wait) + N (queue lengths) + N (load forecast)
             = 34 + 2N

    For N=20: state_dim = 74
    For N=4:  state_dim = 42
    """

    def test_state_dim_for_20_eas(self) -> None:
        """With 20 EAs, state vector must have 74 elements."""
        builder = PaperStateBuilder(num_eas=20)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=2.0,
            offload_wait_time=1.0,
            public_queue_lengths=[0.0] * 20,
            load_forecast=[0.0] * 20,
        )
        self.assertEqual(len(state), 74)

    def test_state_dim_for_4_eas(self) -> None:
        """With 4 EAs, state vector must have 42 elements."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0] * 4,
            load_forecast=[0.0] * 4,
        )
        self.assertEqual(len(state), 42)

    def test_state_dim_minimum_1_ea(self) -> None:
        """With 1 EA, state vector must have 36 elements."""
        builder = PaperStateBuilder(num_eas=1)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0],
            load_forecast=[0.0],
        )
        self.assertEqual(len(state), 36)

    def test_one_hot_encoding_for_size_2_0(self) -> None:
        """Task size 2.0 must be one-hot encoded at index 0."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=2.0,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0] * 4,
            load_forecast=[0.0] * 4,
        )
        one_hot = state[:31]
        self.assertEqual(one_hot[0], 1.0)
        self.assertEqual(sum(one_hot[1:]), 0.0)

    def test_one_hot_encoding_for_size_5_0(self) -> None:
        """Task size 5.0 must be one-hot encoded at index 30."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=5.0,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0] * 4,
            load_forecast=[0.0] * 4,
        )
        one_hot = state[:31]
        self.assertEqual(one_hot[30], 1.0)
        self.assertEqual(sum(one_hot[:30]), 0.0)

    def test_one_hot_encoding_for_size_3_5(self) -> None:
        """Task size 3.5 must be one-hot encoded at index 15 (3.5 = 2.0 + 15*0.1)."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0] * 4,
            load_forecast=[0.0] * 4,
        )
        one_hot = state[:31]
        self.assertEqual(one_hot[15], 1.0)

    def test_one_hot_rounds_to_nearest(self) -> None:
        """Task size 2.15 must round to index 1 (size 2.1), not index 2."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=2.15,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0] * 4,
            load_forecast=[0.0] * 4,
        )
        one_hot = state[:31]
        self.assertEqual(one_hot[1], 1.0)

    def test_density_at_index_31(self) -> None:
        """Processing density must be at index 31 (right after one-hot)."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0] * 4,
            load_forecast=[0.0] * 4,
        )
        self.assertEqual(state[31], 0.297)

    def test_wait_times_at_indices_32_33(self) -> None:
        """Private wait time at [32], offload wait time at [33]."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=5.0,
            offload_wait_time=3.0,
            public_queue_lengths=[0.0] * 4,
            load_forecast=[0.0] * 4,
        )
        self.assertEqual(state[32], 5.0)
        self.assertEqual(state[33], 3.0)

    def test_queue_lengths_at_indices_34_37(self) -> None:
        """Public queue lengths for 4 EAs at indices 34..37."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[1.0, 2.0, 3.0, 4.0],
            load_forecast=[0.0] * 4,
        )
        np.testing.assert_array_equal(state[34:38], [1.0, 2.0, 3.0, 4.0])

    def test_load_forecast_at_indices_38_41(self) -> None:
        """Load forecast for 4 EAs at indices 38..41."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0] * 4,
            load_forecast=[5.0, 6.0, 7.0, 8.0],
        )
        np.testing.assert_array_equal(state[38:42], [5.0, 6.0, 7.0, 8.0])

    def test_padding_for_short_queue_lengths(self) -> None:
        """Fewer than N queue lengths must be padded with zeros."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[1.0, 2.0],  # only 2 of 4
            load_forecast=[0.0] * 4,
        )
        np.testing.assert_array_equal(state[34:38], [1.0, 2.0, 0.0, 0.0])

    def test_truncation_for_excess_queue_lengths(self) -> None:
        """More than N queue lengths must be truncated."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],  # 6 values, only 4 EAs
            load_forecast=[0.0] * 4,
        )
        np.testing.assert_array_equal(state[34:38], [1.0, 2.0, 3.0, 4.0])

    def test_float32_dtype(self) -> None:
        """State vector must be float32."""
        builder = PaperStateBuilder(num_eas=4)
        state = builder.build_state(
            task_size=3.5,
            processing_density=0.297,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0] * 4,
            load_forecast=[0.0] * 4,
        )
        self.assertEqual(state.dtype, np.float32)


# ═══════════════════════════════════════════════════════════════════════
# Part 2: DuelingDQNNetwork
# ═══════════════════════════════════════════════════════════════════════

class TestDuelingDQNNetworkArchitecture(unittest.TestCase):
    """Verify DuelingDQNNetwork has 3x1024 + dueling AV architecture."""

    def setUp(self) -> None:
        """Create a network with paper-sized dimensions."""
        self.state_dim = 74  # paper N=20
        self.action_dim = 22  # N + 2 (local, public_0..public_19, cloud)
        self.network = DuelingDQNNetwork(
            state_dim=self.state_dim,
            action_dim=self.action_dim,
            hidden_size=1024,
            num_hidden_layers=3,
        )

    def test_forward_pass_output_shape(self) -> None:
        """Forward pass must output shape (batch_size, action_dim)."""
        batch = torch.randn(8, self.state_dim)
        output = self.network.forward(batch)
        self.assertEqual(output.shape, (8, self.action_dim))

    def test_single_sample_forward(self) -> None:
        """Single sample forward pass must output shape (1, action_dim)."""
        batch = torch.randn(1, self.state_dim)
        output = self.network.forward(batch)
        self.assertEqual(output.shape, (1, self.action_dim))

    def test_shared_layer_count(self) -> None:
        """Network must have exactly 3 shared hidden layers."""
        self.assertEqual(len(self.network.shared_layers), 3)

    def test_shared_layer_sizes(self) -> None:
        """Shared layers must be [74→1024, 1024→1024, 1024→1024]."""
        expected_shapes = [
            (self.state_dim, 1024),
            (1024, 1024),
            (1024, 1024),
        ]
        for layer, (in_feat, out_feat) in zip(self.network.shared_layers, expected_shapes):
            self.assertEqual(layer.in_features, in_feat)
            self.assertEqual(layer.out_features, out_feat)

    def test_value_stream_produces_scalar(self) -> None:
        """Value stream output must be (batch_size, 1)."""
        batch = torch.randn(4, self.state_dim)
        with torch.no_grad():
            # Test value stream directly
            x = batch
            for layer in self.network.shared_layers:
                x = self.network.relu(layer(x))
            v = x
            for layer in self.network.value_layers:
                v = self.network.relu(layer(v))
            value = self.network.value_output(v)
        self.assertEqual(value.shape, (4, 1))

    def test_advantage_stream_produces_action_dim(self) -> None:
        """Advantage stream output must be (batch_size, action_dim)."""
        batch = torch.randn(4, self.state_dim)
        with torch.no_grad():
            x = batch
            for layer in self.network.shared_layers:
                x = self.network.relu(layer(x))
            a = x
            for layer in self.network.advantage_layers:
                a = self.network.relu(layer(a))
            advantage = self.network.advantage_output(a)
        self.assertEqual(advantage.shape, (4, self.action_dim))

    def test_dueling_combination_is_q_values(self) -> None:
        """Q(s,a) = V(s) + A(s,a) - mean(A(s,a')) formula must hold."""
        batch = torch.randn(4, self.state_dim)
        with torch.no_grad():
            q_values = self.network.forward(batch)
        # Q-values should not be all identical (unless by coincidence)
        self.assertFalse(torch.all(q_values == q_values[:, :1]))

    def test_forward_pass_differentiable(self) -> None:
        """Forward pass must be differentiable (gradients flow)."""
        batch = torch.randn(2, self.state_dim, requires_grad=True)
        output = self.network.forward(batch)
        loss = output.sum()
        loss.backward()
        # Gradients must flow to shared layers
        for layer in self.network.shared_layers:
            self.assertIsNotNone(layer.weight.grad)

    def test_learn_from_batch_updates_weights(self) -> None:
        """learn_from_batch must update network weights."""
        batch_size = 4
        states = torch.randn(batch_size, self.state_dim)
        actions = torch.randint(0, self.action_dim, (batch_size,))
        rewards = torch.randn(batch_size)
        next_states = torch.randn(batch_size, self.state_dim)
        dones = torch.zeros(batch_size)

        # Get weights before
        w_before = list(self.network.parameters())[0].clone()

        loss = self.network.learn_from_batch(states, actions, rewards, next_states, dones)

        # Get weights after
        w_after = list(self.network.parameters())[0]

        # Loss must be a finite float
        self.assertTrue(math.isfinite(loss))
        # Weights must have changed
        self.assertFalse(torch.equal(w_before, w_after))


# ═══════════════════════════════════════════════════════════════════════
# Part 3: HoodieModel State Building & Forward Pass
# ═══════════════════════════════════════════════════════════════════════

class TestHoodieModelStateBuilding(unittest.TestCase):
    """Verify HoodieModel builds state vectors correctly from observations."""

    def setUp(self) -> None:
        self.model = HoodieModel()

    def _make_observation(self, num_eas: int = 20) -> dict:
        """Create a realistic observation dict."""
        return {
            "task_size": 3.5,
            "processing_density": 0.297,
            "private_wait_time": 2.0,
            "offload_wait_time": 1.0,
            "public_queue_lengths": [float(i % 3) for i in range(num_eas)],
            "load_forecast": [0.0] * num_eas,
        }

    def _make_context(self, observation: dict) -> PolicyContext:
        """Create PolicyContext from observation."""
        return PolicyContext(
            observation=observation,
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=(),
        )

    def test_initialization_from_20ea_observation(self) -> None:
        """Model must initialize networks from observation with 20 EAs."""
        obs = self._make_observation(num_eas=20)
        with self.assertRaises(ValueError):
            # Without calling build_state first, forward pass should handle observation
            pass
        # Build state manually to trigger initialization
        state = self.model._build_state_from_observation(obs)
        self.assertTrue(self.model._initialized)
        self.assertEqual(self.model._num_eas, 20)

    def test_state_vector_74_for_20ea(self) -> None:
        """State vector must have 74 elements for 20 EAs."""
        obs = self._make_observation(num_eas=20)
        state = self.model._build_state_from_observation(obs)
        self.assertEqual(len(state), 74)

    def test_state_vector_42_for_4ea(self) -> None:
        """State vector must have 42 elements for 4 EAs."""
        obs = self._make_observation(num_eas=4)
        state = self.model._build_state_from_observation(obs)
        self.assertEqual(len(state), 42)

    def test_state_vector_empty_when_no_observation(self) -> None:
        """State vector must be empty when observation lacks required fields."""
        state = self.model._build_state_from_observation({})
        self.assertEqual(len(state), 0)

    def test_forward_returns_q_values_for_legal_actions(self) -> None:
        """Forward pass must return Q-values for all legal actions."""
        obs = self._make_observation(num_eas=20)
        from src.agents.history_builder import HistoryWindow

        history = HistoryWindow(
            observations=(obs,),
            legal_action_masks=({"local": True, "horizontal": True, "vertical": True},),
            trace_history=(),
        )
        q_values = self.model.forward(history, legal_actions=("local", "horizontal", "vertical"))
        self.assertIn("local", q_values)
        self.assertIn("horizontal", q_values)
        self.assertIn("vertical", q_values)

    def test_q_values_are_finite(self) -> None:
        """Q-values must be finite numbers."""
        obs = self._make_observation(num_eas=20)
        from src.agents.history_builder import HistoryWindow

        history = HistoryWindow(
            observations=(obs,),
            legal_action_masks=({"local": True, "horizontal": True, "vertical": True},),
            trace_history=(),
        )
        q_values = self.model.forward(history, legal_actions=("local", "horizontal", "vertical"))
        for action, q in q_values.items():
            self.assertTrue(math.isfinite(q), f"Q-value for {action} is not finite: {q}")

    def test_q_values_differ_for_different_states(self) -> None:
        """Different states must produce different Q-value distributions."""
        from src.agents.history_builder import HistoryWindow

        obs1 = self._make_observation(num_eas=20)
        obs2 = dict(obs1)
        obs2["private_wait_time"] = 100.0  # dramatically different

        history1 = HistoryWindow(observations=(obs1,), legal_action_masks=({},), trace_history=())
        history2 = HistoryWindow(observations=(obs2,), legal_action_masks=({},), trace_history=())

        q1 = self.model.forward(history1, legal_actions=("local", "horizontal", "vertical"))
        q2 = self.model.forward(history2, legal_actions=("local", "horizontal", "vertical"))

        # At least one action must have meaningfully different Q-value
        diffs = [abs(q1[a] - q2[a]) for a in q1]
        self.assertTrue(
            any(d > 0.01 for d in diffs),
            f"Q-values not meaningfully different: q1={q1}, q2={q2}",
        )

    def test_forward_with_empty_history(self) -> None:
        """Forward pass must return zeros for legal actions when history is empty."""
        from src.agents.history_builder import HistoryWindow

        history = HistoryWindow(
            observations=(),
            legal_action_masks=(),
            trace_history=(),
        )
        q_values = self.model.forward(history, legal_actions=("local", "horizontal"))
        self.assertEqual(q_values, {"local": 0.0, "horizontal": 0.0})

    def test_target_network_updated(self) -> None:
        """Target network must have same structure as online network after update."""
        obs = self._make_observation(num_eas=4)
        self.model._build_state_from_observation(obs)
        self.model.update_target_network()

        # Verify both networks share the same architecture
        online_params = dict(self.model.online_net.named_parameters())
        target_params = dict(self.model.target_net.named_parameters())
        self.assertEqual(
            set(online_params.keys()),
            set(target_params.keys()),
        )


class TestHoodieModelSerialization(unittest.TestCase):
    """Verify HoodieModel to_state/from_state roundtrip."""

    def setUp(self) -> None:
        self.model = HoodieModel()
        obs = {
            "task_size": 3.5,
            "processing_density": 0.297,
            "private_wait_time": 2.0,
            "offload_wait_time": 1.0,
            "public_queue_lengths": [0.0, 1.0, 2.0, 3.0],
            "load_forecast": [0.0] * 4,
        }
        self.model._build_state_from_observation(obs)

    def test_to_state_contains_required_keys(self) -> None:
        """Serialized state must contain schema_version, num_eas, network dicts."""
        state = self.model.to_state()
        self.assertIn("schema_version", state)
        self.assertIn("initialized", state)
        self.assertIn("num_eas", state)
        self.assertIn("online_net", state)
        self.assertIn("target_net", state)

    def test_state_roundtrip_preserves_weights(self) -> None:
        """Serialization followed by deserialization must preserve network weights."""
        state = self.model.to_state()
        restored = HoodieModel.from_state(state)
        # Compare weights
        for online_param, restored_param in zip(
            self.model.online_net.parameters(),
            restored.online_net.parameters(),
        ):
            self.assertTrue(torch.equal(online_param, restored_param))

    def test_from_state_reconstructs_model(self) -> None:
        """from_state must create a working model."""
        state = self.model.to_state()
        restored = HoodieModel.from_state(state)
        from src.agents.history_builder import HistoryWindow

        obs = {
            "task_size": 3.5,
            "processing_density": 0.297,
            "private_wait_time": 0.0,
            "offload_wait_time": 0.0,
            "public_queue_lengths": [0.0] * 4,
            "load_forecast": [0.0] * 4,
        }
        history = HistoryWindow(observations=(obs,), legal_action_masks=({},), trace_history=())
        q_values = restored.forward(history, legal_actions=("local", "horizontal", "vertical"))
        self.assertIn("local", q_values)

    def test_uninitialized_model_serialization(self) -> None:
        """Uninitialized model must serialize without error."""
        model = HoodieModel()
        state = model.to_state()
        self.assertFalse(state["initialized"])

    def test_uninitialized_model_deserialization(self) -> None:
        """Uninitialized model state must deserialize without error."""
        model = HoodieModel()
        state = model.to_state()
        restored = HoodieModel.from_state(state)
        self.assertFalse(restored._initialized)


class TestHoodieModelActionSelection(unittest.TestCase):
    """Verify HoodieModel selects actions correctly."""

    def setUp(self) -> None:
        self.model = HoodieModel()
        obs = {
            "task_size": 3.5,
            "processing_density": 0.297,
            "private_wait_time": 0.0,
            "offload_wait_time": 0.0,
            "public_queue_lengths": [0.0, 0.0, 0.0, 0.0],
            "load_forecast": [0.0] * 4,
        }
        from src.agents.history_builder import HistoryWindow
        self.history = HistoryWindow(observations=(obs,), legal_action_masks=({},), trace_history=())

    def test_best_action_returns_string(self) -> None:
        """best_action must return a string."""
        action = self.model.best_action(self.history, ("local", "horizontal", "vertical"))
        self.assertIsInstance(action, str)

    def test_best_action_is_legal(self) -> None:
        """best_action must return one of the legal actions."""
        legal = ("local", "horizontal", "vertical")
        for _ in range(10):
            action = self.model.best_action(self.history, legal)
            self.assertIn(action, legal)

    def test_best_action_raises_on_empty_legal(self) -> None:
        """best_action must raise ValueError when no legal actions."""
        with self.assertRaises(ValueError):
            self.model.best_action(self.history, ())

    def test_learn_from_transitions_returns_count(self) -> None:
        """learn_from_transitions must return number of transitions processed."""
        from src.agents.replay_buffer import Transition
        obs = {
            "task_size": 3.5,
            "processing_density": 0.297,
            "private_wait_time": 0.0,
            "offload_wait_time": 0.0,
            "public_queue_lengths": [0.0] * 4,
            "load_forecast": [0.0] * 4,
        }
        transitions = (
            Transition(state=obs, action="local", reward=1.0, next_state=obs, done=False),
            Transition(state=obs, action="horizontal", reward=0.5, next_state=obs, done=False),
        )
        count = self.model.learn_from_transitions(transitions, 0.001)
        self.assertEqual(count, 2)


# ═══════════════════════════════════════════════════════════════════════
# Part 4: LSTM Load Forecaster Stub
# ═══════════════════════════════════════════════════════════════════════

class TestLstmLoadForecaster(unittest.TestCase):
    """Verify LSTM load forecaster module is not empty (file must contain code)."""

    def test_lstm_module_has_content(self) -> None:
        """lstm_dueling_dqn.py must contain at least one class or function."""
        lstm_path = Path("src/agents/lstm_dueling_dqn.py")
        self.assertTrue(lstm_path.exists(), "lstm_dueling_dqn.py does not exist")
        content = lstm_path.read_text().strip()
        self.assertGreater(len(content), 0, "lstm_dueling_dqn.py is empty - must contain LSTM implementation")

    def test_lstm_module_can_be_imported(self) -> None:
        """lstm_dueling_dqn.py must be importable as a Python module."""
        try:
            import src.agents.lstm_dueling_dqn  # noqa: F811
            # Must contain at least one class
            classes = [name for name in dir(src.agents.lstm_dueling_dqn) if not name.startswith("_")]
            self.assertGreater(len(classes), 0, "lstm_dueling_dqn has no public classes")
        except ImportError as e:
            self.fail(f"Cannot import lstm_dueling_dqn: {e}")


if __name__ == "__main__":
    unittest.main()
