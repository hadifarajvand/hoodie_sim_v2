from __future__ import annotations

import random
import unittest

from src.agents.hoodie_agent import HoodieAgent
from src.config.training_config import TrainingConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.task import Task
from src.environment.topology import TopologyGraph
from src.evaluation.config import EvaluationConfig
from src.evaluation.runner import EvaluationRunner
from src.training.delayed_reward_training import DelayedRewardTraining
from src.training.seed_management import SeedManagement
from src.training.training_loop import TrainingLoop


class _StubModel:
    def forward(self, history, legal_actions):
        return {action: float(index) for index, action in enumerate(legal_actions)}


class TrainingLoopIntegrationTests(unittest.TestCase):
    def _topology(self) -> TopologyGraph:
        return TopologyGraph(
            node_ids=("1", "2", "cloud"),
            legal_adjacency={
                "1": ("2", "cloud"),
                "2": ("1", "cloud"),
            },
        )

    def _eval_config(self) -> EvaluationConfig:
        return EvaluationConfig(
            policy_name="HOODIE",
            seed=31,
            trace_id="training",
            episode_count=2,
            episode_length=2,
        )

    def _training_config(self) -> TrainingConfig:
        return TrainingConfig(
            learning_rate=0.01,
            batch_size=4,
            replay_buffer_capacity=3,
            target_network_update_frequency=1,
            episode_count=2,
            episode_length=2,
            seed_management=SeedManagement(training_seed=17, evaluation_seed=31),
            policy_name="HOODIE",
            trace_id="training",
            trace_mode="deterministic_seed",
            device="cpu",
        )

    def test_training_loop_runs_multiple_episodes_without_modifying_evaluation_behavior(self) -> None:
        topology = self._topology()
        evaluation_config = self._eval_config()

        baseline_runner = EvaluationRunner(policy=HoodieAgent(), config=evaluation_config, topology=topology)
        baseline_result = baseline_runner.run()

        trained_agent = HoodieAgent()
        trained_agent.model = _StubModel()
        loop = TrainingLoop(policy=trained_agent, config=self._training_config(), topology=topology)
        loop.run()

        post_training_runner = EvaluationRunner(policy=HoodieAgent(), config=evaluation_config, topology=topology)
        post_training_result = post_training_runner.run()

        self.assertEqual(baseline_result, post_training_result)
        self.assertEqual(len(loop.logger.entries), 2)

    def test_transitions_are_recorded_in_replay_buffer(self) -> None:
        topology = self._topology()
        agent = HoodieAgent()
        agent.model = _StubModel()

        loop = TrainingLoop(policy=agent, config=self._training_config(), topology=topology)
        summaries = loop.run()

        self.assertEqual(len(agent.replay_buffer), 3)
        self.assertEqual([summary.transitions_recorded for summary in summaries], [2, 2])
        self.assertLessEqual(agent.replay_buffer.capacity, 3)
        self.assertTrue(all(transition.delta_slots >= 1 for transition in agent.replay_buffer._items))

    def test_delayed_rewards_are_respected(self) -> None:
        handler = DelayedRewardTraining()
        task = Task(
            task_id=1,
            source_agent_id=1,
            arrival_slot=0,
            size=10,
            processing_density=1,
            timeout_length=2,
            absolute_deadline_slot=2,
        )

        handler.stage_transition(
            task=task,
            state={"slot": 0},
            action="local",
            next_state={"slot": 1},
            done=False,
        )

        self.assertIsNone(handler.consume_ready_transition(task))
        task.terminal_outcome = "completed"
        task.completion_slot = 1
        task.reward_emitted = True
        ready = handler.consume_ready_transition(task)

        self.assertIsNotNone(ready)
        self.assertEqual(ready.reward, -1.0)
        self.assertEqual(ready.state, {"slot": 0})
        self.assertEqual(ready.next_state, {"slot": 1})

    def test_reward_matches_documented_recovered_behavior(self) -> None:
        handler = DelayedRewardTraining()
        completed = Task(
            task_id=2,
            source_agent_id=1,
            arrival_slot=0,
            size=10,
            processing_density=1,
            timeout_length=2,
            absolute_deadline_slot=2,
            completion_slot=3,
            terminal_outcome="completed",
            reward_emitted=True,
        )
        dropped = Task(
            task_id=3,
            source_agent_id=1,
            arrival_slot=0,
            size=10,
            processing_density=1,
            timeout_length=2,
            absolute_deadline_slot=2,
            terminal_outcome="dropped",
            reward_emitted=True,
        )

        self.assertEqual(handler.reward_for_task(completed), -3.0)
        self.assertEqual(handler.reward_for_task(dropped), -40.0)

    def test_deterministic_training_updates_produce_identical_model_parameters(self) -> None:
        topology = self._topology()
        config = self._training_config()

        first_agent = HoodieAgent()
        second_agent = HoodieAgent()

        TrainingLoop(policy=first_agent, config=config, topology=topology).run()
        TrainingLoop(policy=second_agent, config=config, topology=topology).run()

        self.assertEqual(first_agent.model.learned_action_preferences, second_agent.model.learned_action_preferences)
        self.assertEqual(first_agent.target_network.parameters, second_agent.target_network.parameters)

    def test_trained_agent_state_changes_evaluation_action_distribution(self) -> None:
        topology = self._topology()
        config = self._training_config()

        trained_agent = HoodieAgent()
        TrainingLoop(policy=trained_agent, config=config, topology=topology).run()

        trained_result = EvaluationRunner(
            policy=trained_agent,
            config=self._eval_config(),
            topology=topology,
        ).run()
        untrained_result = EvaluationRunner(
            policy=HoodieAgent(),
            config=self._eval_config(),
            topology=topology,
        ).run()

        trained_actions = [record["selected_action"] for record in trained_result["per_trace"][0]["raw_records"]]
        untrained_actions = [record["selected_action"] for record in untrained_result["per_trace"][0]["raw_records"]]

        self.assertNotEqual(trained_actions, untrained_actions)
        self.assertTrue(all(action in {"local", "horizontal", "vertical", "compute_local", "offload_horizontal", "offload_vertical"} for action in trained_actions))
        self.assertTrue(any(action != "vertical" for action in trained_actions))

    def test_config_values_are_loaded_and_used(self) -> None:
        topology = self._topology()
        agent = HoodieAgent()
        agent.model = _StubModel()
        config = self._training_config()
        loop = TrainingLoop(policy=agent, config=config, topology=topology)

        self.assertEqual(agent.replay_buffer.capacity, config.replay_buffer_capacity)
        self.assertEqual(loop.config.learning_rate, 0.01)
        self.assertEqual(loop.config.batch_size, 4)
        self.assertEqual(loop.config.target_network_update_frequency, 1)
        self.assertEqual(loop.config.seed_management.training_seed, 17)
        self.assertEqual(loop.config.seed_management.evaluation_seed, 31)

        loop.run()
        snapshot = loop.logger.snapshot()
        self.assertEqual(snapshot["entries"][0]["episode_index"], 0)
        self.assertEqual(snapshot["context"]["config"]["learning_rate"], 0.01)
        self.assertEqual(snapshot["context"]["seeds"]["training_seed"], 17)
        self.assertNotIn("average_delay", snapshot["context"])
        self.assertNotIn("drop_ratio", snapshot["context"])

    def test_evaluation_runner_uses_runtime_compute_capacities(self) -> None:
        topology = self._topology()
        runtime = SharedRuntimeParameters(
            local_service_capacity=0.25,
            public_service_capacity=0.75,
            cloud_service_capacity=1.5,
        )
        runner = EvaluationRunner(
            policy=HoodieAgent(),
            config=self._eval_config(),
            topology=topology,
            runtime_parameters=runtime,
        )

        trace = runner._trace_for_episode(0)
        metrics = runner._evaluate_episode(trace)

        self.assertEqual(metrics.policy_name, "HOODIE")
        self.assertEqual(runtime.to_compute_config().cpu_capacity_per_slot_agent, 0.25)
        self.assertEqual(runtime.to_compute_config().cpu_capacity_per_slot_edge, 0.75)
        self.assertEqual(runtime.to_compute_config().cpu_capacity_per_slot_cloud, 1.5)

    def test_training_loop_applies_replay_seed_from_config(self) -> None:
        topology = self._topology()
        config = self._training_config()
        config.replay_seed = 99
        agent = HoodieAgent()
        agent.model = _StubModel()

        TrainingLoop(policy=agent, config=config, topology=topology)

        expected_sample = random.Random(99).sample(range(5), 2)
        actual_sample = agent.replay_buffer._rng.sample(range(5), 2)
        self.assertEqual(agent.replay_buffer.seed, 99)
        self.assertEqual(actual_sample, expected_sample)


if __name__ == "__main__":
    unittest.main()
