from __future__ import annotations

from dataclasses import dataclass
from math import ceil


def compute_cycles_required(task_size_mbits: float, processing_density_gcycles_per_mbit: float) -> float:
    if task_size_mbits < 0:
        raise ValueError("task_size_mbits must be greater than or equal to zero")
    if processing_density_gcycles_per_mbit <= 0:
        raise ValueError("processing_density_gcycles_per_mbit must be greater than zero")
    return float(task_size_mbits) * float(processing_density_gcycles_per_mbit)


def compute_delay_slots(cycles_required: float, cpu_capacity_per_slot: float) -> int:
    if cycles_required < 0:
        raise ValueError("cycles_required must be greater than or equal to zero")
    if cpu_capacity_per_slot <= 0:
        raise ValueError("cpu_capacity_per_slot must be greater than zero")
    if cycles_required == 0:
        return 0
    return int(ceil(float(cycles_required) / float(cpu_capacity_per_slot)))


@dataclass(frozen=True, slots=True)
class ComputationDelayExample:
    task_size_mbits: float
    processing_density_gcycles_per_mbit: float
    cycles_required: float
    cpu_capacity_per_slot: float
    delay_slots: int

    def to_dict(self) -> dict[str, object]:
        return {
            "task_size_mbits": self.task_size_mbits,
            "processing_density_gcycles_per_mbit": self.processing_density_gcycles_per_mbit,
            "cycles_required": self.cycles_required,
            "cpu_capacity_per_slot": self.cpu_capacity_per_slot,
            "delay_slots": self.delay_slots,
        }
