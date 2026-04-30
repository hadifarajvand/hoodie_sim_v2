from __future__ import annotations

import unittest

from src.agents.hoodie_agent import HoodieAgent
from src.policies.flc import FullLocalComputingPolicy
from src.evaluation.config import EvaluationConfig
from src.evaluation.runner import EvaluationRunner
from src.environment.topology import TopologyGraph


class HoodiePlaceholderIntegrationTests(unittest.TestCase):
    def test_hoodie_agent_runs_through_shared_environment(self) -> None:
        topology = TopologyGraph(
            node_ids=("1", "2", "cloud"),
            legal_adjacency={
                "1": ("2", "cloud"),
                "2": ("1", "cloud"),
            },
        )
        runner = EvaluationRunner(
            policy=HoodieAgent(),
            config=EvaluationConfig(policy_name="HOODIE", seed=23, trace_id="hoodie", episode_count=1, episode_length=1),
            topology=topology,
        )

        result = runner.run()

        self.assertEqual(result["metadata"]["policy_name"], "HOODIE")
        self.assertEqual(len(result["per_trace"]), 1)
        self.assertIn("average_delay", result["aggregate"])

    def test_hoodie_differs_from_flc_on_mixed_legal_actions(self) -> None:
        topology = TopologyGraph(
            node_ids=("1", "2", "cloud"),
            legal_adjacency={
                "1": ("2", "cloud"),
                "2": ("1", "cloud"),
            },
        )
        config = EvaluationConfig(policy_name="HOODIE", seed=23, trace_id="hoodie", episode_count=1, episode_length=2)
        hoodie_result = EvaluationRunner(policy=HoodieAgent(), config=config, topology=topology).run()
        flc_result = EvaluationRunner(policy=FullLocalComputingPolicy(), config=config, topology=topology).run()

        hoodie_actions = [record["selected_action"] for record in hoodie_result["per_trace"][0]["raw_records"]]
        flc_actions = [record["selected_action"] for record in flc_result["per_trace"][0]["raw_records"]]

        self.assertNotEqual(hoodie_actions, flc_actions)
        self.assertTrue(any(action != "local" for action in hoodie_actions))


if __name__ == "__main__":
    unittest.main()
