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
from src.policies.policy_interface import PolicyContext


class HoodieProposedMethodLearningTests(unittest.TestCase):
    def test_dqn_interface_selects_highest_q_action_and_records_trace(self) -> None:
        dqn = DQNInterface(state_feature_order=("load", "deadline"))
        state = {"load": 2.0, "deadline": 1.0}
        dqn.set_q_values(state, {"local": 1.0, "horizontal": 4.0, "vertical": 2.0})

        self.assertEqual(dqn.state_vector(state), (2.0, 1.0))
        self.assertEqual(dqn.q_values(state, ["local", "horizontal", "vertical"]), {"local": 1.0, "horizontal": 4.0, "vertical": 2.0})
        self.assertEqual(dqn.choose_action({"local": 1.0, "horizontal": 2.0}), "horizontal")
        self.assertEqual(dqn.select_action(state, ["local", "horizontal", "vertical"]), "horizontal")
        self.assertEqual(dqn.decision_trace[-1].chosen_action, "horizontal")
        self.assertEqual(dqn.decision_trace[-1].state_vector, (2.0, 1.0))
        self.assertEqual(dqn.decision_trace[-1].legal_actions, ("local", "horizontal", "vertical"))
        self.assertEqual(dqn.to_dict()["decision_trace"][0]["chosen_action"], "horizontal")

    def test_dqn_tie_breaking_and_empty_action_validation(self) -> None:
        dqn = DQNInterface()
        state = {"state_value": 1.0}
        dqn.set_q_values(state, {"vertical": 3.0, "horizontal": 3.0, "local": 3.0})
        legal_actions = ("vertical", "horizontal", "local")
        self.assertEqual(dqn.select_action(state, legal_actions), "vertical")
        self.assertEqual(dqn.select_action(state, legal_actions), "vertical")
        with self.assertRaises(ValueError):
            dqn.q_values(state, [])
        with self.assertRaises(ValueError):
            dqn.select_action(state, [])

    def test_epsilon_greedy_schedule_respects_decay_boundary_and_inference(self) -> None:
        dqn = DQNInterface()
        dqn.set_q_values({"state_value": 1.0}, {"local": 1.0, "horizontal": 3.0, "vertical": 2.0})

        schedule = EpsilonGreedyTrainingSchedule(total_episodes=8, exploration_seed=1)
        self.assertEqual(schedule.epsilon(0), 1.0)
        self.assertEqual(schedule.epsilon(4), 0.0)
        self.assertEqual(schedule.epsilon(6), 0.0)
        self.assertEqual(schedule.epsilon_for_inference(), 0.0)
        with self.assertRaises(ValueError):
            schedule.epsilon(-1)

        exploratory_action = schedule.select_action(
            dqn,
            {"state_value": 1.0},
            ["local", "horizontal", "vertical"],
            episode_index=0,
            force_mode="explore",
            deterministic_exploration=True,
        )
        self.assertEqual(exploratory_action, "local")
        self.assertEqual(schedule.decision_trace[-1].mode, "explore")
        self.assertEqual(schedule.decision_trace[-1].epsilon, 1.0)
        self.assertEqual(schedule.decision_trace[-1].selected_action, "local")

        exploit_action = schedule.select_action(
            dqn,
            {"state_value": 1.0},
            ["local", "horizontal", "vertical"],
            episode_index=4,
            force_mode="exploit",
        )
        self.assertEqual(exploit_action, "horizontal")
        self.assertEqual(schedule.decision_trace[-1].mode, "exploit")

        inference_action = schedule.select_action(
            dqn,
            {"state_value": 1.0},
            ["local", "horizontal", "vertical"],
            episode_index=7,
            use_inference=True,
        )
        self.assertEqual(inference_action, "horizontal")
        self.assertEqual(schedule.decision_trace[-1].mode, "inference")
        self.assertEqual(schedule.decision_trace[-1].epsilon, 0.0)

        with self.assertRaises(ValueError):
            schedule.select_action(dqn, {"state_value": 1.0}, [], episode_index=0)
        with self.assertRaises(ValueError):
            EpsilonGreedyTrainingSchedule(total_episodes=0)

    def test_learning_interfaces_cover_double_dqn_dueling_and_lstm_shapes(self) -> None:
        double_dqn = DoubleDQNTargetRule()
        self.assertEqual(double_dqn.select_action({"local": 1.0, "horizontal": 3.0}, ("local", "horizontal")), "horizontal")
        self.assertEqual(double_dqn.select_action({"local": 5.0, "horizontal": 5.0, "vertical": 1.0}, ("local", "horizontal", "vertical")), "local")
        self.assertEqual(
            double_dqn.target_value({"local": 1.0, "horizontal": 3.0}, {"local": 8.0, "horizontal": 5.0}, ("local", "horizontal")),
            5.0,
        )
        self.assertEqual(double_dqn.decision_trace[-1].chosen_action, "horizontal")
        self.assertEqual(double_dqn.decision_trace[-1].target_value, 5.0)
        self.assertEqual(double_dqn.to_dict()["decision_trace"][-1]["chosen_action"], "horizontal")
        with self.assertRaises(ValueError):
            double_dqn.select_action({"local": 1.0}, ())
        with self.assertRaises(ValueError):
            double_dqn.target_value({"local": 1.0}, {"local": 2.0}, ())

        dueling = DuelingDQNInterface(value_weight=2.0, advantage_weights={"local": 1.0, "horizontal": 3.0, "vertical": 2.0})
        q_values = dueling.q_values({"state_value": 2.0}, ("local", "horizontal", "vertical"))
        self.assertEqual(q_values, {"local": 1.0, "horizontal": 3.0, "vertical": 2.0})
        self.assertEqual(dueling.choose_action({"state_value": 2.0}, ("local", "horizontal", "vertical")), "horizontal")
        self.assertEqual(dueling.decision_trace[-1].value_estimate, 2.0)
        self.assertEqual(dueling.decision_trace[-1].raw_advantages, {"local": 1.0, "horizontal": 3.0, "vertical": 2.0})
        self.assertEqual(dueling.decision_trace[-1].mean_advantage, 2.0)
        self.assertEqual(dueling.decision_trace[-1].q_values, {"local": 1.0, "horizontal": 3.0, "vertical": 2.0})
        self.assertEqual(dueling.decision_trace[-1].selected_action, "horizontal")
        self.assertEqual(dueling.to_dict()["decision_trace"][-1]["selected_action"], "horizontal")
        tie_dueling = DuelingDQNInterface(advantage_weights={"local": 0.0, "horizontal": 0.0, "vertical": 0.0})
        self.assertEqual(tie_dueling.choose_action({"state_value": 1.0}, ("vertical", "horizontal", "local")), "vertical")
        with self.assertRaises(ValueError):
            DuelingDQNInterface(advantage_weights={"local": 1.0}).q_values({"state_value": 1.0}, ("local", "horizontal"))
        with self.assertRaises(ValueError):
            DuelingDQNInterface(advantage_weights={"local": 1.0, "horizontal": 2.0}).q_values({}, ("local", "horizontal"))
        with self.assertRaises(ValueError):
            DuelingDQNInterface(advantage_weights={"local": 1.0, "horizontal": 2.0}).q_values({"state_value": 1.0}, [])

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
        self.assertEqual(len(replay), 2)
        self.assertEqual(replay.to_dict()["size"], 2)
        self.assertEqual(replay.latest().action, "vertical")
        self.assertEqual(len(replay.sample_batch(1)), 1)
        self.assertEqual(len(replay.sample(1)), 1)
        self.assertEqual(len(replay.sample_batch(10)), 2)
        deterministic_sample = replay.sample_batch(2, deterministic=True, seed=1)
        self.assertEqual([transition.action for transition in deterministic_sample], ["horizontal", "vertical"])
        random_sample = replay.sample_batch(2, deterministic=False, seed=1)
        self.assertEqual(len(random_sample), 2)
        replay.clear()
        self.assertTrue(replay.is_empty())
        self.assertIsNone(replay.latest())
        self.assertEqual(replay.sample_batch(1), ())

        inference = InferenceMode()
        self.assertEqual(inference.choose_action({"local": 1.0, "horizontal": 2.0, "vertical": 2.0}), "vertical")

        model = DistributedEdgeAgentDecisionModel(
            agent_id="EA-9",
            dueling_interface=DuelingDQNInterface(advantage_weights={"local": 0.0, "horizontal": 2.0}),
        )
        self.assertEqual(model.choose_action({"state_value": 2.0}, ["local", "horizontal"], episode_index=0, use_inference=True), "horizontal")
        context = PolicyContext(
            observation={
                "slot": 2,
                "queue_load": 0.1,
                "current_slot": 2,
                "absolute_deadline_slot": 12,
                "fallback_hints": {"local": 1.0, "horizontal": 2.0, "vertical": 3.0},
            },
            legal_action_mask={
                "local": True,
                "compute_local": True,
                "horizontal": True,
                "offload_horizontal": True,
                "vertical": True,
                "offload_vertical": True,
            },
            trace_history=("trace-1",),
        )
        context_model = DistributedEdgeAgentDecisionModel(agent_id="EA-10")
        self.assertEqual(context_model.choose_action(context, episode_index=0), "local")
        self.assertEqual(context_model.decision_history[-1]["chosen_action"], "local")
        self.assertEqual(context_model.to_dict()["decision_history_size"], 1)
        model.record_transition({"slot": 1}, "local", -1.0, {"slot": 2}, False)
        self.assertEqual(len(model.sample_replay_batch(1)), 1)
        self.assertEqual(model.forecast_next_load([1.0, 3.0, 5.0]), 3.0)
        self.assertEqual(model.recover_delayed_load([4.0, 6.0]), 6.0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
