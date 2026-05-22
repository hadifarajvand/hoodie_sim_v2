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
    same_slot_generated_count: int
    same_slot_admitted_count: int
    serialized_admission_backlog_count: int
    max_serialization_lag_slots: int
    mean_serialization_lag_slots: float
    tasks_delayed_by_serialization: list[str]
    tasks_expired_after_serialization_delay: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActionExposureMetrics:
    legal_local_count: int
    legal_horizontal_count: int
    legal_vertical_count: int
    selected_local_count: int
    selected_horizontal_count: int
    selected_vertical_count: int
    exposure_ratio_by_action: dict[str, float]
    selection_ratio_by_action: dict[str, float]
    legal_but_unselected_by_action: dict[str, int]
    action_entropy: float
    per_action_completion_rate: dict[str, float]
    per_action_drop_rate: dict[str, float]
    per_action_pending_rate: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class QueuePressureMetrics:
    private_queue_admission_count: int
    public_queue_admission_count: int
    cloud_queue_admission_count: int
    private_queue_terminal_count: int
    public_queue_terminal_count: int
    cloud_queue_terminal_count: int
    per_queue_completion_rate: dict[str, float]
    per_queue_drop_rate: dict[str, float]
    queue_wait_time_mean: float
    queue_wait_time_max: int
    queue_pressure_index: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OffloadPathPressureMetrics:
    transmission_started_count: int
    transmission_completed_count: int
    transmission_delay_slots_mean: float
    transmission_delay_slots_max: int
    transmission_to_admission_lag: float
    execution_start_after_transmission_lag: float
    offloaded_completed_count: int
    offloaded_dropped_count: int
    offloaded_pending_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BudgetComparisonMetrics:
    representative_task_ids: list[str]
    expected_min_compute_slots: float
    expected_transmission_slots: float
    observed_queue_wait_slots: float
    observed_execution_progress_slots: float
    observed_task_age_at_drop_or_completion: float
    deadline_margin_at_completion: float
    deadline_overrun_at_drop: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
