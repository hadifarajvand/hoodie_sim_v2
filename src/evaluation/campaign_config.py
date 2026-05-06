from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def _normalize_names(values: tuple[str, ...], label: str) -> tuple[str, ...]:
    if not values:
        raise ValueError(f"{label} must not be empty")
    normalized = tuple(value.strip() for value in values if value and value.strip())
    if len(normalized) != len(values):
        raise ValueError(f"{label} must not contain empty names")
    return normalized


def _normalize_seeds(values: tuple[int, ...]) -> tuple[int, ...]:
    if not values:
        raise ValueError("seeds must not be empty")
    normalized: list[int] = []
    for value in values:
        if not isinstance(value, int):
            raise TypeError("seeds must be integers")
        normalized.append(value)
    return tuple(normalized)


@dataclass(slots=True)
class CampaignConfig:
    campaign_name: str
    policy_names: tuple[str, ...]
    scenario_names: tuple[str, ...]
    seeds: tuple[int, ...]
    output_dir: Path
    episode_length: int | None = None
    created_at_override: str | None = None
    dependency_change_note: str = "No dependency files changed."

    def __post_init__(self) -> None:
        if not isinstance(self.campaign_name, str) or not self.campaign_name.strip():
            raise ValueError("campaign_name must not be empty")
        self.campaign_name = self.campaign_name.strip()
        self.policy_names = tuple(sorted(_normalize_names(tuple(self.policy_names), "policy_names")))
        self.scenario_names = tuple(sorted(_normalize_names(tuple(self.scenario_names), "scenario_names")))
        self.seeds = tuple(sorted(_normalize_seeds(tuple(self.seeds))))
        self.output_dir = Path(self.output_dir)
        if self.episode_length is not None and self.episode_length <= 0:
            raise ValueError("episode_length must be greater than zero when provided")
