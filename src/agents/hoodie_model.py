from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .dueling_dqn import DuelingDQN
from .replay_buffer import Transition
from .history_builder import HistoryWindow


@dataclass(slots=True)
class HoodieModel:
    dueling_dqn: DuelingDQN = field(default_factory=DuelingDQN)
    learned_action_preferences: dict[str, float] = field(default_factory=dict)
    action_biases: dict[str, float] = field(default_factory=dict)

    def _action_hint(self, history: HistoryWindow, action: str) -> float:
        if not history.observations:
            return 0.0
        latest_observation = history.observations[-1]
        if "topology" not in latest_observation:
            return 0.0
        fallback_hints = latest_observation.get("fallback_hints")
        if not isinstance(fallback_hints, dict):
            return 0.0
        canonical_action = {
            "compute_local": "local",
            "offload_horizontal": "horizontal",
            "offload_vertical": "vertical",
        }.get(action, action)
        hint = fallback_hints.get(canonical_action)
        if isinstance(hint, (int, float)):
            return float(hint)
        return 0.0

    def forward(self, history: HistoryWindow, legal_actions: tuple[str, ...]) -> dict[str, float]:
        features = {
            "state_value": float(len(history.observations) + len(history.trace_history)),
        }
        q_values = self.dueling_dqn.q_values(features, legal_actions)
        scored_actions: dict[str, float] = {}
        for action in legal_actions:
            learned_preference = self.learned_action_preferences.get(action, 0.0)
            scored_actions[action] = (
                q_values.get(action, 0.0)
                + learned_preference
                + self._action_hint(history, action)
                + self.action_biases.get(action, 0.0)
            )
        return scored_actions

    def best_action(self, history: HistoryWindow, legal_actions: tuple[str, ...]) -> str:
        q_values = self.forward(history, legal_actions)
        if not q_values:
            raise ValueError("No legal actions available")
        return max(q_values, key=q_values.get)

    def update_action_preference(self, action: str, reward: float, learning_rate: float) -> float:
        current = self.learned_action_preferences.get(action, 0.0)
        updated = current + learning_rate * (reward - current)
        self.learned_action_preferences[action] = updated
        return updated

    def learn_from_transitions(self, transitions: tuple[Transition, ...], learning_rate: float) -> int:
        updated = 0
        for transition in transitions:
            self.update_action_preference(transition.action, transition.reward, learning_rate)
            updated += 1
        return updated

    def to_state(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "dueling_dqn": {
                "value_weight": self.dueling_dqn.value_weight,
                "advantage_weights": dict(self.dueling_dqn.advantage_weights),
            },
            "learned_action_preferences": dict(self.learned_action_preferences),
            "action_biases": dict(self.action_biases),
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "HoodieModel":
        schema_version = int(state.get("schema_version", 1))
        if schema_version != 1:
            raise ValueError(f"Unsupported HoodieModel state schema version: {schema_version}")
        dueling_state = state.get("dueling_dqn", {})
        if not isinstance(dueling_state, dict):
            raise ValueError("HoodieModel state dueling_dqn must be a mapping")
        model = cls()
        model.dueling_dqn.value_weight = float(dueling_state.get("value_weight", model.dueling_dqn.value_weight))
        advantage_weights = dueling_state.get("advantage_weights", {})
        if not isinstance(advantage_weights, dict):
            raise ValueError("HoodieModel state advantage_weights must be a mapping")
        model.dueling_dqn.advantage_weights = {str(action): float(value) for action, value in advantage_weights.items()}

        learned_preferences = state.get("learned_action_preferences", {})
        if not isinstance(learned_preferences, dict):
            raise ValueError("HoodieModel state learned_action_preferences must be a mapping")
        model.learned_action_preferences = {str(action): float(value) for action, value in learned_preferences.items()}

        action_biases = state.get("action_biases", {})
        if not isinstance(action_biases, dict):
            raise ValueError("HoodieModel state action_biases must be a mapping")
        model.action_biases = {str(action): float(value) for action, value in action_biases.items()}
        return model
