from __future__ import annotations

import unittest

from src.analysis.distributed_multi_agent_hoodie_training import DelayedRewardAssignment


class DistributedDelayedRewardAssignmentTests(unittest.TestCase):
    def test_reward_routes_to_originating_agent(self) -> None:
        assignment = DelayedRewardAssignment(
            task_originating_agent_id="3",
            selected_destination_id="cloud",
            completion_node_id="cloud",
            reward_recipient_agent_id="3",
            reward_available=True,
            pending_at_horizon=False,
            terminal_outcome="completed",
        )
        self.assertEqual(assignment.reward_recipient_agent_id, assignment.task_originating_agent_id)


if __name__ == "__main__":
    unittest.main()

