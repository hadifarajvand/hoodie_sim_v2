"""Full paper campaign configuration (N_E=5000) — config only, never executed.

Every value here is traceable to the HOODIE paper (Table 4 / Algorithm 1, OCR at
``resources/papers/hoodie/ocr/merged.txt``) or to a verified repository mechanism
already validated on the bounded branches. No training is run by this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# --- Paper Table 4 / Algorithm 1 constants (exact) -------------------------------
PAPER_NE = 5000                      # Number of training episodes N_E (Table 4)
PAPER_T = 110                        # Time slots per episode (Table 4)
PAPER_EPSILON_START = 1.0            # Algorithm 1 line 680
PAPER_EPSILON_FINAL = 0.0           # decays to 0
PAPER_EPSILON_DECAY_EPISODES = PAPER_NE // 2   # linear 1->0 over first N_E/2 episodes
PAPER_EPSILON_UNIT = "episode"
PAPER_TARGET_UPDATE_FREQUENCY = 2000           # N_copy (Table 4)
PAPER_TARGET_UPDATE_UNIT = "episode"           # "every N_copy training episodes" (Alg.1 L587)
PAPER_TARGET_UPDATE_APPROVAL = "paper_aligned_episode_sync_approved"
PAPER_TARGET_UPDATE_EVIDENCE = "ocr_recovered_algorithm_1_episode_copy"
PAPER_LEARNING_RATE = 7e-7
PAPER_GAMMA = 0.99
PAPER_BATCH_SIZE = 64
PAPER_REPLAY_SIZE = 10_000
PAPER_HIDDEN_LAYERS = (1024, 1024, 1024)
PAPER_LSTM_CELLS = 20
PAPER_LSTM_LOOKBACK = 10
PAPER_NUM_AGENTS = 20
PAPER_DROP_PENALTY = 40

# --- Verified repository mechanisms (validated on bounded branches) ---------------
STATE_REPRESENTATION_PROFILE = "deadline_queue_feasibility_v1"
CALIBRATION_PROFILE = "paper_aligned_feasible_v1"
RECONCILIATION_PROFILE = "horizon_aware_recovered_reward_event"
CREDIT_ASSIGNMENT = "per_task_delayed_reward"   # paper Alg.1 lines 19-22
EVALUATION_EPISODE_COUNT = 100

# --- Measured timing (single CPU core, this repo) --------------------------------
MEASURED_TRAIN_SEC_PER_EPISODE = 1.73
MEASURED_EVAL_SEC_PER_EPISODE = 1.29

# --- Operational policy ----------------------------------------------------------
CHECKPOINT_EVERY_EPISODES = 250                 # 20 checkpoints across N_E
EVAL_AT_EPISODES = (250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000)


@dataclass(frozen=True, slots=True)
class FullPaperCampaignConfig:
    number_of_training_episodes: int = PAPER_NE
    episode_length: int = PAPER_T
    number_of_agents: int = PAPER_NUM_AGENTS

    epsilon_start: float = PAPER_EPSILON_START
    epsilon_final: float = PAPER_EPSILON_FINAL
    epsilon_decay_episodes: int = PAPER_EPSILON_DECAY_EPISODES
    epsilon_schedule_unit: str = PAPER_EPSILON_UNIT

    target_update_frequency: int = PAPER_TARGET_UPDATE_FREQUENCY
    target_update_unit: str = PAPER_TARGET_UPDATE_UNIT

    learning_rate: float = PAPER_LEARNING_RATE
    gamma: float = PAPER_GAMMA
    batch_size: int = PAPER_BATCH_SIZE
    replay_memory_capacity: int = PAPER_REPLAY_SIZE
    q_network_hidden_layers: tuple[int, ...] = PAPER_HIDDEN_LAYERS
    lstm_cells: int = PAPER_LSTM_CELLS
    lstm_lookback_w: int = PAPER_LSTM_LOOKBACK

    state_representation_profile: str = STATE_REPRESENTATION_PROFILE
    calibration_profile: str = CALIBRATION_PROFILE
    reconciliation_profile: str = RECONCILIATION_PROFILE
    credit_assignment: str = CREDIT_ASSIGNMENT
    evaluation_episode_count: int = EVALUATION_EPISODE_COUNT

    checkpoint_every_episodes: int = CHECKPOINT_EVERY_EPISODES
    eval_at_episodes: tuple[int, ...] = EVAL_AT_EPISODES

    # Hard guard: this object describes a config; it must never auto-run.
    execute: bool = False

    def __post_init__(self) -> None:
        if self.number_of_training_episodes != PAPER_NE:
            raise ValueError("Full paper campaign requires N_E == 5000 (config-only).")
        if self.episode_length != PAPER_T:
            raise ValueError("episode_length must equal paper T=110.")
        if self.epsilon_schedule_unit != "episode":
            raise ValueError("Paper epsilon schedule is episode-based.")
        if self.epsilon_decay_episodes != PAPER_NE // 2:
            raise ValueError("Paper epsilon decays over the first N_E/2 episodes.")
        if self.execute is not False:
            raise ValueError(
                "FullPaperCampaignConfig is config-only; execute must be False. "
                "Running 5000 is an explicit, separate operator action (see runbook)."
            )

    # Derived estimates -----------------------------------------------------------
    def estimated_train_seconds(self, sec_per_episode: float = MEASURED_TRAIN_SEC_PER_EPISODE) -> float:
        return self.number_of_training_episodes * sec_per_episode

    def estimated_eval_seconds(self, sec_per_episode: float = MEASURED_EVAL_SEC_PER_EPISODE) -> float:
        # candidate evals at each checkpoint + 4 fixed baselines + 2 oracle policies.
        candidate_evals = len(self.eval_at_episodes)
        comparator_evals = 4 + 2
        return (candidate_evals + comparator_evals) * self.evaluation_episode_count * sec_per_episode

    def estimated_total_hours(self) -> float:
        return (self.estimated_train_seconds() + self.estimated_eval_seconds()) / 3600.0

    def epsilon_at(self, episode_index: int) -> float:
        if episode_index >= self.epsilon_decay_episodes:
            return self.epsilon_final
        frac = episode_index / self.epsilon_decay_episodes
        return self.epsilon_start + (self.epsilon_final - self.epsilon_start) * frac

    def to_dict(self) -> dict[str, Any]:
        return {
            "number_of_training_episodes_N_E": self.number_of_training_episodes,
            "episode_length_T": self.episode_length,
            "number_of_agents_N": self.number_of_agents,
            "epsilon": {
                "start": self.epsilon_start,
                "final": self.epsilon_final,
                "decay_episodes": self.epsilon_decay_episodes,
                "schedule_unit": self.epsilon_schedule_unit,
                "paper_reference": "Algorithm 1 line 680 (linear 1->0 over first N_E/2 episodes, 0 after)",
            },
            "target_update": {
                "frequency_N_copy": self.target_update_frequency,
                "unit": self.target_update_unit,
                "approval_status": PAPER_TARGET_UPDATE_APPROVAL,
                "evidence_status": PAPER_TARGET_UPDATE_EVIDENCE,
                "paper_reference": "Algorithm 1 line 587 / Table 4 N_copy=2000",
            },
            "optimizer": {"name": "Adam", "learning_rate": self.learning_rate, "loss": "MSE"},
            "gamma": self.gamma,
            "batch_size": self.batch_size,
            "replay_memory_capacity": self.replay_memory_capacity,
            "q_network_hidden_layers": list(self.q_network_hidden_layers),
            "lstm_cells": self.lstm_cells,
            "lstm_lookback_w": self.lstm_lookback_w,
            "techniques": ["LSTM", "Dueling DQN", "Double DQN"],
            "state_representation_profile": self.state_representation_profile,
            "calibration_profile": self.calibration_profile,
            "reconciliation_profile": self.reconciliation_profile,
            "credit_assignment": self.credit_assignment,
            "reward_equation": "Eq. 20: completed -> -Phi_n(t); dropped -> -C (C=40)",
            "evaluation_episode_count": self.evaluation_episode_count,
            "checkpoint_every_episodes": self.checkpoint_every_episodes,
            "eval_at_episodes": list(self.eval_at_episodes),
            "execute": self.execute,
            "estimated_train_hours": round(self.estimated_train_seconds() / 3600.0, 2),
            "estimated_eval_hours": round(self.estimated_eval_seconds() / 3600.0, 2),
            "estimated_total_hours": round(self.estimated_total_hours(), 2),
        }


def build_full_campaign_config() -> FullPaperCampaignConfig:
    return FullPaperCampaignConfig()
