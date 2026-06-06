from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np

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


@dataclass
class TrainingStepMetrics:
    loss: float
    average_reward: float
    epsilon: float
    transitions_consumed: int
    gradient_steps: int


class LinearQModel:
    def __init__(self, input_dim: int, action_dim: int, seed: int) -> None:
        rng = np.random.default_rng(seed)
        self.weights = rng.normal(scale=0.01, size=(input_dim, action_dim)).astype(np.float32)
        self.bias = np.zeros(action_dim, dtype=np.float32)

    def predict(self, states: np.ndarray) -> np.ndarray:
        return states @ self.weights + self.bias

    def copy(self) -> "LinearQModel":
        new = object.__new__(LinearQModel)
        new.weights = self.weights.copy()
        new.bias = self.bias.copy()
        return new

    def apply_gradient(self, states: np.ndarray, actions: np.ndarray, td_error: np.ndarray, learning_rate: float) -> float:
        batch_size = states.shape[0]
        grad_w = np.zeros_like(self.weights)
        grad_b = np.zeros_like(self.bias)
        for idx in range(batch_size):
            action = int(actions[idx])
            grad_w[:, action] += states[idx] * td_error[idx]
            grad_b[action] += td_error[idx]
        self.weights += learning_rate * grad_w / batch_size
        self.bias += learning_rate * grad_b / batch_size
        return float(np.mean(td_error ** 2))


class DQNTrainer:
    def __init__(self, cfg: TrainerConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        self.replay_buffer = ReplayBuffer(capacity=10000, seed=cfg.seed)
        self.rng = np.random.default_rng(cfg.seed)
        self.policy_net = LinearQModel(cfg.input_dim, cfg.action_dim, cfg.seed)
        self.target_net = self.policy_net.copy()
        self.gradient_steps = 0
        self.losses: list[float] = []

    def select_action(self, state: np.ndarray, epsilon: float) -> int:
        if self.rng.random() < epsilon:
            return int(self.rng.integers(0, self.cfg.action_dim))
        q_values = self.policy_net.predict(state.reshape(1, -1))[0]
        return int(np.argmax(q_values))

    def push(self, transition: Transition) -> None:
        self.replay_buffer.push(transition)

    def train_step(self) -> TrainingStepMetrics | None:
        if len(self.replay_buffer) < self.cfg.batch_size:
            return None
        indices = self.replay_buffer.sample_indices(self.cfg.batch_size)
        batch = [self.replay_buffer.to_list()[int(index)] for index in indices]
        states = np.stack([t.state for t in batch]).astype(np.float32)
        actions = np.asarray([t.action for t in batch], dtype=np.int64)
        rewards = np.asarray([t.reward for t in batch], dtype=np.float32)
        next_states = np.stack([t.next_state for t in batch]).astype(np.float32)
        dones = np.asarray([float(t.done) for t in batch], dtype=np.float32)

        q_values = self.policy_net.predict(states)
        next_policy_q = self.policy_net.predict(next_states)
        next_target_q = self.target_net.predict(next_states)
        if self.cfg.algorithm == "ddqn":
            next_actions = np.argmax(next_policy_q, axis=1)
            next_q = next_target_q[np.arange(len(batch)), next_actions]
        else:
            next_q = np.max(next_target_q, axis=1)
        targets = rewards + self.cfg.gamma * next_q * (1.0 - dones)
        current = q_values[np.arange(len(batch)), actions]
        td_error = targets - current
        loss = self.policy_net.apply_gradient(states, actions, td_error, self.cfg.learning_rate)
        self.gradient_steps += 1
        self.losses.append(loss)
        if self.gradient_steps % self.cfg.target_update_interval == 0:
            self.target_net = self.policy_net.copy()
        epsilon = max(0.01, 1.0 - self.gradient_steps / max(1, self.cfg.target_update_interval))
        return TrainingStepMetrics(
            loss=float(loss),
            average_reward=float(np.mean(rewards)),
            epsilon=float(epsilon),
            transitions_consumed=int(self.cfg.batch_size),
            gradient_steps=int(self.gradient_steps),
        )

    def save(self, path: str | Path, epochs_completed: int) -> str:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "algorithm": self.cfg.algorithm,
            "seed": self.cfg.seed,
            "state_dim": self.cfg.input_dim,
            "action_count": self.cfg.action_dim,
            "epochs_completed": int(epochs_completed),
            "training_config": asdict(self.cfg),
            "policy_weights": self.policy_net.weights.tolist(),
            "policy_bias": self.policy_net.bias.tolist(),
            "target_weights": self.target_net.weights.tolist(),
            "target_bias": self.target_net.bias.tolist(),
            "gradient_steps": self.gradient_steps,
        }
        path.write_text(json_dumps(payload))
        return str(path)

    def load(self, path: str | Path) -> None:
        payload = json_loads(Path(path).read_text())
        self.policy_net.weights = np.asarray(payload["policy_weights"], dtype=np.float32)
        self.policy_net.bias = np.asarray(payload["policy_bias"], dtype=np.float32)
        self.target_net.weights = np.asarray(payload["target_weights"], dtype=np.float32)
        self.target_net.bias = np.asarray(payload["target_bias"], dtype=np.float32)


def json_dumps(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, indent=2, sort_keys=True)


def json_loads(content: str) -> dict[str, Any]:
    import json

    return json.loads(content)
