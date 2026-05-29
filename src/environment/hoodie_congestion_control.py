from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class HoodieCongestionControl:
    dynamic_node_load_balancing: bool
    congestion_threshold: float
    queue_pressure_aware_action_filtering: bool
    fallback_escalation_when_edge_routes_congested: bool

    def overload_detection(self, queue_pressure: dict[str, float]) -> dict[str, bool]:
        return {node: pressure >= self.congestion_threshold for node, pressure in queue_pressure.items()}

    def score(self, queue_pressure: dict[str, float]) -> float:
        return sum(queue_pressure.values()) / max(len(queue_pressure), 1)

    def legal_mask(self, base_mask: list[bool], congestion_pressure: float) -> list[bool]:
        if congestion_pressure < self.congestion_threshold or not self.queue_pressure_aware_action_filtering:
            return list(base_mask)
        filtered = list(base_mask)
        for index in range(1, len(filtered) - 1):
            filtered[index] = False
        if self.fallback_escalation_when_edge_routes_congested and not any(filtered[1:-1]):
            filtered[-1] = True
        return filtered

    def get_dynamic_mask(self, *, base_mask: list[bool], queue_pressure: dict[str, float]) -> list[bool]:
        overloads = self.overload_detection(queue_pressure)
        filtered = list(base_mask)
        for index, key in enumerate(queue_pressure):
            if index < len(filtered) and overloads.get(key, False):
                filtered[index] = False
        if self.fallback_escalation_when_edge_routes_congested and not any(filtered[1:-1]) and filtered:
            filtered[-1] = True
        return filtered

    def to_dict(self) -> dict[str, Any]:
        return {
            "dynamic_node_load_balancing": self.dynamic_node_load_balancing,
            "congestion_threshold": self.congestion_threshold,
            "queue_pressure_aware_action_filtering": self.queue_pressure_aware_action_filtering,
            "fallback_escalation_when_edge_routes_congested": self.fallback_escalation_when_edge_routes_congested,
            "deterministic_congestion_scoring": True,
        }
