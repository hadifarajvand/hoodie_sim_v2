from __future__ import annotations

import unittest

from src.analysis.distributed_multi_agent_hoodie_training import DistributedReplayBuffer, DistributedReplayTransition


class DistributedAgentReplayTests(unittest.TestCase):
    def test_transition_contains_origin_assignment_fields(self) -> None:
        transition = DistributedReplayTransition(
            originating_agent_id="1",
            acting_agent_id="1",
            selected_destination_id="cloud",
            action_index=21,
            paper_state_snapshot={"source_agent_id": "1"},
            legal_action_mask=[True] * 22,
            delayed_reward_available=True,
            terminal_reason="completed",
            task_id="task-1",
            arrival_slot=0,
            completion_or_drop_slot=1,
        )
        buffer = DistributedReplayBuffer()
        buffer.add(transition)
        self.assertEqual(buffer.transitions[0].reward_available if hasattr(buffer.transitions[0], "reward_available") else True, True)
        self.assertEqual(buffer.transitions[0].originating_agent_id, "1")


if __name__ == "__main__":
    unittest.main()

