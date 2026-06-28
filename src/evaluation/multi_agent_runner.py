from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from src.agents.hoodie_agent import HoodieAgent
from src.agents.multi_agent_pool import MultiAgentHoodiePool
from src.environment.compute_config import ComputeConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.task import Task
from src.environment.topology import TopologyGraph
from src.policies.policy_interface import PolicyContext

from .config import EvaluationConfig
from .fairness_checks import assert_fair_evaluation
from .metric_storage import persist_metrics
from .metrics import TaskEvaluationRecord, TraceMetrics, evaluate_run, evaluate_trace
from .run_metadata import RunMetadata
from .trace_protocol import EvaluationTrace, build_deterministic_trace


@dataclass(slots=True)
class MultiAgentEvaluationRunner:
    """Evaluates multiple HOEDIE agents operating in a shared environment.
    
    Each agent makes independent decisions based on local observations,
    but all agents interact within the same simulated environment.
    """
    agent_pool: MultiAgentHoodiePool
    config: EvaluationConfig
    topology: TopologyGraph | None = None
    runtime_parameters: SharedRuntimeParameters | None = None

    def _trace_for_episode(self, episode_index: int) -> EvaluationTrace:
        """Create deterministic trace for episode."""
        trace_id = f"{self.config.trace_id}-{episode_index}"
        return build_deterministic_trace(trace_id, self.config.seed + episode_index, self.config.episode_length)

    def _evaluate_agent_episode(
        self, 
        agent_id: str, 
        agent: HoodieAgent, 
        trace: EvaluationTrace,
        agent_ids: List[str]
    ) -> TraceMetrics:
        """Evaluate a single agent's performance over an episode.
        
        Args:
            agent_id: Identifier for the agent being evaluated
            agent: The agent instance to evaluate
            trace: Trace for this episode
            agent_ids: List of all agent IDs in the simulation (for observation building)
        """
        # Local import to avoid circular dependency:
        #   gym_adapter → evaluation.trace_protocol → evaluation.__init__ → multi_agent_runner → gym_adapter
        from src.environment.gym_adapter import HoodieGymEnvironment

        env = HoodieGymEnvironment(
            episode_length=self.config.episode_length,
            topology=self.topology,
            runtime_parameters=self.runtime_parameters or SharedRuntimeParameters(),
            compute_config=ComputeConfig(
                cpu_capacity_per_slot_agent=0.5,
                cpu_capacity_per_slot_edge=0.5,
                cpu_capacity_per_slot_cloud=3.0,
            ),
            policy_name=self.config.policy_name,
        )
        observation, _info = env.reset(seed=trace.seed)
        records: list[TaskEvaluationRecord] = []
        
        while True:
            current_task = env.current_task
            if current_task is None:
                # No task to act on
                observation, reward, terminated, truncated, info = env.step(None)
                # Still need to process the step to advance simulation
                if terminated or truncated:
                    break
                continue
            
            # Build observation for this specific agent
            agent_observation = env.observe_flat(current_task)
            # Extract the observation for this agent's perspective
            if str(current_task.source_agent_id) in agent_observation:
                agent_specific_obs = agent_observation[str(current_task.source_agent_id)]
            else:
                # Fallback to flat observation if agent-specific not available
                agent_specific_obs = agent_observation
            
            legal_action_mask = agent_observation.get("legal_action_mask", {}) if isinstance(agent_observation, dict) else {}
            
            context = PolicyContext(
                observation=agent_specific_obs,
                legal_action_mask=legal_action_mask,
                trace_history=(trace.trace_id,),
            )
            
            # Get action from this specific agent
            action = agent.choose_action(context)
            
            # Step the environment with the action
            observation, reward, terminated, truncated, info = env.step(action)
            
            # Process finalized tasks (rewards, etc.)
            for finalized in info.get("finalized_tasks", []):
                # Only record rewards for tasks that belong to this agent
                if str(finalized.get("source_agent_id", "")) == agent_id:
                    records.append(
                        TaskEvaluationRecord(
                            task_id=int(finalized["task_id"]),
                            arrival_slot=int(finalized["arrival_slot"]),
                            completion_slot=int(finalized["completion_slot"]) if finalized.get("completion_slot") is not None else None,
                            terminal_outcome=finalized.get("terminal_outcome"),
                            selected_action=finalized.get("selected_action"),
                            resolved_destination=finalized.get("resolved_destination"),
                            delay=(
                                int(finalized["completion_slot"]) - int(finalized["arrival_slot"])
                                if finalized.get("terminal_outcome") == "completed" and finalized.get("completion_slot") is not None
                                else None
                            ),
                        )
                    )
            
            if terminated or truncated:
                break
                
        return evaluate_trace(
            trace_id=trace.trace_id,
            policy_name=self.config.policy_name,
            seed=trace.seed,
            device=self.config.device,
            records=records,
        )

    def run(self) -> dict[str, object]:
        """Run evaluation for all agents in the pool."""
        from ..agents.hoodie_agent import HoodieAgent  # Import here to avoid circular issues
        
        if not hasattr(self, 'agent_pool') or self.agent_pool is None:
            raise ValueError("agent_pool must be provided")
            
        agent_ids = list(self.agent_pool.agents.keys())
        trace_metrics = []
        
        for episode_index in range(self.config.episode_count):
            trace = self._trace_for_episode(episode_index)
            
            # Evaluate each agent independently
            agent_metrics = []
            for agent_id, agent in self.agent_pool.agents.items():
                metrics = self._evaluate_agent_episode(agent_id, agent, trace, agent_ids)
                agent_metrics.append(metrics)
            
            # For multi-agent evaluation, we typically want to aggregate performance
            # Simple approach: use the first agent's metrics as representative
            # More sophisticated approaches could average rewards, etc.
            if agent_metrics:
                trace_metrics.append(agent_metrics[0])  # Use first agent as representative
            
            if self.config.output_dir is not None:
                # Save metrics for this episode
                if trace_metrics:
                    persist_metrics(self.config.output_dir, trace_metrics[-1])
        
        run_metrics = evaluate_run(trace_metrics)
        metadata = RunMetadata(
            policy_name=self.config.policy_name,
            trace_id=self.config.trace_id,
            seed=self.config.seed,
            device=self.config.device,
            trace_mode=self.config.trace_mode,
        )
        
        return {
            "metadata": metadata.to_dict(),
            "per_trace": [metric.to_dict() for metric in trace_metrics],
            "aggregate": run_metrics,
        }


# Export for backward compatibility - the original EvaluationRunner remains unchanged
# Users who want multi-agent evaluation should import and use MultiAgentEvaluationRunner explicitly