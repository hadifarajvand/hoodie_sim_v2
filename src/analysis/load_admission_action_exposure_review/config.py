from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

FEATURE_ID = "046-load-admission-action-exposure-review"

TraceStrategy = Literal[
    "environment_default_policy_probe",
    "force_local_legal_probe",
    "force_horizontal_legal_probe",
    "force_vertical_legal_probe",
    "mixed_legal_round_robin_probe",
]

TRACE_STRATEGIES: tuple[TraceStrategy, ...] = (
    "environment_default_policy_probe",
    "force_local_legal_probe",
    "force_horizontal_legal_probe",
    "force_vertical_legal_probe",
    "mixed_legal_round_robin_probe",
)


@dataclass(frozen=True, slots=True)
class LoadAdmissionActionExposureConfig:
    feature_id: str = FEATURE_ID
    episode_length: int = 110
    timeout_slots: int = 20
    node_count: int = 20
    arrival_probability: float = 0.5
    seeds: list[int] = field(default_factory=lambda: [0, 1, 2])
    strategies: tuple[TraceStrategy, ...] = TRACE_STRATEGIES
    no_runtime_repair: bool = True
    no_training: bool = True

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("LoadAdmissionActionExposureConfig.feature_id mismatch.")
        if self.episode_length != 110 or self.timeout_slots != 20 or self.node_count != 20:
            raise ValueError("Paper-default runtime constants must remain fixed.")
        if self.arrival_probability != 0.5:
            raise ValueError("arrival_probability must remain 0.5.")
        if list(self.seeds) != [0, 1, 2]:
            raise ValueError("seeds must remain [0, 1, 2].")
        if tuple(self.strategies) != TRACE_STRATEGIES:
            raise ValueError("strategies must match the approved probe grid.")
        if self.no_runtime_repair is not True or self.no_training is not True:
            raise ValueError("diagnostic-only flags must stay true.")
