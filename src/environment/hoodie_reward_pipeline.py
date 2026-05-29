from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class HoodieDelayedRewardPipeline:
    ownership_tracking_enabled: bool = True
    pending_rewards: dict[str, dict[str, Any]] = field(default_factory=dict)

    def register_pending(self, *, correlation_id: str, originating_agent_id: str, dispatching_agent_id: str, task_id: str) -> dict[str, Any]:
        record = {
            "correlation_id": correlation_id,
            "originating_agent_id": originating_agent_id,
            "dispatching_agent_id": dispatching_agent_id,
            "task_id": task_id,
            "reward_ready": False,
        }
        self.pending_rewards[correlation_id] = record
        return record

    def resolve_reward(self, *, correlation_id: str, completion_node_id: str, reward: float) -> dict[str, Any]:
        record = self.pending_rewards.get(correlation_id)
        if record is None:
            raise KeyError(correlation_id)
        reward_event = {
            **record,
            "completion_node_id": completion_node_id,
            "reward_recipient_agent_id": record["originating_agent_id"],
            "reward": reward,
            "reward_ready": True,
            "ownership_tracking_enabled": self.ownership_tracking_enabled,
        }
        self.pending_rewards.pop(correlation_id, None)
        return reward_event

    def route_reward(self, *, originating_agent_id: str, completion_node_id: str, reward: float, correlation_id: str = "corr-0", dispatching_agent_id: str | None = None, task_id: str = "task-0") -> dict[str, Any]:
        self.register_pending(correlation_id=correlation_id, originating_agent_id=originating_agent_id, dispatching_agent_id=dispatching_agent_id or originating_agent_id, task_id=task_id)
        return self.resolve_reward(correlation_id=correlation_id, completion_node_id=completion_node_id, reward=reward)
