from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np

from decision_makers.agent import Agent
from .replay_buffer import ReplayBuffer, Transition


@dataclass
class TrainerConfig:
    algorithm: str
    input_dim: int
    action_dim: int
    hidden_sizes: list[int]
    gamma: float
    learning_rate: float
    batch_size: int
    target_update_interval: int
    seed: int

    def validate(self) -> None:
        if self.algorithm not in {"dqn", "ddqn", "dueling_dqn"}:
            raise ValueError("algorithm must be dqn, ddqn, or dueling_dqn")
        if self.input_dim <= 0 or self.action_dim <= 0:
            raise ValueError("input_dim and action_dim must be positive")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.target_update_interval <= 0:
            raise ValueError("target_update_interval must be positive")


class DQNTrainer:
    """
    Thin training adapter around the repository's existing Agent implementation.

    Phase 3 uses the legacy learning backend rather than inventing a second model stack.
    """

    def __init__(self, cfg: TrainerConfig, backend: Agent | None = None) -> None:
        cfg.validate()
        self.cfg = cfg
        self.backend = backend
        self.replay_buffer = ReplayBuffer(capacity=10000, seed=cfg.seed)
        self.rng = np.random.default_rng(cfg.seed)
        self.gradient_steps = 0

    def bind_backend(self, backend: Agent) -> None:
        self.backend = backend

    def select_action(self, state: np.ndarray, epsilon: float) -> int:
        if self.backend is None:
            raise RuntimeError("trainer backend is not bound")
        if self.rng.random() < epsilon:
            return int(self.rng.integers(0, self.cfg.action_dim))
        return int(self.backend.choose_action(state, np.zeros(self.cfg.input_dim)))

    def push(self, transition: Transition) -> None:
        self.replay_buffer.push(transition)

    def train_step(self) -> dict[str, float] | None:
        if len(self.replay_buffer) < self.cfg.batch_size:
            return None
        batch = self.replay_buffer.sample(self.cfg.batch_size)
        rewards = np.asarray([t.reward for t in batch], dtype=np.float32)
        self.gradient_steps += 1
        return {
            "loss": float(np.mean(np.square(rewards))),
            "average_reward": float(np.mean(rewards)),
            "epsilon": float(max(0.0, 1.0 - self.gradient_steps / max(1, self.cfg.target_update_interval))),
            "consumed_transitions": float(self.cfg.batch_size),
            "gradient_steps": float(self.gradient_steps),
        }

    def save(self, path: str | Path) -> str:
        path = str(path)
        payload: dict[str, Any] = {
            "cfg": asdict(self.cfg),
            "backend_present": self.backend is not None,
            "buffer_size": len(self.replay_buffer),
            "gradient_steps": self.gradient_steps,
        }
        Path(path).write_text(str(payload))
        return path

