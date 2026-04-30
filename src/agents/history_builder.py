from __future__ import annotations

from dataclasses import dataclass, field

from src.policies.policy_interface import PolicyContext


@dataclass(slots=True)
class HistoryWindow:
    observations: tuple[dict[str, object], ...] = ()
    legal_action_masks: tuple[dict[str, bool], ...] = ()
    trace_history: tuple[object, ...] = ()
    window_size: int = 10

    def as_features(self) -> dict[str, object]:
        return {
            "trace_history_length": len(self.trace_history),
            "observation_count": len(self.observations),
            "latest_observation": self.observations[-1] if self.observations else {},
            "latest_legal_action_mask": self.legal_action_masks[-1] if self.legal_action_masks else {},
            "window_size": self.window_size,
        }


@dataclass(slots=True)
class HistoryBuilder:
    window_size: int = 10
    observation_history: list[dict[str, object]] = field(default_factory=list)
    legal_action_history: list[dict[str, bool]] = field(default_factory=list)

    def build(self, context: PolicyContext) -> HistoryWindow:
        observations = tuple((*self.observation_history, context.observation)[-self.window_size :])
        legal_action_masks = tuple((*self.legal_action_history, context.legal_action_mask)[-self.window_size :])
        return HistoryWindow(
            observations=observations,
            legal_action_masks=legal_action_masks,
            trace_history=context.trace_history[-self.window_size :],
            window_size=self.window_size,
        )

    def record(self, context: PolicyContext) -> None:
        self.observation_history.append(dict(context.observation))
        self.legal_action_history.append(dict(context.legal_action_mask))
        if len(self.observation_history) > self.window_size:
            self.observation_history = self.observation_history[-self.window_size :]
            self.legal_action_history = self.legal_action_history[-self.window_size :]
