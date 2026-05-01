from __future__ import annotations

import unittest

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint
from src.policies.flc import FullLocalComputingPolicy
from src.policies.policy_interface import PolicyContext


class GymEnvironmentTests(unittest.TestCase):
    def _env(self, *, topology: TopologyGraph | None = None, runtime_parameters: SharedRuntimeParameters | None = None) -> HoodieGymEnvironment:
        return HoodieGymEnvironment(
            episode_length=5,
            topology=topology,
            runtime_parameters=runtime_parameters or SharedRuntimeParameters(),
            policy_name="FLC",
        )

    def _single_task_trace(self, *, task_id: int = 1, timeout_length: int = 2, absolute_deadline_slot: int | None = None) -> EvaluationTrace:
        deadline = timeout_length if absolute_deadline_slot is None else absolute_deadline_slot
        return EvaluationTrace(
            trace_id=f"single-task-{task_id}",
            seed=task_id,
            tasks=(
                TraceTaskBlueprint(
                    task_id=task_id,
                    source_agent_id=1,
                    arrival_slot=0,
                    size=32.0,
                    processing_density=1.0,
                    timeout_length=timeout_length,
                    absolute_deadline_slot=deadline,
                ),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": f"single-task-{task_id}", "seed": str(task_id)},
        )

    def _run_policy_episode(self, env: HoodieGymEnvironment, policy: object, seed: int) -> list[tuple]:
        observation, _info = env.reset(seed=seed)
        sequence: list[tuple] = []
        while True:
            current_task = env.current_task
            if current_task is None:
                action = None
            else:
                action = policy.choose_action(
                    PolicyContext(
                        observation=observation if current_task is None else env.observe_flat(current_task),
                        legal_action_mask=env.legal_action_mask(current_task),
                        trace_history=(env.trace.trace_id if env.trace is not None else "",),
                    )
                )
            observation, reward, terminated, truncated, info = env.step(action)
            finalized = tuple((task["task_id"], task["terminal_outcome"]) for task in info["finalized_tasks"])
            sequence.append((reward, terminated, truncated, finalized, info["slot"]))
            if terminated or truncated:
                return sequence

    def test_reset_seed_is_deterministic(self) -> None:
        env_a = self._env()
        env_b = self._env()

        obs_a, info_a = env_a.reset(seed=13)
        obs_b, info_b = env_b.reset(seed=13)

        self.assertEqual(obs_a, obs_b)
        self.assertEqual(info_a["trace_id"], info_b["trace_id"])
        self.assertEqual(env_a.trace.tasks[0], env_b.trace.tasks[0])

    def test_same_seed_same_policy_produces_same_trace_reward_and_outcome_sequence(self) -> None:
        env_a = self._env(runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"))
        env_b = self._env(runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"))
        policy_a = FullLocalComputingPolicy()
        policy_b = FullLocalComputingPolicy()

        sequence_a = self._run_policy_episode(env_a, policy_a, seed=23)
        sequence_b = self._run_policy_episode(env_b, policy_b, seed=23)

        self.assertEqual(sequence_a, sequence_b)

    def test_single_slot_step_returns_rl_tuple(self) -> None:
        env = self._env(runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"))
        observation, info = env.reset(seed=7)

        self.assertEqual(list(observation.keys()), ["1"])
        self.assertIn("legal_action_mask", observation["1"])
        next_obs, reward, terminated, truncated, step_info = env.step("local")

        self.assertIsInstance(next_obs, dict)
        self.assertIsInstance(reward, float)
        self.assertFalse(truncated)
        self.assertIsInstance(terminated, bool)
        self.assertIn("metrics", step_info)
        self.assertIn("queue_load", step_info)
        self.assertIn("truncated", step_info)
        self.assertGreaterEqual(step_info["slot"], 0)
        self.assertGreaterEqual(len(step_info["finalized_tasks"]), 0)
        self.assertEqual(env.observe_flat()["legal_action_mask"]["local"], True)

    def test_truncation_at_slot_horizon(self) -> None:
        env = HoodieGymEnvironment(
            episode_length=1,
            topology=None,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            policy_name="FLC",
        )
        env.reset(seed=3)
        _obs, _reward, terminated, truncated, info = env.step("local")

        self.assertFalse(terminated)
        self.assertTrue(truncated)
        self.assertTrue(info["truncated"])
        self.assertFalse(info["terminated"])

    def test_semantic_completion_sets_terminated_and_not_truncated(self) -> None:
        env = self._env(runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"))
        env.trace = self._single_task_trace(task_id=17, timeout_length=5, absolute_deadline_slot=5)
        env._pending_arrivals = {0: [env.trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()
        _obs, _reward0, terminated0, truncated0, _info0 = env.step("local")
        _obs, _reward1, terminated1, truncated1, info1 = env.step(None)

        self.assertFalse(terminated0)
        self.assertFalse(truncated0)
        self.assertTrue(terminated1)
        self.assertFalse(truncated1)
        self.assertFalse(info1["truncated"])
        self.assertTrue(info1["terminated"])

    def test_action_legality_under_topology(self) -> None:
        topology = TopologyGraph(node_ids=("1", "2", "cloud"), legal_adjacency={"1": ("2", "cloud")})
        env = self._env(topology=topology)
        obs, _info = env.reset(seed=4)

        self.assertIn("1", obs)
        self.assertTrue(obs["1"]["legal_action_mask"]["local"])
        self.assertTrue(obs["1"]["legal_action_mask"]["horizontal"])
        self.assertTrue(obs["1"]["legal_action_mask"]["vertical"])

    def test_illegal_actions_are_rejected_without_remapping(self) -> None:
        horizontal_only = TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)})
        vertical_only = TopologyGraph(node_ids=("1", "cloud"), legal_adjacency={"1": ("cloud",)})

        env_horizontal = self._env(topology=horizontal_only)
        env_horizontal.reset(seed=8)
        with self.assertRaises(ValueError):
            env_horizontal.step("vertical")

        env_vertical = self._env(topology=vertical_only)
        env_vertical.reset(seed=9)
        with self.assertRaises(ValueError):
            env_vertical.step("horizontal")

    def test_local_queue_admission(self) -> None:
        env = self._env(runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"))
        env.reset(seed=5)
        _obs, _reward, _terminated, _truncated, info = env.step("local")

        self.assertEqual(info["queue_load"], 1)
        self.assertEqual(len(env._private_queues["1"].tasks), 1)
        self.assertEqual(env._private_queues["1"].tasks[0].queue_state, "private_queue")

    def test_horizontal_offload_path(self) -> None:
        topology = TopologyGraph(node_ids=("1", "2", "cloud"), legal_adjacency={"1": ("2", "cloud")})
        env = self._env(topology=topology)
        env.reset(seed=6)
        _obs, _reward, _terminated, _truncated, info = env.step("horizontal")

        self.assertEqual(len(env._offloading_queues[("1", "2")].tasks), 1)
        self.assertEqual(env._offloading_queues[("1", "2")].tasks[0].queue_state, "offloading_queue")
        self.assertEqual(info["queue_load"], 1)

    def test_vertical_cloud_offload_path(self) -> None:
        topology = TopologyGraph(node_ids=("1", "cloud"), legal_adjacency={"1": ("cloud",)})
        env = self._env(topology=topology)
        env.reset(seed=9)
        _obs, _reward, _terminated, _truncated, info = env.step("vertical")

        self.assertEqual(len(env._offloading_queues[("1", "cloud")].tasks), 1)
        self.assertEqual(env._offloading_queues[("1", "cloud")].tasks[0].queue_state, "offloading_queue")
        self.assertEqual(info["queue_load"], 1)

    def test_public_queue_admission_after_offload(self) -> None:
        topology = TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)})
        env = self._env(topology=topology)
        env.trace = self._single_task_trace(task_id=11)
        env._pending_arrivals = {0: [env.trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()
        env.step("horizontal")
        env.step(None)

        self.assertIn(("2", "1"), env._public_queues)
        self.assertEqual(len(env._public_queues[("2", "1")].tasks), 1)
        self.assertEqual(env._public_queues[("2", "1")].tasks[0].queue_state, "public_queue")

    def test_same_slot_arrivals_are_not_stranded(self) -> None:
        env = self._env(runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"))
        trace = EvaluationTrace(
            trace_id="multi-arrival",
            seed=99,
            tasks=(
                TraceTaskBlueprint(task_id=1, source_agent_id=1, arrival_slot=0, size=16.0, processing_density=1.0, timeout_length=4, absolute_deadline_slot=4),
                TraceTaskBlueprint(task_id=2, source_agent_id=1, arrival_slot=0, size=20.0, processing_density=1.0, timeout_length=4, absolute_deadline_slot=4),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": "multi-arrival", "seed": "99"},
        )
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0], trace.tasks[1]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        self.assertEqual(env.current_task.task_id, 1)
        env.step("local")
        self.assertIsNotNone(env.current_task)
        self.assertEqual(env.current_task.task_id, 2)

    def test_delayed_reward_after_completion(self) -> None:
        env = self._env(runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"))
        env.trace = self._single_task_trace(task_id=17, timeout_length=5, absolute_deadline_slot=5)
        env._pending_arrivals = {0: [env.trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()
        _obs, reward0, terminated0, _truncated0, info0 = env.step("local")
        _obs, reward1, terminated1, _truncated1, info1 = env.step(None)

        self.assertEqual(reward0, 0.0)
        self.assertLess(reward1, 0.0)
        self.assertTrue(any(task["terminal_outcome"] == "completed" for task in info1["finalized_tasks"]))
        self.assertTrue(terminated1)

    def test_delayed_reward_after_drop(self) -> None:
        env = self._env(runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"))
        custom_trace = self._single_task_trace(task_id=1, timeout_length=0, absolute_deadline_slot=0)
        env.trace = custom_trace
        env._pending_arrivals = {0: [custom_trace.tasks[0]]}  # type: ignore[assignment]
        env._current_task = env._load_current_task()
        env.current_slot = 0
        _obs, reward0, _terminated0, _truncated0, _info0 = env.step("local")
        _obs, reward1, _terminated1, _truncated1, info1 = env.step("local")

        self.assertEqual(reward0, 0.0)
        self.assertLess(reward1, 0.0)
        self.assertTrue(any(task["terminal_outcome"] == "dropped" for task in info1["finalized_tasks"]))

    def test_fractional_paper_values_survive_runtime_observation(self) -> None:
        from src.environment.traffic_config import TrafficConfig
        from src.environment.traffic_generator import TrafficGenerator

        config = TrafficConfig(
            scenario_name="paper_default",
            number_of_agents=1,
            episode_length=1,
            arrival_probability=1.0,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.0,
            task_size_mbits_max=2.1,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )
        trace = TrafficGenerator.generate(config, seed=1)
        self.assertEqual(trace.records[0].size, 2.1)
        self.assertEqual(trace.records[0].processing_density, 0.297)

        env = HoodieGymEnvironment(
            episode_length=config.episode_length,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            trace_source=None,
            policy_name="FLC",
        )
        env.trace = trace.evaluation_trace
        env._pending_arrivals = {0: [trace.records[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        self.assertEqual(env.current_task.size, 2.1)
        self.assertEqual(env.current_task.processing_density, 0.297)

    def test_full_episode_with_flc_policy(self) -> None:
        env = self._env(runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"))
        policy = FullLocalComputingPolicy()
        env.trace = self._single_task_trace(task_id=19, timeout_length=5, absolute_deadline_slot=5)
        env._pending_arrivals = {0: [env.trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()
        observation = env.observe_flat()
        terminated = False
        steps = 0
        while not terminated and steps < 20:
            current_task = env.current_task
            if current_task is None:
                action = None
            else:
                action = policy.choose_action(
                    PolicyContext(
                        observation=observation,
                        legal_action_mask=observation["legal_action_mask"],
                        trace_history=("trace-19",),
                    )
                )
            observation, _reward, terminated, _truncated, _info = env.step(action)
            if env.current_task is not None:
                observation = env.observe_flat()
            steps += 1

        self.assertTrue(terminated)
        self.assertGreater(steps, 0)

    def test_metric_update_consistency(self) -> None:
        env = self._env(runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"))
        env.trace = self._single_task_trace(task_id=21, timeout_length=5, absolute_deadline_slot=5)
        env._pending_arrivals = {0: [env.trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()
        _obs, _reward, _terminated, _truncated, info0 = env.step("local")
        _obs, _reward, terminated, _truncated, info1 = env.step(None)

        metrics = info1["metrics"]
        finalized = info0["finalized_tasks"] + info1["finalized_tasks"]
        self.assertEqual(metrics["completed"] + metrics["dropped"], float(len(finalized)))
        self.assertTrue(terminated)


if __name__ == "__main__":
    unittest.main()
