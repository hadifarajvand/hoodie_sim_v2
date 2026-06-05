from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class TaskRecord:
    task_id: int
    source_ea_id: int
    arrival_slot: int
    size_mbits: float
    processing_density_gcycles_per_mbit: float
    timeout_slots: int
    deadline_slot: int
    policy: str
    decision_level_1: str | None
    destination_node_id: int | None
    path_type: str
    status: str = "pending"
    private_queue_enter_slot: int | None = None
    offloading_queue_enter_slot: int | None = None
    public_queue_enter_slot: int | None = None
    queue_exit_slot: int | None = None
    final_completion_slot: int | None = None
    drop_slot: int | None = None
    reward_collection_slot: int | None = None
    reward: float | None = None
    delay_slots: int | None = None
    delay_sec: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["metadata"] = dict(self.metadata)
        return payload


@dataclass(slots=True)
class QueueState:
    episode_id: str
    slot: int
    node_id: int
    queue_type: str
    source_ea_id: int
    queue_length_workload: float
    queue_length_unit: str
    active: bool
    allocated_cpu_ghz: float
    arrived_task_ids: list[int] = field(default_factory=list)
    completed_task_ids: list[int] = field(default_factory=list)
    dropped_task_ids: list[int] = field(default_factory=list)
    remaining_task_ids: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PublicQueueActiveSet:
    episode_id: str
    slot: int
    node_id: int
    active_public_queue_source_ids: list[int]
    active_public_queue_count: int
    total_public_cpu_ghz: float
    cpu_share_per_active_queue_ghz: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StateSnapshot:
    episode_id: str
    slot: int
    ea_id: int
    task_id: int
    task_size_mbits: float
    private_wait_slots: int
    offloading_wait_slots: int
    public_queue_footprint: dict[str, Any]
    load_history_matrix_shape: tuple[int, int]
    load_history_matrix_values: list[list[int]]
    forecast_mode: str
    forecast_values: list[float]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["load_history_matrix_shape"] = list(self.load_history_matrix_shape)
        return payload


@dataclass(slots=True)
class PolicyDecision:
    episode_id: str
    slot: int
    ea_id: int
    task_id: int
    policy: str
    state_snapshot_id: str
    decision_level_1: str
    destination_node_id: int | None
    path_type: str
    legal_action: bool
    illegal_reason: str | None
    candidate_latency_table_id: str | None = None
    selected_estimated_latency_slots: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RewardEvent:
    episode_id: str
    reward_collection_slot: int
    task_id: int
    source_ea_id: int
    policy: str
    original_action_slot: int
    completed_or_dropped: str
    delay_slots: int
    reward: float
    drop_penalty_applied: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MetricAggregate:
    figure_id: str
    sweep_name: str
    sweep_value: float | str
    policy: str
    episode_count: int
    arrived_tasks: int
    completed_tasks: int
    dropped_tasks: int
    unresolved_tasks: int
    average_delay_sec: float
    paper_style_negative_delay_sec: float
    drop_ratio: float
    drop_ratio_percent: float
    average_reward: float
    total_reward: float
    throughput: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DegeneracyDiagnostic:
    figure_id: str
    sweep_name: str
    sweep_value: float | str
    policy: str
    zero_completion_detected: bool
    single_task_trace_detected: bool
    drop_saturation_detected: bool
    all_policy_tie_detected: bool
    missing_sweep_injection_detected: bool
    severity: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

