from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.policies.policy_interface import PolicyContext, SharedPolicy

from .ddqn import DoubleDQNAgent, ReplayTransition
from .history_builder import HistoryBuilder
from .observation_schema import ObservationSchema


@dataclass(slots=True)
class HoodieAgent(SharedPolicy):
    policy_name: str = "HOODIE"
    observation_schema: ObservationSchema = field(default_factory=ObservationSchema)
    history_builder: HistoryBuilder = field(default_factory=HistoryBuilder)
    learner: DoubleDQNAgent = field(default_factory=DoubleDQNAgent)
    use_lstm: bool = True
    causal_history: list[dict[str, Any]] = field(default_factory=list)

    def _features(self, context: PolicyContext) -> tuple[float, ...]:
        observation = dict(context.observation)
        observation["causal_history_length"] = float(len(self.causal_history))
        return self.observation_schema.encode(observation)

    def choose_action(self, context: PolicyContext) -> str:
        legal_actions = tuple(action for action, allowed in context.legal_action_mask.items() if allowed)
        features = self._features(context)
        action = self.learner.select(features, legal_actions)
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
        state_tuple = self.observation_schema.encode(state)
        next_state_tuple = self.observation_schema.encode(next_state)
        self.learner.replay.add(ReplayTransition(state_tuple, action, reward, next_state_tuple, done))

    def learn_from_replay(self, batch_size: int, learning_rate: float) -> int:
        self.learner.learning_rate = learning_rate
        self.learner.batch_size = batch_size
        return self.learner.update()

    def sync_target_network(self) -> None:
        self.learner.target.value_bias = self.learner.online.value_bias
        self.learner.target.advantage_biases = dict(self.learner.online.advantage_biases)

    def export_state(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "policy_name": self.policy_name,
            "use_lstm": self.use_lstm,
            "causal_history": list(self.causal_history),
            "online": {
                "value_bias": self.learner.online.value_bias,
                "advantage_biases": dict(self.learner.online.advantage_biases),
            },
            "target": {
                "value_bias": self.learner.target.value_bias,
                "advantage_biases": dict(self.learner.target.advantage_biases),
            },
            "replay": [transition.__dict__ for transition in self.learner.replay.items],
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "HoodieAgent":
        agent = cls(use_lstm=bool(state.get("use_lstm", True)))
        agent.causal_history = list(state.get("causal_history", []))
        online = state.get("online", {})
        target = state.get("target", {})
        agent.learner.online.value_bias = float(online.get("value_bias", 0.0))
        agent.learner.online.advantage_biases = {str(k): float(v) for k, v in online.get("advantage_biases", {}).items()}
        agent.learner.target.value_bias = float(target.get("value_bias", 0.0))
        agent.learner.target.advantage_biases = {str(k): float(v) for k, v in target.get("advantage_biases", {}).items()}
        for payload in state.get("replay", []):
            agent.learner.replay.add(ReplayTransition(tuple(payload["state"]), payload["action"], float(payload["reward"]), tuple(payload["next_state"]), bool(payload["done"])))
        return agent
