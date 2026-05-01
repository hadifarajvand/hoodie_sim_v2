from __future__ import annotations

from dataclasses import dataclass

from src.evaluation.trace_protocol import EvaluationTrace

from .traffic_config import TrafficConfig


@dataclass(slots=True)
class TrafficSummary:
    scenario_name: str
    seed: int
    configured_arrival_probability: float
    observed_arrival_probability: float
    total_arrivals: int
    arrivals_per_slot: tuple[int, ...]
    arrivals_per_agent: dict[str, int]
    task_size_mbits_range: tuple[float, float]


def _window_bounds(trace: EvaluationTrace, window_slots: int | None, config: TrafficConfig) -> tuple[int, int]:
    trace_end_slot = max((task.arrival_slot for task in trace.tasks), default=config.episode_length - 1)
    if window_slots is None:
        return 0, config.episode_length
    width = min(max(1, window_slots), config.episode_length)
    start_slot = max(0, trace_end_slot + 1 - width)
    return start_slot, start_slot + width


def summarize_traffic(
    trace: EvaluationTrace,
    config: TrafficConfig,
    seed: int,
    window_slots: int | None = None,
) -> TrafficSummary:
    start_slot, end_slot = _window_bounds(trace, window_slots, config)
    relevant_tasks = [task for task in trace.tasks if start_slot <= task.arrival_slot < end_slot]
    slot_counts = [0 for _ in range(end_slot - start_slot)]
    agent_counts = {str(agent_id): 0 for agent_id in range(1, config.number_of_agents + 1)}
    for task in relevant_tasks:
        slot_counts[task.arrival_slot - start_slot] += 1
        agent_key = str(task.source_agent_id)
        agent_counts[agent_key] = agent_counts.get(agent_key, 0) + 1
    window_width = max(1, end_slot - start_slot)
    return TrafficSummary(
        scenario_name=config.scenario_name,
        seed=seed,
        configured_arrival_probability=config.arrival_probability,
        observed_arrival_probability=len(relevant_tasks) / float(config.number_of_agents * window_width),
        total_arrivals=len(relevant_tasks),
        arrivals_per_slot=tuple(slot_counts),
        arrivals_per_agent=dict(sorted(agent_counts.items(), key=lambda item: int(item[0]))),
        task_size_mbits_range=(config.task_size_mbits_min, config.task_size_mbits_max),
    )


class TrafficObserver:
    @staticmethod
    def summarize(
        trace: EvaluationTrace,
        config: TrafficConfig,
        seed: int,
        window_slots: int | None = None,
    ) -> TrafficSummary:
        return summarize_traffic(trace, config, seed, window_slots=window_slots)
