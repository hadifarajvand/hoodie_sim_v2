from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DelayedRewardAssignment:
    task_originating_agent_id: str
    selected_destination_id: str
    completion_node_id: str
    reward_recipient_agent_id: str
    reward_available: bool
    pending_at_horizon: bool
    terminal_outcome: str

