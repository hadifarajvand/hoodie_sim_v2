from __future__ import annotations

from dataclasses import replace
import unittest
from unittest import mock

from src.agents.hoodie_agent import HoodieAgent
from src.config.config_freeze import FrozenConfig, FrozenConfigError
from src.evaluation.comparison_runner import ComparisonRunner
from src.evaluation.config import EvaluationConfig
from src.evaluation.runner import EvaluationRunner
from src.evaluation.validation_artifacts import build_validation_artifacts
import src.evaluation.validation_runner as validation_runner_module
from src.evaluation.validation_runner import ValidationRunner
from src.environment.topology import TopologyGraph
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy


class ValidationPipelineTests(unittest.TestCase):
    def _topology(self) -> TopologyGraph:
        return TopologyGraph(
            node_ids=("1", "2", "cloud"),
            legal_adjacency={
                "1": ("2", "cloud"),
                "2": ("1", "cloud"),
            },
        )

    def _config(self) -> EvaluationConfig:
        return EvaluationConfig(policy_name="validation", seed=41, trace_id="val", episode_count=2, episode_length=2)

    def test_identical_traces_are_used_across_policies(self) -> None:
        runner = ValidationRunner(
            policies={"FLC": FullLocalComputingPolicy(), "HO": HorizontalOffloadingPolicy()},
            config=self._config(),
            topology=self._topology(),
        )

        result = runner.run()
        self.assertEqual(result.policy_results[0].trace_results["metadata"]["trace_id"], "val")
        self.assertEqual(result.policy_results[1].trace_results["metadata"]["trace_id"], "val")
        self.assertEqual(result.policy_results[0].trace_results["metadata"]["seed"], 41)
        self.assertEqual(result.policy_results[1].trace_results["metadata"]["seed"], 41)

    def test_fairness_enforcement_rejects_mismatched_config_or_seed(self) -> None:
        runner = ValidationRunner(
            policies={"FLC": FullLocalComputingPolicy(), "HO": HorizontalOffloadingPolicy()},
            config=self._config(),
            topology=self._topology(),
        )
        original = validation_runner_module.ValidationRunner._trace_for_policy

        def mismatched_trace(self, policy_name: str, episode_index: int):
            trace = original(self, policy_name, episode_index)
            if policy_name == "HO":
                return trace.__class__(
                    trace_id=f"{trace.trace_id}-mismatch",
                    seed=trace.seed + 1,
                    tasks=trace.tasks,
                    metadata=trace.metadata,
                )
            return trace

        with mock.patch.object(validation_runner_module.ValidationRunner, "_trace_for_policy", new=mismatched_trace):
            with self.assertRaises(ValueError):
                runner.run()

    def test_metrics_match_evaluation_runner_outputs_exactly(self) -> None:
        topology = self._topology()
        config = self._config()
        validation = ValidationRunner(
            policies={"FLC": FullLocalComputingPolicy(), "HO": HorizontalOffloadingPolicy()},
            config=config,
            topology=topology,
        ).run()

        comparison = ComparisonRunner(validation).run()
        self.assertEqual(comparison["baseline_policy_name"], "FLC")
        self.assertEqual(comparison["policy_order"], ("FLC", "HO"))

        expected = EvaluationRunner(
            policy=FullLocalComputingPolicy(),
            config=replace(config, policy_name="FLC"),
            topology=topology,
        ).run()
        self.assertEqual(validation.policy_results[0].trace_results, expected)

    def test_validation_does_not_alter_metrics(self) -> None:
        topology = self._topology()
        config = self._config()
        validation = ValidationRunner(
            policies={"FLC": FullLocalComputingPolicy(), "HO": HorizontalOffloadingPolicy()},
            config=config,
            topology=topology,
        ).run()
        artifacts = build_validation_artifacts(validation)

        self.assertEqual(artifacts.validation.policy_results[0].trace_results["aggregate"], validation.policy_results[0].trace_results["aggregate"])
        serialized = artifacts.to_dict()
        self.assertEqual(serialized["baseline_policy_name"], "FLC")
        self.assertEqual(serialized["policy_results"]["baseline"]["policy_name"], "FLC")
        self.assertEqual(serialized["policy_results"]["compared_policies"][0]["policy_name"], "HO")
        self.assertEqual(serialized["comparison"]["comparisons"][0]["aggregate"], validation.policy_results[1].trace_results["aggregate"])
        self.assertIn("evaluation_config_snapshot", serialized)
        self.assertIn("evaluation_config_hash", serialized)

    def test_each_policy_records_its_actual_policy_name(self) -> None:
        topology = self._topology()
        config = self._config()
        validation = ValidationRunner(
            policies={"FLC": FullLocalComputingPolicy(), "HO": HorizontalOffloadingPolicy()},
            config=config,
            topology=topology,
        ).run()

        for policy_result in validation.policy_results:
            trace_results = policy_result.trace_results
            for per_trace in trace_results["per_trace"]:
                self.assertEqual(per_trace["policy_name"], policy_result.policy_name)
                self.assertEqual(per_trace["metadata"]["policy_name"], policy_result.policy_name)

    def test_config_immutability_after_freeze(self) -> None:
        config = self._config()
        frozen = FrozenConfig(config)
        config.seed = 99

        with self.assertRaises(FrozenConfigError):
            frozen.ensure_unchanged()


if __name__ == "__main__":
    unittest.main()
