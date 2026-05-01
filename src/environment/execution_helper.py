from __future__ import annotations

from dataclasses import dataclass

from .task import Task


def derive_cycles_required(size: float, processing_density: float) -> float:
    return float(size) * float(processing_density)


@dataclass(slots=True)
class ExecutionProgressRecord:
    task_id: int
    slot: int
    destination_kind: str
    cycles_before: float
    cycles_consumed: float
    cycles_after: float
    completed: bool


def step_execution(task: Task, compute_capacity: float, *, slot: int, destination_kind: str) -> ExecutionProgressRecord:
    if compute_capacity <= 0:
        raise ValueError("compute_capacity must be greater than zero")

    cycles_before = float(task.cycles_remaining)
    if task.completion_slot is None and cycles_before <= 0.0 and task.cycles_required <= 0.0:
        cycles_before = derive_cycles_required(task.size, task.processing_density)
    cycles_consumed = min(cycles_before, float(compute_capacity))
    cycles_after = max(0.0, cycles_before - float(compute_capacity))
    task.cycles_remaining = cycles_after
    task.metadata["execution_destination_kind"] = destination_kind
    task.metadata["execution_progress_slot"] = slot
    task.metadata["execution_cycles_before"] = cycles_before
    task.metadata["execution_cycles_consumed"] = cycles_consumed
    task.metadata["execution_cycles_after"] = cycles_after
    if cycles_after <= 0.0 and task.completion_slot is None:
        task.completion_slot = slot + 1
    completed = task.completion_slot is not None and task.completion_slot <= slot
    return ExecutionProgressRecord(
        task_id=task.task_id,
        slot=slot,
        destination_kind=destination_kind,
        cycles_before=cycles_before,
        cycles_consumed=cycles_consumed,
        cycles_after=cycles_after,
        completed=completed,
    )
