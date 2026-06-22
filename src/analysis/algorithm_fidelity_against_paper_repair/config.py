from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.analysis.paper_faithful_simulation_production.profiles import ProductionProfile

FEATURE_ID = "algorithm-fidelity-against-paper-repair"
TRAINING_BUDGETS = [50, 100, 200, 300, 500, 750, 1000]
MAX_TRAINING_BUDGET = 1000
EVALUATION_EPISODE_COUNT = 100
EPISODE_LENGTH = 110
PAPER_EPSILON_START = 1.0
PAPER_EPSILON_FINAL = 0.0
PAPER_EPSILON_DECAY_EPISODES = 2500
PAPER_TARGET_UPDATE_FREQUENCY = 2000
PAPER_TARGET_UPDATE_APPROVAL = "paper_aligned_episode_sync_approved"
PAPER_TARGET_UPDATE_EVIDENCE = "ocr_recovered_algorithm_1_episode_copy"


@dataclass(frozen=True, slots=True)
class AlgorithmFidelityConfig:
    training_budgets: list[int] = field(default_factory=lambda: list(TRAINING_BUDGETS))
    max_training_budget: int = MAX_TRAINING_BUDGET
    evaluation_episode_count: int = EVALUATION_EPISODE_COUNT
    episode_length: int = EPISODE_LENGTH
    paper_epsilon_start: float = PAPER_EPSILON_START
    paper_epsilon_final: float = PAPER_EPSILON_FINAL
    paper_epsilon_decay_episodes: int = PAPER_EPSILON_DECAY_EPISODES
    paper_target_update_frequency: int = PAPER_TARGET_UPDATE_FREQUENCY

    def __post_init__(self) -> None:
        if self.training_budgets != TRAINING_BUDGETS:
            raise ValueError("training_budgets must equal [50, 100, 200, 300, 500, 750, 1000].")
        if self.max_training_budget != MAX_TRAINING_BUDGET:
            raise ValueError("max_training_budget must equal 1000.")
        if self.evaluation_episode_count != EVALUATION_EPISODE_COUNT:
            raise ValueError("evaluation_episode_count must equal 100.")
        if self.episode_length != EPISODE_LENGTH:
            raise ValueError("episode_length must equal 110.")
        if self.paper_epsilon_start != PAPER_EPSILON_START:
            raise ValueError("paper_epsilon_start must equal 1.0.")
        if self.paper_epsilon_final != PAPER_EPSILON_FINAL:
            raise ValueError("paper_epsilon_final must equal 0.0.")
        if self.paper_epsilon_decay_episodes != PAPER_EPSILON_DECAY_EPISODES:
            raise ValueError("paper_epsilon_decay_episodes must equal 2500.")
        if self.paper_target_update_frequency != PAPER_TARGET_UPDATE_FREQUENCY:
            raise ValueError("paper_target_update_frequency must equal 2000.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": FEATURE_ID,
            "training_budgets": list(self.training_budgets),
            "max_training_budget": self.max_training_budget,
            "evaluation_episode_count": self.evaluation_episode_count,
            "episode_length": self.episode_length,
            "paper_epsilon_start": self.paper_epsilon_start,
            "paper_epsilon_final": self.paper_epsilon_final,
            "paper_epsilon_decay_episodes": self.paper_epsilon_decay_episodes,
            "paper_target_update_frequency": self.paper_target_update_frequency,
            "calibration_profile": "paper_aligned_feasible_v1",
            "state_representation_profile": "deadline_queue_feasibility_v1",
        }


def build_profile() -> ProductionProfile:
    return ProductionProfile(training_budgets=list(TRAINING_BUDGETS), max_training_budget=MAX_TRAINING_BUDGET)
