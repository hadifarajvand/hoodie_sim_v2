from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any

from src.evaluation.policy_registry import PolicyRegistry


FIXED_SEEDS: tuple[int, ...] = (7, 11, 13)
FIXED_SCENARIOS: tuple[str, ...] = ("paper_default", "moderate", "heavy")
FIXED_EPISODE_LENGTHS: tuple[int, ...] = (4, 6)
REUSED_METRICS: tuple[str, ...] = ("completed_tasks", "dropped_tasks", "throughput", "average_delay")


@dataclass(slots=True)
class SensitivitySetting:
    seed: int
    scenario_name: str
    episode_length: int
    supported: bool = True
    notes: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "seed": self.seed,
            "scenario_name": self.scenario_name,
            "episode_length": self.episode_length,
            "supported": self.supported,
            "notes": self.notes,
        }


def supported_baseline_policies() -> tuple[str, ...]:
    return PolicyRegistry.supported_names()


def build_sensitivity_settings() -> tuple[SensitivitySetting, ...]:
    settings: list[SensitivitySetting] = []
    for seed, scenario_name, episode_length in product(FIXED_SEEDS, FIXED_SCENARIOS, FIXED_EPISODE_LENGTHS):
        settings.append(
            SensitivitySetting(
                seed=seed,
                scenario_name=scenario_name,
                episode_length=episode_length,
                supported=True,
                notes="Supported through the current public evaluation interface.",
            )
        )
    return tuple(settings)

