from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class HoodieSynchronization:
    distributed_timestep_synchronization: bool = True
    completed_agents_by_cycle: dict[int, set[str]] = field(default_factory=dict)

    def register_completion(self, *, decision_cycle: int, agent_id: str, expected_agent_count: int) -> dict[str, Any]:
        completed = self.completed_agents_by_cycle.setdefault(decision_cycle, set())
        completed.add(agent_id)
        barrier_reached = len(completed) >= expected_agent_count
        return {
            "decision_cycle": decision_cycle,
            "agent_id": agent_id,
            "barrier_reached": barrier_reached,
            "completed_agent_count": len(completed),
            "expected_agent_count": expected_agent_count,
            "distributed_timestep_synchronization": self.distributed_timestep_synchronization,
        }

    def barrier(self, decision_cycle: int) -> dict[str, Any]:
        completed = self.completed_agents_by_cycle.get(decision_cycle, set())
        return {
            "decision_cycle": decision_cycle,
            "barrier_reached": bool(completed),
            "completed_agent_count": len(completed),
            "distributed_timestep_synchronization": self.distributed_timestep_synchronization,
        }
