from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from random import Random
import json
from typing import Any

from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint

from .traffic_config import TrafficConfig


def _size_for_task(config: TrafficConfig, task_id: int, seed: int) -> float:
    values = config.task_size_values
    if not values:
        raise ValueError("Traffic configuration produced no task-size values")
    return values[(seed + task_id - 1) % len(values)]


@dataclass(slots=True)
class TrafficTrace:
    trace_id: str
    seed: int
    config: TrafficConfig
    records: tuple[TraceTaskBlueprint, ...]
    metadata: dict[str, str] = field(default_factory=dict)
    _evaluation_trace: EvaluationTrace | None = field(default=None, repr=False, compare=False)

    @property
    def evaluation_trace(self) -> EvaluationTrace:
        if self._evaluation_trace is None:
            self._evaluation_trace = EvaluationTrace(
                trace_id=self.trace_id,
                seed=self.seed,
                tasks=self.records,
                metadata=dict(self.metadata),
            )
        return self._evaluation_trace

    @property
    def summary(self) -> "TrafficSummary":
        from .traffic_observer import summarize_traffic

        return summarize_traffic(self.evaluation_trace, self.config, self.seed)

    def to_trace_payload(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "seed": self.seed,
            "metadata": dict(self.metadata),
            "tasks": [
                {
                    "task_id": blueprint.task_id,
                    "source_agent_id": blueprint.source_agent_id,
                    "arrival_slot": blueprint.arrival_slot,
                    "size": blueprint.size,
                    "processing_density": blueprint.processing_density,
                    "timeout_length": blueprint.timeout_length,
                    "absolute_deadline_slot": blueprint.absolute_deadline_slot,
                }
                for blueprint in self.records
            ],
        }

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_trace_payload(), indent=2), encoding="utf-8")


@dataclass(slots=True)
class TrafficGenerator:
    @staticmethod
    def generate(config: TrafficConfig, seed: int) -> TrafficTrace:
        rng = Random(seed)
        tasks: list[TraceTaskBlueprint] = []
        task_id = 0
        for arrival_slot in range(config.episode_length):
            for source_agent_id in range(1, config.number_of_agents + 1):
                if rng.random() >= config.arrival_probability:
                    continue
                task_id += 1
                size = _size_for_task(config, task_id, seed)
                timeout_length = config.timeout_slots
                absolute_deadline_slot = arrival_slot + timeout_length
                tasks.append(
                    TraceTaskBlueprint(
                        task_id=task_id,
                        source_agent_id=source_agent_id,
                        arrival_slot=arrival_slot,
                        size=size,
                        processing_density=config.processing_density_gcycles_per_mbit,
                        timeout_length=timeout_length,
                        absolute_deadline_slot=absolute_deadline_slot,
                    )
                )
        tasks.sort(key=lambda blueprint: (blueprint.arrival_slot, blueprint.source_agent_id, blueprint.task_id))
        trace_id = f"{config.scenario_name}-{seed}"
        metadata = {
            "scenario_name": config.scenario_name,
            "seed": str(seed),
            "configured_arrival_probability": str(config.arrival_probability),
            "number_of_agents": str(config.number_of_agents),
            "episode_length": str(config.episode_length),
            "slot_duration_seconds": str(config.slot_duration_seconds),
            "timeout_slots": str(config.timeout_slots),
            "task_size_mbits_min": str(config.task_size_mbits_min),
            "task_size_mbits_max": str(config.task_size_mbits_max),
            "task_size_mbits_step": str(config.task_size_mbits_step),
            "processing_density_gcycles_per_mbit": str(config.processing_density_gcycles_per_mbit),
        }
        return TrafficTrace(
            trace_id=trace_id,
            seed=seed,
            config=config,
            records=tuple(tasks),
            metadata=metadata,
        )


def generate_traffic_trace(config: TrafficConfig, seed: int) -> TrafficTrace:
    return TrafficGenerator.generate(config, seed)


def generate_traffic_evaluation_trace(config: TrafficConfig, seed: int) -> EvaluationTrace:
    return TrafficGenerator.generate(config, seed).evaluation_trace
