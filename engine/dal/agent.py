from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..euls_core import ActionDecision
from .agent_state import EdgeAgentState


@dataclass
class EdgeAgent:
    state: EdgeAgentState
    policy: Any | None = None

    @property
    def agent_id(self) -> int:
        return int(self.state.agent_id)

    def bind_policy(self, policy: Any) -> None:
        self.policy = policy

    def decide(self, event: dict[str, Any], context: dict[str, Any]) -> ActionDecision:
        queue_view = context.get("state", context)
        self.state.last_decision_snapshot = {
            "event": event,
            "context_keys": sorted(queue_view.keys()) if isinstance(queue_view, dict) else [],
        }
        policy = self.policy
        if policy is not None and hasattr(policy, "select_action"):
            decision = policy.select_action(queue_view)
            if isinstance(decision, ActionDecision):
                return decision
            if decision == 3:
                return ActionDecision.cloud(getattr(policy, "name", "POLICY"))
            if decision == 0:
                return ActionDecision.local(getattr(policy, "name", "POLICY"))
            return ActionDecision.edge(int(decision), getattr(policy, "name", "POLICY"))
        return ActionDecision.local(getattr(policy, "name", "POLICY") if policy is not None else "FIFO")
