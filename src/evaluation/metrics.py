from __future__ import annotations

from dataclasses import dataclass, field, asdict
from math import isnan
from typing import Iterable

from .metric_formulas import average_delay, drop_ratio, throughput


@dataclass(slots=True)
class TaskEvaluationRecord:
    task_id: int
    arrival_slot: int
    completion_slot: int | None
    terminal_outcome: str | None
    selected_action: str | None
    resolved_destination: str | None
    delay: int | None


@dataclass(slots=True)
class TraceMetrics:
    trace_id: str
    policy_name: str
    seed: int
    device: str
    average_delay: float
    drop_ratio: float
    throughput: int
    completed_tasks: int
    dropped_tasks: int
    total_tasks: int
    raw_records: list[TaskEvaluationRecord] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["raw_records"] = [asdict(record) for record in self.raw_records]
        return payload


def evaluate_trace(
    *,
    trace_id: str,
    policy_name: str,
    seed: int,
    device: str,
    records: Iterable[TaskEvaluationRecord],
) -> TraceMetrics:
    record_list = list(records)
    completed_delays = [record.delay for record in record_list if record.delay is not None]
    completed_tasks = sum(1 for record in record_list if record.terminal_outcome == "completed")
    dropped_tasks = sum(1 for record in record_list if record.terminal_outcome == "dropped")
    total_tasks = len(record_list)
    return TraceMetrics(
        trace_id=trace_id,
        policy_name=policy_name,
        seed=seed,
        device=device,
        average_delay=average_delay(completed_delays),
        drop_ratio=drop_ratio(dropped_tasks, total_tasks),
        throughput=throughput(completed_tasks),
        completed_tasks=completed_tasks,
        dropped_tasks=dropped_tasks,
        total_tasks=total_tasks,
        raw_records=record_list,
        metadata={"trace_id": trace_id, "seed": seed, "device": device, "policy_name": policy_name},
    )


def evaluate_run(trace_metrics: list[TraceMetrics]) -> dict[str, float | int]:
    if not trace_metrics:
        return {"average_delay": 0.0, "drop_ratio": 0.0, "throughput": 0}
    total_completed = sum(metric.completed_tasks for metric in trace_metrics)
    weighted_delay_sum = sum(
        metric.average_delay * metric.completed_tasks for metric in trace_metrics
    )
    average_delay_value = float(weighted_delay_sum / total_completed) if total_completed else 0.0
    drop_ratio_value = drop_ratio(
        sum(metric.dropped_tasks for metric in trace_metrics),
        sum(metric.total_tasks for metric in trace_metrics),
    )
    throughput_value = throughput(total_completed)
    return {
        "average_delay": average_delay_value,
        "drop_ratio": drop_ratio_value,
        "throughput": throughput_value,
    }


def aggregate_terminal_rewards(per_agent_episode_rewards: Iterable[Iterable[float | int | None]]) -> float:
    agent_totals: list[float] = []
    for rewards in per_agent_episode_rewards:
        reward_values: list[float] = []
        for reward in rewards:
            if reward is None:
                continue
            reward_value = float(reward)
            if isnan(reward_value):
                continue
            reward_values.append(reward_value)
        if reward_values:
            agent_totals.append(sum(reward_values))
    if not agent_totals:
        return 0.0
    return float(sum(agent_totals) / len(agent_totals))
