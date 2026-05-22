from __future__ import annotations

from dataclasses import dataclass

FEATURE_ID = "047-exposure-matrix-review"
FEATURE_TITLE = "Exposure-Matrix Review"
DEFAULT_EPISODE_LENGTH = 110
DEFAULT_TIMEOUT_SLOTS = 20
DEFAULT_NODE_COUNT = 20
DEFAULT_ARRIVAL_PROBABILITY = 0.5
DEFAULT_SEEDS = (0, 1, 2)
DEFAULT_STRATEGIES = (
    "environment_default_policy_probe",
    "force_local_legal_probe",
    "force_horizontal_legal_probe",
    "force_vertical_legal_probe",
    "mixed_legal_round_robin_probe",
)


@dataclass(frozen=True, slots=True)
class ExposureMatrixConfig:
    feature_id: str = FEATURE_ID
    episode_length: int = DEFAULT_EPISODE_LENGTH
    timeout_slots: int = DEFAULT_TIMEOUT_SLOTS
    node_count: int = DEFAULT_NODE_COUNT
    arrival_probability: float = DEFAULT_ARRIVAL_PROBABILITY
    seeds: tuple[int, ...] = DEFAULT_SEEDS
    strategies: tuple[str, ...] = DEFAULT_STRATEGIES
    no_runtime_repair: bool = True
    no_training: bool = True

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 047-exposure-matrix-review")
        if self.episode_length != DEFAULT_EPISODE_LENGTH:
            raise ValueError("episode_length must equal 110")
        if self.timeout_slots != DEFAULT_TIMEOUT_SLOTS:
            raise ValueError("timeout_slots must equal 20")
        if self.node_count != DEFAULT_NODE_COUNT:
            raise ValueError("node_count must equal 20")
        if self.arrival_probability != DEFAULT_ARRIVAL_PROBABILITY:
            raise ValueError("arrival_probability must equal 0.5")
        if tuple(self.seeds) != DEFAULT_SEEDS:
            raise ValueError("seeds must equal [0, 1, 2]")
        if tuple(self.strategies) != DEFAULT_STRATEGIES:
            raise ValueError("strategies must equal the approved five-strategy probe grid")
        if not self.no_runtime_repair:
            raise ValueError("no_runtime_repair must be true")
        if not self.no_training:
            raise ValueError("no_training must be true")
