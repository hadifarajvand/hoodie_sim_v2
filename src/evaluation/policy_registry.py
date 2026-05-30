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


def _policy_aliases() -> dict[str, str]:
    return {
        "FULL_LOCAL_COMPUTING": "FLC",
        "VERTICAL_OFFLOADING": "VO",
        "HORIZONTAL_OFFLOADING": "HO",
        "RANDOM_OFFLOADING": "RO",
        "BALANCED_COOPERATION_OFFLOADING": "BCO",
        "MINIMUM_LATENCY_ESTIMATE_OFFLOADING": "MLEO",
        "ADAPTIVE_OFFLOADING": "ADAPTIVE",
        "HOODIE": "ADAPTIVE",
    }


@dataclass(slots=True)
class PolicyRegistry:
    @staticmethod
    def supported_names() -> tuple[str, ...]:
        return tuple(_policy_factories().keys())

    @staticmethod
    def resolve(name: str) -> object:
        factories = _policy_factories()
        normalized = name.strip().upper().replace("-", "_")
        canonical = _policy_aliases().get(normalized, normalized)
        if canonical not in factories:
            supported = ", ".join(sorted(factories))
            aliases = ", ".join(sorted(_policy_aliases()))
            raise ValueError(
                f"Unsupported policy name: {name!r}. Supported policies: {supported}. "
                f"Supported aliases: {aliases}."
            )
        return factories[canonical]()
