from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from src.policies.interface import PolicyContext, ReplayTrainablePolicy

from .ddqn import DoubleDQNAgent, ReplayTransition
from .history_builder import HistoryBuilder
from .observation_schema import ObservationSchema


_ACTION_INDEX = {
    "local": 0,
    "compute_local": 0,
    "horizontal": 1,
    "offload_horizontal": 1,
    "vertical": 2,
    "offload_vertical": 2,
    "cloud": 2,
}


@dataclass(slots=True)
class HoodieAgent(ReplayTrainablePolicy):
    policy_name: str = "HOODIE"
    observation_schema: ObservationSchema = field(default_factory=ObservationSchema)
    history_builder: HistoryBuilder = field(default_factory=HistoryBuilder)
    learner: DoubleDQNAgent = field(default_factory=DoubleDQNAgent)
    use_lstm: bool = True
    exploration_epsilon: float = 0.0
    causal_history: list[dict[str, Any]] = field(default_factory=list)

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
    ) -> "HoodieAgent":
        schema = ObservationSchema()
        learner = DoubleDQNAgent(
            input_dim=len(schema.feature_names),
            action_dim=3,
            seed=seed,
            learning_rate=learning_rate,
            gamma=discount_factor,
            batch_size=batch_size,
            capacity=replay_capacity,
            warmup_size=batch_size,
            target_update_interval=target_update_interval,
            device_name=device_name,
        )
        return cls(observation_schema=schema, learner=learner, use_lstm=use_lstm)

    def _features(self, context: PolicyContext | dict[str, object]) -> tuple[float, ...]:
        observation = dict(context.observation if isinstance(context, PolicyContext) else context)
        # Until the explicit LSTM forecaster is attached, the causal history feature is
        # deterministic and contains past observations only. The no-LSTM ablation is zeroed.
        observation["causal_history_length"] = (
            float(len(self.causal_history)) if self.use_lstm else 0.0
        )
        if "task_size" not in observation and "size" in observation:
            observation["task_size"] = observation["size"]
        return self.observation_schema.encode(observation)

    @staticmethod
    def _canonical_legal_actions(mask: dict[str, bool]) -> tuple[str, ...]:
        legal: list[str] = []
        if mask.get("local") or mask.get("compute_local"):
            legal.append("local")
        if mask.get("horizontal") or mask.get("offload_horizontal") or any(
            key.startswith("horizontal_") and allowed for key, allowed in mask.items()
        ):
            legal.append("horizontal")
        if mask.get("vertical") or mask.get("offload_vertical") or mask.get("cloud"):
            legal.append("vertical")
        return tuple(legal)

    def choose_action(self, context: PolicyContext) -> str:
        legal_actions = self._canonical_legal_actions(context.legal_action_mask)
        features = self._features(context)
        action = self.learner.select(
            features, legal_actions, epsilon=self.exploration_epsilon
        )
        self.history_builder.record(context)
        self.causal_history.append(dict(context.observation))
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
        state_tuple = self._features(state)
        next_state_tuple = self._features(next_state)
        action_index = _ACTION_INDEX.get(str(action))
        if action_index is None:
            raise ValueError(f"unsupported action for replay: {action!r}")
        raw_mask = next_state.get("legal_action_mask", {})
        if isinstance(raw_mask, dict):
            legal = set(self._canonical_legal_actions({str(k): bool(v) for k, v in raw_mask.items()}))
        else:
            legal = {"local", "horizontal", "vertical"}
        if not legal:
            legal = {"local", "horizontal", "vertical"}
        legal_mask = np.array(
            [name in legal for name in ("local", "horizontal", "vertical")], dtype=bool
        )
        self.learner.replay.add(
            ReplayTransition(
                np.asarray(state_tuple, dtype=np.float32),
                action_index,
                float(reward),
                np.asarray(next_state_tuple, dtype=np.float32),
                bool(done),
                legal_mask,
            )
        )

    def learn_from_replay(self, batch_size: int, learning_rate: float) -> float | None:
        self.learner.configure(learning_rate=learning_rate, batch_size=batch_size)
        return self.learner.update(batch_size=batch_size)

    def sync_target_network(self) -> None:
        self.learner.sync_target_network()

    def attach_learner(self, learner: object, enabled: bool = True) -> None:
        if not enabled:
            return
        if isinstance(learner, DoubleDQNAgent):
            self.learner = learner

    def export_state(self) -> dict[str, Any]:
        return {
            "schema_version": 3,
            "policy_name": self.policy_name,
            "use_lstm": self.use_lstm,
            "exploration_epsilon": self.exploration_epsilon,
            "causal_history": list(self.causal_history),
            "learner": self.learner.export_state(),
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "HoodieAgent":
        # Accept both the wrapped HoodieAgent state and legacy raw DDQN state.
        wrapped = state.get("learner") if isinstance(state.get("learner"), dict) else None
        learner_state = wrapped or (
            state if "online_state_dict" in state and "target_state_dict" in state else {}
        )
        agent = cls(use_lstm=bool(state.get("use_lstm", True)))
        agent.exploration_epsilon = float(state.get("exploration_epsilon", 0.0))
        agent.causal_history = list(state.get("causal_history", []))
        if learner_state:
            agent.learner = DoubleDQNAgent.from_state(learner_state)
        return agent
