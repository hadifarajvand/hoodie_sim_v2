from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class OpenAgentDecision:
    source_agent_id: int
    decision_slot: int
    state: dict[str, Any]
    action: str
    interval_reward: float = 0.0


@dataclass(frozen=True, slots=True)
class EventSMDPTransition:
    source_agent_id: int
    state: dict[str, Any]
    action: str
    reward: float
    next_state: dict[str, Any]
    delta_slots: int
    done: bool


class AgentEventSMDPAccumulator:
    """Build one non-overlapping transition between decisions of each EA.

    Task outcomes are assigned to the open interval of their source EA using
    the within-interval discount from Equation (59). A transition is emitted
    only when that same EA receives its next task, or at the terminal epoch.
    """

    def __init__(self, *, gamma: float) -> None:
        if not 0.0 <= float(gamma) <= 1.0:
            raise ValueError("gamma must be in [0, 1]")
        self.gamma = float(gamma)
        self._open: dict[int, OpenAgentDecision] = {}

    @property
    def open_agent_ids(self) -> tuple[int, ...]:
        return tuple(sorted(self._open))

    def observe_decision(self, event: dict[str, Any]) -> EventSMDPTransition | None:
        source_agent_id = int(event["source_agent_id"])
        decision_slot = int(event["decision_slot"])
        state = dict(event["state"])
        action = str(event["action"])

        previous = self._open.get(source_agent_id)
        transition = None
        if previous is not None:
            delta_slots = decision_slot - previous.decision_slot
            if delta_slots <= 0:
                raise ValueError(
                    "Consecutive decisions of one EA must occur at increasing slots"
                )
            transition = EventSMDPTransition(
                source_agent_id=source_agent_id,
                state=previous.state,
                action=previous.action,
                reward=previous.interval_reward,
                next_state=state,
                delta_slots=delta_slots,
                done=False,
            )

        self._open[source_agent_id] = OpenAgentDecision(
            source_agent_id=source_agent_id,
            decision_slot=decision_slot,
            state=state,
            action=action,
        )
        return transition

    def observe_resolution(self, event: dict[str, Any]) -> None:
        # The environment's TaskResolutionEvent serializes this field as
        # ``source_id``.  ``source_agent_id`` remains accepted for tests and
        # external campaign adapters.
        source_value = event.get("source_agent_id", event.get("source_id"))
        if source_value is None:
            raise KeyError("resolution event requires source_id")
        source_agent_id = int(source_value)
        open_decision = self._open.get(source_agent_id)
        if open_decision is None:
            # A resolution without an open source interval can only originate
            # from an invalid trace or an episode that began mid-lifecycle.  It
            # is ignored here and caught by the campaign accounting audit.
            return
        resolution_slot = int(event["resolution_slot"])
        exponent = max(0, resolution_slot - open_decision.decision_slot)
        task_reward = float(event["task_reward"])
        open_decision.interval_reward += (self.gamma ** exponent) * task_reward

    def finalize_terminal(
        self,
        *,
        terminal_slot: int,
    ) -> list[EventSMDPTransition]:
        transitions: list[EventSMDPTransition] = []
        for source_agent_id in sorted(self._open):
            previous = self._open[source_agent_id]
            delta_slots = max(1, int(terminal_slot) - previous.decision_slot)
            transitions.append(
                EventSMDPTransition(
                    source_agent_id=source_agent_id,
                    state=previous.state,
                    action=previous.action,
                    reward=previous.interval_reward,
                    next_state={
                        "terminal": True,
                        "source_agent_id": source_agent_id,
                        "slot": int(terminal_slot),
                        "legal_action_mask": {},
                    },
                    delta_slots=delta_slots,
                    done=True,
                )
            )
        self._open.clear()
        return transitions
