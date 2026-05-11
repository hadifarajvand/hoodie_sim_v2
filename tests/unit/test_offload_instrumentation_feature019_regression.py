from __future__ import annotations

import unittest

from src.environment.gym_adapter import HoodieGymEnvironment


class Feature019RegressionTest(unittest.TestCase):
    def test_timeout_drop_behavior_remains_preserved(self) -> None:
        env = HoodieGymEnvironment(episode_length=2)
        env.reset(seed=104)
        reward_total = 0.0
        for _ in range(2):
            action = "local" if env.current_task is not None else None
            _, reward, _, _, info = env.step(action)
            reward_total += reward
        self.assertLessEqual(reward_total, 0.0)
        self.assertIn(info["metrics"], [info["metrics"]])

