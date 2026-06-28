from __future__ import annotations

import unittest
from typing import Dict, List

from src.agents.hoodie_agent import HoodieAgent
from src.agents.multi_agent_pool import MultiAgentHoodiePool
from src.evaluation.multi_agent_runner import MultiAgentEvaluationRunner
from src.policies.policy_interface import PolicyContext
from src.environment.topology import TopologyGraph


class MultiAgentEvaluationRunnerTests(unittest.TestCase):
    """Test multi-agent evaluation runner functionality."""
    
    def test_multi_agent_evaluation_runner_exists(self) -> None:
        """Should be able to import MultiAgentEvaluationRunner."""
        from src.evaluation.multi_agent_runner import MultiAgentEvaluationRunner
        self.assertIsNotNone(MultiAgentEvaluationRunner)
    
    def test_can_create_evaluation_runner_with_agent_pool(self) -> None:
        """Should be able to create evaluation runner with agent pool."""
        from src.evaluation.multi_agent_runner import MultiAgentEvaluationRunner
        from src.evaluation.config import EvaluationConfig
        
        agent_ids = ["1", "2"]
        pool = MultiAgentHoodiePool(agent_ids)
        config = EvaluationConfig(
            policy_name="HOODIE",
            seed=42,
            trace_id="test-trace",
            episode_count=1,
            episode_length=2,
        )
        
        runner = MultiAgentEvaluationRunner(
            agent_pool=pool,
            config=config,
        )
        
        self.assertIsNotNone(runner)
        self.assertEqual(runner.agent_pool, pool)
        self.assertEqual(runner.config, config)
    
    def test_evaluation_runner_uses_topology_and_runtime_params(self) -> None:
        """Should store topology and runtime parameters correctly."""
        from src.evaluation.multi_agent_runner import MultiAgentEvaluationRunner
        from src.evaluation.config import EvaluationConfig
        
        agent_ids = ["1"]
        pool = MultiAgentHoodiePool(agent_ids)
        config = EvaluationConfig(
            policy_name="HOODIE",
            seed=42,
            trace_id="test-trace",
            episode_count=1,
            episode_length=2,
        )
        
        # Mock topology and runtime params
        topology = TopologyGraph.from_approved_assumption_registry(
            "resources/papers/hoodie/recovered/user-approved-assumption-registry.json"
        )
        from src.environment.runtime_model import SharedRuntimeParameters
        runtime_params = SharedRuntimeParameters()
        
        runner = MultiAgentEvaluationRunner(
            agent_pool=pool,
            config=config,
            topology=topology,
            runtime_parameters=runtime_params,
        )
        
        self.assertEqual(runner.topology, topology)
        self.assertEqual(runner.runtime_parameters, runtime_params)


if __name__ == "__main__":
    unittest.main()