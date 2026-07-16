from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from src.policies.interface import PolicyContext, ReplayTrainablePolicy

from .ddqn import DoubleDQNAgent, ReplayTransition
from .history_builder import HistoryBuilder
from .observation_schema import ObservationSchema


@dataclass(slots=True)
class HoodieAgent(ReplayTrainablePolicy):
    policy_name: str = "HOODIE"
    observation_schema: ObservationSchema = field(default_factory=ObservationSchema)
    history_builder: HistoryBuilder = field(default_factory=HistoryBuilder)
    learner: DoubleDQNAgent = field(default_factory=DoubleDQNAgent)
    use_lstm: bool = True
    exploration_epsilon: float = 0.0
    causal_history: list[dict[str, Any]] = field(default_factory=list)

    def _features(self, context: PolicyContext) -> tuple[float, ...]:
        observation = dict(context.observation)
        observation["causal_history_length"] = float(len(self.causal_history)) if self.use_lstm else 0.0
        return self.observation_schema.encode(observation)

    def choose_action(self, context: PolicyContext) -> str:
        legal_actions = tuple(action for action, allowed in context.legal_action_mask.items() if allowed)
        features = self._features(context)
        action = self.learner.select(features, legal_actions, epsilon=self.exploration_epsilon)
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
        state_tuple = self.observation_schema.encode(state)
        next_state_tuple = self.observation_schema.encode(next_state)
        action_index = {"local": 0, "horizontal": 1, "vertical": 2}.get(str(action))
        if action_index is None:
            raise ValueError(f"unsupported action for replay: {action!r}")
        self.learner.replay.add(ReplayTransition(state_tuple, action_index, reward, next_state_tuple, done, np.array([True, True, True])))

    def learn_from_replay(self, batch_size: int, learning_rate: float) -> int:
        self.learner.learning_rate = learning_rate
        self.learner.batch_size = batch_size
        return self.learner.update()

    def sync_target_network(self) -> None:
        self.learner.sync_target_network()

    def attach_learner(self, learner: object, enabled: bool = True) -> None:
        if not enabled:
            return
        if hasattr(learner, "to_state_dict") and hasattr(learner, "from_state_dict"):
            self.learner = learner  # type: ignore[assignment]

    def export_state(self) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "policy_name": self.policy_name,
            "use_lstm": self.use_lstm,
            "causal_history": list(self.causal_history),
            "learner": self.learner.export_state(),
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "HoodieAgent":
        agent = cls(use_lstm=bool(state.get("use_lstm", True)))
        agent.causal_history = list(state.get("causal_history", []))
        learner_state = state.get("learner", {})
        agent.learner = DoubleDQNAgent.from_state(learner_state) if learner_state else DoubleDQNAgent()
        return agent
