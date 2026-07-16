from __future__ import annotations

from typing import Any, Iterable

import numpy as np
import torch

from .recurrent_ddqn import RecurrentDDQNLearner, RecurrentDoubleDQNAgent


class DestinationRecurrentDoubleDQNAgent(RecurrentDoubleDQNAgent):
    """Recurrent DDQN with a destination-specific action vocabulary.

    The legacy learner exposed only three action families (local, horizontal, and
    vertical).  HOODIE's decision, however, must identify the actual horizontal
    destination.  This adapter keeps the proven recurrent learner implementation
    while sizing its output layer and replay masks to one local action, every legal
    horizontal destination of the owning Edge Agent, and one cloud action.
    """

    def __init__(
        self,
        *,
        state_dim: int,
        action_order: Iterable[str],
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
        order = tuple(str(action) for action in action_order)
        if len(order) < 2:
            raise ValueError("destination-specific action_order must contain at least two actions")
        if len(order) != len(set(order)):
            raise ValueError("destination-specific action_order must be unique")
        if order[0] != "local":
            raise ValueError("destination-specific action_order must start with local")
        if order[-1] != "cloud":
            raise ValueError("destination-specific action_order must end with cloud")
        invalid = [
            action
            for action in order[1:-1]
            if not action.startswith("horizontal_")
        ]
        if invalid:
            raise ValueError(f"unsupported destination actions: {invalid}")

        # RecurrentDoubleDQNAgent.select reads ACTION_ORDER through the instance,
        # so assigning it here preserves the existing selection implementation.
        self.action_order = order
        self.ACTION_ORDER = order
        self.learner = RecurrentDDQNLearner(
            state_dim=state_dim,
            action_dim=len(order),
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

    def select(
        self,
        window: np.ndarray,
        legal_actions: Iterable[str],
        *,
        epsilon: float = 0.0,
    ) -> str:
        legal = set(str(action) for action in legal_actions)
        unsupported = legal - set(self.action_order)
        if unsupported:
            raise ValueError(
                f"legal actions are absent from this learner's action vocabulary: {sorted(unsupported)}"
            )
        return super().select(window, legal, epsilon=epsilon)

    def export_state(self) -> dict[str, Any]:
        payload = self.learner.state_dict()
        payload["learner_kind"] = "destination_recurrent_ddqn"
        payload["action_order"] = list(self.action_order)
        return payload

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "DestinationRecurrentDoubleDQNAgent":
        saved_device = str(state.get("device_name", "cpu"))
        if saved_device.startswith("cuda") and not torch.cuda.is_available():
            saved_device = "cpu"
        if saved_device.startswith("mps") and not (
            getattr(torch.backends, "mps", None) is not None
            and torch.backends.mps.is_available()
        ):
            saved_device = "cpu"

        raw_order = state.get("action_order")
        if raw_order is None:
            action_dim = int(state.get("action_dim", 3))
            if action_dim != 3:
                raise ValueError(
                    "destination checkpoint is missing action_order for a non-legacy action dimension"
                )
            raw_order = ("local", "horizontal_legacy", "cloud")
        action_order = tuple(str(action) for action in raw_order)
        if int(state.get("action_dim", len(action_order))) != len(action_order):
            raise ValueError("checkpoint action_dim does not match action_order")

        agent = cls(
            state_dim=int(state["state_dim"]),
            action_order=action_order,
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
