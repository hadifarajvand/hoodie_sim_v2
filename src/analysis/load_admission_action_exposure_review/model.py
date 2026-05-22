from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True, slots=True)
class LoadPressureMetrics:
    generated_task_count: int
    admitted_task_count: int
    terminal_task_count: int
    completed_task_count: int
    dropped_task_count: int
    pending_at_horizon_count: int
    generated_per_slot: float
    admitted_per_slot: float
    terminal_per_slot: float
    completion_rate: float
    drop_rate: float
    pending_rate: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AdmissionSerializationMetrics:
    evidence_population: str
    same_slot_generated_count: int | None
    same_slot_admitted_count: int | None
    serialized_admission_backlog_count: int | None
    max_serialization_lag_slots: int | None
    mean_serialization_lag_slots: float | None
    tasks_delayed_by_serialization: list[str]
    tasks_expired_after_serialization_delay: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActionExposureMetrics:
    evidence_population: str
    legal_local_count: int | None
    legal_horizontal_count: int | None
    legal_vertical_count: int | None
    selected_local_count: int | None
    selected_horizontal_count: int | None
    selected_vertical_count: int | None
    exposure_ratio_by_action: dict[str, float | None]
    selection_ratio_by_action: dict[str, float | None]
    legal_but_unselected_by_action: dict[str, int | None]
    action_entropy: float | None
    per_action_completion_rate: dict[str, float | None]
    per_action_drop_rate: dict[str, float | None]
    per_action_pending_rate: dict[str, float | None]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class QueuePressureMetrics:
    evidence_population: str
    private_queue_admission_count: int | None
    public_queue_admission_count: int | None
    cloud_queue_admission_count: int | None
    private_queue_terminal_count: int | None
    public_queue_terminal_count: int | None
    cloud_queue_terminal_count: int | None
    per_queue_completion_rate: dict[str, float | None]
    per_queue_drop_rate: dict[str, float | None]
    queue_wait_time_mean: float | None
    queue_wait_time_max: int | None
    queue_pressure_index: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OffloadPathPressureMetrics:
    evidence_population: str
    transmission_started_count: int | None
    transmission_completed_count: int | None
    transmission_delay_slots_mean: float | None
    transmission_delay_slots_max: int | None
    transmission_to_admission_lag: float | None
    execution_start_after_transmission_lag: float | None
    offloaded_completed_count: int | None
    offloaded_dropped_count: int | None
    offloaded_pending_count: int | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BudgetComparisonMetrics:
    evidence_population: str
    representative_task_ids: list[str]
    expected_min_compute_slots: float | None
    expected_transmission_slots: float | None
    observed_queue_wait_slots: float | None
    observed_execution_progress_slots: float | None
    observed_task_age_at_drop_or_completion: float | None
    deadline_margin_at_completion: float | None
    deadline_overrun_at_drop: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
