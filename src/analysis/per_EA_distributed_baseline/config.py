"""Config for the per-EA distributed baseline. No proposed-method parameters."""

from __future__ import annotations

from dataclasses import dataclass, field

NUM_AGENTS = 20                       # paper N_EA = 20 (Table 4)
EPISODE_LENGTH = 110                  # paper T
EVALUATION_EPISODE_COUNT = 100
SMOKE_BUDGETS = [50, 100, 200, 300, 500, 750, 1000]
SMOKE_EVAL_AT = [50, 100, 200, 300, 500, 750, 1000]
FULL_NE = 5000
FULL_CHECKPOINTS = list(range(250, 5001, 250))
FULL_EVAL_AT = [250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]

# Paper-aligned schedules (per agent).
PAPER_EPSILON_START = 1.0
PAPER_EPSILON_FINAL = 0.0
SMOKE_EPSILON_DECAY_EPISODES = 500    # N/2 for the 1000-episode smoke horizon
FULL_EPSILON_DECAY_EPISODES = 2500    # N_E/2 for the 5000 horizon
PAPER_TARGET_UPDATE_FREQUENCY = 2000  # N_copy episodes
PAPER_LEARNING_RATE = 7e-7
PAPER_GAMMA = 0.99
PAPER_BATCH = 64
PAPER_REPLAY = 10_000

STATE_REPRESENTATION_PROFILE = "deadline_queue_feasibility_v1"
RECONCILIATION_PROFILE = "horizon_aware_recovered_reward_event"
CREDIT_ASSIGNMENT = "per_task_delayed_reward"

# Guarded full-campaign execution.
EXECUTION_ENV_CONFIRMATION = "HOODIE_EXECUTE_DISTRIBUTED_FULL_CAMPAIGN"
EXECUTION_DISABLED_MESSAGE = (
    "Full distributed campaign execution is disabled by default. "
    "Pass --execute-full-distributed-campaign only after explicit user approval."
)


@dataclass(frozen=True, slots=True)
class DistributedBaselineConfig:
    num_agents: int = NUM_AGENTS
    episode_length: int = EPISODE_LENGTH
    evaluation_episode_count: int = EVALUATION_EPISODE_COUNT
    smoke_budgets: list[int] = field(default_factory=lambda: list(SMOKE_BUDGETS))
    smoke_eval_at: list[int] = field(default_factory=lambda: list(SMOKE_EVAL_AT))
    full_ne: int = FULL_NE
    full_checkpoints: list[int] = field(default_factory=lambda: list(FULL_CHECKPOINTS))
    full_eval_at: list[int] = field(default_factory=lambda: list(FULL_EVAL_AT))
    epsilon_start: float = PAPER_EPSILON_START
    epsilon_final: float = PAPER_EPSILON_FINAL
    smoke_epsilon_decay_episodes: int = SMOKE_EPSILON_DECAY_EPISODES
    full_epsilon_decay_episodes: int = FULL_EPSILON_DECAY_EPISODES
    target_update_frequency: int = PAPER_TARGET_UPDATE_FREQUENCY
    learning_rate: float = PAPER_LEARNING_RATE
    gamma: float = PAPER_GAMMA
    batch_size: int = PAPER_BATCH
    replay_memory_capacity: int = PAPER_REPLAY
    state_representation_profile: str = STATE_REPRESENTATION_PROFILE
    reconciliation_profile: str = RECONCILIATION_PROFILE
    credit_assignment: str = CREDIT_ASSIGNMENT

    def __post_init__(self) -> None:
        if self.num_agents != NUM_AGENTS:
            raise ValueError("Paper N_EA = 20.")
        if self.episode_length != EPISODE_LENGTH:
            raise ValueError("episode_length must equal paper T=110.")

    def to_dict(self) -> dict:
        return {
            "num_agents": self.num_agents,
            "episode_length": self.episode_length,
            "evaluation_episode_count": self.evaluation_episode_count,
            "smoke_budgets": list(self.smoke_budgets),
            "smoke_eval_at": list(self.smoke_eval_at),
            "full_ne": self.full_ne,
            "full_checkpoints": list(self.full_checkpoints),
            "full_eval_at": list(self.full_eval_at),
            "epsilon": {
                "start": self.epsilon_start, "final": self.epsilon_final,
                "smoke_decay_episodes": self.smoke_epsilon_decay_episodes,
                "full_decay_episodes": self.full_epsilon_decay_episodes,
                "schedule_unit": "episode", "per_agent": True,
            },
            "target_update_frequency_episodes": self.target_update_frequency,
            "per_agent_target_sync": True,
            "learning_rate": self.learning_rate,
            "gamma": self.gamma,
            "batch_size": self.batch_size,
            "replay_memory_capacity_per_agent": self.replay_memory_capacity,
            "per_agent_replay": True,
            "state_representation_profile": self.state_representation_profile,
            "reconciliation_profile": self.reconciliation_profile,
            "credit_assignment": self.credit_assignment,
            "techniques": ["LSTM", "Dueling DQN", "Double DQN"],
            "proposed_method_logic": "none (paper-faithful baseline only)",
        }


def build_distributed_config() -> DistributedBaselineConfig:
    return DistributedBaselineConfig()
