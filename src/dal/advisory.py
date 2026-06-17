from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DALAdvisory:
    task_id: int | None
    current_slot: int
    absolute_deadline_slot: int | None
    remaining_slots_to_deadline: int | None
    deadline_pressure: str
    private_queue_load: int
    offloading_queue_load: int
    public_queue_load: int
    total_queue_load: int
    local_feasibility: str
    horizontal_feasibility: str
    vertical_feasibility: str
    advisory_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["advisory_notes"] = list(self.advisory_notes)
        return payload


def _deadline_pressure(current_slot: int, absolute_deadline_slot: int | None) -> tuple[str, int | None]:
    if absolute_deadline_slot is None:
        return "none", None
    remaining = absolute_deadline_slot - current_slot
    if current_slot > absolute_deadline_slot:
        return "expired", remaining
    if remaining <= 1:
        return "critical", remaining
    if remaining <= 3:
        return "high", remaining
    if remaining <= 7:
        return "medium", remaining
    return "low", remaining


def _queue_loads(environment: Any) -> tuple[int, int, int]:
    private_load = sum(len(queue.tasks) for queue in getattr(environment, "_private_queues", {}).values())
    offloading_load = sum(len(queue.tasks) for queue in getattr(environment, "_offloading_queues", {}).values())
    public_load = sum(len(queue.tasks) for queue in getattr(environment, "_public_queues", {}).values())
    return private_load, offloading_load, public_load


def _feasibility(deadline_pressure: str, task_present: bool) -> tuple[str, str, str]:
    if not task_present:
        return "blocked_no_task", "blocked_no_task", "blocked_no_task"
    if deadline_pressure in {"expired", "critical"}:
        return "risky_deadline_pressure", "risky_queue_pressure", "risky_queue_pressure"
    if deadline_pressure in {"high", "medium"}:
        return "risky_deadline_pressure", "feasible_if_legal", "feasible_if_legal"
    return "feasible_now", "feasible_if_legal", "feasible_if_legal"


def build_dal_advisory(environment: Any, task: Any | None = None) -> DALAdvisory:
    current_task = task or getattr(environment, "current_task", None)
    task_id = getattr(current_task, "task_id", None)
    absolute_deadline_slot = getattr(current_task, "absolute_deadline_slot", None)
    current_slot = int(getattr(environment, "current_slot", 0))
    deadline_pressure, remaining_slots = _deadline_pressure(current_slot, absolute_deadline_slot)
    private_load, offloading_load, public_load = _queue_loads(environment)
    total_queue_load = private_load + offloading_load + public_load
    local_feasibility, horizontal_feasibility, vertical_feasibility = _feasibility(deadline_pressure, current_task is not None)
    notes: list[str] = [
        "read_only_advisory",
        "deterministic_payload",
    ]
    if deadline_pressure == "expired":
        notes.append("deadline_has_passed")
    elif deadline_pressure in {"critical", "high"}:
        notes.append("deadline_pressure_present")
    if total_queue_load > 0:
        notes.append("queue_pressure_present")
    return DALAdvisory(
        task_id=task_id,
        current_slot=current_slot,
        absolute_deadline_slot=absolute_deadline_slot,
        remaining_slots_to_deadline=remaining_slots,
        deadline_pressure=deadline_pressure,
        private_queue_load=private_load,
        offloading_queue_load=offloading_load,
        public_queue_load=public_load,
        total_queue_load=total_queue_load,
        local_feasibility=local_feasibility,
        horizontal_feasibility=horizontal_feasibility,
        vertical_feasibility=vertical_feasibility,
        advisory_notes=tuple(notes),
    )


def build_dal_advisory_payload(environment: Any, task: Any | None = None) -> dict[str, Any]:
    return build_dal_advisory(environment, task).to_dict()
