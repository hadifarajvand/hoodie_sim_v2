from __future__ import annotations

import unittest
from unittest.mock import patch

from src.evaluation.config import EvaluationConfig
from src.evaluation.fairness_checks import assert_fair_evaluation
from src.evaluation.metrics import TaskEvaluationRecord, evaluate_trace
from src.evaluation.runner import EvaluationRunner
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy
from src.policies.policy_interface import PolicyContext
from src.evaluation.trace_protocol import build_deterministic_trace
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment import gym_adapter as gym_adapter_module


class FixedActionPolicy:
    def __init__(self, action: str) -> None:
        self.action = action

    def choose_action(self, context: PolicyContext) -> str:
        self.last_context = context
        if self.action == "mask_aware":
            if context.legal_action_mask.get("vertical", False):
                return "vertical"
            if context.legal_action_mask.get("horizontal", False):
                return "horizontal"
            return "local"
        return self.action


class EvaluationRunnerTests(unittest.TestCase):
    def test_multiple_policies_share_the_same_runner(self) -> None:
        topology = TopologyGraph(
            node_ids=("1", "2", "3", "cloud"),
            legal_adjacency={
                "1": ("2", "cloud"),
                "2": ("1", "cloud"),
                "3": ("1", "cloud"),
            },
        )
        runner_a = EvaluationRunner(
            policy=FullLocalComputingPolicy(),
            config=EvaluationConfig(policy_name="FLC", seed=7, trace_id="trace-a", episode_count=1),
            topology=topology,
        )
        runner_b = EvaluationRunner(
            policy=HorizontalOffloadingPolicy(),
            config=EvaluationConfig(policy_name="HO", seed=7, trace_id="trace-a", episode_count=1),
            topology=topology,
        )

        result_a = runner_a.run()
        result_b = runner_b.run()

        self.assertEqual(result_a["metadata"]["trace_id"], "trace-a")
        self.assertEqual(result_b["metadata"]["trace_id"], "trace-a")
        self.assertIn("average_delay", result_a["aggregate"])
        self.assertIn("average_delay", result_b["aggregate"])

    def test_identical_seeds_produce_identical_results(self) -> None:
        config = EvaluationConfig(policy_name="FLC", seed=11, trace_id="same-trace", episode_count=2)
        runner_one = EvaluationRunner(policy=FixedActionPolicy("local"), config=config)
        runner_two = EvaluationRunner(policy=FixedActionPolicy("local"), config=config)

        self.assertEqual(runner_one.run(), runner_two.run())

    def test_different_seeds_produce_different_results(self) -> None:
        runner_one = EvaluationRunner(
            policy=FixedActionPolicy("local"),
            config=EvaluationConfig(policy_name="FLC", seed=13, trace_id="trace-x", episode_count=1),
        )
        runner_two = EvaluationRunner(
            policy=FixedActionPolicy("local"),
            config=EvaluationConfig(policy_name="FLC", seed=17, trace_id="trace-x", episode_count=1),
        )

        self.assertNotEqual(runner_one.run()["aggregate"], runner_two.run()["aggregate"])

    def test_metrics_are_computed_through_centralized_module_only(self) -> None:
        records = [
            TaskEvaluationRecord(1, 0, 1, "completed", "local", "self", 1),
            TaskEvaluationRecord(2, 1, None, "dropped", "local", "self", None),
        ]
        with (
            patch("src.evaluation.metrics.average_delay", return_value=9.5) as average_delay,
            patch("src.evaluation.metrics.drop_ratio", return_value=0.25) as drop_ratio,
            patch("src.evaluation.metrics.throughput", return_value=17) as throughput,
        ):
            trace_metrics = evaluate_trace(
                trace_id="trace-z",
                policy_name="FLC",
                seed=1,
                device="cpu",
                records=records,
            )

            self.assertEqual(trace_metrics.average_delay, 9.5)
            self.assertEqual(trace_metrics.drop_ratio, 0.25)
            self.assertEqual(trace_metrics.throughput, 17)
            self.assertEqual(average_delay.call_count, 1)
            self.assertEqual(drop_ratio.call_count, 1)
            self.assertEqual(throughput.call_count, 1)

    def test_runner_uses_shared_topology_derived_policy_inputs(self) -> None:
        topology = TopologyGraph(
            node_ids=("1", "2", "3", "cloud"),
            legal_adjacency={
                "1": ("cloud",),
                "2": ("cloud",),
                "3": ("cloud",),
            },
        )
        runner = EvaluationRunner(
            policy=FixedActionPolicy("mask_aware"),
            config=EvaluationConfig(
                policy_name="FLC",
                seed=5,
                trace_id="topology-trace",
                episode_count=1,
                episode_length=3,
            ),
            topology=topology,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
        )

        result = runner.run()

        self.assertEqual(
            runner.policy.last_context.legal_action_mask,
            {
                "local": True,
                "compute_local": True,
                "horizontal": False,
                "offload_horizontal": False,
                "vertical": True,
                "offload_vertical": True,
            },
        )
        self.assertIn("fallback_hints", runner.policy.last_context.observation)
        self.assertEqual(runner.policy.last_context.observation["topology"], ("cloud",))
        first_record = result["per_trace"][0]["raw_records"][0]
        self.assertEqual(first_record["resolved_destination"], "cloud")
        self.assertIn(first_record["terminal_outcome"], {"completed", "dropped"})
        if first_record["terminal_outcome"] == "completed":
            self.assertIsNotNone(first_record["delay"])

    def test_fairness_checks_reject_mismatched_evaluation_conditions(self) -> None:
        trace_a = build_deterministic_trace("fair-a", 21, 2)
        trace_b = build_deterministic_trace("fair-b", 21, 3)
        config_a = EvaluationConfig(policy_name="FLC", seed=21, trace_id="fair", episode_count=1, episode_length=2)
        config_b = EvaluationConfig(policy_name="FLC", seed=21, trace_id="fair", episode_count=1, episode_length=3)

        with self.assertRaises(ValueError):
            assert_fair_evaluation("FLC", "HO", trace_a, trace_b, config_a, config_b)

    def test_runner_does_not_force_reward_or_terminal_state_when_runtime_has_set_it(self) -> None:
        runner = EvaluationRunner(
            policy=FixedActionPolicy("local"),
            config=EvaluationConfig(policy_name="FLC", seed=9, trace_id="runtime-trace", episode_count=1, episode_length=3),
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
        )

        result = runner.run()
        record = result["per_trace"][0]["raw_records"][0]

        self.assertIn(record["terminal_outcome"], {"completed", "dropped"})
        if record["terminal_outcome"] == "completed":
            self.assertEqual(record["delay"], 1)
        else:
            self.assertIsNone(record["delay"])
        self.assertTrue(runner.policy.last_context.legal_action_mask["local"])
        self.assertEqual(record["resolved_destination"], "self")

    def test_runner_requires_topology_backed_destination_for_offload_actions(self) -> None:
        runner = EvaluationRunner(
            policy=FixedActionPolicy("horizontal"),
            config=EvaluationConfig(policy_name="HO", seed=3, trace_id="dest-trace", episode_count=1, episode_length=1),
        )

        with self.assertRaises(ValueError):
            runner.run()

    def test_runner_uses_shared_runtime_timing_path(self) -> None:
        topology = TopologyGraph(
            node_ids=("1", "2", "3", "cloud"),
            legal_adjacency={
                "1": ("cloud",),
                "2": ("cloud",),
                "3": ("cloud",),
            },
        )
        runner = EvaluationRunner(
            policy=FixedActionPolicy("vertical"),
            config=EvaluationConfig(policy_name="VO", seed=19, trace_id="runtime-path", episode_count=1, episode_length=3),
            topology=topology,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
        )

        with patch.object(gym_adapter_module, "advance_shared_runtime", wraps=gym_adapter_module.advance_shared_runtime) as shared_progress:
            runner.run()

        self.assertGreater(shared_progress.call_count, 0)


if __name__ == "__main__":
    unittest.main()
