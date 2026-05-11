from __future__ import annotations

import unittest

from src.environment.gym_adapter import HoodieGymEnvironment


class Feature024RegressionTest(unittest.TestCase):
    def test_local_compute_and_deterministic_ordering_remain_matches(self) -> None:
        env_a = HoodieGymEnvironment(episode_length=3)
        env_b = HoodieGymEnvironment(episode_length=3)
        env_a.reset(seed=201)
        env_b.reset(seed=201)
        rewards_a = []
        rewards_b = []
        for _ in range(3):
            action_a = "local" if env_a.current_task is not None else None
            action_b = "local" if env_b.current_task is not None else None
            _, reward_a, *_ = env_a.step(action_a)
            _, reward_b, *_ = env_b.step(action_b)
            rewards_a.append(reward_a)
            rewards_b.append(reward_b)
        self.assertEqual(rewards_a, rewards_b)
        self.assertEqual(env_a._history[0].selected_action, env_b._history[0].selected_action)

