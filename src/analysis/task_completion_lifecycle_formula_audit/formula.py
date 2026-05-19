from __future__ import annotations

from dataclasses import dataclass

from src.environment.link_rate_config import compute_transmission_delay, mbits_to_bits, seconds_to_slots


@dataclass(frozen=True, slots=True)
class ExpectedCompletionEstimate:
    task_size_mbits: float
    task_cycles_gcycles: float
    local_compute_slots: int
    public_compute_slots: int
    cloud_compute_slots: int
    horizontal_transmission_slots: int
    vertical_transmission_slots: int
    local_min_total_slots: int
    horizontal_min_total_slots: int
    vertical_min_total_slots: int

    def to_dict(self) -> dict[str, object]:
        return {
            "task_size_mbits": self.task_size_mbits,
            "task_cycles_gcycles": self.task_cycles_gcycles,
            "local_compute_slots": self.local_compute_slots,
            "public_compute_slots": self.public_compute_slots,
            "cloud_compute_slots": self.cloud_compute_slots,
            "horizontal_transmission_slots": self.horizontal_transmission_slots,
            "vertical_transmission_slots": self.vertical_transmission_slots,
            "local_min_total_slots": self.local_min_total_slots,
            "horizontal_min_total_slots": self.horizontal_min_total_slots,
            "vertical_min_total_slots": self.vertical_min_total_slots,
        }


class FormulaAuditCalculator:
    def __init__(self, *, slot_duration_seconds: float = 0.1, processing_density_gcycles_per_mbit: float = 0.297, cpu_private_gcycles_per_slot: float = 0.5, cpu_public_gcycles_per_slot: float = 0.5, cpu_cloud_gcycles_per_slot: float = 3.0, horizontal_rate_mbps: float = 30.0, vertical_rate_mbps: float = 10.0) -> None:
        self.slot_duration_seconds = slot_duration_seconds
        self.processing_density_gcycles_per_mbit = processing_density_gcycles_per_mbit
        self.cpu_private_gcycles_per_slot = cpu_private_gcycles_per_slot
        self.cpu_public_gcycles_per_slot = cpu_public_gcycles_per_slot
        self.cpu_cloud_gcycles_per_slot = cpu_cloud_gcycles_per_slot
        self.horizontal_rate_mbps = horizontal_rate_mbps
        self.vertical_rate_mbps = vertical_rate_mbps

    def compute_task_cycles_gcycles(self, task_size_mbits: float) -> float:
        return float(task_size_mbits) * float(self.processing_density_gcycles_per_mbit)

    def compute_execution_slots(self, task_size_mbits: float, cpu_gcycles_per_slot: float) -> int:
        cycles = self.compute_task_cycles_gcycles(task_size_mbits)
        return seconds_to_slots(cycles / cpu_gcycles_per_slot, 1.0, rounding_policy="ceil")

    def compute_local_slots(self, task_size_mbits: float) -> int:
        return self.compute_execution_slots(task_size_mbits, self.cpu_private_gcycles_per_slot)

    def compute_public_slots(self, task_size_mbits: float) -> int:
        return self.compute_execution_slots(task_size_mbits, self.cpu_public_gcycles_per_slot)

    def compute_cloud_slots(self, task_size_mbits: float) -> int:
        return self.compute_execution_slots(task_size_mbits, self.cpu_cloud_gcycles_per_slot)

    def compute_transmission_slots(self, task_size_mbits: float, rate_mbps: float) -> int:
        result = compute_transmission_delay(
            payload_bits=mbits_to_bits(task_size_mbits),
            data_rate_bps=rate_mbps * 1_000_000.0,
            slot_duration_seconds=self.slot_duration_seconds,
            rounding_policy="ceil",
        )
        return result.delay_slots

    def build_estimate(self, task_size_mbits: float) -> ExpectedCompletionEstimate:
        local_compute_slots = self.compute_local_slots(task_size_mbits)
        public_compute_slots = self.compute_public_slots(task_size_mbits)
        cloud_compute_slots = self.compute_cloud_slots(task_size_mbits)
        horizontal_transmission_slots = self.compute_transmission_slots(task_size_mbits, self.horizontal_rate_mbps)
        vertical_transmission_slots = self.compute_transmission_slots(task_size_mbits, self.vertical_rate_mbps)
        return ExpectedCompletionEstimate(
            task_size_mbits=float(task_size_mbits),
            task_cycles_gcycles=self.compute_task_cycles_gcycles(task_size_mbits),
            local_compute_slots=local_compute_slots,
            public_compute_slots=public_compute_slots,
            cloud_compute_slots=cloud_compute_slots,
            horizontal_transmission_slots=horizontal_transmission_slots,
            vertical_transmission_slots=vertical_transmission_slots,
            local_min_total_slots=local_compute_slots,
            horizontal_min_total_slots=horizontal_transmission_slots + public_compute_slots,
            vertical_min_total_slots=vertical_transmission_slots + cloud_compute_slots,
        )

