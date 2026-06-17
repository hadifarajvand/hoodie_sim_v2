from __future__ import annotations

import unittest

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.replay_hash import build_euls_replay_payload, stable_replay_hash
from src.environment.lifecycle_trace import LifecycleTraceConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class EULSReplayDeterminismTests(unittest.TestCase):
    def _env(self) -> HoodieGymEnvironment:
        return HoodieGymEnvironment(
            episode_length=6,
            topology=TopologyGraph(node_ids=("1", "2", "cloud"), legal_adjacency={"1": ("2", "cloud")}),
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=1.0, cpu_capacity_per_slot_cloud=1.0),
            policy_name="FLC",
            trace_config=LifecycleTraceConfig(trace_enabled=True),
        )

    def _trace(self, *, seed: int, trace_id: str = "replay-trace") -> EvaluationTrace:
        return EvaluationTrace(
            trace_id=trace_id,
            seed=seed,
            tasks=(
                TraceTaskBlueprint(task_id=1, source_agent_id=1, arrival_slot=0, size=32.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5),
                TraceTaskBlueprint(task_id=2, source_agent_id=1, arrival_slot=0, size=32.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5),
                TraceTaskBlueprint(task_id=3, source_agent_id=1, arrival_slot=0, size=32.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": trace_id, "seed": str(seed)},
        )

    def _run_episode(self, env: HoodieGymEnvironment, *, seed: int) -> tuple[dict[str, object], str]:
        trace = self._trace(seed=seed)
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0], trace.tasks[1], trace.tasks[2]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        while True:
            current_task = env.current_task
            if current_task is None:
                action = None
            elif current_task.task_id == 1:
                action = "local"
            elif current_task.task_id == 2:
                action = "horizontal"
            else:
                action = "vertical"
            _obs, _reward, terminated, truncated, _info = env.step(action)
            if terminated or truncated:
                break

        payload = build_euls_replay_payload(env)
        return payload, stable_replay_hash(payload)

    def test_same_seed_same_trace_same_policy_produces_same_payload_and_hash(self) -> None:
        env_a = self._env()
        env_b = self._env()

        payload_a, hash_a = self._run_episode(env_a, seed=17)
        payload_b, hash_b = self._run_episode(env_b, seed=17)

        self.assertEqual(payload_a, payload_b)
        self.assertEqual(hash_a, hash_b)

    def test_different_seed_or_trace_changes_hash(self) -> None:
        env_a = self._env()
        env_b = self._env()

        payload_a, hash_a = self._run_episode(env_a, seed=17)
        payload_b, hash_b = self._run_episode(env_b, seed=23)

        self.assertNotEqual(payload_a["trace"], payload_b["trace"])
        self.assertNotEqual(hash_a, hash_b)

    def test_hash_excludes_volatile_fields(self) -> None:
        env = self._env()
        payload, hash_value = self._run_episode(env, seed=19)
        noisy = dict(payload)
        noisy["timestamp"] = "2026-06-17T12:00:00Z"
        noisy["cwd"] = "/tmp/volatile/workdir"
        noisy["queue_state_snapshot"] = dict(noisy["queue_state_snapshot"])  # type: ignore[assignment]
        noisy["queue_state_snapshot"]["absolute_path"] = "/private/tmp/volatile"
        noisy["lifecycle_trace_events"] = [dict(event, timestamp="volatile") if isinstance(event, dict) else event for event in noisy["lifecycle_trace_events"]]

        self.assertEqual(hash_value, stable_replay_hash(noisy))

    def test_queue_state_progression_and_terminal_metrics_are_captured(self) -> None:
        env = self._env()
        payload, _hash_value = self._run_episode(env, seed=31)

        self.assertIn("private", payload["queue_state_snapshot"])
        self.assertIn("offloading", payload["queue_state_snapshot"])
        self.assertIn("public", payload["queue_state_snapshot"])
        self.assertGreaterEqual(len(payload["history"]), 1)
        self.assertGreaterEqual(int(payload["metrics"]["completed"]), 1)
        self.assertIn("reward", payload["metrics"])
        self.assertTrue(payload["trace"]["tasks"])

    def test_repeated_runs_keep_terminal_outcomes_and_metrics_stable(self) -> None:
        env_a = self._env()
        env_b = self._env()

        payload_a, _hash_a = self._run_episode(env_a, seed=41)
        payload_b, _hash_b = self._run_episode(env_b, seed=41)

        self.assertEqual(payload_a["metrics"], payload_b["metrics"])
        self.assertEqual(payload_a["history"], payload_b["history"])
        self.assertEqual(payload_a["finalized_task_count"], payload_b["finalized_task_count"])
        self.assertEqual(payload_a["queue_state_snapshot"], payload_b["queue_state_snapshot"])


if __name__ == "__main__":
    unittest.main()
