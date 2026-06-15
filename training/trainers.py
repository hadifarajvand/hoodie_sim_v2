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
        if not self.hidden_sizes:
            raise ValueError("hidden_sizes must not be empty")
        if any(size <= 0 for size in self.hidden_sizes):
            raise ValueError("hidden_sizes must contain only positive integers")
        if not np.isfinite(self.gamma) or not (0.0 <= self.gamma <= 1.0):
            raise ValueError("gamma must be finite and within [0, 1]")
        if not np.isfinite(self.learning_rate) or self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive and finite")
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


def _activation(x: np.ndarray) -> np.ndarray:
    return np.maximum(x, 0.0)


def _activation_grad(x: np.ndarray) -> np.ndarray:
    return (x > 0).astype(np.float32)


class MLPQModel:
    def __init__(self, input_dim: int, action_dim: int, hidden_sizes: list[int], seed: int) -> None:
        self.input_dim = input_dim
        self.action_dim = action_dim
        self.hidden_sizes = list(hidden_sizes)
        self.architecture = "mlp_q_network"
        self.q_model_type = "mlp_q_network"
        rng = np.random.default_rng(seed)
        layer_sizes = [input_dim, *hidden_sizes, action_dim]
        self.weights = [
            rng.normal(scale=0.05, size=(layer_sizes[idx], layer_sizes[idx + 1])).astype(np.float32)
            for idx in range(len(layer_sizes) - 1)
        ]
        self.biases = [np.zeros(layer_sizes[idx + 1], dtype=np.float32) for idx in range(len(layer_sizes) - 1)]

    def copy(self) -> "MLPQModel":
        new = object.__new__(MLPQModel)
        new.input_dim = self.input_dim
        new.action_dim = self.action_dim
        new.hidden_sizes = list(self.hidden_sizes)
        new.architecture = self.architecture
        new.q_model_type = self.q_model_type
        new.weights = [w.copy() for w in self.weights]
        new.biases = [b.copy() for b in self.biases]
        return new

    def _forward(self, states: np.ndarray) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray]]:
        activations = [states.astype(np.float32)]
        pre_activations: list[np.ndarray] = []
        x = activations[0]
        for idx, (weight, bias) in enumerate(zip(self.weights, self.biases, strict=False)):
            z = x @ weight + bias
            pre_activations.append(z)
            if idx < len(self.weights) - 1:
                x = _activation(z)
            else:
                x = z
            activations.append(x)
        return x, activations, pre_activations

    def predict(self, states: np.ndarray) -> np.ndarray:
        q_values, _, _ = self._forward(states)
        return q_values

    def apply_gradient(self, states: np.ndarray, actions: np.ndarray, td_error: np.ndarray, learning_rate: float) -> float:
        batch_size = states.shape[0]
        q_values, activations, pre_activations = self._forward(states)
        grad_output = np.zeros_like(q_values)
        grad_output[np.arange(batch_size), actions] = -td_error
        grad_output /= batch_size

        grad_weights = [np.zeros_like(weight) for weight in self.weights]
        grad_biases = [np.zeros_like(bias) for bias in self.biases]
        grad = grad_output
        for layer_idx in reversed(range(len(self.weights))):
            grad_weights[layer_idx] = activations[layer_idx].T @ grad
            grad_biases[layer_idx] = np.sum(grad, axis=0)
            if layer_idx > 0:
                grad = (grad @ self.weights[layer_idx].T) * _activation_grad(pre_activations[layer_idx - 1])

        for idx in range(len(self.weights)):
            self.weights[idx] -= learning_rate * grad_weights[idx]
            self.biases[idx] -= learning_rate * grad_biases[idx]
        return float(np.mean(td_error ** 2))

    def metadata(self) -> dict[str, Any]:
        return {
            "q_model_type": self.q_model_type,
            "architecture": self.architecture,
            "hidden_sizes": list(self.hidden_sizes),
        }


class DuelingMLPQModel(MLPQModel):
    def __init__(self, input_dim: int, action_dim: int, hidden_sizes: list[int], seed: int) -> None:
        super().__init__(input_dim, action_dim, hidden_sizes, seed)
        self.architecture = "dueling_mlp_q_network"
        self.q_model_type = "dueling_mlp_q_network"
        rng = np.random.default_rng(seed + 1)
        shared_sizes = [input_dim, *hidden_sizes]
        self.shared_weights = [
            rng.normal(scale=0.05, size=(shared_sizes[idx], shared_sizes[idx + 1])).astype(np.float32)
            for idx in range(len(shared_sizes) - 1)
        ]
        self.shared_biases = [np.zeros(shared_sizes[idx + 1], dtype=np.float32) for idx in range(len(shared_sizes) - 1)]
        value_input = hidden_sizes[-1]
        self.value_weight = rng.normal(scale=0.05, size=(value_input, 1)).astype(np.float32)
        self.value_bias = np.zeros(1, dtype=np.float32)
        self.advantage_weight = rng.normal(scale=0.05, size=(value_input, action_dim)).astype(np.float32)
        self.advantage_bias = np.zeros(action_dim, dtype=np.float32)
        self.weights = self.shared_weights + [self.value_weight, self.advantage_weight]
        self.biases = self.shared_biases + [self.value_bias, self.advantage_bias]

    def copy(self) -> "DuelingMLPQModel":
        new = object.__new__(DuelingMLPQModel)
        new.input_dim = self.input_dim
        new.action_dim = self.action_dim
        new.hidden_sizes = list(self.hidden_sizes)
        new.architecture = self.architecture
        new.q_model_type = self.q_model_type
        new.shared_weights = [w.copy() for w in self.shared_weights]
        new.shared_biases = [b.copy() for b in self.shared_biases]
        new.value_weight = self.value_weight.copy()
        new.value_bias = self.value_bias.copy()
        new.advantage_weight = self.advantage_weight.copy()
        new.advantage_bias = self.advantage_bias.copy()
        new.weights = new.shared_weights + [new.value_weight, new.advantage_weight]
        new.biases = new.shared_biases + [new.value_bias, new.advantage_bias]
        return new

    def _shared_forward(self, states: np.ndarray) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray]]:
        activations = [states.astype(np.float32)]
        pre_activations: list[np.ndarray] = []
        x = activations[0]
        for weight, bias in zip(self.shared_weights, self.shared_biases, strict=False):
            z = x @ weight + bias
            pre_activations.append(z)
            x = _activation(z)
            activations.append(x)
        return x, activations, pre_activations

    def predict(self, states: np.ndarray) -> np.ndarray:
        trunk, _, _ = self._shared_forward(states)
        value = trunk @ self.value_weight + self.value_bias
        advantage = trunk @ self.advantage_weight + self.advantage_bias
        return value + advantage - np.mean(advantage, axis=1, keepdims=True)

    def apply_gradient(self, states: np.ndarray, actions: np.ndarray, td_error: np.ndarray, learning_rate: float) -> float:
        batch_size = states.shape[0]
        trunk, activations, pre_activations = self._shared_forward(states)
        value = trunk @ self.value_weight + self.value_bias
        advantage = trunk @ self.advantage_weight + self.advantage_bias
        q_values = value + advantage - np.mean(advantage, axis=1, keepdims=True)

        grad_q = np.zeros_like(q_values)
        grad_q[np.arange(batch_size), actions] = -td_error
        grad_q /= batch_size

        grad_value = np.sum(grad_q, axis=1, keepdims=True)
        grad_advantage = grad_q - np.mean(grad_q, axis=1, keepdims=True)

        grad_value_weight = trunk.T @ grad_value
        grad_value_bias = np.sum(grad_value, axis=0)
        grad_advantage_weight = trunk.T @ grad_advantage
        grad_advantage_bias = np.sum(grad_advantage, axis=0)

        grad_trunk = grad_value @ self.value_weight.T + grad_advantage @ self.advantage_weight.T
        for layer_idx in reversed(range(len(self.shared_weights))):
            grad_weight = activations[layer_idx].T @ grad_trunk
            grad_bias = np.sum(grad_trunk, axis=0)
            if layer_idx > 0:
                grad_trunk = (grad_trunk @ self.shared_weights[layer_idx].T) * _activation_grad(pre_activations[layer_idx - 1])
            self.shared_weights[layer_idx] -= learning_rate * grad_weight
            self.shared_biases[layer_idx] -= learning_rate * grad_bias

        self.value_weight -= learning_rate * grad_value_weight
        self.value_bias -= learning_rate * grad_value_bias
        self.advantage_weight -= learning_rate * grad_advantage_weight
        self.advantage_bias -= learning_rate * grad_advantage_bias
        return float(np.mean(td_error ** 2))

    def metadata(self) -> dict[str, Any]:
        return {
            "q_model_type": self.q_model_type,
            "architecture": self.architecture,
            "hidden_sizes": list(self.hidden_sizes),
        }


class DQNTrainer:
    def __init__(self, cfg: TrainerConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        self.replay_buffer = ReplayBuffer(capacity=10000, seed=cfg.seed)
        self.rng = np.random.default_rng(cfg.seed)
        if cfg.algorithm == "dueling_dqn":
            self.policy_net = DuelingMLPQModel(cfg.input_dim, cfg.action_dim, cfg.hidden_sizes, cfg.seed)
            self.target_net = self.policy_net.copy()
        else:
            self.policy_net = MLPQModel(cfg.input_dim, cfg.action_dim, cfg.hidden_sizes, cfg.seed)
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

    def _compute_dqn_targets(self, rewards: np.ndarray, next_states: np.ndarray, dones: np.ndarray) -> np.ndarray:
        next_q = np.max(self.target_net.predict(next_states), axis=1)
        return rewards + self.cfg.gamma * next_q * (1.0 - dones)

    def _compute_ddqn_targets(self, rewards: np.ndarray, next_states: np.ndarray, dones: np.ndarray) -> np.ndarray:
        next_policy_q = self.policy_net.predict(next_states)
        next_target_q = self.target_net.predict(next_states)
        next_actions = np.argmax(next_policy_q, axis=1)
        next_q = next_target_q[np.arange(len(next_actions)), next_actions]
        return rewards + self.cfg.gamma * next_q * (1.0 - dones)

    def _compute_targets(self, rewards: np.ndarray, next_states: np.ndarray, dones: np.ndarray) -> np.ndarray:
        if self.cfg.algorithm == "ddqn":
            return self._compute_ddqn_targets(rewards, next_states, dones)
        return self._compute_dqn_targets(rewards, next_states, dones)

    def train_step(self) -> TrainingStepMetrics | None:
        if len(self.replay_buffer) < self.cfg.batch_size:
            return None
        indices = self.replay_buffer.sample_indices(self.cfg.batch_size)
        batch = [self.replay_buffer.to_list()[int(index)] for index in indices]
        for transition in batch:
            transition.validate()
            if transition.action < 0 or transition.action >= self.cfg.action_dim:
                raise ValueError("transition action is out of range for the configured action_dim")
        states = np.stack([t.state for t in batch]).astype(np.float32)
        actions = np.asarray([t.action for t in batch], dtype=np.int64)
        rewards = np.asarray([t.reward for t in batch], dtype=np.float32)
        next_states = np.stack([t.next_state for t in batch]).astype(np.float32)
        dones = np.asarray([float(t.done) for t in batch], dtype=np.float32)

        q_values = self.policy_net.predict(states)
        targets = self._compute_targets(rewards, next_states, dones)
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
            "policy_weights": [w.tolist() for w in getattr(self.policy_net, "weights", [])],
            "policy_bias": [b.tolist() for b in getattr(self.policy_net, "biases", [])],
            "target_weights": [w.tolist() for w in getattr(self.target_net, "weights", [])],
            "target_bias": [b.tolist() for b in getattr(self.target_net, "biases", [])],
            "gradient_steps": self.gradient_steps,
            "model_architecture": self.policy_net.architecture,
            "q_model_type": self.policy_net.q_model_type,
            "hidden_sizes": list(self.cfg.hidden_sizes),
        }
        if self.cfg.algorithm == "dueling_dqn":
            payload.update(
                {
                    "shared_weights": [w.tolist() for w in self.policy_net.shared_weights],
                    "shared_biases": [b.tolist() for b in self.policy_net.shared_biases],
                    "value_weight": self.policy_net.value_weight.tolist(),
                    "value_bias": self.policy_net.value_bias.tolist(),
                    "advantage_weight": self.policy_net.advantage_weight.tolist(),
                    "advantage_bias": self.policy_net.advantage_bias.tolist(),
                    "target_shared_weights": [w.tolist() for w in self.target_net.shared_weights],
                    "target_shared_biases": [b.tolist() for b in self.target_net.shared_biases],
                    "target_value_weight": self.target_net.value_weight.tolist(),
                    "target_value_bias": self.target_net.value_bias.tolist(),
                    "target_advantage_weight": self.target_net.advantage_weight.tolist(),
                    "target_advantage_bias": self.target_net.advantage_bias.tolist(),
                }
            )
        path.write_text(json_dumps(payload))
        return str(path)

    def load(self, path: str | Path) -> None:
        payload = json_loads(Path(path).read_text())
        if payload["algorithm"] != self.cfg.algorithm:
            raise ValueError("checkpoint algorithm does not match trainer configuration")
        if payload["hidden_sizes"] != self.cfg.hidden_sizes:
            raise ValueError("checkpoint hidden_sizes do not match trainer configuration")
        self.gradient_steps = int(payload.get("gradient_steps", 0))
        if self.cfg.algorithm == "dueling_dqn":
            self.policy_net.shared_weights = [np.asarray(weight, dtype=np.float32) for weight in payload["shared_weights"]]
            self.policy_net.shared_biases = [np.asarray(bias, dtype=np.float32) for bias in payload["shared_biases"]]
            self.policy_net.value_weight = np.asarray(payload["value_weight"], dtype=np.float32)
            self.policy_net.value_bias = np.asarray(payload["value_bias"], dtype=np.float32)
            self.policy_net.advantage_weight = np.asarray(payload["advantage_weight"], dtype=np.float32)
            self.policy_net.advantage_bias = np.asarray(payload["advantage_bias"], dtype=np.float32)
            self.policy_net.weights = self.policy_net.shared_weights + [self.policy_net.value_weight, self.policy_net.advantage_weight]
            self.policy_net.biases = self.policy_net.shared_biases + [self.policy_net.value_bias, self.policy_net.advantage_bias]
            self.target_net.shared_weights = [np.asarray(weight, dtype=np.float32) for weight in payload["target_shared_weights"]]
            self.target_net.shared_biases = [np.asarray(bias, dtype=np.float32) for bias in payload["target_shared_biases"]]
            self.target_net.value_weight = np.asarray(payload["target_value_weight"], dtype=np.float32)
            self.target_net.value_bias = np.asarray(payload["target_value_bias"], dtype=np.float32)
            self.target_net.advantage_weight = np.asarray(payload["target_advantage_weight"], dtype=np.float32)
            self.target_net.advantage_bias = np.asarray(payload["target_advantage_bias"], dtype=np.float32)
            self.target_net.weights = self.target_net.shared_weights + [self.target_net.value_weight, self.target_net.advantage_weight]
            self.target_net.biases = self.target_net.shared_biases + [self.target_net.value_bias, self.target_net.advantage_bias]
        else:
            self.policy_net.weights = [np.asarray(weight, dtype=np.float32) for weight in payload["policy_weights"]]
            self.policy_net.biases = [np.asarray(bias, dtype=np.float32) for bias in payload["policy_bias"]]
            self.target_net.weights = [np.asarray(weight, dtype=np.float32) for weight in payload["target_weights"]]
            self.target_net.biases = [np.asarray(bias, dtype=np.float32) for bias in payload["target_bias"]]


def json_dumps(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, indent=2, sort_keys=True)


def json_loads(content: str) -> dict[str, Any]:
    import json

    return json.loads(content)
