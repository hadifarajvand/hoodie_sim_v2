from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from src.environment.task import Task


@dataclass(slots=True)
class TraceTaskBlueprint:
    task_id: int
    source_agent_id: int
    arrival_slot: int
    size: float
    processing_density: float
    timeout_length: int
    absolute_deadline_slot: int
    cycles_required: float = 0.0
    cycles_remaining: float = 0.0

    def __post_init__(self) -> None:
        self.size = float(self.size)
        self.processing_density = float(self.processing_density)
        self.cycles_required = float(self.cycles_required or self.size * self.processing_density)
        self.cycles_remaining = float(self.cycles_remaining or self.cycles_required)
        if self.cycles_remaining > self.cycles_required:
            self.cycles_remaining = float(self.cycles_required)

    def build(self) -> Task:
        return Task(
            task_id=self.task_id,
            source_agent_id=self.source_agent_id,
            arrival_slot=self.arrival_slot,
            size=self.size,
            processing_density=self.processing_density,
            timeout_length=self.timeout_length,
            absolute_deadline_slot=self.absolute_deadline_slot,
            cycles_required=self.cycles_required,
            cycles_remaining=self.cycles_remaining,
        )


@dataclass(slots=True)
class EvaluationTrace:
    trace_id: str
    seed: int
    tasks: tuple[TraceTaskBlueprint, ...]
    metadata: dict[str, str] = field(default_factory=dict)


def build_deterministic_trace(trace_id: str, seed: int, episode_length: int) -> EvaluationTrace:
    rng = Random(seed)
    tasks: list[TraceTaskBlueprint] = []
    for index in range(episode_length):
        arrival_slot = index
        size = rng.randint(10, 100)
        processing_density = rng.randint(1, 5)
        timeout_length = rng.randint(2, 5)
        absolute_deadline_slot = arrival_slot + timeout_length
        tasks.append(
            TraceTaskBlueprint(
                task_id=index + 1,
                source_agent_id=(index % 3) + 1,
                arrival_slot=arrival_slot,
                size=size,
                processing_density=processing_density,
                timeout_length=timeout_length,
                absolute_deadline_slot=absolute_deadline_slot,
            )
        )
    return EvaluationTrace(
        trace_id=trace_id,
        seed=seed,
        tasks=tuple(tasks),
        metadata={"mode": "deterministic_seed", "trace_id": trace_id, "seed": str(seed)},
    )


def trace_signature(trace: EvaluationTrace) -> dict[str, object]:
    return {
        "trace_id": trace.trace_id,
        "seed": trace.seed,
        "episode_length": len(trace.tasks),
        "mode": trace.metadata.get("mode", "deterministic_seed"),
    }
