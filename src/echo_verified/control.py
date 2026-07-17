from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Sequence


@dataclass(frozen=True, slots=True)
class WaitingTask:
    task_id: str
    arrival_slot: int
    deadline_slot: int
    source_service_slots: int
    downstream_slots: int = 0


@dataclass(frozen=True, slots=True)
class QueueCandidate:
    task: WaitingTask
    predicted_completion_slot: int
    ert_slots: int
    lateness_slots: int


@dataclass(frozen=True, slots=True)
class QueueSelection:
    selected: WaitingTask | None
    candidates: tuple[QueueCandidate, ...]
    expired_task_ids: tuple[str, ...]
    used_minimum_lateness: bool


@dataclass(frozen=True, slots=True)
class RouteEstimate:
    route_id: str
    route_index: int
    predicted_completion_slot: int
    deadline_slot: int
    physically_available: bool = True

    @property
    def ert_slots(self) -> int:
        return int(self.deadline_slot) - int(self.predicted_completion_slot)

    @property
    def lateness_slots(self) -> int:
        return max(0, -self.ert_slots)


@dataclass(frozen=True, slots=True)
class EffectiveRouteSet:
    allowed_route_ids: tuple[str, ...]
    mask: tuple[bool, ...]
    fallback_route_id: str | None
    filtered_route_ids: tuple[str, ...]
    physical_route_ids: tuple[str, ...]


def select_next_waiting_task(
    tasks: Sequence[WaitingTask],
    *,
    current_slot: int,
    residual_active_service_slots: int = 0,
) -> QueueSelection:
    """Select the next waiting source task at an idle-resource opportunity.

    The caller must invoke this only when the source processor or transmitter is
    idle. Active work is not represented in ``tasks`` and is never preempted.
    Expired waiting tasks are excluded. Every remaining task is evaluated as if
    served next, matching the current manuscript's service-opportunity rule.
    """

    if residual_active_service_slots < 0:
        raise ValueError("residual_active_service_slots must be non-negative")

    expired = tuple(
        task.task_id for task in tasks if int(task.deadline_slot) < int(current_slot)
    )
    candidates: list[QueueCandidate] = []
    for task in tasks:
        if int(task.deadline_slot) < int(current_slot):
            continue
        completion = (
            int(current_slot)
            + int(residual_active_service_slots)
            + int(task.source_service_slots)
            + int(task.downstream_slots)
            - 1
        )
        ert = int(task.deadline_slot) - completion
        candidates.append(
            QueueCandidate(
                task=task,
                predicted_completion_slot=completion,
                ert_slots=ert,
                lateness_slots=max(0, -ert),
            )
        )

    if not candidates:
        return QueueSelection(
            selected=None,
            candidates=(),
            expired_task_ids=expired,
            used_minimum_lateness=False,
        )

    feasible = [candidate for candidate in candidates if candidate.ert_slots >= 0]
    if feasible:
        chosen = min(
            feasible,
            key=lambda candidate: (
                candidate.ert_slots,
                candidate.task.arrival_slot,
                candidate.task.task_id,
            ),
        )
        used_minimum_lateness = False
    else:
        chosen = min(
            candidates,
            key=lambda candidate: (
                candidate.lateness_slots,
                candidate.task.arrival_slot,
                candidate.task.task_id,
            ),
        )
        used_minimum_lateness = True

    return QueueSelection(
        selected=chosen.task,
        candidates=tuple(candidates),
        expired_task_ids=expired,
        used_minimum_lateness=used_minimum_lateness,
    )


def build_effective_route_set(
    estimates: Sequence[RouteEstimate],
) -> EffectiveRouteSet:
    """Apply physical availability, deadline filtering, and all-late fallback."""

    ordered = tuple(sorted(estimates, key=lambda estimate: estimate.route_index))
    physical = tuple(estimate for estimate in ordered if estimate.physically_available)
    if not physical:
        raise ValueError("at least one physical route is required")

    feasible = tuple(estimate for estimate in physical if estimate.ert_slots >= 0)
    fallback: RouteEstimate | None = None
    if feasible:
        allowed = feasible
    else:
        fallback = min(
            physical,
            key=lambda estimate: (estimate.lateness_slots, estimate.route_index),
        )
        allowed = (fallback,)

    allowed_ids = {estimate.route_id for estimate in allowed}
    physical_ids = tuple(estimate.route_id for estimate in physical)
    filtered = tuple(
        estimate.route_id for estimate in physical if estimate.route_id not in allowed_ids
    )
    mask = tuple(
        estimate.physically_available and estimate.route_id in allowed_ids
        for estimate in ordered
    )
    return EffectiveRouteSet(
        allowed_route_ids=tuple(estimate.route_id for estimate in allowed),
        mask=mask,
        fallback_route_id=fallback.route_id if fallback is not None else None,
        filtered_route_ids=filtered,
        physical_route_ids=physical_ids,
    )


def _legal_indices(mask: Sequence[bool]) -> tuple[int, ...]:
    legal = tuple(index for index, allowed in enumerate(mask) if bool(allowed))
    if not legal:
        raise ValueError("mask contains no legal action")
    return legal


def masked_epsilon_greedy(
    q_values: Sequence[float],
    mask: Sequence[bool],
    *,
    epsilon: float,
    rng: random.Random,
) -> int:
    """Use the same mask for exploration and exploitation."""

    if len(q_values) != len(mask):
        raise ValueError("q_values and mask must have the same length")
    legal = _legal_indices(mask)
    epsilon = min(1.0, max(0.0, float(epsilon)))
    if rng.random() < epsilon:
        return rng.choice(legal)
    best_value = max(float(q_values[index]) for index in legal)
    return min(index for index in legal if math.isclose(float(q_values[index]), best_value))


def masked_double_dqn_target(
    *,
    reward: float,
    gamma: float,
    terminal: bool,
    online_next_q: Sequence[float],
    target_next_q: Sequence[float],
    next_mask: Sequence[bool],
) -> tuple[float, int | None]:
    """Select the next action online under the mask, then evaluate it in target Q."""

    if terminal:
        return float(reward), None
    if not (len(online_next_q) == len(target_next_q) == len(next_mask)):
        raise ValueError("next-state arrays must have the same length")
    legal = _legal_indices(next_mask)
    best_value = max(float(online_next_q[index]) for index in legal)
    selected = min(
        index for index in legal if math.isclose(float(online_next_q[index]), best_value)
    )
    target = float(reward) + float(gamma) * float(target_next_q[selected])
    return target, selected


def apply_deadline_drop_penalty(
    base_reward: float,
    *,
    dropped: bool,
    fixed_penalty: float,
) -> float:
    """Apply exactly one additional fixed penalty to a realized deadline drop."""

    if fixed_penalty < 0:
        raise ValueError("fixed_penalty must be non-negative")
    return float(base_reward) - (float(fixed_penalty) if dropped else 0.0)


def observation_contains_ert(feature_names: Sequence[str]) -> bool:
    """Fail-closed helper used by tests and smoke reports."""

    forbidden = ("ert", "lateness", "deadline_mask", "route_mask")
    return any(any(token in name.lower() for token in forbidden) for name in feature_names)


def assert_task_conservation(*, generated: int, successful: int, dropped: int) -> None:
    if generated < 0 or successful < 0 or dropped < 0:
        raise ValueError("task counts must be non-negative")
    if int(generated) != int(successful) + int(dropped):
        raise AssertionError(
            f"task conservation violated: generated={generated}, "
            f"successful={successful}, dropped={dropped}"
        )
