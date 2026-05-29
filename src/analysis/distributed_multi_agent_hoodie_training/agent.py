from __future__ import annotations

from dataclasses import dataclass, field

from .policy import DistributedEpsilonGreedyPolicy
from .replay import DistributedReplayBuffer
from .schedule import EpsilonScheduleState


@dataclass(slots=True)
class DistributedAgent:
    agent_id: str
    online_network_owner_agent_id: str
    target_network_owner_agent_id: str
    optimizer_class: str = "Adam"
    replay_buffer: DistributedReplayBuffer = field(default_factory=DistributedReplayBuffer)
    policy: DistributedEpsilonGreedyPolicy = field(default_factory=DistributedEpsilonGreedyPolicy)
    epsilon_state: EpsilonScheduleState = field(default_factory=EpsilonScheduleState)
    target_sync_events: int = 0

    def summary(self) -> dict[str, str | int]:
        return {
            "agent_id": self.agent_id,
            "online_network_owner_agent_id": self.online_network_owner_agent_id,
            "target_network_owner_agent_id": self.target_network_owner_agent_id,
            "optimizer_class": self.optimizer_class,
            "replay_size": len(self.replay_buffer.transitions),
            "policy_class": self.policy.__class__.__name__,
        }

