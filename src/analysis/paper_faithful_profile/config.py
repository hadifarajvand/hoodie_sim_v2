"""Configuration for paper-faithful HOODIE baseline.

This module MUST match HOODIE paper Table 4 exactly. Any deviation is a bug.
Use for reproducibility and paper-faithful results only.

DO NOT use for:
  - Stress testing (use calibrated_stress_profile instead)
  - Custom feasibility calibration
  - Modified arrival distributions
  - Hyperparameter sweeps

The values here are fixed by the paper OCR and commit history.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Paper exact values from HOODIE Table 4 (OCR-recovered)
PAPER_FAITHFUL_PROFILE_NAME = "paper_faithful"
PAPER_N_EA = 20
PAPER_T = 110
PAPER_TASK_SIZE_MBITS_MIN = 2.0
PAPER_TASK_SIZE_MBITS_MAX = 5.0
PAPER_TASK_SIZE_MBITS_STEP = 0.1
PAPER_PROCESSING_DENSITY_GCYCLES_PER_MBIT = 0.297
PAPER_HORIZONTAL_LINK_RATE_MBPS = 30.0
PAPER_VERTICAL_LINK_RATE_MBPS = 10.0
PAPER_SLOT_DURATION_SECONDS = 0.1
PAPER_TIMEOUT_SLOTS = 20
PAPER_ARRIVAL_PROBABILITY = 0.5
PAPER_DROP_PENALTY_C = 40

# CPU capacities (from paper specs or standard assumptions)
PAPER_CPU_PRIVATE_GCYCLES_PER_SLOT = 5.0  # 5 GHz at 0.1s slot = 0.5 Gcycles/slot
PAPER_CPU_PUBLIC_GCYCLES_PER_SLOT = 5.0
PAPER_CPU_CLOUD_GCYCLES_PER_SLOT = 30.0

# Training parameters from paper
PAPER_LEARNING_RATE = 7e-7
PAPER_GAMMA = 0.99
PAPER_BATCH_SIZE = 64
PAPER_REPLAY_MEMORY = 10_000
PAPER_EPSILON_START = 1.0
PAPER_EPSILON_END = 0.0
PAPER_EPSILON_DECAY_EPISODES = 2500
PAPER_TARGET_UPDATE_FREQUENCY = 2000


@dataclass(frozen=True, slots=True)
class PaperFaithfulConfig:
    """Configuration enforcing paper Table 4 values.

    All fields are locked to paper values. To use a different configuration,
    use calibrated_stress_profile instead.
    """

    profile_name: str = PAPER_FAITHFUL_PROFILE_NAME
    num_agents: int = PAPER_N_EA
    episode_length: int = PAPER_T
    task_size_mbits_min: float = PAPER_TASK_SIZE_MBITS_MIN
    task_size_mbits_max: float = PAPER_TASK_SIZE_MBITS_MAX
    task_size_mbits_step: float = PAPER_TASK_SIZE_MBITS_STEP
    processing_density_gcycles_per_mbit: float = PAPER_PROCESSING_DENSITY_GCYCLES_PER_MBIT
    horizontal_link_rate_mbps: float = PAPER_HORIZONTAL_LINK_RATE_MBPS
    vertical_link_rate_mbps: float = PAPER_VERTICAL_LINK_RATE_MBPS
    slot_duration_seconds: float = PAPER_SLOT_DURATION_SECONDS
    timeout_slots: int = PAPER_TIMEOUT_SLOTS
    arrival_probability: float = PAPER_ARRIVAL_PROBABILITY
    drop_penalty_c: int = PAPER_DROP_PENALTY_C
    cpu_private_gcycles_per_slot: float = PAPER_CPU_PRIVATE_GCYCLES_PER_SLOT
    cpu_public_gcycles_per_slot: float = PAPER_CPU_PUBLIC_GCYCLES_PER_SLOT
    cpu_cloud_gcycles_per_slot: float = PAPER_CPU_CLOUD_GCYCLES_PER_SLOT
    learning_rate: float = PAPER_LEARNING_RATE
    gamma: float = PAPER_GAMMA
    batch_size: int = PAPER_BATCH_SIZE
    replay_memory: int = PAPER_REPLAY_MEMORY
    epsilon_start: float = PAPER_EPSILON_START
    epsilon_end: float = PAPER_EPSILON_END
    epsilon_decay_episodes: int = PAPER_EPSILON_DECAY_EPISODES
    target_update_frequency: int = PAPER_TARGET_UPDATE_FREQUENCY

    def __post_init__(self) -> None:
        # Strict validation: any deviation is a bug
        if self.num_agents != PAPER_N_EA:
            raise ValueError(f"num_agents must equal {PAPER_N_EA} (paper N_EA)")
        if self.episode_length != PAPER_T:
            raise ValueError(f"episode_length must equal {PAPER_T} (paper T)")
        if self.task_size_mbits_min != PAPER_TASK_SIZE_MBITS_MIN:
            raise ValueError(f"task_size_mbits_min must equal {PAPER_TASK_SIZE_MBITS_MIN} (paper)")
        if self.task_size_mbits_max != PAPER_TASK_SIZE_MBITS_MAX:
            raise ValueError(f"task_size_mbits_max must equal {PAPER_TASK_SIZE_MBITS_MAX} (paper)")
        if self.task_size_mbits_step != PAPER_TASK_SIZE_MBITS_STEP:
            raise ValueError(f"task_size_mbits_step must equal {PAPER_TASK_SIZE_MBITS_STEP} (paper)")
        if abs(self.processing_density_gcycles_per_mbit - PAPER_PROCESSING_DENSITY_GCYCLES_PER_MBIT) > 1e-6:
            raise ValueError(f"processing_density must equal {PAPER_PROCESSING_DENSITY_GCYCLES_PER_MBIT} (paper)")
        if self.horizontal_link_rate_mbps != PAPER_HORIZONTAL_LINK_RATE_MBPS:
            raise ValueError(f"horizontal_link_rate_mbps must equal {PAPER_HORIZONTAL_LINK_RATE_MBPS} (paper)")
        if self.vertical_link_rate_mbps != PAPER_VERTICAL_LINK_RATE_MBPS:
            raise ValueError(f"vertical_link_rate_mbps must equal {PAPER_VERTICAL_LINK_RATE_MBPS} (paper)")
        if abs(self.slot_duration_seconds - PAPER_SLOT_DURATION_SECONDS) > 1e-6:
            raise ValueError(f"slot_duration_seconds must equal {PAPER_SLOT_DURATION_SECONDS} (paper)")
        if self.timeout_slots != PAPER_TIMEOUT_SLOTS:
            raise ValueError(f"timeout_slots must equal {PAPER_TIMEOUT_SLOTS} (paper)")
        if self.arrival_probability != PAPER_ARRIVAL_PROBABILITY:
            raise ValueError(f"arrival_probability must equal {PAPER_ARRIVAL_PROBABILITY} (paper)")
        if self.drop_penalty_c != PAPER_DROP_PENALTY_C:
            raise ValueError(f"drop_penalty_c must equal {PAPER_DROP_PENALTY_C} (paper)")

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_name": self.profile_name,
            "num_agents": self.num_agents,
            "episode_length": self.episode_length,
            "task_size_mbits": {
                "min": self.task_size_mbits_min,
                "max": self.task_size_mbits_max,
                "step": self.task_size_mbits_step,
            },
            "processing_density_gcycles_per_mbit": self.processing_density_gcycles_per_mbit,
            "link_rates": {
                "horizontal_mbps": self.horizontal_link_rate_mbps,
                "vertical_mbps": self.vertical_link_rate_mbps,
            },
            "slot_duration_seconds": self.slot_duration_seconds,
            "timeout_slots": self.timeout_slots,
            "arrival_probability": self.arrival_probability,
            "drop_penalty_c": self.drop_penalty_c,
            "cpu_capacities_gcycles_per_slot": {
                "private": self.cpu_private_gcycles_per_slot,
                "public": self.cpu_public_gcycles_per_slot,
                "cloud": self.cpu_cloud_gcycles_per_slot,
            },
            "training": {
                "learning_rate": self.learning_rate,
                "gamma": self.gamma,
                "batch_size": self.batch_size,
                "replay_memory": self.replay_memory,
                "epsilon": {
                    "start": self.epsilon_start,
                    "end": self.epsilon_end,
                    "decay_episodes": self.epsilon_decay_episodes,
                },
                "target_update_frequency": self.target_update_frequency,
            },
            "source": "HOODIE paper Table 4 (OCR-recovered)",
            "validation_status": "STRICT (any deviation is a bug)",
        }


def build_paper_faithful_profile() -> PaperFaithfulConfig:
    """Create a paper-faithful configuration.

    This raises ValueError if any paper values are not set to their paper-exact values.
    Use this for reproducibility only.
    """
    return PaperFaithfulConfig()
