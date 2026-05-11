from __future__ import annotations

from dataclasses import dataclass

from .computation_delay import compute_delay_slots


@dataclass(frozen=True, slots=True)
class CompletionSlotContract:
    formula: str
    current_slot: int
    cycles_required: float
    cpu_capacity_per_slot: float
    delay_slots: int
    completion_slot: int
    zero_delay_policy: str

    def to_dict(self) -> dict[str, object]:
        return {
            "formula": self.formula,
            "current_slot": self.current_slot,
            "cycles_required": self.cycles_required,
            "cpu_capacity_per_slot": self.cpu_capacity_per_slot,
            "delay_slots": self.delay_slots,
            "completion_slot": self.completion_slot,
            "zero_delay_policy": self.zero_delay_policy,
        }


def compute_completion_slot(current_slot: int, cycles_required: float, cpu_capacity_per_slot: float) -> CompletionSlotContract:
    if current_slot < 0:
        raise ValueError("current_slot must be greater than or equal to zero")
    delay_slots = compute_delay_slots(cycles_required, cpu_capacity_per_slot)
    return CompletionSlotContract(
        formula="completion_slot = current_slot + delay_slots; delay_slots = ceil(cycles_required / cpu_capacity_per_slot)",
        current_slot=current_slot,
        cycles_required=float(cycles_required),
        cpu_capacity_per_slot=float(cpu_capacity_per_slot),
        delay_slots=delay_slots,
        completion_slot=current_slot + delay_slots,
        zero_delay_policy="explicit_zero_delay",
    )
