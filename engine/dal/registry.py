from __future__ import annotations

from dataclasses import dataclass, field

from .agent import EdgeAgent


@dataclass
class AgentRegistry:
    agents: dict[int, EdgeAgent] = field(default_factory=dict)

    def register(self, agent: EdgeAgent) -> None:
        self.agents[int(agent.agent_id)] = agent

    def register_agent(self, agent_id: int, agent: EdgeAgent) -> None:
        self.agents[int(agent_id)] = agent

    def get(self, agent_id: int) -> EdgeAgent | None:
        return self.agents.get(int(agent_id))

    def __iter__(self):
        for agent_id in sorted(self.agents):
            yield self.agents[agent_id]

    def ids(self) -> list[int]:
        return sorted(self.agents)

    def items(self):
        for agent_id in sorted(self.agents):
            yield agent_id, self.agents[agent_id]
