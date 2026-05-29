from __future__ import annotations

import unittest

from src.analysis.distributed_multi_agent_hoodie_training import DistributedEpsilonGreedyPolicy, EpsilonScheduleState


class DistributedEpsilonScheduleTests(unittest.TestCase):
    def test_epsilon_decays_deterministically(self) -> None:
        state = EpsilonScheduleState(epsilon_start=1.0, epsilon_end=0.1, decay_steps=10)
        self.assertAlmostEqual(state.epsilon(0), 1.0)
        self.assertAlmostEqual(state.epsilon(10), 0.1)
        policy = DistributedEpsilonGreedyPolicy()
        action = policy.choose(legal_action_mask=[False, True, True], step=1, rng_seed=7, epsilon_state=state)
        self.assertIn(action, (1, 2))


if __name__ == "__main__":
    unittest.main()

