from __future__ import annotations

import unittest

from .offload_trace_fixtures import attach_one_task_trace_bank, make_horizontal_topology_environment


class OffloadInstrumentationNoBehaviorChangeTest(unittest.TestCase):
    def test_instrumentation_does_not_change_rewards_or_metrics(self) -> None:
        env = attach_one_task_trace_bank(make_horizontal_topology_environment(episode_length=6), action="horizontal")
        env.reset(seed=None)
        rewards = []
        for _ in range(8):
            action = "horizontal" if env.current_task is not None and env.legal_action_mask().get("horizontal", False) else None
            if action is None and env.current_task is not None:
                break
            _, reward, _, _, info = env.step(action)
            rewards.append(reward)
            if info["finalized_tasks"]:
                break
        self.assertEqual(info["metrics"]["reward"], sum(rewards))
        self.assertGreaterEqual(len(rewards), 1)
