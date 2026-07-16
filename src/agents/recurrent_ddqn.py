from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Any, Iterable

import numpy as np
import torch

from .ddqn import ReplayBuffer, Transition, masked_epsilon_greedy, _select_device
from .lstm_dueling_dqn import LSTM_Dueling_DQN


@dataclass(slots=True)
class RecurrentDDQNLearner:
    state_dim: int
    action_dim: int = 3
    lookback: int = 10
    hidden_dims: tuple[int, ...] = (1024, 1024, 1024)
    lstm_hidden: int = 20
    use_lstm: bool = True
    gamma: float = 0.99
    learning_rate: float = 7e-7
    batch_size: int = 64
    capacity: int = 10_000
    warmup_size: int = 64
    seed: int = 0
    device_name: str | None = None
    target_update_interval: int = 2_000
    grad_clip_norm: float | None = 10.0
    online_network: LSTM_Dueling_DQN = field(init=False)
    target_network: LSTM_Dueling_DQN = field(init=False)
    optimizer: torch.optim.Optimizer = field(init=False)
    replay_buffer: ReplayBuffer = field(init=False)
    device: torch.device = field(init=False)
    training_steps: int = field(default=0, init=False)
    target_update_steps: int = field(default=0, init=False)
    rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.device = _select_device(self.device_name)
        self.rng = random.Random(self.seed)
        self.online_network = LSTM_Dueling_DQN(
            state_dim=self.state_dim,
            lookback=self.lookback,
            num_actions=self.action_dim,
            hidden_sizes=list(self.hidden_dims),
            lstm_hidden=self.lstm_hidden,
            use_lstm=self.use_lstm,
            seed=self.seed,
        ).to(self.device)
        self.target_network = LSTM_Dueling_DQN(
            state_dim=self.state_dim,
            lookback=self.lookback,
            num_actions=self.action_dim,
            hidden_sizes=list(self.hidden_dims),
            lstm_hidden=self.lstm_hidden,
            use_lstm=self.use_lstm,
            seed=self.seed + 1,
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

    def _validate_window(self, value: np.ndarray | torch.Tensor) -> torch.Tensor:
        tensor = torch.as_tensor(value, dtype=torch.float32, device=self.device)
        if tensor.shape != (self.lookback, self.state_dim):
            raise ValueError(
                f"state window must have shape {(self.lookback, self.state_dim)}, got {tuple(tensor.shape)}"
            )
        return tensor

    def select_action(
        self,
        state_window: np.ndarray | torch.Tensor,
        legal_mask: torch.Tensor,
        epsilon: float,
        *,
        evaluation: bool = False,
    ) -> int:
        window = self._validate_window(state_window)
        self.online_network.eval()
        with torch.no_grad():
            q_values = self.online_network(window.unsqueeze(0)).squeeze(0)
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
        state_array = np.asarray(state, dtype=np.float32)
        next_array = np.asarray(next_state, dtype=np.float32)
        if state_array.shape != (self.lookback, self.state_dim):
            raise ValueError("invalid recurrent replay state shape")
        if next_array.shape != (self.lookback, self.state_dim):
            raise ValueError("invalid recurrent replay next-state shape")
        mask = np.asarray(legal_mask, dtype=bool)
        if mask.shape != (self.action_dim,):
            raise ValueError("legal_mask shape does not match action_dim")
        self.replay_buffer.add(
            Transition(
                state=state_array,
                action=int(action),
                reward=float(reward),
                next_state=next_array,
                done=bool(done),
                legal_mask=mask,
            )
        )

    def learn_from_replay(self, batch_size: int | None = None) -> dict[str, float] | None:
        requested = self.batch_size if batch_size is None else int(batch_size)
        if len(self.replay_buffer) < max(self.warmup_size, requested):
            return None
        batch = self.replay_buffer.sample(requested)
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
            next_online = self.online_network(next_state).masked_fill(
                ~legal_mask, float("-inf")
            )
            no_legal = ~legal_mask.any(dim=1)
            if no_legal.any():
                next_online[no_legal] = 0.0
            next_action = torch.argmax(next_online, dim=1)
            next_target = self.target_network(next_state).gather(
                1, next_action.unsqueeze(1)
            ).squeeze(1)
            target = reward + self.gamma * next_target * (~done).float()
        loss = torch.nn.functional.mse_loss(q_values, target)
        self.optimizer.zero_grad(set_to_none=True)
        loss.backward()
        if self.grad_clip_norm is not None:
            torch.nn.utils.clip_grad_norm_(
                self.online_network.parameters(), float(self.grad_clip_norm)
            )
        self.optimizer.step()
        self.training_steps += 1
        if (
            self.target_update_interval > 0
            and self.training_steps % self.target_update_interval == 0
        ):
            self.sync_target_network()
        return {"loss": float(loss.detach().cpu().item())}

    def sync_target_network(self) -> None:
        self.target_network.load_state_dict(self.online_network.state_dict())
        self.target_network.eval()
        self.target_update_steps += 1

    def state_dict(self) -> dict[str, Any]:
        return {
            "learner_kind": "recurrent_ddqn",
            "schema_version": 1,
            "state_dim": self.state_dim,
            "action_dim": self.action_dim,
            "lookback": self.lookback,
            "hidden_dims": self.hidden_dims,
            "lstm_hidden": self.lstm_hidden,
            "use_lstm": self.use_lstm,
            "gamma": self.gamma,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "capacity": self.capacity,
            "warmup_size": self.warmup_size,
            "seed": self.seed,
            "device_name": str(self.device),
            "target_update_interval": self.target_update_interval,
            "grad_clip_norm": self.grad_clip_norm,
            "online_state_dict": self.online_network.state_dict(),
            "target_state_dict": self.target_network.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "replay_buffer": self.replay_buffer.state_dict(),
            "rng_state": self.rng.getstate(),
            "training_steps": self.training_steps,
            "target_update_steps": self.target_update_steps,
        }

    def load_state_dict(self, state: dict[str, Any]) -> None:
        self.online_network.load_state_dict(dict(state["online_state_dict"]))
        self.target_network.load_state_dict(dict(state["target_state_dict"]))
        self.optimizer.load_state_dict(state["optimizer_state_dict"])
        for optimizer_state in self.optimizer.state.values():
            for key, value in optimizer_state.items():
                if isinstance(value, torch.Tensor):
                    optimizer_state[key] = value.to(self.device)
        self.replay_buffer.load_state_dict(state["replay_buffer"])
        self.rng.setstate(state["rng_state"])
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


class RecurrentDoubleDQNAgent:
    ACTION_ORDER = ("local", "horizontal", "vertical")

    def __init__(
        self,
        *,
        state_dim: int,
        lookback: int = 10,
        seed: int = 0,
        hidden_dims: tuple[int, ...] = (1024, 1024, 1024),
        lstm_hidden: int = 20,
        use_lstm: bool = True,
        learning_rate: float = 7e-7,
        gamma: float = 0.99,
        batch_size: int = 64,
        capacity: int = 10_000,
        warmup_size: int = 64,
        target_update_interval: int = 2_000,
        device_name: str | None = None,
    ) -> None:
        self.learner = RecurrentDDQNLearner(
            state_dim=state_dim,
            action_dim=3,
            lookback=lookback,
            hidden_dims=hidden_dims,
            lstm_hidden=lstm_hidden,
            use_lstm=use_lstm,
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

    @property
    def use_lstm(self) -> bool:
        return self.learner.use_lstm

    @use_lstm.setter
    def use_lstm(self, enabled: bool) -> None:
        enabled = bool(enabled)
        self.learner.use_lstm = enabled
        self.learner.online_network.use_lstm = enabled
        self.learner.target_network.use_lstm = enabled

    @property
    def lookback(self) -> int:
        return self.learner.lookback

    @property
    def state_dim(self) -> int:
        return self.learner.state_dim

    def select(
        self,
        window: np.ndarray,
        legal_actions: Iterable[str],
        *,
        epsilon: float = 0.0,
    ) -> str:
        legal = set(legal_actions)
        if not legal:
            raise ValueError("no supported legal actions available")
        mask = torch.tensor(
            [name in legal for name in self.ACTION_ORDER],
            dtype=torch.bool,
            device=self.learner.device,
        )
        selected = self.learner.select_action(window, mask, epsilon)
        return self.ACTION_ORDER[selected]

    def configure(self, **kwargs: Any) -> None:
        self.learner.configure(**kwargs)

    def update(self, batch_size: int | None = None) -> float | None:
        result = self.learner.learn_from_replay(batch_size)
        return None if result is None else float(result["loss"])

    def sync_target_network(self) -> None:
        self.learner.sync_target_network()

    def export_state(self) -> dict[str, Any]:
        return self.learner.state_dict()

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "RecurrentDoubleDQNAgent":
        saved_device = str(state.get("device_name", "cpu"))
        if saved_device.startswith("cuda") and not torch.cuda.is_available():
            saved_device = "cpu"
        if saved_device.startswith("mps") and not (
            getattr(torch.backends, "mps", None) is not None
            and torch.backends.mps.is_available()
        ):
            saved_device = "cpu"
        agent = cls(
            state_dim=int(state["state_dim"]),
            lookback=int(state.get("lookback", 10)),
            seed=int(state.get("seed", 0)),
            hidden_dims=tuple(state.get("hidden_dims", (1024, 1024, 1024))),
            lstm_hidden=int(state.get("lstm_hidden", 20)),
            use_lstm=bool(state.get("use_lstm", True)),
            learning_rate=float(state.get("learning_rate", 7e-7)),
            gamma=float(state.get("gamma", 0.99)),
            batch_size=int(state.get("batch_size", 64)),
            capacity=int(state.get("capacity", 10_000)),
            warmup_size=int(state.get("warmup_size", 64)),
            target_update_interval=int(state.get("target_update_interval", 2_000)),
            device_name=saved_device,
        )
        agent.learner.load_state_dict(state)
        agent.replay = agent.learner.replay_buffer
        return agent
