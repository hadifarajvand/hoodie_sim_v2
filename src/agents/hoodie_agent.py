from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from src.policies.interface import PolicyContext, ReplayTrainablePolicy

from .ddqn import DoubleDQNAgent, ReplayTransition
from .history_builder import HistoryBuilder
from .observation_schema import ObservationSchema
from .recurrent_ddqn import RecurrentDoubleDQNAgent

_ACTION_INDEX = {
    "local": 0,
    "compute_local": 0,
    "horizontal": 1,
    "offload_horizontal": 1,
    "vertical": 2,
    "offload_vertical": 2,
    "cloud": 2,
}

Learner = DoubleDQNAgent | RecurrentDoubleDQNAgent


@dataclass(slots=True)
class HoodieAgent(ReplayTrainablePolicy):
    policy_name: str = "HOODIE"
    observation_schema: ObservationSchema = field(default_factory=ObservationSchema)
    history_builder: HistoryBuilder = field(default_factory=HistoryBuilder)
    learner: Learner = field(default_factory=DoubleDQNAgent)
    use_lstm: bool = True
    exploration_epsilon: float = 0.0
    causal_history: list[tuple[float, ...]] = field(default_factory=list)
    decision_windows: dict[str, list[list[float]]] = field(default_factory=dict)

    @classmethod
    def configured(
        cls,
        *,
        seed: int,
        use_lstm: bool,
        learning_rate: float,
        discount_factor: float,
        batch_size: int,
        replay_capacity: int,
        target_update_interval: int,
        device_name: str | None = None,
        hidden_dims: tuple[int, ...] = (1024, 1024, 1024),
        lookback: int = 10,
        lstm_hidden: int = 20,
    ) -> "HoodieAgent":
        schema = ObservationSchema()
        learner = RecurrentDoubleDQNAgent(
            state_dim=len(schema.feature_names),
            lookback=lookback,
            seed=seed,
            hidden_dims=hidden_dims,
            lstm_hidden=lstm_hidden,
            use_lstm=use_lstm,
            learning_rate=learning_rate,
            gamma=discount_factor,
            batch_size=batch_size,
            capacity=replay_capacity,
            warmup_size=batch_size,
            target_update_interval=target_update_interval,
            device_name=device_name,
        )
        return cls(
            observation_schema=schema,
            learner=learner,
            use_lstm=use_lstm,
        )

    def _history_limit(self) -> int:
        return self.learner.lookback if isinstance(self.learner, RecurrentDoubleDQNAgent) else 1

    def _trim_history(self) -> None:
        limit = self._history_limit()
        if len(self.causal_history) > limit:
            del self.causal_history[:-limit]

    def _feature_vector(
        self, context: PolicyContext | dict[str, object]
    ) -> tuple[float, ...]:
        observation = dict(
            context.observation if isinstance(context, PolicyContext) else context
        )
        if "task_size" not in observation and "size" in observation:
            observation["task_size"] = observation["size"]
        if "private_wait_time" not in observation:
            observation["private_wait_time"] = observation.get(
                "private_queue_wait", observation.get("queue_load", 0.0)
            )
        if "offload_wait_time" not in observation:
            observation["offload_wait_time"] = observation.get(
                "offloading_queue_wait", observation.get("queue_load", 0.0)
            )
        observation["causal_history_length"] = (
            float(len(self.causal_history)) if self.use_lstm else 0.0
        )
        return self.observation_schema.encode(observation)

    def _window(self, current: tuple[float, ...]) -> np.ndarray:
        if isinstance(self.learner, RecurrentDoubleDQNAgent):
            rows = list(self.causal_history[-(self.learner.lookback - 1) :]) + [
                current
            ]
            padding = [
                tuple(0.0 for _ in range(self.learner.state_dim))
                for _ in range(self.learner.lookback - len(rows))
            ]
            return np.asarray(padding + rows, dtype=np.float32)
        return np.asarray(current, dtype=np.float32)

    @staticmethod
    def _canonical_legal_actions(mask: dict[str, bool]) -> tuple[str, ...]:
        legal: list[str] = []
        if mask.get("local") or mask.get("compute_local"):
            legal.append("local")
        if mask.get("horizontal") or mask.get("offload_horizontal") or any(
            key.startswith("horizontal_") and allowed
            for key, allowed in mask.items()
        ):
            legal.append("horizontal")
        if mask.get("vertical") or mask.get("offload_vertical") or mask.get("cloud"):
            legal.append("vertical")
        return tuple(legal)

    def choose_action(self, context: PolicyContext) -> str:
        legal_actions = self._canonical_legal_actions(context.legal_action_mask)
        features = self._feature_vector(context)
        state = self._window(features)
        action = self.learner.select(
            state, legal_actions, epsilon=self.exploration_epsilon
        )
        task_id = str(context.observation.get("task_id", len(self.decision_windows)))
        self.decision_windows[task_id] = state.tolist()
        self.history_builder.record(context)
        self.causal_history.append(features)
        self._trim_history()
        return action

    def record_transition(
        self,
        state: dict[str, object],
        action: str,
        reward: float,
        next_state: dict[str, object],
        done: bool,
        *,
        delta_slots: int = 1,
    ) -> None:
        del delta_slots
        action_index = _ACTION_INDEX.get(str(action))
        if action_index is None:
            raise ValueError(f"unsupported action for replay: {action!r}")
        task_id = str(state.get("task_id", ""))
        current_vector = self._feature_vector(state)
        if isinstance(self.learner, RecurrentDoubleDQNAgent):
            remembered = self.decision_windows.pop(task_id, None)
            state_value = (
                np.asarray(remembered, dtype=np.float32)
                if remembered is not None
                else self._window(current_vector)
            )
            next_value = self._window(self._feature_vector(next_state))
        else:
            state_value = np.asarray(current_vector, dtype=np.float32)
            next_value = np.asarray(
                self._feature_vector(next_state), dtype=np.float32
            )
        raw_mask = next_state.get("legal_action_mask", {})
        if isinstance(raw_mask, dict):
            legal = set(
                self._canonical_legal_actions(
                    {str(key): bool(value) for key, value in raw_mask.items()}
                )
            )
        else:
            legal = {"local", "horizontal", "vertical"}
        if not legal:
            legal = {"local", "horizontal", "vertical"}
        legal_mask = np.asarray(
            [name in legal for name in ("local", "horizontal", "vertical")],
            dtype=bool,
        )
        if isinstance(self.learner, RecurrentDoubleDQNAgent):
            self.learner.learner.record_transition(
                state_value,
                action_index,
                float(reward),
                next_value,
                bool(done),
                legal_mask,
            )
        else:
            self.learner.replay.add(
                ReplayTransition(
                    state_value,
                    action_index,
                    float(reward),
                    next_value,
                    bool(done),
                    legal_mask,
                )
            )

    def learn_from_replay(
        self, batch_size: int, learning_rate: float
    ) -> float | None:
        self.learner.configure(
            learning_rate=learning_rate, batch_size=batch_size
        )
        return self.learner.update(batch_size=batch_size)

    def sync_target_network(self) -> None:
        self.learner.sync_target_network()

    def attach_learner(self, learner: object, enabled: bool = True) -> None:
        if enabled and isinstance(
            learner, (DoubleDQNAgent, RecurrentDoubleDQNAgent)
        ):
            self.learner = learner
            self._trim_history()

    def export_state(self) -> dict[str, Any]:
        self._trim_history()
        return {
            "schema_version": 5,
            "policy_name": self.policy_name,
            "use_lstm": self.use_lstm,
            "exploration_epsilon": self.exploration_epsilon,
            "causal_history": [list(row) for row in self.causal_history],
            "learner": self.learner.export_state(),
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "HoodieAgent":
        wrapped = (
            state.get("learner")
            if isinstance(state.get("learner"), dict)
            else None
        )
        learner_state = wrapped or (
            state
            if "online_state_dict" in state and "target_state_dict" in state
            else {}
        )
        use_lstm = bool(state.get("use_lstm", learner_state.get("use_lstm", True)))
        agent = cls(use_lstm=use_lstm)
        agent.exploration_epsilon = float(
            state.get("exploration_epsilon", 0.0)
        )
        agent.causal_history = [
            tuple(float(value) for value in row)
            for row in state.get("causal_history", [])
        ]
        if learner_state:
            if learner_state.get("learner_kind") == "recurrent_ddqn":
                agent.learner = RecurrentDoubleDQNAgent.from_state(learner_state)
                agent.learner.use_lstm = use_lstm
            else:
                agent.learner = DoubleDQNAgent.from_state(learner_state)
        agent._trim_history()
        return agent
