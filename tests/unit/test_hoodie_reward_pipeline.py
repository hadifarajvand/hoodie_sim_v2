from __future__ import annotations

import unittest

from src.environment.hoodie_reward_pipeline import HoodieDelayedRewardPipeline


class HoodieRewardPipelineTests(unittest.TestCase):
    def test_reward_returns_to_originating_agent(self) -> None:
        pipeline = HoodieDelayedRewardPipeline()
        pipeline.register_pending(correlation_id="corr-1", originating_agent_id="7", dispatching_agent_id="2", task_id="task-1")
        reward = pipeline.resolve_reward(correlation_id="corr-1", completion_node_id="cloud", reward=1.0)
        self.assertEqual(reward["reward_recipient_agent_id"], "7")
        self.assertEqual(reward["originating_agent_id"], "7")


if __name__ == "__main__":
    unittest.main()

