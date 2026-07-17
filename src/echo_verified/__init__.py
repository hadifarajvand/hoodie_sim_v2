"""Verified ECHO control primitives locked to the current manuscript.

This package is intentionally isolated from the historical ECHO implementation.
It provides executable specification tests and a deterministic smoke scenario;
it is not itself a substitute for the full HOODIE training campaign.
"""

from .control import (
    EffectiveRouteSet,
    QueueSelection,
    RouteEstimate,
    WaitingTask,
    apply_deadline_drop_penalty,
    build_effective_route_set,
    masked_double_dqn_target,
    masked_epsilon_greedy,
    select_next_waiting_task,
)

__all__ = [
    "EffectiveRouteSet",
    "QueueSelection",
    "RouteEstimate",
    "WaitingTask",
    "apply_deadline_drop_penalty",
    "build_effective_route_set",
    "masked_double_dqn_target",
    "masked_epsilon_greedy",
    "select_next_waiting_task",
]
