from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DistributedReplayTransition:
    originating_agent_id: str
    acting_agent_id: str
    selected_destination_id: str
    action_index: int
    paper_state_snapshot: dict
    legal_action_mask: list[bool]
    delayed_reward_available: bool
    terminal_reason: str
    task_id: str
    arrival_slot: int
    completion_or_drop_slot: int | None


@dataclass(slots=True)
class DistributedReplayBuffer:
    transitions: list[DistributedReplayTransition] = field(default_factory=list)

    def add(self, transition: DistributedReplayTransition) -> None:
        self.transitions.append(transition)

