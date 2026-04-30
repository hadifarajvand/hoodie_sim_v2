from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .history_builder import HistoryWindow


def _normalize_mask(legal_action_mask: dict[str, bool] | tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(legal_action_mask, tuple):
        return legal_action_mask
    return tuple(action for action, allowed in legal_action_mask.items() if allowed)


def _extract_hint_features(observation: dict[str, object]) -> dict[str, float]:
    features: dict[str, float] = {}
    slot = observation.get("slot")
    if isinstance(slot, (int, float)):
        features["slot"] = float(slot)
    queue_load = observation.get("queue_load")
    if isinstance(queue_load, (int, float)):
        features["queue_load"] = float(queue_load)
    load_hint = observation.get("load_hint")
    if isinstance(load_hint, (int, float)):
        features["load_hint"] = float(load_hint)
    topology = observation.get("topology")
    if isinstance(topology, (tuple, list)):
        features["topology_size"] = float(len(topology))
    fallback_hints = observation.get("fallback_hints")
    if isinstance(fallback_hints, dict):
        numeric_hints = [float(value) for value in fallback_hints.values() if isinstance(value, (int, float))]
        if numeric_hints:
            features["fallback_hint_count"] = float(len(numeric_hints))
            features["fallback_hint_total"] = float(sum(numeric_hints))
    return features


@dataclass(slots=True)
class TorchRLTensorAdapter:
    feature_names: tuple[str, ...] = (
        "slot",
        "queue_load",
        "load_hint",
        "topology_size",
        "fallback_hint_count",
        "fallback_hint_total",
        "history_length",
        "trace_history_length",
    )

    def adapt(self, history: HistoryWindow, legal_actions: dict[str, bool] | tuple[str, ...]) -> dict[str, object]:
        latest_observation = history.observations[-1] if history.observations else {}
        if not isinstance(latest_observation, dict):
            latest_observation = {}
        legal_action_tuple = _normalize_mask(legal_actions)
        legal_action_index = {action: index for index, action in enumerate(legal_action_tuple)}
        action_mask = tuple(1.0 for _ in legal_action_tuple)
        action_mask_by_name = {action: 1.0 for action in legal_action_tuple}
        feature_values = [0.0 for _ in self.feature_names]
        hint_features = _extract_hint_features(latest_observation)
        feature_values[0] = hint_features.get("slot", 0.0)
        feature_values[1] = hint_features.get("queue_load", 0.0)
        feature_values[2] = hint_features.get("load_hint", 0.0)
        feature_values[3] = hint_features.get("topology_size", 0.0)
        feature_values[4] = hint_features.get("fallback_hint_count", 0.0)
        feature_values[5] = hint_features.get("fallback_hint_total", 0.0)
        feature_values[6] = float(len(history.observations))
        feature_values[7] = float(len(history.trace_history))
        return {
            "schema_version": 1,
            "features": tuple(feature_values),
            "feature_names": self.feature_names,
            "legal_actions": legal_action_tuple,
            "legal_action_index": legal_action_index,
            "action_mask": action_mask,
            "action_mask_by_name": action_mask_by_name,
            "history_length": len(history.observations),
            "trace_history_length": len(history.trace_history),
            "latest_observation": latest_observation,
        }

