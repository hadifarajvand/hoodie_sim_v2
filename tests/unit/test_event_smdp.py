from __future__ import annotations

import unittest

from src.training.event_smdp import AgentEventSMDPAccumulator


class AgentEventSMDPTests(unittest.TestCase):
    def test_reward_is_discounted_inside_source_interval(self) -> None:
        accumulator = AgentEventSMDPAccumulator(gamma=0.9)
        self.assertIsNone(
            accumulator.observe_decision(
                {
                    "source_agent_id": 1,
                    "decision_slot": 0,
                    "state": {"slot": 0},
                    "action": "local",
                }
            )
        )
        accumulator.observe_resolution(
            {
                "source_id": 1,
                "resolution_slot": 2,
                "task_reward": -5.0,
            }
        )

        transition = accumulator.observe_decision(
            {
                "source_agent_id": 1,
                "decision_slot": 3,
                "state": {"slot": 3},
                "action": "cloud",
            }
        )

        self.assertIsNotNone(transition)
        assert transition is not None
        self.assertEqual(transition.delta_slots, 3)
        self.assertAlmostEqual(transition.reward, (0.9**2) * -5.0)
        self.assertFalse(transition.done)
        self.assertEqual(transition.next_state, {"slot": 3})

    def test_agents_have_independent_decision_intervals(self) -> None:
        accumulator = AgentEventSMDPAccumulator(gamma=1.0)
        accumulator.observe_decision(
            {
                "source_agent_id": 1,
                "decision_slot": 0,
                "state": {"agent": 1, "slot": 0},
                "action": "local",
            }
        )
        accumulator.observe_decision(
            {
                "source_agent_id": 2,
                "decision_slot": 1,
                "state": {"agent": 2, "slot": 1},
                "action": "cloud",
            }
        )
        accumulator.observe_resolution(
            {"source_id": 1, "resolution_slot": 2, "task_reward": -2.0}
        )
        accumulator.observe_resolution(
            {"source_id": 2, "resolution_slot": 3, "task_reward": -4.0}
        )

        transition_1 = accumulator.observe_decision(
            {
                "source_agent_id": 1,
                "decision_slot": 4,
                "state": {"agent": 1, "slot": 4},
                "action": "horizontal_2",
            }
        )
        self.assertEqual(transition_1.reward, -2.0)
        self.assertEqual(transition_1.delta_slots, 4)
        self.assertEqual(accumulator.open_agent_ids, (1, 2))

        terminal = accumulator.finalize_terminal(terminal_slot=6)
        by_agent = {transition.source_agent_id: transition for transition in terminal}
        self.assertEqual(by_agent[1].reward, 0.0)
        self.assertEqual(by_agent[1].delta_slots, 2)
        self.assertEqual(by_agent[2].reward, -4.0)
        self.assertEqual(by_agent[2].delta_slots, 5)
        self.assertTrue(by_agent[1].done)
        self.assertTrue(by_agent[2].done)


if __name__ == "__main__":
    unittest.main()
