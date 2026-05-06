from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.policies import (
    AdaptiveOffloadingPolicy,
    BalancedCooperationOffloadingPolicy,
    FullLocalComputingPolicy,
    HorizontalOffloadingPolicy,
    MinimumLatencyEstimateOffloadingPolicy,
    RandomOffloadingPolicy,
    VerticalOffloadingPolicy,
)


def _policy_factories() -> dict[str, Callable[[], object]]:
    return {
        "FLC": FullLocalComputingPolicy,
        "VO": VerticalOffloadingPolicy,
        "HO": HorizontalOffloadingPolicy,
        "RO": lambda: RandomOffloadingPolicy(seed=0),
        "BCO": BalancedCooperationOffloadingPolicy,
        "MLEO": MinimumLatencyEstimateOffloadingPolicy,
        "ADAPTIVE": AdaptiveOffloadingPolicy,
    }


@dataclass(slots=True)
class PolicyRegistry:
    @staticmethod
    def supported_names() -> tuple[str, ...]:
        return tuple(_policy_factories().keys())

    @staticmethod
    def resolve(name: str) -> object:
        factories = _policy_factories()
        if name not in factories:
            raise ValueError(f"Unsupported policy name: {name}")
        return factories[name]()
