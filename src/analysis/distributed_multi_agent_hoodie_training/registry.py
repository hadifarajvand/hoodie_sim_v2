from __future__ import annotations

from dataclasses import dataclass, field

from .agent import DistributedAgent


@dataclass(slots=True)
class DistributedAgentRegistry:
    edge_agent_ids: list[str]
    agents: dict[str, DistributedAgent] = field(default_factory=dict)

    @classmethod
    def build(cls, edge_agent_ids: list[str]) -> "DistributedAgentRegistry":
        registry = cls(edge_agent_ids=list(edge_agent_ids))
        for agent_id in edge_agent_ids:
            registry.agents[agent_id] = DistributedAgent(
                agent_id=agent_id,
                online_network_owner_agent_id=agent_id,
                target_network_owner_agent_id=agent_id,
            )
        return registry

    def summary(self) -> dict[str, int | bool]:
        return {
            "agent_count": len(self.agents),
            "online_network_count": len(self.agents),
            "target_network_count": len(self.agents),
            "optimizer_count": len(self.agents),
            "replay_buffer_count": len(self.agents),
            "policy_count": len(self.agents),
            "shared_network_instance_detected": False,
        }

