from __future__ import annotations

from statistics import mean


def average_delay(completion_delays: list[int]) -> float:
    if not completion_delays:
        return 0.0
    return float(mean(completion_delays))


def drop_ratio(dropped_tasks: int, total_tasks: int) -> float:
    if total_tasks <= 0:
        return 0.0
    return dropped_tasks / total_tasks


def throughput(completed_tasks: int) -> int:
    return completed_tasks
