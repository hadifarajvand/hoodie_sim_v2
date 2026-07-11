from __future__ import annotations

import unittest

import torch

from src.analysis.full_training_reproduction_campaign import (
    PAPER_STATE_DIM,
    ReplayTransition,
    build_state_vector,
    build_state_window,
    build_state_window_tensor,
)
from src.analysis.full_training_reproduction_campaign.replay import zero_state_row


class TestPaperReplayTransition74D(unittest.TestCase):
    """Test ReplayTransition with 74-dimensional state vectors (paper-faithful)."""

    def setUp(self) -> None:
        self.state_dim = PAPER_STATE_DIM  # 74
        self.lookback_w = 10
        self.action_count = 22

    def _window(self, dim: int | None = None) -> tuple[tuple[float, ...], ...]:
        """Helper: make a valid state window of 10 rows, each of given dimension."""
        d = dim or self.state_dim
        return tuple(tuple(float(i * d + j) for j in range(d)) for i in range(self.lookback_w))

    def _mask(self) -> tuple[bool, ...]:
        return tuple([True] * self.action_count)

    def test_valid_74d_transition_passes_validation(self) -> None:
        """A ReplayTransition with 10x74 state must pass __post_init__ validation."""
        w = self._window()
        t = ReplayTransition(
            state=w, action=0, legal_action_mask=self._mask(),
            next_state=w, reward=0.0, reward_available=False,
            terminal=False, terminal_reason=None, pending_at_horizon=False,
            arrival_slot=0, completion_or_drop_slot=None,
            agent_id=0, episode_id=0, step_id=0,
            state_dim=self.state_dim, action_count=self.action_count,
        )
        self.assertEqual(len(t.state), self.lookback_w)
        self.assertEqual(len(t.state[0]), self.state_dim)

    def test_wrong_state_dimension_raises_value_error(self) -> None:
        """A ReplayTransition where a row has != 74 elements must raise ValueError."""
        bad_window = list(self._window())
        bad_window[0] = (0.0, 1.0, 2.0)          # 3 elements instead of 74
        with self.assertRaises(ValueError):
            ReplayTransition(
                state=tuple(bad_window), action=0, legal_action_mask=self._mask(),
                next_state=tuple(bad_window), reward=0.0, reward_available=False,
                terminal=False, terminal_reason=None, pending_at_horizon=False,
                arrival_slot=0, completion_or_drop_slot=None,
                agent_id=0, episode_id=0, step_id=0,
                state_dim=self.state_dim, action_count=self.action_count,
            )

    def test_build_state_vector_returns_74_elements(self) -> None:
        """build_state_vector(state_dim=74) must produce a 74-element tuple."""
        obs = {
            "size": 3.5, "processing_density": 2.5,
            "private_wait_time": 0.0, "offload_wait_time": 0.0,
            "public_queue_lengths": [0.0] * 20,
            "load_forecast": [0.0] * 20,
        }
        vec = build_state_vector(observation=obs, current_task=None,
                                 episode_length=10, state_dim=self.state_dim)
        self.assertIsInstance(vec, tuple)
        self.assertEqual(len(vec), self.state_dim)
        self.assertTrue(all(isinstance(x, float) for x in vec))

    def test_build_state_window_produces_10x74_shape(self) -> None:
        """build_state_window(state_dim=74) must return 10 rows, each 74 elements."""
        history = [tuple(float(i) for i in range(self.state_dim))] * 15
        window = build_state_window(history, lookback_w=self.lookback_w,
                                    state_dim=self.state_dim)
        self.assertEqual(len(window), self.lookback_w)
        for row in window:
            self.assertEqual(len(row), self.state_dim)

    def test_zero_state_row_returns_74_zeros(self) -> None:
        """zero_state_row(74) must return a 74-element tuple of 0.0."""
        zeros = zero_state_row(state_dim=self.state_dim)
        self.assertEqual(len(zeros), self.state_dim)
        self.assertTrue(all(v == 0.0 for v in zeros))

    def test_build_state_window_tensor_produces_correct_shape(self) -> None:
        """build_state_window_tensor on 10x74 must yield torch.Size([10, 74])."""
        window = tuple(
            tuple(float(i * self.state_dim + j) for j in range(self.state_dim))
            for i in range(self.lookback_w)
        )
        tensor = build_state_window_tensor(window)
        self.assertIsInstance(tensor, torch.Tensor)
        self.assertEqual(tensor.shape, torch.Size([self.lookback_w, self.state_dim]))
        self.assertEqual(tensor.dtype, torch.float32)


if __name__ == "__main__":
    unittest.main()
