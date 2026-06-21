"""Explicit profiles for the paper-faithful simulation production pipeline.

Paper parameters are sourced from the OCR-recovered HOODIE paper Table 4
(``resources/papers/hoodie/ocr/merged.txt``). Where the repository runs a
calibrated/feasible value instead of the paper-exact value, both are recorded so
the deviation stays explicit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SIMULATION_PROFILE = "paper_faithful_base"
CALIBRATION_PROFILE = "paper_aligned_feasible_v1"
STATE_REPRESENTATION_PROFILE = "deadline_queue_feasibility_v1"
RECONCILIATION_PROFILE = "horizon_aware_recovered_reward_event"

# Paper-exact Table 4 values (the full 5000-episode campaign is NOT executed).
PAPER_EXACT = {
    "number_of_agents_N_EA": 20,
    "number_of_time_slots_T": 110,
    "time_slot_duration_sec": 0.1,
    "task_timeout_slots": 20,
    "cpu_freq_private_ghz": 5,
    "cpu_freq_public_ghz": 5,
    "cpu_freq_cloud_ghz": 30,
    "drop_penalty_C": 40,
    "learning_rate": 7e-7,
    "q_network_hidden_layers": "3 x 1024 neurons",
    "lstm_cells": "1 x 20",
    "replay_memory_size": 10000,
    "batch_size": 64,
    "optimizer": "Adam",
    "loss_function": "MSE",
    "number_of_training_episodes_N_E": 5000,
    "techniques": ["LSTM", "Dueling DQN", "Double DQN"],
    "exploration": "epsilon-greedy",
    "source": "resources/papers/hoodie/ocr/merged.txt (Table 4)",
}

# Bounded medium-smoke budgets actually executed by this pipeline.
MEDIUM_SMOKE_BUDGETS = [50, 100, 200, 300]
MAX_TRAINING_BUDGET = 300
EVALUATION_EPISODE_COUNT = 100
EPISODE_LENGTH = 110  # matches paper T = 110
FORBIDDEN_BUDGETS = [5000]


@dataclass(frozen=True, slots=True)
class ProductionProfile:
    simulation_profile: str = SIMULATION_PROFILE
    calibration_profile: str = CALIBRATION_PROFILE
    state_representation_profile: str = STATE_REPRESENTATION_PROFILE
    reconciliation_profile: str = RECONCILIATION_PROFILE
    training_budgets: list[int] = field(default_factory=lambda: list(MEDIUM_SMOKE_BUDGETS))
    max_training_budget: int = MAX_TRAINING_BUDGET
    evaluation_episode_count: int = EVALUATION_EPISODE_COUNT
    episode_length: int = EPISODE_LENGTH

    def __post_init__(self) -> None:
        if any(b in FORBIDDEN_BUDGETS for b in self.training_budgets):
            raise ValueError("forbidden training budget present")
        if self.max_training_budget > MAX_TRAINING_BUDGET:
            raise ValueError("max_training_budget exceeds bounded medium-smoke ceiling")
        if self.episode_length != EPISODE_LENGTH:
            raise ValueError("episode_length must equal paper T=110")

    def to_dict(self) -> dict[str, Any]:
        return {
            "simulation_profile": self.simulation_profile,
            "calibration_profile": self.calibration_profile,
            "state_representation_profile": self.state_representation_profile,
            "reconciliation_profile": self.reconciliation_profile,
            "training_budgets": list(self.training_budgets),
            "max_training_budget": self.max_training_budget,
            "evaluation_episode_count": self.evaluation_episode_count,
            "episode_length": self.episode_length,
            "paper_exact_parameters": PAPER_EXACT,
        }
