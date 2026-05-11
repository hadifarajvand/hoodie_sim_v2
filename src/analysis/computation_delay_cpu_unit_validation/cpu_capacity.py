from __future__ import annotations

from dataclasses import dataclass

from src.environment.compute_config import ComputeConfig


@dataclass(frozen=True, slots=True)
class CpuCapacityEntry:
    name: str
    value: float | None
    status: str
    source: str
    notes: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": self.value,
            "status": self.status,
            "source": self.source,
            "notes": self.notes,
        }


def build_cpu_capacity_contract() -> dict[str, object]:
    compute = ComputeConfig()
    return {
        "EA_private": CpuCapacityEntry(
            name="EA_private",
            value=None,
            status="unrecoverable",
            source="resources/papers/hoodie/recovered/paper-parameter-registry.json",
            notes="Paper evidence does not recover an EA private CPU capacity.",
        ).to_dict(),
        "EA_public": CpuCapacityEntry(
            name="EA_public",
            value=None,
            status="unrecoverable",
            source="resources/papers/hoodie/recovered/paper-parameter-registry.json",
            notes="Paper evidence does not recover an EA public CPU capacity.",
        ).to_dict(),
        "cloud": CpuCapacityEntry(
            name="cloud",
            value=None,
            status="unrecoverable",
            source="resources/papers/hoodie/recovered/paper-parameter-registry.json",
            notes="Paper evidence does not recover a cloud CPU capacity.",
        ).to_dict(),
        "runtime": {
            "cpu_capacity_per_slot_agent": compute.cpu_capacity_per_slot_agent,
            "cpu_capacity_per_slot_edge": compute.cpu_capacity_per_slot_edge,
            "cpu_capacity_per_slot_cloud": compute.cpu_capacity_per_slot_cloud,
        },
    }
