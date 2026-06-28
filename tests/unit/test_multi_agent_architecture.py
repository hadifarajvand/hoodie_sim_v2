from __future__ import annotations

import unittest
from typing import Dict, List

from src.agents.hoodie_agent import HoodieAgent
from src.policies.policy_interface import PolicyContext


class MultiAgentArchitectureTests(unittest.TestCase):
    """Test multi-agent HOODIE architecture implementation."""
    
    def test_multi_agent_hoodie_pool_exists(self) -> None:
        """Should be able to import MultiAgentHoodiePool from src.agents."""
        # This should fail initially because we haven't implemented it yet
        from src.agents.multi_agent_pool import MultiAgentHoodiePool
        self.assertIsNotNone(MultiAgentHoodiePool)
    
    def test_create_20_independent_agents(self) -> None:
        """Should create exactly 20 independent agents for 20 edge agents."""
        from src.agents.multi_agent_pool import MultiAgentHoodiePool
        
        agent_ids = [str(i) for i in range(1, 21)]
        pool = MultiAgentHoodiePool(agent_ids)
        
        # Should have 20 agents
        self.assertEqual(len(pool.agents), 20)
        
        # Each agent should be independent (different instances)
        agent_list = list(pool.agents.values())
        for i in range(len(agent_list)):
            for j in range(i + 1, len(agent_list)):
                self.assertIsNot(agent_list[i], agent_list[j])
    
    def test_agents_act_independently_on_local_observations(self) -> None:
        """Each agent should make decisions based only on its own observation."""
        from src.agents.multi_agent_pool import MultiAgentHoodiePool
        
        agent_ids = [str(i) for i in range(1, 6)]  # Test with 5 agents for speed
        pool = MultiAgentHoodiePool(agent_ids)
        
        # Create different contexts for each agent
        contexts = {}
        for agent_id in agent_ids:
            contexts[agent_id] = PolicyContext(
                observation={
                    "slot": int(agent_id),  # Different slot for each agent
                    "topology": ("2", "cloud"),  # Same topology
                    "fallback_hints": {"local": 1, "horizontal": 2},  # Same hints
                },
                legal_action_mask={"local": True, "horizontal": True},
                trace_history=(),
            )
        
        # Get actions from all agents
        actions = pool.choose_actions(contexts)
        
        # Each agent should have made a decision
        self.assertEqual(len(actions), 5)
        for agent_id in agent_ids:
            self.assertIn(agent_id, actions)
            self.assertIn(actions[agent_id], ["local", "horizontal"])
    
    def test_agents_learn_independently(self) -> None:
        """Each agent should learn from their own experiences independently."""
        from src.agents.multi_agent_pool import MultiAgentHoodiePool
        
        agent_ids = ["1", "2"]
        pool = MultiAgentHoodiePool(agent_ids)
        
        # Give different experiences to each agent
        transitions = {
            "1": (
                {"slot": 0},  # state
                "local",      # action
                10.0,         # reward (positive)
                {"slot": 1},  # next_state
                False         # done
            ),
            "2": (
                {"slot": 0},  # state
                "local",      # action
                -10.0,        # reward (negative)
                {"slot": 1},  # next_state
                False         # done
            )
        }
        
        # Record transitions
        pool.record_transitions(transitions)
        
        # Learn from replay
        updates = pool.learn_from_replay(batch_size=1, learning_rate=0.5)
        
        # Both agents should have learned (update count = 1 each)
        self.assertEqual(updates["1"], 1)
        self.assertEqual(updates["2"], 1)
        
        # Agent 1 should have increased preference for local (positive reward)
        # Agent 2 should have decreased preference for local (negative reward)
        pref1 = pool.agents["1"].model.learned_action_preferences.get("local", 0.0)
        pref2 = pool.agents["2"].model.learned_action_preferences.get("local", 0.0)
        
        self.assertGreater(pref1, 0.0)  # Positive reward increases preference
        self.assertLess(pref2, 0.0)     # Negative reward decreases preference
    
    def test_target_network_sync_works_for_all_agents(self) -> None:
        """Should be able to sync target networks for all agents."""
        from src.agents.multi_agent_pool import MultiAgentHoodiePool
        
        agent_ids = [str(i) for i in range(1, 4)]  # Test with 3 agents
        pool = MultiAgentHoodiePool(agent_ids)
        
        # This should not raise an exception
        pool.sync_target_networks()
        
        # Verify each agent has a target network
        for agent_id in agent_ids:
            agent = pool.agents[agent_id]
            self.assertIsNotNone(agent.target_network)

    def test_duplicate_agent_ids_raises_error(self) -> None:
        """Should raise ValueError when duplicate agent IDs are provided."""
        from src.agents.multi_agent_pool import MultiAgentHoodiePool
        
        # Test with duplicate IDs
        with self.assertRaises(ValueError) as context:
            MultiAgentHoodiePool(["1", "2", "2", "3"])
        
        self.assertIn("Duplicate agent IDs found", str(context.exception))
        self.assertIn("['2']", str(context.exception))


if __name__ == "__main__":
    unittest.main()