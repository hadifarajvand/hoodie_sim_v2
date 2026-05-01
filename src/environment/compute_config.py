from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ComputeConfig:
    cpu_capacity_per_slot_agent: float = 32.0
    cpu_capacity_per_slot_edge: float = 64.0
    cpu_capacity_per_slot_cloud: float = 128.0

    def __post_init__(self) -> None:
        if self.cpu_capacity_per_slot_agent <= 0:
            raise ValueError("cpu_capacity_per_slot_agent must be greater than zero")
        if self.cpu_capacity_per_slot_edge <= 0:
            raise ValueError("cpu_capacity_per_slot_edge must be greater than zero")
        if self.cpu_capacity_per_slot_cloud <= 0:
            raise ValueError("cpu_capacity_per_slot_cloud must be greater than zero")

    def capacity_for(self, destination_kind: str) -> float:
        if destination_kind in {"agent", "local", "self"}:
            return self.cpu_capacity_per_slot_agent
        if destination_kind in {"edge", "public", "horizontal"}:
            return self.cpu_capacity_per_slot_edge
        if destination_kind in {"cloud", "vertical"}:
            return self.cpu_capacity_per_slot_cloud
        raise ValueError(f"Unsupported execution destination: {destination_kind}")
