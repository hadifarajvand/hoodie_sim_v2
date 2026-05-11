from __future__ import annotations

import unittest

from .offload_trace_fixtures import attach_one_task_trace_bank, make_horizontal_topology_environment


class OffloadLifecycleTraceVisibilityHorizontalTest(unittest.TestCase):
    def test_horizontal_trace_contains_lifecycle_events(self) -> None:
        env = attach_one_task_trace_bank(make_horizontal_topology_environment(episode_length=6), action="horizontal")
        observation, info = env.reset(seed=None)
        self.assertTrue(observation)
        seen = []
        for _ in range(8):
            action = "horizontal" if env.current_task is not None and env.legal_action_mask().get("horizontal", False) else None
            if action is None and env.current_task is not None:
                break
            observation, reward, terminated, truncated, info = env.step(action)
            if info["finalized_tasks"]:
                seen = info["finalized_tasks"][0]["offload_lifecycle_events"]
                break
        self.assertIn("selected_action", seen)
        self.assertIn("queued_public", seen)
        self.assertIn("transmission_started", seen)
        self.assertIn("transmission_completed", seen)
        self.assertIn("execution_started", seen)
        self.assertIn("execution_completed", seen)
        self.assertIn("reward_emitted", seen)
