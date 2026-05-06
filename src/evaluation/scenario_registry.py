from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.environment.traffic_config import TrafficConfig, TrafficScenarioPreset


def _scenario_factories() -> dict[str, Callable[[], TrafficConfig]]:
    return {
        "paper_default": TrafficScenarioPreset.paper_default,
        "moderate": TrafficScenarioPreset.moderate,
        "heavy": TrafficScenarioPreset.heavy,
        "extreme": TrafficScenarioPreset.extreme,
    }


@dataclass(slots=True)
class ScenarioRegistry:
    @staticmethod
    def supported_names() -> tuple[str, ...]:
        return tuple(_scenario_factories().keys())

    @staticmethod
    def resolve(name: str, episode_length_override: int | None = None) -> TrafficConfig:
        factories = _scenario_factories()
        if name not in factories:
            raise ValueError(f"Unsupported scenario name: {name}")
        config = factories[name]()
        if episode_length_override is not None:
            config.episode_length = episode_length_override
        return config

