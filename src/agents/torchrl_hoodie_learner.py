from __future__ import annotations

from dataclasses import dataclass, field
from importlib.util import find_spec
from typing import Any, Iterable

from .replay_buffer import Transition

_TORCH_AVAILABLE = find_spec("torch") is not None
_TORCHRL_AVAILABLE = find_spec("torchrl") is not None


def _as_transition_dict(transition: Transition | dict[str, Any]) -> dict[str, Any]:
    if isinstance(transition, Transition):
        return {
            "state": transition.state,
            "action": transition.action,
            "reward": transition.reward,
            "next_state": transition.next_state,
            "done": transition.done,
        }
    if not isinstance(transition, dict):
        raise TypeError("Transition must be a dataclass Transition or a mapping")
    return transition


@dataclass(slots=True)
class TorchRLHoodieLearner:
    learned_action_preferences: dict[str, float] = field(default_factory=dict)
    schema_version: int = 1

    @staticmethod
    def is_available() -> bool:
        return _TORCH_AVAILABLE and _TORCHRL_AVAILABLE

    @classmethod
    def require_available(cls) -> None:
        if not cls.is_available():
            raise RuntimeError("TorchRL learner is unavailable because torch and/or torchrl are not installed")

    def score(self, adapted_state: dict[str, Any]) -> dict[str, Any]:
        legal_actions = tuple(adapted_state.get("legal_actions", ()))
        if not legal_actions:
            raise ValueError("adapted_state.legal_actions must contain at least one action")

        action_mask_by_name = adapted_state.get("action_mask_by_name")
        if action_mask_by_name is None:
            action_mask = tuple(adapted_state.get("action_mask", ()))
            action_mask_by_name = {
                action: float(mask_value)
                for action, mask_value in zip(legal_actions, action_mask, strict=False)
            }
        if not isinstance(action_mask_by_name, dict):
            raise TypeError("adapted_state.action_mask_by_name must be a mapping when provided")

        scores: dict[str, float] = {}
        for index, action in enumerate(legal_actions):
            if float(action_mask_by_name.get(action, 0.0)) <= 0.0:
                continue
            features = adapted_state.get("features", ())
            feature_value = float(features[index % len(features)]) if features else 0.0
            scores[action] = feature_value + self.learned_action_preferences.get(action, 0.0)

        return {
            "schema_version": self.schema_version,
            "legal_actions": legal_actions,
            "action_scores": scores,
            "action_mask_by_name": {
                action: float(action_mask_by_name.get(action, 0.0)) for action in legal_actions if float(action_mask_by_name.get(action, 0.0)) > 0.0
            },
        }

    def update(self, transitions: Iterable[Transition | dict[str, Any]], learning_rate: float) -> int:
        updated = 0
        for transition in transitions:
            payload = _as_transition_dict(transition)
            action = str(payload["action"])
            reward = float(payload["reward"])
            current = self.learned_action_preferences.get(action, 0.0)
            self.learned_action_preferences[action] = current + learning_rate * (reward - current)
            updated += 1
        return updated

    def state_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "learned_action_preferences": {
                action: self.learned_action_preferences[action]
                for action in sorted(self.learned_action_preferences)
            },
        }

    def load_state_dict(self, state: dict[str, Any]) -> None:
        schema_version = int(state.get("schema_version", 1))
        if schema_version != self.schema_version:
            raise ValueError(f"Unsupported TorchRLHoodieLearner state schema version: {schema_version}")
        learned = state.get("learned_action_preferences", {})
        if not isinstance(learned, dict):
            raise TypeError("learned_action_preferences must be a mapping")
        self.learned_action_preferences = {str(action): float(value) for action, value in learned.items()}
