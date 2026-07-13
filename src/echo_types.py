from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class EchoSourceMetadata:
    source_document_id: str
    method_revision_id: str
    evaluation_revision_id: str
    exported_at_utc: str
    method_sha256: str
    evaluation_sha256: str


@dataclass(frozen=True, slots=True)
class EchoTaskSpec:
    task_id: int
    source_agent_id: int
    arrival_slot: int
    size_mbits: float
    processing_density_gcycles_per_mbit: float
    timeout_slots: int
    absolute_deadline_slot: int

    @property
    def cycles_required_gcycles(self) -> float:
        return float(self.size_mbits) * float(self.processing_density_gcycles_per_mbit)


@dataclass(frozen=True, slots=True)
class EchoAction:
    canonical_index: int
    kind: str
    source_agent_id: int
    destination_node_id: str
    action_id: str


@dataclass(frozen=True, slots=True)
class EchoActionMask:
    values: tuple[int, ...]
    allowed_action_ids: tuple[str, ...]
    fallback_action_id: str | None = None
    reasons: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EchoQueueEstimate:
    waiting_slots: int
    completion_slot: int
    ert_slots: int
    lateness_slots: int


@dataclass(frozen=True, slots=True)
class EchoCandidateEstimate:
    action_id: str
    destination_node_id: str
    transmission_slots: int
    destination_waiting_slots: int
    destination_service_slots: int
    completion_slot: int
    ert_slots: int
    lateness_slots: int
    deadline_feasible: bool


@dataclass(frozen=True, slots=True)
class EchoTransition:
    state: dict[str, Any]
    action_id: str
    reward: float
    next_state: dict[str, Any]
    delta_slots: int
    terminal: bool
    predicted_risk: bool
    dropped: bool
