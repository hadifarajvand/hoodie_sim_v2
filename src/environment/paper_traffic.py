from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any


TASK_SIZE_SET_MBITS: tuple[float, ...] = tuple(round(2.0 + 0.1 * index, 1) for index in range(0, 31))
PAPER_TRAFFIC_VERSION = "paper_traffic_v1"


@dataclass(slots=True)
class PaperTrafficContract:
    edge_agent_count: int
    slot_count: int
    arrival_probability_p: float
    seed: int
    arrivals_by_slot_agent: tuple[tuple[int, ...], ...]
    generated_task_count: int
    no_task_count: int
    deterministic_replay_available: bool
    traffic_model_version: str = PAPER_TRAFFIC_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_agent_count": self.edge_agent_count,
            "slot_count": self.slot_count,
            "arrival_probability_p": self.arrival_probability_p,
            "seed": self.seed,
            "arrivals_by_slot_agent": [list(row) for row in self.arrivals_by_slot_agent],
            "generated_task_count": self.generated_task_count,
            "no_task_count": self.no_task_count,
            "deterministic_replay_available": self.deterministic_replay_available,
            "traffic_model_version": self.traffic_model_version,
        }


@dataclass(slots=True)
class TaskSizeSample:
    task_size_mbits: float
    task_size_source: str
    task_size_set: tuple[float, ...]
    task_size_seed: int
    task_size_distribution: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_size_mbits": self.task_size_mbits,
            "task_size_source": self.task_size_source,
            "task_size_set": list(self.task_size_set),
            "task_size_seed": self.task_size_seed,
            "task_size_distribution": self.task_size_distribution,
        }


@dataclass(slots=True)
class ProcessingDensityContract:
    processing_density_gcycles_per_mbit: float
    processing_cycles_gcycles: float
    task_size_mbits: float
    density_source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "processing_density_gcycles_per_mbit": self.processing_density_gcycles_per_mbit,
            "processing_cycles_gcycles": self.processing_cycles_gcycles,
            "task_size_mbits": self.task_size_mbits,
            "density_source": self.density_source,
        }


def build_bernoulli_arrivals(*, edge_agent_count: int = 20, slot_count: int = 110, arrival_probability_p: float = 0.5, seed: int = 7) -> PaperTrafficContract:
    rng = Random(seed)
    arrivals: list[tuple[int, ...]] = []
    generated = 0
    for _slot in range(slot_count):
        row = tuple(1 if rng.random() < arrival_probability_p else 0 for _agent in range(edge_agent_count))
        generated += sum(row)
        arrivals.append(row)
    total_slots = edge_agent_count * slot_count
    return PaperTrafficContract(
        edge_agent_count=edge_agent_count,
        slot_count=slot_count,
        arrival_probability_p=arrival_probability_p,
        seed=seed,
        arrivals_by_slot_agent=tuple(arrivals),
        generated_task_count=generated,
        no_task_count=total_slots - generated,
        deterministic_replay_available=True,
    )


def build_task_size_sample(*, task_size_seed: int = 7, index: int = 0, deterministic_cycle: bool = True) -> TaskSizeSample:
    task_size = TASK_SIZE_SET_MBITS[index % len(TASK_SIZE_SET_MBITS)] if deterministic_cycle else Random(task_size_seed).choice(TASK_SIZE_SET_MBITS)
    return TaskSizeSample(
        task_size_mbits=task_size,
        task_size_source="paper_task_size_set",
        task_size_set=TASK_SIZE_SET_MBITS,
        task_size_seed=task_size_seed,
        task_size_distribution="deterministic_cycle" if deterministic_cycle else "seeded_choice",
    )


def build_processing_density_contract(*, task_size_mbits: float = 2.0, density: float = 0.297) -> ProcessingDensityContract:
    return ProcessingDensityContract(
        processing_density_gcycles_per_mbit=density,
        processing_cycles_gcycles=task_size_mbits * density,
        task_size_mbits=task_size_mbits,
        density_source="paper_processing_density_default",
    )

