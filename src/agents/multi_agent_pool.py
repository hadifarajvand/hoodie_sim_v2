from __future__ import annotations

from typing import Dict, List

from src.agents.hoodie_agent import HoodieAgent
from src.policies.policy_interface import PolicyContext


class MultiAgentHoodiePool:
    """Manages a pool of independent HOODIE agents, one per edge agent.
    
    Each agent in the pool maintains its own neural network weights,
    experience replay buffer, and learning state, enabling true distributed
    reinforcement learning where each edge agent learns from its own experience
    while sharing the same network architecture and hyperparameters.
    """
    
    def __init__(self, agent_ids: List[str]) -> None:
        """Create a pool with one HoodieAgent per agent_id.
        
        Args:
            agent_ids: List of unique identifiers for edge agents
            
        Raises:
            ValueError: If agent_ids contains duplicates
        """
        if len(agent_ids) != len(set(agent_ids)):
            duplicates = [id for id in set(agent_ids) if agent_ids.count(id) > 1]
            raise ValueError(f"Duplicate agent IDs found: {duplicates}")
            
        self.agents: Dict[str, HoodieAgent] = {}
        for agent_id in agent_ids:
            self.agents[agent_id] = HoodieAgent()
    
    def choose_actions(self, contexts: Dict[str, PolicyContext]) -> Dict[str, str]:
        """Get action decisions from all agents based on their observations.
        
        Args:
            contexts: Mapping from agent_id to PolicyContext for that agent
            
        Returns:
            Mapping from agent_id to chosen action string
            
        Note:
            Only agents present in both the pool and contexts will have actions computed.
            Agents in the pool but missing from contexts will be skipped.
        """
        actions = {}
        for agent_id, context in contexts.items():
            if agent_id in self.agents:
                actions[agent_id] = self.agents[agent_id].choose_action(context)
        return actions
    
    def record_transitions(self, transitions: Dict[str, tuple]) -> None:
        """Record transitions for each agent's experience.
        
        Args:
            transitions: Mapping from agent_id to (state, action, reward, next_state, done) tuple
            
        Note:
            Only agents present in both the pool and transitions will have their experience recorded.
            Agents in the pool but missing from transitions will be ignored.
        """
        for agent_id, transition in transitions.items():
            if agent_id in self.agents:
                state, action, reward, next_state, done = transition
                self.agents[agent_id].record_transition(state, action, reward, next_state, done)
    
    def learn_from_replay(self, batch_size: int, learning_rate: float) -> Dict[str, int]:
        """Learn from experience replay for all agents.
        
        Args:
            batch_size: Number of transitions to sample for learning per agent
            learning_rate: Learning rate for the update
            
        Returns:
            Mapping from agent_id to number of updates performed (0 to batch_size)
        """
        updates = {}
        for agent_id, agent in self.agents.items():
            updates[agent_id] = agent.learn_from_replay(batch_size, learning_rate)
        return updates
    
    def sync_target_networks(self) -> None:
        """Synchronize target networks for all agents.
        
        This performs a hard copy of the online network weights to the target network
        for each agent in the pool, following the DQN target network update strategy.
        """
        for agent in self.agents.values():
            agent.sync_target_network()