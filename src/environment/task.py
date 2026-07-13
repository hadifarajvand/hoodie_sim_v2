from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class Task:
    task_id: int
    source_agent_id: int
    arrival_slot: int
    size: float
    processing_density: float
    timeout_length: int
    absolute_deadline_slot: int
    cycles_required: float = 0.0
    cycles_remaining: float = 0.0
    selected_action: Optional[str] = None
    resolved_destination: Optional[str] = None
    queue_state: str = "created"
    start_slot: Optional[int] = None
    completion_slot: Optional[int] = None
    terminal_outcome: Optional[str] = None
    reward_emitted: bool = False
    drop_flag: bool = False
    metadata: dict[str, object] = field(default_factory=dict)
    decision_slot: Optional[int] = None
    predicted_ert_slots: Optional[int] = None
    predicted_lateness_slots: Optional[int] = None
    predicted_risk: Optional[float] = None
    transmission_start_slot: Optional[int] = None
    transmission_completion_slot: Optional[int] = None
    destination_admission_slot: Optional[int] = None
    computation_start_slot: Optional[int] = None
    resolution_slot: Optional[int] = None
    resolution_reason: Optional[str] = None

    def __post_init__(self) -> None:
        self.size = float(self.size)
        self.processing_density = float(self.processing_density)
        self.cycles_required = float(self.cycles_required or self.size * self.processing_density)
        self.cycles_remaining = float(self.cycles_remaining or self.cycles_required)
        if self.cycles_remaining > self.cycles_required:
            self.cycles_remaining = float(self.cycles_required)
        self._sync_metadata_fields()

    @property
    def timeout(self) -> int:
        return int(self.timeout_length)

    @property
    def source_ea(self) -> int:
        return int(self.source_agent_id)

    @property
    def task_size(self) -> float:
        return float(self.size)

    @property
    def computation_density(self) -> float:
        return float(self.processing_density)

    @property
    def selected_destination(self) -> Optional[str]:
        return self.resolved_destination

    @selected_destination.setter
    def selected_destination(self, value: Optional[str]) -> None:
        self.resolved_destination = value
        self.metadata["selected_destination"] = value

    @property
    def success_state(self) -> Optional[str]:
        return self.terminal_outcome

    @success_state.setter
    def success_state(self, value: Optional[str]) -> None:
        self.terminal_outcome = value
        self.drop_flag = value == "dropped"
        self.metadata["success_state"] = value

    def mark_decision(
        self,
        *,
        action: str,
        destination: Optional[str],
        slot: int,
        predicted_ert_slots: Optional[int] = None,
        predicted_lateness_slots: Optional[int] = None,
        predicted_risk: Optional[float] = None,
    ) -> None:
        self.selected_action = action
        self.selected_destination = destination
        self.decision_slot = int(slot)
        self.predicted_ert_slots = None if predicted_ert_slots is None else int(predicted_ert_slots)
        self.predicted_lateness_slots = None if predicted_lateness_slots is None else int(predicted_lateness_slots)
        self.predicted_risk = None if predicted_risk is None else float(predicted_risk)
        self._sync_metadata_fields()

    def mark_resolution(self, *, slot: int, outcome: str, reason: str) -> None:
        self.completion_slot = self.completion_slot if self.completion_slot is not None else int(slot)
        self.resolution_slot = int(slot)
        self.success_state = outcome
        self.resolution_reason = reason
        self.reward_emitted = False
        self._sync_metadata_fields()

    def _sync_metadata_fields(self) -> None:
        self.metadata.setdefault("task_id", self.task_id)
        self.metadata.setdefault("source_ea", self.source_agent_id)
        self.metadata.setdefault("arrival_slot", self.arrival_slot)
        self.metadata.setdefault("timeout", self.timeout_length)
        self.metadata.setdefault("absolute_deadline_slot", self.absolute_deadline_slot)
        self.metadata.setdefault("task_size", self.size)
        self.metadata.setdefault("computation_density", self.processing_density)
        self.metadata.setdefault("required_cycles", self.cycles_required)
        self.metadata["selected_action"] = self.selected_action
        self.metadata["selected_destination"] = self.resolved_destination
        self.metadata["decision_slot"] = self.decision_slot
        self.metadata["predicted_ert_slots"] = self.predicted_ert_slots
        self.metadata["predicted_lateness_slots"] = self.predicted_lateness_slots
        self.metadata["predicted_risk"] = self.predicted_risk
        self._sync_optional_metadata_field("transmission_start_slot", self.transmission_start_slot)
        self._sync_optional_metadata_field("transmission_completion_slot", self.transmission_completion_slot)
        self._sync_optional_metadata_field("destination_admission_slot", self.destination_admission_slot)
        self._sync_optional_metadata_field("computation_start_slot", self.computation_start_slot)
        self._sync_optional_metadata_field("completion_slot", self.completion_slot)
        self._sync_optional_metadata_field("resolution_slot", self.resolution_slot)
        self.metadata["success_state"] = self.terminal_outcome
        self._sync_optional_metadata_field("resolution_reason", self.resolution_reason)

    def _sync_optional_metadata_field(self, key: str, value: Optional[int | str | float]) -> None:
        if value is None:
            self.metadata.pop(key, None)
        else:
            self.metadata[key] = value
