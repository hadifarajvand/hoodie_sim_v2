from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import hashlib
import math
import random

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from src.policies.interface import PolicyContext


CANONICAL_ACTIONS = ("local", "horizontal", "vertical")


@dataclass(slots=True)
class ReplayTransition:
    state: tuple[float, ...]
    action: str
    reward: float
    next_state: tuple[float, ...]
    done: bool


@dataclass(slots=True)
class ReplayBuffer:
    capacity: int = 4096
    seed: int = 0
    items: list[ReplayTransition] = field(default_factory=list)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def add(self, transition: ReplayTransition) -> None:
        self.items.append(transition)
        if len(self.items) > self.capacity:
            del self.items[: len(self.items) - self.capacity]

    def sample(self, batch_size: int) -> tuple[ReplayTransition, ...]:
        if batch_size <= 0 or not self.items:
            return ()
        batch_size = min(batch_size, len(self.items))
        indices = self._rng.sample(range(len(self.items)), batch_size)
        return tuple(self.items[index] for index in indices)

    def state_dict(self) -> dict[str, Any]:
        return {"capacity": self.capacity, "seed": self.seed, "items": list(self.items), "rng_state": self._rng.getstate()}

    def load_state_dict(self, state: dict[str, Any]) -> None:
        self.capacity = int(state.get("capacity", self.capacity))
        self.seed = int(state.get("seed", self.seed))
        self.items = list(state.get("items", []))
        self._rng = random.Random(self.seed)
        rng_state = state.get("rng_state")
        if rng_state is not None:
            self._rng.setstate(rng_state)


class DuelingQNetwork(nn.Module):
    def __init__(self, input_dim: int, action_dim: int = len(CANONICAL_ACTIONS), hidden_dim: int = 64) -> None:
        super().__init__()
        self.input_dim = input_dim
        self.action_dim = action_dim
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.value_stream = nn.Sequential(nn.Linear(hidden_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, 1))
        self.advantage_stream = nn.Sequential(nn.Linear(hidden_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, action_dim))
        self.reset_parameters()

    def reset_parameters(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.kaiming_uniform_(module.weight, a=math.sqrt(5))
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        encoded = self.encoder(features)
        value = self.value_stream(encoded)
        advantage = self.advantage_stream(encoded)
        return value + advantage - advantage.mean(dim=-1, keepdim=True)


@dataclass(slots=True)
class DoubleDQNAgent:
    input_dim: int = 5
    action_names: tuple[str, ...] = CANONICAL_ACTIONS
    hidden_dim: int = 64
    gamma: float = 0.99
    learning_rate: float = 1e-3
    batch_size: int = 8
    update_interval: int = 4
    target_mix: float = 1.0
    warmup_size: int = 4
    capacity: int = 4096
    seed: int = 0
    device_name: str | None = None
    online: DuelingQNetwork = field(init=False)
    target: DuelingQNetwork = field(init=False)
    replay: ReplayBuffer = field(init=False)
    optimizer: torch.optim.Optimizer = field(init=False)
    epsilon: float = 0.1
    steps: int = 0
    target_updates: int = 0
    training: bool = True

    def __post_init__(self) -> None:
        self.device = self._select_device(self.device_name)
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)
        random.seed(self.seed)
        self.online = DuelingQNetwork(self.input_dim, len(self.action_names), self.hidden_dim).to(self.device)
        self.target = DuelingQNetwork(self.input_dim, len(self.action_names), self.hidden_dim).to(self.device)
        self.target.load_state_dict(self.online.state_dict())
        self.replay = ReplayBuffer(capacity=self.capacity, seed=self.seed)
        self.optimizer = torch.optim.Adam(self.online.parameters(), lr=self.learning_rate)

    def _select_device(self, device_name: str | None) -> torch.device:
        if device_name:
            return torch.device(device_name)
        if torch.cuda.is_available():
            return torch.device("cuda")
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    def _tensor(self, features: tuple[float, ...] | list[float]) -> torch.Tensor:
        return torch.tensor(features, dtype=torch.float32, device=self.device).unsqueeze(0)

    def _legal_indices(self, legal_actions: tuple[str, ...]) -> list[int]:
        return [index for index, action in enumerate(self.action_names) if action in legal_actions]

    def _q_values(self, features: tuple[float, ...]) -> torch.Tensor:
        return self.online(self._tensor(features)).squeeze(0)

    def _masked_q_values(self, features: tuple[float, ...], legal_actions: tuple[str, ...]) -> torch.Tensor:
        q_values = self._q_values(features)
        mask = torch.full_like(q_values, float("-inf"))
        for index in self._legal_indices(legal_actions):
            mask[index] = q_values[index]
        return mask

    def select(self, features: tuple[float, ...], legal_actions: tuple[str, ...]) -> str:
        if not legal_actions:
            raise ValueError("No legal actions")
        legal_actions = tuple(legal_actions)
        if self.training and random.random() < self.epsilon:
            return random.choice(legal_actions)
        masked = self._masked_q_values(features, legal_actions)
        best_value = torch.max(masked)
        best_indices = [index for index, value in enumerate(masked.tolist()) if value == best_value.item()]
        chosen_index = min(best_indices)
        return self.action_names[chosen_index]

    def masked_epsilon_greedy(self, features: tuple[float, ...], legal_actions: tuple[str, ...], epsilon: float) -> str:
        previous = self.epsilon
        previous_training = self.training
        self.epsilon = epsilon
        self.training = True
        try:
            return self.select(features, legal_actions)
        finally:
            self.epsilon = previous
            self.training = previous_training

    def _batch_tensor(self, batch: tuple[ReplayTransition, ...]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        states = torch.tensor([transition.state for transition in batch], dtype=torch.float32, device=self.device)
        next_states = torch.tensor([transition.next_state for transition in batch], dtype=torch.float32, device=self.device)
        actions = torch.tensor([self.action_names.index(transition.action) for transition in batch], dtype=torch.long, device=self.device)
        rewards = torch.tensor([transition.reward for transition in batch], dtype=torch.float32, device=self.device)
        dones = torch.tensor([transition.done for transition in batch], dtype=torch.float32, device=self.device)
        return states, next_states, actions, rewards, dones

    def update(self) -> int:
        if len(self.replay.items) < self.warmup_size:
            return 0
        batch = self.replay.sample(self.batch_size)
        if not batch:
            return 0
        states, next_states, actions, rewards, dones = self._batch_tensor(batch)
        q_values = self.online(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            next_online = self.online(next_states).argmax(dim=1, keepdim=True)
            next_target = self.target(next_states).gather(1, next_online).squeeze(1)
            targets = rewards + (1.0 - dones) * self.gamma * next_target
        loss = F.smooth_l1_loss(q_values, targets)
        self.optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.online.parameters(), max_norm=1.0)
        self.optimizer.step()
        self.steps += 1
        if self.steps % self.update_interval == 0:
            self.sync_target_network()
        return len(batch)

    def sync_target_network(self) -> None:
        if self.target_mix >= 1.0:
            self.target.load_state_dict(self.online.state_dict())
        else:
            target_state = self.target.state_dict()
            online_state = self.online.state_dict()
            for key, value in online_state.items():
                target_state[key] = self.target_mix * value + (1.0 - self.target_mix) * target_state[key]
            self.target.load_state_dict(target_state)
        self.target_updates += 1

    def export_state(self) -> dict[str, Any]:
        return {
            "input_dim": self.input_dim,
            "action_names": self.action_names,
            "hidden_dim": self.hidden_dim,
            "gamma": self.gamma,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "update_interval": self.update_interval,
            "target_mix": self.target_mix,
            "warmup_size": self.warmup_size,
            "capacity": self.capacity,
            "seed": self.seed,
            "epsilon": self.epsilon,
            "steps": self.steps,
            "target_updates": self.target_updates,
            "training": self.training,
            "device_name": self.device.type,
            "online_state_dict": self.online.state_dict(),
            "target_state_dict": self.target.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "replay": self.replay.state_dict(),
            "python_rng_state": random.getstate(),
            "numpy_rng_state": np.random.get_state(),
            "torch_rng_state": torch.get_rng_state(),
            "cuda_rng_state": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "DoubleDQNAgent":
        agent = cls(
            input_dim=int(state.get("input_dim", 5)),
            action_names=tuple(state.get("action_names", CANONICAL_ACTIONS)),
            hidden_dim=int(state.get("hidden_dim", 64)),
            gamma=float(state.get("gamma", 0.99)),
            learning_rate=float(state.get("learning_rate", 1e-3)),
            batch_size=int(state.get("batch_size", 8)),
            update_interval=int(state.get("update_interval", 4)),
            target_mix=float(state.get("target_mix", 1.0)),
            warmup_size=int(state.get("warmup_size", 4)),
            capacity=int(state.get("capacity", 4096)),
            seed=int(state.get("seed", 0)),
            device_name=state.get("device_name"),
        )
        agent.epsilon = float(state.get("epsilon", 0.1))
        agent.steps = int(state.get("steps", 0))
        agent.target_updates = int(state.get("target_updates", 0))
        agent.training = bool(state.get("training", True))
        agent.online.load_state_dict(state["online_state_dict"])
        agent.target.load_state_dict(state["target_state_dict"])
        agent.optimizer.load_state_dict(state["optimizer_state_dict"])
        agent.replay.load_state_dict(state["replay"])
        random.setstate(state["python_rng_state"])
        np.random.set_state(state["numpy_rng_state"])
        torch.set_rng_state(state["torch_rng_state"])
        if torch.cuda.is_available() and state.get("cuda_rng_state") is not None:
            torch.cuda.set_rng_state_all(state["cuda_rng_state"])
        return agent
