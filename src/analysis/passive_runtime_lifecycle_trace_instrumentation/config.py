from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

FEATURE_ID = "044-passive-runtime-lifecycle-trace-instrumentation"

TraceStrategy = Literal[
    "environment_default_policy_probe",
    "force_local_legal_probe",
    "force_horizontal_legal_probe",
    "force_vertical_legal_probe",
    "mixed_legal_round_robin_probe",
]

TRACE_EVENT_TYPES: tuple[str, ...] = (
    "task_generated",
    "task_admitted",
    "transmission_started",
    "transmission_completed",
    "execution_started",
    "execution_progress",
    "execution_completed",
    "deadline_reached",
    "deadline_expired",
    "task_completed",
    "task_dropped",
    "reward_emitted",
    "pending_at_horizon",
)

TRACE_STRATEGIES: tuple[TraceStrategy, ...] = (
    "environment_default_policy_probe",
    "force_local_legal_probe",
    "force_horizontal_legal_probe",
    "force_vertical_legal_probe",
    "mixed_legal_round_robin_probe",
)


@dataclass(slots=True)
class PassiveRuntimeLifecycleTraceConfig:
    feature_id: str = FEATURE_ID
    episode_length: int = 110
    timeout_slots: int = 20
    arrival_probability: float = 0.5
    node_count: int = 20
    slot_duration_seconds: float = 0.1
    task_size_mbits_min: float = 2.0
    task_size_mbits_max: float = 5.0
    processing_density_gcycles_per_mbit: float = 0.297
    cpu_capacity_private_gcycles_per_slot: float = 0.5
    cpu_capacity_public_gcycles_per_slot: float = 0.5
    cpu_capacity_cloud_gcycles_per_slot: float = 3.0
    horizontal_data_rate_mbps: float = 30.0
    vertical_data_rate_mbps: float = 10.0
    seeds: list[int] = field(default_factory=lambda: [0, 1, 2])
    strategies: tuple[TraceStrategy, ...] = TRACE_STRATEGIES
    trace_enabled: bool = True

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.feature_id must match the feature id.")
        if self.episode_length != 110:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.episode_length must equal 110.")
        if self.timeout_slots != 20:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.timeout_slots must equal 20.")
        if self.arrival_probability != 0.5:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.arrival_probability must equal 0.5.")
        if self.node_count != 20:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.node_count must equal 20.")
        if self.slot_duration_seconds != 0.1:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.slot_duration_seconds must equal 0.1.")
        if self.task_size_mbits_min != 2.0 or self.task_size_mbits_max != 5.0:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.task_size_mbits_min/max must equal 2.0/5.0.")
        if self.processing_density_gcycles_per_mbit != 0.297:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.processing_density_gcycles_per_mbit must equal 0.297.")
        if self.cpu_capacity_private_gcycles_per_slot != 0.5 or self.cpu_capacity_public_gcycles_per_slot != 0.5 or self.cpu_capacity_cloud_gcycles_per_slot != 3.0:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.cpu capacity defaults must equal 0.5/0.5/3.0.")
        if self.horizontal_data_rate_mbps != 30.0 or self.vertical_data_rate_mbps != 10.0:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.data rates must equal 30.0/10.0.")
        if list(self.seeds) != [0, 1, 2]:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.seeds must equal [0, 1, 2].")
        if tuple(self.strategies) != TRACE_STRATEGIES:
            raise ValueError("PassiveRuntimeLifecycleTraceConfig.strategies must match the approved probe strategies.")

