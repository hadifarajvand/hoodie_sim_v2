from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

FEATURE_ID = "042-paper-default-terminal-exposure-probe"

ProbeStrategy = Literal[
    "environment_default_policy_probe",
    "force_local_legal_probe",
    "force_horizontal_legal_probe",
    "force_vertical_legal_probe",
    "mixed_legal_round_robin_probe",
]


@dataclass(slots=True)
class TerminalExposureProbeConfig:
    feature_id: str = FEATURE_ID
    episode_length: int = 110
    timeout_slots: int = 20
    slot_duration_seconds: float = 0.1
    arrival_probability: float = 0.5
    node_count: int = 20
    seeds: list[int] = field(default_factory=lambda: [0, 1, 2])
    strategies: tuple[ProbeStrategy, ...] = (
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
            raise ValueError("TerminalExposureProbeConfig.feature_id must equal 042-paper-default-terminal-exposure-probe.")
        if self.episode_length != 110:
            raise ValueError("TerminalExposureProbeConfig.episode_length must equal 110.")
        if self.timeout_slots != 20:
            raise ValueError("TerminalExposureProbeConfig.timeout_slots must equal 20.")
        if self.slot_duration_seconds != 0.1:
            raise ValueError("TerminalExposureProbeConfig.slot_duration_seconds must equal 0.1.")
        if self.arrival_probability != 0.5:
            raise ValueError("TerminalExposureProbeConfig.arrival_probability must equal 0.5.")
        if self.node_count != 20:
            raise ValueError("TerminalExposureProbeConfig.node_count must equal 20.")
        if list(self.seeds) != [0, 1, 2]:
            raise ValueError("TerminalExposureProbeConfig.seeds must equal [0, 1, 2].")
        if self.no_training is not True:
            raise ValueError("TerminalExposureProbeConfig.no_training must remain true.")
        if self.no_runtime_mutation is not True:
            raise ValueError("TerminalExposureProbeConfig.no_runtime_mutation must remain true.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "episode_length": self.episode_length,
            "timeout_slots": self.timeout_slots,
            "slot_duration_seconds": self.slot_duration_seconds,
            "arrival_probability": self.arrival_probability,
            "node_count": self.node_count,
            "seeds": list(self.seeds),
            "strategies": list(self.strategies),
            "no_training": self.no_training,
            "no_runtime_mutation": self.no_runtime_mutation,
        }
