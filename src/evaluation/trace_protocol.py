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


def build_deterministic_trace(
    trace_id: str,
    seed: int,
    episode_length: int,
    *,
    agent_count: int = 20,
    arrival_probability: float = 1.0,
    timeout_length: int = 20,
    drain_slots: int = 0,
) -> EvaluationTrace:
    """Build one paired task trace using the paper-compatible arrival process.

    Every EA receives an independent Bernoulli arrival opportunity in every
    decision slot.  The final ``drain_slots`` contain no arrivals and are kept
    in the trace metadata so all policies execute the same episode horizon.

    ``drain_slots`` defaults to zero for backward compatibility.  Paper-default
    experiments call this function with ``episode_length=110`` and
    ``drain_slots=10``, yielding 100 decision slots followed by 10 drain slots.
    """

    if episode_length <= 0:
        raise ValueError("episode_length must be positive")
    if agent_count <= 0:
        raise ValueError("agent_count must be positive")
    if not 0.0 <= float(arrival_probability) <= 1.0:
        raise ValueError("arrival_probability must be in [0, 1]")
    if timeout_length <= 0:
        raise ValueError("timeout_length must be positive")
    if not 0 <= drain_slots < episode_length:
        raise ValueError("drain_slots must satisfy 0 <= drain_slots < episode_length")

    rng = Random(seed)
    tasks: list[TraceTaskBlueprint] = []
    next_task_id = 1
    decision_slots = episode_length - drain_slots
    admissible_sizes = tuple(round(2.0 + 0.1 * index, 1) for index in range(31))

    for arrival_slot in range(decision_slots):
        for source_agent_id in range(1, agent_count + 1):
            if rng.random() > float(arrival_probability):
                continue
            size = rng.choice(admissible_sizes)
            processing_density = 0.297
            absolute_deadline_slot = arrival_slot + timeout_length - 1
            tasks.append(
                TraceTaskBlueprint(
                    task_id=next_task_id,
                    source_agent_id=source_agent_id,
                    arrival_slot=arrival_slot,
                    size=size,
                    processing_density=processing_density,
                    timeout_length=timeout_length,
                    absolute_deadline_slot=absolute_deadline_slot,
                )
            )
            next_task_id += 1

    return EvaluationTrace(
        trace_id=trace_id,
        seed=seed,
        tasks=tuple(tasks),
        metadata={
            "mode": "independent_bernoulli_per_ea",
            "trace_id": trace_id,
            "seed": str(seed),
            "agent_count": str(agent_count),
            "arrival_probability": str(float(arrival_probability)),
            "episode_length": str(episode_length),
            "decision_slots": str(decision_slots),
            "drain_slots": str(drain_slots),
            "task_count": str(len(tasks)),
        },
    )


def trace_signature(trace: EvaluationTrace) -> dict[str, object]:
    return {
        "trace_id": trace.trace_id,
        "seed": trace.seed,
        "episode_length": int(trace.metadata.get("episode_length", len(trace.tasks))),
        "decision_slots": int(trace.metadata.get("decision_slots", len(trace.tasks))),
        "drain_slots": int(trace.metadata.get("drain_slots", 0)),
        "task_count": len(trace.tasks),
        "mode": trace.metadata.get("mode", "deterministic_seed"),
    }
