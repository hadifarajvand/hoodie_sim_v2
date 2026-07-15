from __future__ import annotations

from statistics import mean, pstdev

from .schemas import AggregateRecord, TaskRecord


def aggregate_records(records: list[TaskRecord], *, denominator_contract: str = "offered") -> AggregateRecord:
    offered = len(records)
    completed = sum(1 for record in records if record.outcome == "completed")
    dropped = sum(1 for record in records if record.outcome == "dropped")
    delays = [record.end_to_end_delay for record in records if record.end_to_end_delay is not None]
    action_distribution: dict[str, int] = {}
    reward_sum = 0.0
    for record in records:
        action_distribution[record.selected_action] = action_distribution.get(record.selected_action, 0) + 1
        reward_sum += record.reward
    average_delay = mean(delays) if delays else 0.0
    spread = pstdev(delays) if len(delays) > 1 else 0.0
    completion_ratio = completed / offered if offered else 0.0
    drop_ratio = dropped / offered if offered else 0.0
    return AggregateRecord(offered, completed, dropped, completion_ratio, drop_ratio, average_delay, {"delay": spread}, action_distribution, {"reward": reward_sum}, (average_delay - spread, average_delay + spread), 1, denominator_contract)
