from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Any, Iterable

import numpy as np
import torch
from torch import nn


def _select_device(preferred: str | None = None) -> torch.device:
    if preferred is not None:
        requested = torch.device(preferred)
        if requested.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available")
        if requested.type == "mps" and not (
            getattr(torch.backends, "mps", None) is not None
            and torch.backends.mps.is_available()
        ):
            raise RuntimeError("MPS was requested but is not available")
        return requested
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


class DuelingQNetwork(nn.Module):
    def __init__(
        self,
        input_dim: int,
        action_dim: int,
        hidden_dims: tuple[int, ...] = (256, 256),
        *,
        seed: int = 0,
    ) -> None:
        super().__init__()
        if input_dim <= 0:
            raise ValueError("input_dim must be positive")
        if action_dim <= 1:
            raise ValueError("action_dim must be > 1")
        if not hidden_dims or any(width <= 0 for width in hidden_dims):
            raise ValueError("hidden_dims must contain positive widths")
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
            self.value_head = nn.Sequential(
                nn.Linear(current, current), nn.ReLU(), nn.Linear(current, 1)
            )
            self.advantage_head = nn.Sequential(
                nn.Linear(current, current), nn.ReLU(), nn.Linear(current, self.action_dim)
            )
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
    def __init__(
        self,
        capacity: int,
        *,
        seed: int,
        warmup_size: int = 1,
        batch_size: int = 32,
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if warmup_size < 0:
            raise ValueError("warmup_size must be non-negative")
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
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
        overflow = len(self._items) - self.capacity
        if overflow > 0:
            del self._items[:overflow]

    def sample(self, batch_size: int | None = None) -> tuple[Transition, ...]:
        size = self.batch_size if batch_size is None else int(batch_size)
        if size <= 0:
            raise ValueError("batch_size must be positive")
        if len(self._items) < size:
            raise ValueError("not enough transitions")
        indices = self._rng.sample(range(len(self._items)), size)
        return tuple(self._items[index] for index in indices)

    def as_list(self) -> list[Transition]:
        return list(self._items)

    def state_dict(self) -> dict[str, Any]:
        return {
            "capacity": self.capacity,
            "warmup_size": self.warmup_size,
            "batch_size": self.batch_size,
            "seed": self._seed,
            "rng_state": self._rng.getstate(),
            "items": list(self._items),
        }

    def load_state_dict(self, state: dict[str, Any]) -> None:
        self.capacity = int(state["capacity"])
        self.warmup_size = int(state["warmup_size"])
        self.batch_size = int(state["batch_size"])
        self._seed = int(state["seed"])
        self._rng = random.Random(self._seed)
        self._rng.setstate(state["rng_state"])
        self._items = list(state["items"])[-self.capacity :]


def masked_epsilon_greedy(
    q_values: torch.Tensor,
    legal_mask: torch.Tensor,
    epsilon: float,
    rng: random.Random,
) -> int:
    if q_values.ndim != 1:
        raise ValueError("q_values must be 1D")
    if legal_mask.ndim != 1 or legal_mask.numel() != q_values.numel():
        raise ValueError("legal_mask must be 1D and match q_values")
    legal_mask = legal_mask.to(dtype=torch.bool, device=q_values.device)
    legal_indices = [index for index, allowed in enumerate(legal_mask.tolist()) if allowed]
    if not legal_indices:
        raise ValueError("No legal actions available")
    epsilon = min(1.0, max(0.0, float(epsilon)))
    if rng.random() < epsilon:
        return rng.choice(legal_indices)
    legal_q = q_values.clone()
    legal_q[~legal_mask] = float("-inf")
    max_value = torch.max(legal_q[legal_mask])
    best = [index for index in legal_indices if torch.isclose(legal_q[index], max_value)]
    return min(best)


@dataclass(slots=True)
class DDQNLearner:
    input_dim: int
    action_dim: int = 3
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
    online_network: DuelingQNetwork = field(init=False)
    target_network: DuelingQNetwork = field(init=False)
    optimizer: torch.optim.Optimizer = field(init=False)
    replay_buffer: ReplayBuffer = field(init=False)
    device: torch.device = field(init=False)
    training_steps: int = field(default=0, init=False)
    target_update_steps: int = field(default=0, init=False)
    rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        if not 0.0 <= float(self.gamma) <= 1.0:
            raise ValueError("gamma must be in [0, 1]")
        self.device = _select_device(self.device_name)
        self.rng = random.Random(self.seed)
        self.online_network = DuelingQNetwork(
            self.input_dim, self.action_dim, self.hidden_dims, seed=self.seed
        ).to(self.device)
        self.target_network = DuelingQNetwork(
            self.input_dim, self.action_dim, self.hidden_dims, seed=self.seed + 1
        ).to(self.device)
        self.target_network.load_state_dict(self.online_network.state_dict())
        self.target_network.eval()
        self.optimizer = torch.optim.Adam(
            self.online_network.parameters(), lr=float(self.learning_rate)
        )
        self.replay_buffer = ReplayBuffer(
            self.capacity,
            seed=self.seed,
            warmup_size=self.warmup_size,
            batch_size=self.batch_size,
        )

    def configure(
        self,
        *,
        learning_rate: float | None = None,
        batch_size: int | None = None,
        gamma: float | None = None,
        target_update_interval: int | None = None,
    ) -> None:
        if learning_rate is not None:
            if learning_rate <= 0:
                raise ValueError("learning_rate must be positive")
            self.learning_rate = float(learning_rate)
            for group in self.optimizer.param_groups:
                group["lr"] = self.learning_rate
        if batch_size is not None:
            if batch_size <= 0:
                raise ValueError("batch_size must be positive")
            self.batch_size = int(batch_size)
            self.replay_buffer.batch_size = self.batch_size
        if gamma is not None:
            if not 0.0 <= float(gamma) <= 1.0:
                raise ValueError("gamma must be in [0, 1]")
            self.gamma = float(gamma)
        if target_update_interval is not None:
            if target_update_interval <= 0:
                raise ValueError("target_update_interval must be positive")
            self.target_update_interval = int(target_update_interval)

    def select_action(
        self,
        state: torch.Tensor,
        legal_mask: torch.Tensor,
        epsilon: float,
        *,
        evaluation: bool = False,
    ) -> int:
        self.online_network.eval()
        with torch.no_grad():
            q_values = self.online_network(state.to(self.device).unsqueeze(0)).squeeze(0)
        return masked_epsilon_greedy(
            q_values,
            legal_mask.to(self.device),
            0.0 if evaluation else float(epsilon),
            self.rng,
        )

    def record_transition(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        legal_mask: np.ndarray,
    ) -> None:
        mask = np.asarray(legal_mask, dtype=bool)
        if mask.shape != (self.action_dim,):
            raise ValueError("legal_mask shape does not match action_dim")
        self.replay_buffer.add(
            Transition(
                state=np.asarray(state, dtype=np.float32),
                action=int(action),
                reward=float(reward),
                next_state=np.asarray(next_state, dtype=np.float32),
                done=bool(done),
                legal_mask=mask,
            )
        )

    def learn_from_replay(self, batch_size: int | None = None) -> dict[str, float] | None:
        requested_batch = self.replay_buffer.batch_size if batch_size is None else int(batch_size)
        minimum = max(self.replay_buffer.warmup_size, requested_batch)
        if len(self.replay_buffer) < minimum:
            return None
        batch = self.replay_buffer.sample(requested_batch)
        state = torch.as_tensor(
            np.stack([transition.state for transition in batch]),
            dtype=torch.float32,
            device=self.device,
        )
        next_state = torch.as_tensor(
            np.stack([transition.next_state for transition in batch]),
            dtype=torch.float32,
            device=self.device,
        )
        action = torch.as_tensor(
            [transition.action for transition in batch], dtype=torch.long, device=self.device
        )
        reward = torch.as_tensor(
            [transition.reward for transition in batch], dtype=torch.float32, device=self.device
        )
        done = torch.as_tensor(
            [transition.done for transition in batch], dtype=torch.bool, device=self.device
        )
        legal_mask = torch.as_tensor(
            np.stack([transition.legal_mask for transition in batch]),
            dtype=torch.bool,
            device=self.device,
        )

        self.online_network.train()
        q_values = self.online_network(state).gather(1, action.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            next_online = self.online_network(next_state)
            next_online = next_online.masked_fill(~legal_mask, float("-inf"))
            rows_without_legal_actions = ~legal_mask.any(dim=1)
            if rows_without_legal_actions.any():
                next_online[rows_without_legal_actions] = 0.0
            next_action = torch.argmax(next_online, dim=1)
            next_target = self.target_network(next_state).gather(
                1, next_action.unsqueeze(1)
            ).squeeze(1)
            target = reward + self.gamma * next_target * (~done).float()

        # The HOODIE source contract explicitly specifies MSE.
        loss = torch.nn.functional.mse_loss(q_values, target)
        self.optimizer.zero_grad(set_to_none=True)
        loss.backward()
        if self.grad_clip_norm is not None:
            torch.nn.utils.clip_grad_norm_(
                self.online_network.parameters(), float(self.grad_clip_norm)
            )
        self.optimizer.step()
        self.training_steps += 1
        if self.soft_update_tau is not None:
            self._soft_update()
        elif (
            self.target_update_interval > 0
            and self.training_steps % self.target_update_interval == 0
        ):
            self.sync_target_network()
        return {"loss": float(loss.detach().cpu().item())}

    def _soft_update(self) -> None:
        tau = float(self.soft_update_tau)
        if not 0.0 < tau <= 1.0:
            raise ValueError("soft_update_tau must be in (0, 1]")
        with torch.no_grad():
            for target_param, online_param in zip(
                self.target_network.parameters(),
                self.online_network.parameters(),
                strict=True,
            ):
                target_param.data.mul_(1.0 - tau).add_(online_param.data, alpha=tau)
        self.target_update_steps += 1

    def sync_target_network(self) -> None:
        self.target_network.load_state_dict(self.online_network.state_dict())
        self.target_network.eval()
        self.target_update_steps += 1

    def state_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "input_dim": self.input_dim,
            "action_dim": self.action_dim,
            "hidden_dims": self.hidden_dims,
            "gamma": self.gamma,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "capacity": self.capacity,
            "warmup_size": self.warmup_size,
            "seed": self.seed,
            "device_name": str(self.device),
            "target_update_interval": self.target_update_interval,
            "soft_update_tau": self.soft_update_tau,
            "grad_clip_norm": self.grad_clip_norm,
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
        for optimizer_state in self.optimizer.state.values():
            for key, value in optimizer_state.items():
                if isinstance(value, torch.Tensor):
                    optimizer_state[key] = value.to(self.device)
        self.replay_buffer.load_state_dict(state["replay_buffer"])
        self.rng.setstate(state["rng_state"])
        if "python_random_state" in state:
            random.setstate(state["python_random_state"])
        if "numpy_random_state" in state:
            np.random.set_state(state["numpy_random_state"])
        if "torch_random_state" in state:
            torch.set_rng_state(state["torch_random_state"])
        if torch.cuda.is_available() and state.get("cuda_random_state") is not None:
            torch.cuda.set_rng_state_all(state["cuda_random_state"])
        self.training_steps = int(state.get("training_steps", 0))
        self.target_update_steps = int(state.get("target_update_steps", 0))
        self.configure(
            learning_rate=float(state.get("learning_rate", self.learning_rate)),
            batch_size=int(state.get("batch_size", self.batch_size)),
            gamma=float(state.get("gamma", self.gamma)),
            target_update_interval=int(
                state.get("target_update_interval", self.target_update_interval)
            ),
        )

    def save(self, path: str) -> None:
        torch.save(self.state_dict(), path)

    def load(self, path: str) -> None:
        self.load_state_dict(torch.load(path, map_location=self.device, weights_only=False))


ReplayTransition = Transition


class DoubleDQNAgent:
    ACTION_ORDER = ("local", "horizontal", "vertical")

    def __init__(
        self,
        input_dim: int = 5,
        action_dim: int = 3,
        *,
        seed: int = 0,
        hidden_dims: tuple[int, ...] = (256, 256),
        learning_rate: float = 1e-3,
        gamma: float = 0.99,
        batch_size: int = 32,
        capacity: int = 10_000,
        warmup_size: int = 64,
        target_update_interval: int = 100,
        device_name: str | None = None,
    ) -> None:
        if action_dim != len(self.ACTION_ORDER):
            raise ValueError("DoubleDQNAgent currently supports the three physical action families")
        self.learner = DDQNLearner(
            input_dim=input_dim,
            action_dim=action_dim,
            hidden_dims=hidden_dims,
            seed=seed,
            learning_rate=learning_rate,
            gamma=gamma,
            batch_size=batch_size,
            capacity=capacity,
            warmup_size=warmup_size,
            target_update_interval=target_update_interval,
            device_name=device_name,
        )
        self.replay = self.learner.replay_buffer

    def select(
        self,
        features: Iterable[float],
        legal_actions: Iterable[str],
        *,
        epsilon: float = 0.0,
    ) -> str:
        legal_action_set = set(legal_actions)
        legal_indices = [
            index for index, name in enumerate(self.ACTION_ORDER) if name in legal_action_set
        ]
        if not legal_indices:
            raise ValueError("no supported legal actions available")
        feature_tuple = tuple(float(value) for value in features)
        if len(feature_tuple) != self.learner.input_dim:
            raise ValueError(
                f"feature length {len(feature_tuple)} does not match input_dim {self.learner.input_dim}"
            )
        state = torch.tensor(feature_tuple, dtype=torch.float32, device=self.learner.device)
        mask = torch.tensor(
            [index in legal_indices for index in range(len(self.ACTION_ORDER))],
            dtype=torch.bool,
            device=self.learner.device,
        )
        selected = self.learner.select_action(state, mask, epsilon)
        return self.ACTION_ORDER[selected]

    def configure(self, **kwargs: Any) -> None:
        self.learner.configure(**kwargs)

    def update(self, batch_size: int | None = None) -> float | None:
        result = self.learner.learn_from_replay(batch_size=batch_size)
        return None if result is None else float(result["loss"])

    def sync_target_network(self) -> None:
        self.learner.sync_target_network()

    def export_state(self) -> dict[str, Any]:
        return self.learner.state_dict()

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "DoubleDQNAgent":
        saved_device = str(state.get("device_name", "cpu"))
        if saved_device.startswith("cuda") and not torch.cuda.is_available():
            saved_device = "cpu"
        if saved_device.startswith("mps") and not (
            getattr(torch.backends, "mps", None) is not None
            and torch.backends.mps.is_available()
        ):
            saved_device = "cpu"
        agent = cls(
            input_dim=int(state.get("input_dim", 5)),
            action_dim=int(state.get("action_dim", 3)),
            hidden_dims=tuple(state.get("hidden_dims", (256, 256))),
            seed=int(state.get("seed", 0)),
            learning_rate=float(state.get("learning_rate", 1e-3)),
            gamma=float(state.get("gamma", 0.99)),
            batch_size=int(state.get("batch_size", 32)),
            capacity=int(state.get("capacity", 10_000)),
            warmup_size=int(state.get("warmup_size", 64)),
            target_update_interval=int(state.get("target_update_interval", 100)),
            device_name=saved_device,
        )
        agent.learner.load_state_dict(state)
        agent.replay = agent.learner.replay_buffer
        return agent
