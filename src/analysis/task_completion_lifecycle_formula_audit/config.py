from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

FEATURE_ID = "043-task-completion-lifecycle-formula-audit"

AuditStrategy = Literal[
    "environment_default_policy_probe",
    "force_local_legal_probe",
    "force_horizontal_legal_probe",
    "force_vertical_legal_probe",
    "mixed_legal_round_robin_probe",
]


@dataclass(slots=True)
class CompletionLifecycleAuditConfig:
    feature_id: str = FEATURE_ID
    episode_length: int = 110
    timeout_slots: int = 20
    slot_duration_seconds: float = 0.1
    arrival_probability: float = 0.5
    node_count: int = 20
    task_size_range_mbits: tuple[float, float] = (2.0, 5.0)
    processing_density_gcycles_per_mbit: float = 0.297
    cpu_private_gcycles_per_slot: float = 0.5
    cpu_public_gcycles_per_slot: float = 0.5
    cpu_cloud_gcycles_per_slot: float = 3.0
    horizontal_rate_mbps: float = 30.0
    vertical_rate_mbps: float = 10.0
    seeds: list[int] = field(default_factory=lambda: [0, 1, 2])
    strategies: tuple[AuditStrategy, ...] = (
        "environment_default_policy_probe",
        "force_local_legal_probe",
        "force_horizontal_legal_probe",
        "force_vertical_legal_probe",
        "mixed_legal_round_robin_probe",
    )
    no_training: bool = True
    no_runtime_mutation: bool = True

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("CompletionLifecycleAuditConfig.feature_id must equal 043-task-completion-lifecycle-formula-audit.")
        if self.episode_length != 110:
            raise ValueError("CompletionLifecycleAuditConfig.episode_length must equal 110.")
        if self.timeout_slots != 20:
            raise ValueError("CompletionLifecycleAuditConfig.timeout_slots must equal 20.")
        if self.slot_duration_seconds != 0.1:
            raise ValueError("CompletionLifecycleAuditConfig.slot_duration_seconds must equal 0.1.")
        if self.arrival_probability != 0.5:
            raise ValueError("CompletionLifecycleAuditConfig.arrival_probability must equal 0.5.")
        if self.node_count != 20:
            raise ValueError("CompletionLifecycleAuditConfig.node_count must equal 20.")
        if tuple(self.task_size_range_mbits) != (2.0, 5.0):
            raise ValueError("CompletionLifecycleAuditConfig.task_size_range_mbits must equal (2.0, 5.0).")
        if self.processing_density_gcycles_per_mbit != 0.297:
            raise ValueError("CompletionLifecycleAuditConfig.processing_density_gcycles_per_mbit must equal 0.297.")
        if self.cpu_private_gcycles_per_slot != 0.5 or self.cpu_public_gcycles_per_slot != 0.5 or self.cpu_cloud_gcycles_per_slot != 3.0:
            raise ValueError("CompletionLifecycleAuditConfig.cpu capacities must equal 0.5/0.5/3.0.")
        if self.horizontal_rate_mbps != 30.0 or self.vertical_rate_mbps != 10.0:
            raise ValueError("CompletionLifecycleAuditConfig.transmission rates must equal 30.0/10.0.")
        if list(self.seeds) != [0, 1, 2]:
            raise ValueError("CompletionLifecycleAuditConfig.seeds must equal [0, 1, 2].")
        if self.no_training is not True or self.no_runtime_mutation is not True:
            raise ValueError("CompletionLifecycleAuditConfig diagnostic-only flags must remain true.")
