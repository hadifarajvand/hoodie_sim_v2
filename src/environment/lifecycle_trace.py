from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class LifecycleTraceEvent:
    event_type: str
    slot: int
    task_id: int | str | None = None
    source_agent_id: int | str | None = None
    selected_action: str | None = None
    selected_action_family: str | None = None
    selected_action_trace_source: str | None = None
    action_index: int | None = None
    decision_event_id: str | None = None
    selected_action_to_task_join_key: str | None = None
    terminal_outcome_join_key: str | None = None
    strategy: str | None = None
    seed: int | None = None
    agent_id: int | str | None = None
    destination: str | None = None
    queue_type: str | None = None
    host_node_id: str | None = None
    arrival_slot: int | None = None
    absolute_deadline_slot: int | None = None
    task_age_slots: int | None = None
    size_mbits: float | None = None
    processing_density_gcycles_per_mbit: float | None = None
    cycles_required_gcycles: float | None = None
    cycles_before_gcycles: float | None = None
    cycles_consumed_gcycles: float | None = None
    cycles_after_gcycles: float | None = None
    compute_capacity_gcycles_per_slot: float | None = None
    transmission_started_at: int | None = None
    transmission_completed_at: int | None = None
    transmission_delay_slots: int | None = None
    terminal_outcome: str | None = None
    reward: float | None = None
    reward_available: bool | None = None
    pending_at_horizon: bool | None = None
    legality_snapshot: dict[str, bool] | None = None
    trace_source_component: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        extra = payload.pop("extra", {})
        payload.update(extra)
        return {key: value for key, value in payload.items() if value is not None}


@dataclass(slots=True)
class LifecycleTraceRecorder:
    enabled: bool = False
    events: list[LifecycleTraceEvent] = field(default_factory=list)

    def record(self, event: LifecycleTraceEvent) -> None:
        if self.enabled:
            self.events.append(event)

    def emit(self, event_type: str, *, slot: int, trace_source_component: str, **fields: Any) -> None:
        self.record(
            LifecycleTraceEvent(
                event_type=event_type,
                slot=slot,
                trace_source_component=trace_source_component,
                **fields,
            )
        )

    def snapshot(self) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self.events]

    def clear(self) -> None:
        self.events.clear()


@dataclass(frozen=True, slots=True)
class LifecycleTraceConfig:
    trace_enabled: bool = False
