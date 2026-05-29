from __future__ import annotations

from dataclasses import dataclass, field

from .delayed_reward import DelayedRewardAssignment
from .registry import DistributedAgentRegistry
from .replay import DistributedReplayTransition


@dataclass(slots=True)
class DistributedTrainingCoordinator:
    registry: DistributedAgentRegistry
    deterministic_shared_environment_stepping: bool = True
    step_records: list[dict] = field(default_factory=list)

    def record_transition(self, transition: DistributedReplayTransition, reward: float, assignment: DelayedRewardAssignment) -> None:
        self.registry.agents[transition.originating_agent_id].replay_buffer.add(transition)
        self.step_records.append(
            {
                "originating_agent_id": assignment.task_originating_agent_id,
                "reward_recipient_agent_id": assignment.reward_recipient_agent_id,
                "reward": reward,
            }
        )

