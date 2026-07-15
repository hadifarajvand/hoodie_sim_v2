from __future__ import annotations

from dataclasses import dataclass, field
import copy
import math
import random
from typing import Any, Iterable

import numpy as np
import torch
from torch import nn


def _select_device(preferred: str | None = None) -> torch.device:
    if preferred is not None:
        return torch.device(preferred)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _deterministic_init(module: nn.Module) -> None:
    if isinstance(module, nn.Linear):
        nn.init.kaiming_uniform_(module.weight, a=math.sqrt(5))
        if module.bias is not None:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(module.weight)
            bound = 1 / math.sqrt(fan_in) if fan_in > 0 else 0
            nn.init.uniform_(module.bias, -bound, bound)
    elif isinstance(module, nn.LSTM):
        for name, parameter in module.named_parameters():
            if "weight" in name:
                nn.init.xavier_uniform_(parameter)
            else:
                nn.init.zeros_(parameter)


class DuelingQNetwork(nn.Module):
    def __init__(self, input_dim: int, action_dim: int, hidden_dims: tuple[int, ...] = (256, 256), *, seed: int = 0) -> None:
        super().__init__()
        if input_dim <= 0:
            raise ValueError("input_dim must be positive")
        if action_dim <= 1:
            raise ValueError("action_dim must be > 1")
        self.input_dim = int(input_dim)
        self.action_dim = int(action_dim)
        self.hidden_dims = tuple(int(width) for width in hidden_dims)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(int(seed))
            layers: list[nn.Module] = []
            current = self.input_dim
            for width in self.hidden_dims:
                layers.extend((nn.Linear(current, width), nn.ReLU()))
                current = width
            self.encoder = nn.Sequential(*layers)
            self.value_head = nn.Sequential(nn.Linear(current, current), nn.ReLU(), nn.Linear(current, 1))
            self.advantage_head = nn.Sequential(nn.Linear(current, current), nn.ReLU(), nn.Linear(current, self.action_dim))
            self.apply(_deterministic_init)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        features = self.encoder(state)
        value = self.value_head(features)
        advantage = self.advantage_head(features)
        return value + advantage - advantage.mean(dim=-1, keepdim=True)


@dataclass(slots=True, frozen=True)
class Transition:
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    legal_mask: np.ndarray


class ReplayBuffer:
    def __init__(self, capacity: int, *, seed: int, warmup_size: int = 1, batch_size: int = 32) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = int(capacity)
        self.warmup_size = int(warmup_size)
        self.batch_size = int(batch_size)
        self._items: list[Transition] = []
        self._rng = random.Random(seed)
        self._seed = int(seed)

    def __len__(self) -> int:
        return len(self._items)

    def add(self, transition: Transition) -> None:
        self._items.append(transition)
        if len(self._items) > self.capacity:
            del self._items[0 : len(self._items) - self.capacity]

    def sample(self, batch_size: int | None = None) -> tuple[Transition, ...]:
        if batch_size is None:
            batch_size = self.batch_size
        if len(self._items) < batch_size:
            raise ValueError("not enough transitions")
        indices = self._rng.sample(range(len(self._items)), batch_size)
        return tuple(self._items[index] for index in indices)

    def as_list(self) -> list[Transition]:
        return list(self._items)

    def state_dict(self) -> dict[str, Any]:
        return {"capacity": self.capacity, "warmup_size": self.warmup_size, "batch_size": self.batch_size, "seed": self._seed, "rng_state": self._rng.getstate(), "items": list(self._items)}

    def load_state_dict(self, state: dict[str, Any]) -> None:
        self.capacity = int(state["capacity"])
        self.warmup_size = int(state["warmup_size"])
        self.batch_size = int(state["batch_size"])
        self._seed = int(state["seed"])
        self._rng.setstate(state["rng_state"])
        self._items = list(state["items"])


def masked_epsilon_greedy(q_values: torch.Tensor, legal_mask: torch.Tensor, epsilon: float, rng: random.Random) -> int:
    if q_values.ndim != 1:
        raise ValueError("q_values must be 1D")
    legal_indices = [index for index, allowed in enumerate(legal_mask.tolist()) if allowed]
    if not legal_indices:
        raise ValueError("No legal actions available")
    if rng.random() < float(epsilon):
        return rng.choice(legal_indices)
    legal_q = q_values.clone()
    legal_q[~legal_mask] = float("-inf")
    max_value = torch.max(legal_q[legal_mask])
    best = [index for index in legal_indices if torch.isclose(legal_q[index], max_value)]
    return min(best)


@dataclass(slots=True)
class DDQNLearner:
    input_dim: int
    action_dim: int = 22
    hidden_dims: tuple[int, ...] = (256, 256)
    gamma: float = 0.99
    learning_rate: float = 1e-3
    batch_size: int = 32
    capacity: int = 10_000
    warmup_size: int = 64
    seed: int = 0
    device_name: str | None = None
    target_update_interval: int = 100
    soft_update_tau: float | None = None
    grad_clip_norm: float | None = 10.0
    huber_delta: float = 1.0
    online_network: DuelingQNetwork = field(init=False)
    target_network: DuelingQNetwork = field(init=False)
    optimizer: torch.optim.Optimizer = field(init=False)
    replay_buffer: ReplayBuffer = field(init=False)
    device: torch.device = field(init=False)
    training_steps: int = field(default=0, init=False)
    target_update_steps: int = field(default=0, init=False)
    rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.device = _select_device(self.device_name)
        self.rng = random.Random(self.seed)
        self.online_network = DuelingQNetwork(self.input_dim, self.action_dim, self.hidden_dims, seed=self.seed).to(self.device)
        self.target_network = DuelingQNetwork(self.input_dim, self.action_dim, self.hidden_dims, seed=self.seed + 1).to(self.device)
        self.target_network.load_state_dict(self.online_network.state_dict())
        self.optimizer = torch.optim.Adam(self.online_network.parameters(), lr=self.learning_rate)
        self.replay_buffer = ReplayBuffer(self.capacity, seed=self.seed, warmup_size=self.warmup_size, batch_size=self.batch_size)

    def select_action(self, state: torch.Tensor, legal_mask: torch.Tensor, epsilon: float, *, evaluation: bool = False) -> int:
        self.online_network.eval()
        with torch.no_grad():
            q_values = self.online_network(state.to(self.device).unsqueeze(0)).squeeze(0)
        if evaluation:
            epsilon = 0.0
        return masked_epsilon_greedy(q_values, legal_mask.to(self.device), float(epsilon), self.rng)

    def record_transition(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool, legal_mask: np.ndarray) -> None:
        self.replay_buffer.add(Transition(state=state, action=int(action), reward=float(reward), next_state=next_state, done=bool(done), legal_mask=legal_mask))

    def learn_from_replay(self, batch_size: int | None = None) -> dict[str, float] | None:
        if len(self.replay_buffer) < max(self.replay_buffer.warmup_size, batch_size or self.replay_buffer.batch_size):
            return None
        batch = self.replay_buffer.sample(batch_size)
        state = torch.tensor(np.stack([transition.state for transition in batch]), dtype=torch.float32, device=self.device)
        next_state = torch.tensor(np.stack([transition.next_state for transition in batch]), dtype=torch.float32, device=self.device)
        action = torch.tensor([transition.action for transition in batch], dtype=torch.long, device=self.device)
        reward = torch.tensor([transition.reward for transition in batch], dtype=torch.float32, device=self.device)
        done = torch.tensor([transition.done for transition in batch], dtype=torch.bool, device=self.device)
        legal_mask = torch.tensor(np.stack([transition.legal_mask for transition in batch]), dtype=torch.bool, device=self.device)

        q_values = self.online_network(state).gather(1, action.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            next_online = self.online_network(next_state)
            next_online[~legal_mask] = float("-inf")
            next_action = torch.argmax(next_online, dim=1)
            next_target = self.target_network(next_state).gather(1, next_action.unsqueeze(1)).squeeze(1)
            target = reward + self.gamma * next_target * (~done).float()

        loss = torch.nn.functional.smooth_l1_loss(q_values, target)
        self.optimizer.zero_grad(set_to_none=True)
        loss.backward()
        if self.grad_clip_norm is not None:
            torch.nn.utils.clip_grad_norm_(self.online_network.parameters(), self.grad_clip_norm)
        self.optimizer.step()
        self.training_steps += 1
        if self.soft_update_tau is not None:
            self._soft_update()
        elif self.target_update_interval > 0 and self.training_steps % self.target_update_interval == 0:
            self.sync_target_network()
        return {"loss": float(loss.detach().cpu().item())}

    def _soft_update(self) -> None:
        tau = float(self.soft_update_tau)
        with torch.no_grad():
            for target_param, online_param in zip(self.target_network.parameters(), self.online_network.parameters(), strict=True):
                target_param.data.mul_(1.0 - tau).add_(online_param.data, alpha=tau)
        self.target_update_steps += 1

    def sync_target_network(self) -> None:
        self.target_network.load_state_dict(self.online_network.state_dict())
        self.target_update_steps += 1

    def state_dict(self) -> dict[str, Any]:
        return {
            "input_dim": self.input_dim,
            "action_dim": self.action_dim,
            "hidden_dims": self.hidden_dims,
            "gamma": self.gamma,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "capacity": self.capacity,
            "warmup_size": self.warmup_size,
            "seed": self.seed,
            "device_name": self.device_name,
            "target_update_interval": self.target_update_interval,
            "soft_update_tau": self.soft_update_tau,
            "grad_clip_norm": self.grad_clip_norm,
            "huber_delta": self.huber_delta,
            "online_state_dict": self.online_network.state_dict(),
            "target_state_dict": self.target_network.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "replay_buffer": self.replay_buffer.state_dict(),
            "rng_state": self.rng.getstate(),
            "python_random_state": random.getstate(),
            "numpy_random_state": np.random.get_state(),
            "torch_random_state": torch.get_rng_state(),
            "cuda_random_state": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
            "training_steps": self.training_steps,
            "target_update_steps": self.target_update_steps,
        }

    def load_state_dict(self, state: dict[str, Any]) -> None:
        self.online_network.load_state_dict(state["online_state_dict"])
        self.target_network.load_state_dict(state["target_state_dict"])
        self.optimizer.load_state_dict(state["optimizer_state_dict"])
        self.replay_buffer.load_state_dict(state["replay_buffer"])
        self.rng.setstate(state["rng_state"])
        random.setstate(state["python_random_state"])
        np.random.set_state(state["numpy_random_state"])
        torch.set_rng_state(state["torch_random_state"])
        if torch.cuda.is_available() and state.get("cuda_random_state") is not None:
            torch.cuda.set_rng_state_all(state["cuda_random_state"])
        self.training_steps = int(state["training_steps"])
        self.target_update_steps = int(state["target_update_steps"])

    def save(self, path: str) -> None:
        torch.save(self.state_dict(), path)

    def load(self, path: str) -> None:
        self.load_state_dict(torch.load(path, map_location=self.device, weights_only=False))
