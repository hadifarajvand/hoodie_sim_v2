from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import ceil
from typing import Callable, Generic, Iterable, TypeVar

from src.environment.offloading_queue import OffloadingQueue
from src.environment.private_queue import PrivateQueue
from src.environment.task import Task


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ERTPositionEstimate(Generic[T]):
    item: T
    position: int
    source_service_slots: int
    downstream_slots: int
    completion_slot: int
    ert_slots: int
    lateness_slots: int


@dataclass(frozen=True, slots=True)
class ERTOrderResult(Generic[T]):
    ordered_items: tuple[T, ...]
    estimates: tuple[ERTPositionEstimate[T], ...]
    candidate_evaluations: int


def positive_slots(value: float) -> int:
    """Convert a positive amount of work into at least one inclusive slot."""

    return max(1, int(ceil(float(value))))


def construct_ert_order(
    items: Iterable[T],
    *,
    current_slot: int,
    residual_source_slots: int,
    service_slots: Callable[[T], int],
    downstream_slots: Callable[[T], int],
    deadline_slot: Callable[[T], int],
    arrival_slot: Callable[[T], int],
    stable_id: Callable[[T], int],
) -> ERTOrderResult[T]:
    """Construct the non-preemptive ERT order described in Section III-D.

    At each provisional position every unscheduled item is evaluated after the
    already fixed prefix. The smallest non-negative ERT is selected whenever
    any feasible item exists. If all items are predicted late, minimum
    lateness is selected. Original arrival order and stable ID break ties.
    """

    remaining = list(items)
    ordered: list[T] = []
    selected_estimates: list[ERTPositionEstimate[T]] = []
    cumulative_source_slots = max(0, int(residual_source_slots))
    evaluations = 0

    while remaining:
        position = len(ordered)
        candidates: list[ERTPositionEstimate[T]] = []
        for item in remaining:
            source_slots = max(1, int(service_slots(item)))
            tail_slots = max(0, int(downstream_slots(item)))
            completion = (
                int(current_slot)
                + cumulative_source_slots
                + source_slots
                + tail_slots
                - 1
            )
            ert = int(deadline_slot(item)) - completion
            candidates.append(
                ERTPositionEstimate(
                    item=item,
                    position=position,
                    source_service_slots=source_slots,
                    downstream_slots=tail_slots,
                    completion_slot=completion,
                    ert_slots=ert,
                    lateness_slots=max(0, -ert),
                )
            )
            evaluations += 1

        feasible = [candidate for candidate in candidates if candidate.ert_slots >= 0]
        if feasible:
            selected = min(
                feasible,
                key=lambda candidate: (
                    candidate.ert_slots,
                    int(arrival_slot(candidate.item)),
                    int(stable_id(candidate.item)),
                ),
            )
        else:
            selected = min(
                candidates,
                key=lambda candidate: (
                    candidate.lateness_slots,
                    int(arrival_slot(candidate.item)),
                    int(stable_id(candidate.item)),
                ),
            )

        ordered.append(selected.item)
        selected_estimates.append(selected)
        cumulative_source_slots += selected.source_service_slots
        remaining.remove(selected.item)

    return ERTOrderResult(
        ordered_items=tuple(ordered),
        estimates=tuple(selected_estimates),
        candidate_evaluations=evaluations,
    )


def _cycles_to_slots(task: Task, capacity_per_slot: float) -> int:
    if capacity_per_slot <= 0:
        raise ValueError("capacity_per_slot must be positive")
    return positive_slots(max(0.0, float(task.cycles_remaining)) / capacity_per_slot)


def rebuild_private_queue_ert(
    queue: PrivateQueue,
    *,
    current_slot: int,
    capacity_per_slot: float,
) -> ERTOrderResult[Task]:
    """Rebuild only the waiting suffix of a private non-preemptive queue."""

    tasks = list(queue.tasks)
    if not tasks:
        return ERTOrderResult((), (), 0)

    active_head: Task | None = None
    waiting = tasks
    residual_slots = 0
    if tasks[0].computation_start_slot is not None and tasks[0].terminal_outcome is None:
        active_head = tasks[0]
        waiting = tasks[1:]
        residual_slots = _cycles_to_slots(active_head, capacity_per_slot)

    ordered = construct_ert_order(
        waiting,
        current_slot=current_slot,
        residual_source_slots=residual_slots,
        service_slots=lambda task: _cycles_to_slots(task, capacity_per_slot),
        downstream_slots=lambda _task: 0,
        deadline_slot=lambda task: int(task.absolute_deadline_slot),
        arrival_slot=lambda task: int(task.arrival_slot),
        stable_id=lambda task: int(task.task_id),
    )

    prefix = [active_head] if active_head is not None else []
    queue.tasks = deque(prefix + list(ordered.ordered_items))
    if queue.tasks:
        queue.current_head_entered_at = int(
            queue.tasks[0].metadata.get("queue_entered_at", current_slot)
        )
    for index, estimate in enumerate(ordered.estimates, start=len(prefix)):
        estimate.item.metadata["ert_queue_position"] = index
        estimate.item.metadata["ert_queue_completion_estimate"] = estimate.completion_slot
        estimate.item.metadata["ert_queue_value"] = estimate.ert_slots
        estimate.item.metadata["ert_queue_lateness"] = estimate.lateness_slots
    return ordered


def rebuild_offloading_queue_ert(
    queue: OffloadingQueue,
    *,
    current_slot: int,
    destination_waiting_slots: int,
    destination_capacity_per_slot: float,
) -> ERTOrderResult[Task]:
    """Rebuild an outbound queue by end-to-end ERT.

    The active transmission head remains frozen. For the waiting suffix, source
    service is the stored transmission duration. Downstream work includes the
    current destination backlog and the task's own destination computation.
    Since preceding tasks selected into the same outbound prefix will later
    enter the same source-indexed destination queue, their destination service
    is accumulated as part of the downstream estimate for later positions.
    """

    tasks = list(queue.tasks)
    if not tasks:
        return ERTOrderResult((), (), 0)

    active_head: Task | None = None
    waiting = tasks
    residual_slots = 0
    started_at = tasks[0].metadata.get("transmission_started_at")
    if started_at is not None and tasks[0].terminal_outcome is None:
        active_head = tasks[0]
        waiting = tasks[1:]
        total = max(1, int(tasks[0].metadata.get("transmission_delay_slots", 1)))
        residual_slots = max(0, int(started_at) + total - int(current_slot))

    destination_prefix_service = 0

    def downstream(task: Task) -> int:
        nonlocal destination_prefix_service
        return (
            max(0, int(destination_waiting_slots))
            + destination_prefix_service
            + _cycles_to_slots(task, destination_capacity_per_slot)
        )

    # The generic constructor accumulates source transmission service. To also
    # account for the already selected tasks at the destination, rebuild one
    # provisional position at a time and update the destination prefix after
    # each selection.
    remaining = list(waiting)
    selected: list[Task] = []
    estimates: list[ERTPositionEstimate[Task]] = []
    cumulative_source = residual_slots
    evaluations = 0
    while remaining:
        candidates: list[ERTPositionEstimate[Task]] = []
        for task in remaining:
            source_slots = max(1, int(task.metadata.get("transmission_delay_slots", 1)))
            tail_slots = downstream(task)
            completion = (
                int(current_slot)
                + cumulative_source
                + source_slots
                + tail_slots
                - 1
            )
            ert = int(task.absolute_deadline_slot) - completion
            candidates.append(
                ERTPositionEstimate(
                    item=task,
                    position=len(selected),
                    source_service_slots=source_slots,
                    downstream_slots=tail_slots,
                    completion_slot=completion,
                    ert_slots=ert,
                    lateness_slots=max(0, -ert),
                )
            )
            evaluations += 1
        feasible = [candidate for candidate in candidates if candidate.ert_slots >= 0]
        pool = feasible or candidates
        chosen = min(
            pool,
            key=(
                (lambda candidate: (
                    candidate.ert_slots,
                    int(candidate.item.arrival_slot),
                    int(candidate.item.task_id),
                ))
                if feasible
                else (lambda candidate: (
                    candidate.lateness_slots,
                    int(candidate.item.arrival_slot),
                    int(candidate.item.task_id),
                ))
            ),
        )
        selected.append(chosen.item)
        estimates.append(chosen)
        cumulative_source += chosen.source_service_slots
        destination_prefix_service += _cycles_to_slots(
            chosen.item,
            destination_capacity_per_slot,
        )
        remaining.remove(chosen.item)

    result = ERTOrderResult(
        ordered_items=tuple(selected),
        estimates=tuple(estimates),
        candidate_evaluations=evaluations,
    )
    prefix = [active_head] if active_head is not None else []
    queue.tasks = deque(prefix + selected)
    if queue.tasks:
        queue.current_head_entered_at = int(
            queue.tasks[0].metadata.get("queue_entered_at", current_slot)
        )
    for index, estimate in enumerate(result.estimates, start=len(prefix)):
        estimate.item.metadata["ert_queue_position"] = index
        estimate.item.metadata["ert_queue_completion_estimate"] = estimate.completion_slot
        estimate.item.metadata["ert_queue_value"] = estimate.ert_slots
        estimate.item.metadata["ert_queue_lateness"] = estimate.lateness_slots
    return result
