from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Callable, Generic, Iterable, TypeVar


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
    already fixed prefix.  The smallest non-negative ERT is selected whenever
    any feasible item exists.  If all items are predicted late, minimum
    lateness is selected.  Original arrival order and stable ID break ties.
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
