from __future__ import annotations

import random
import unittest

from src.analysis.full_training_reproduction_campaign import ReplayBuffer, ReplayTransition


def _window(base: float) -> tuple[tuple[float, float, float], ...]:
    return tuple((base + index, base + index + 0.1, base + index + 0.2) for index in range(10))


class FullTrainingReplayContractUnitTests(unittest.TestCase):
    def _transition(
        self,
        *,
        action: int,
        reward_available: bool,
        terminal: bool,
        pending_at_horizon: bool,
        terminal_reason: str | None,
        reward: float,
    ) -> ReplayTransition:
        return ReplayTransition(
            state=_window(0.0),
            action=action,
            legal_action_mask=(True, True, True),
            next_state=_window(1.0),
            reward=reward,
            reward_available=reward_available,
            terminal=terminal,
            terminal_reason=terminal_reason,
            pending_at_horizon=pending_at_horizon,
            arrival_slot=0,
            completion_or_drop_slot=1 if terminal else None,
            agent_id=1,
            episode_id=7,
            step_id=3,
        )

    def test_replay_buffer_preserves_delayed_reward_contract(self) -> None:
        buffer = ReplayBuffer(capacity=4, seed=11)
        non_terminal = self._transition(
            action=0,
            reward_available=False,
            terminal=False,
            pending_at_horizon=False,
            terminal_reason=None,
            reward=0.0,
        )
        terminal = self._transition(
            action=2,
            reward_available=True,
            terminal=True,
            pending_at_horizon=False,
            terminal_reason="completed",
            reward=1.0,
        )
        buffer.add(non_terminal)
        buffer.add(terminal)
        batch = buffer.sample(2, rng=random.Random(0))

        self.assertEqual(len(batch.transitions), 2)
        self.assertIn(False, batch.reward_available_tensor.tolist())
        self.assertIn(True, batch.reward_available_tensor.tolist())
        self.assertIn("completed", {transition.terminal_reason for transition in batch.transitions})

    def test_pending_at_horizon_is_not_terminal(self) -> None:
        pending = self._transition(
            action=1,
            reward_available=False,
            terminal=False,
            pending_at_horizon=True,
            terminal_reason="pending_at_horizon",
            reward=0.0,
        )
        self.assertTrue(pending.pending_at_horizon)
        self.assertFalse(pending.terminal)
        with self.assertRaises(ValueError):
            self._transition(
                action=1,
                reward_available=False,
                terminal=True,
                pending_at_horizon=True,
                terminal_reason="pending_at_horizon",
                reward=0.0,
            )

    def test_fake_terminal_samples_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._transition(
                action=1,
                reward_available=True,
                terminal=True,
                pending_at_horizon=False,
                terminal_reason="pending_at_horizon",
                reward=0.0,
            )


if __name__ == "__main__":
    unittest.main()
