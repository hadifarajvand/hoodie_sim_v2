from __future__ import annotations

import unittest

from src.analysis.hoodie_proposed_method.learning_model import (
    DQNInterface,
    DistributedEdgeAgentDecisionModel,
    DoubleDQNTargetRule,
    DuelingDQNInterface,
    EpsilonGreedyTrainingSchedule,
    InferenceMode,
    LSTMForecastRecoveryInterface,
    ReplayMemoryInterface,
)
from src.agents.replay_buffer import Transition


class HoodieProposedMethodLearningTests(unittest.TestCase):
    def test_learning_interfaces_cover_dqn_double_dqn_dueling_and_lstm_shapes(self) -> None:
        dqn = DQNInterface()
        self.assertEqual(dqn.q_values({"state_value": 3.0}, ["local", "horizontal"]), {"local": 3.0, "horizontal": 3.0})

        double_dqn = DoubleDQNTargetRule()
        self.assertEqual(
            double_dqn.target_value({"local": 1.0, "horizontal": 3.0}, {"local": 8.0, "horizontal": 5.0}, ("local", "horizontal")),
            5.0,
        )

        dueling = DuelingDQNInterface(value_weight=2.0, advantage_weights={"local": 1.0, "horizontal": 3.0})
        q_values = dueling.q_values({"state_value": 2.0}, ("local", "horizontal"))
        self.assertEqual(q_values["horizontal"], 5.0)
        self.assertEqual(q_values["local"], 3.0)

        lstm = LSTMForecastRecoveryInterface(lookback_window=3)
        self.assertEqual(lstm.forecast([1.0, 2.0, 3.0, 6.0]), 11.0 / 3.0)
        self.assertEqual(lstm.recover([2.0, 4.0, 8.0]), 8.0)

    def test_training_and_inference_helpers_remain_deterministic(self) -> None:
        replay = ReplayMemoryInterface(capacity=2, seed=11)
        replay.extend(
            (
                Transition(state={"slot": 1}, action="local", reward=-1.0, next_state={"slot": 2}, done=False),
                Transition(state={"slot": 2}, action="horizontal", reward=-2.0, next_state={"slot": 3}, done=False),
                Transition(state={"slot": 3}, action="vertical", reward=-3.0, next_state={"slot": 4}, done=True),
            )
        )
        self.assertEqual(replay.to_dict()["size"], 2)
        self.assertEqual(len(replay.sample_batch(1)), 1)
        self.assertEqual(len(replay.sample_batch(10)), 2)

        schedule = EpsilonGreedyTrainingSchedule(epsilon_start=1.0, epsilon_end=0.0, decay_episodes=8)
        self.assertEqual(schedule.epsilon(0), 1.0)
        self.assertEqual(schedule.epsilon(4), 0.0)

        inference = InferenceMode()
        self.assertEqual(inference.choose_action({"local": 1.0, "horizontal": 2.0, "vertical": 2.0}), "vertical")

        model = DistributedEdgeAgentDecisionModel(
            agent_id="EA-9",
            dueling_interface=DuelingDQNInterface(advantage_weights={"horizontal": 2.0}),
        )
        self.assertEqual(model.choose_action({"state_value": 2.0}, ["local", "horizontal"], episode_index=0, use_inference=True), "horizontal")
        model.record_transition({"slot": 1}, "local", -1.0, {"slot": 2}, False)
        self.assertEqual(len(model.sample_replay_batch(1)), 1)
        self.assertEqual(model.forecast_next_load([1.0, 3.0, 5.0]), 3.0)
        self.assertEqual(model.recover_delayed_load([4.0, 6.0]), 6.0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
