from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Any, Iterator


@dataclass(frozen=True)
class ExperimentConfig:
    workload_levels: tuple[str, ...] = ("low", "medium", "high")
    policies: tuple[str, ...] = ("fifo", "random", "heuristic")
    num_seeds: int = 20
    metrics: tuple[str, ...] = ("latency", "drop_ratio", "utilization")

    def validate(self) -> None:
        if self.num_seeds <= 0:
            raise ValueError("num_seeds must be positive")
        if not self.workload_levels:
            raise ValueError("workload_levels must not be empty")
        if not self.policies:
            raise ValueError("policies must not be empty")
        if not self.metrics:
            raise ValueError("metrics must not be empty")


@dataclass(frozen=True)
class ExperimentalCell:
    workload: str
    policy: str
    seed: int

    def to_dict(self) -> dict[str, Any]:
        return {"workload": self.workload, "policy": self.policy, "seed": self.seed}


def generate_experiment_matrix(config: ExperimentConfig) -> list[ExperimentalCell]:
    config.validate()
    cells: list[ExperimentalCell] = []
    for workload, policy, seed in product(config.workload_levels, config.policies, range(config.num_seeds)):
        cells.append(ExperimentalCell(workload=workload, policy=policy, seed=seed))
    return cells
