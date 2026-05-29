from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class MinimumLatencyEstimationOffloader:
    def select(self, *, legal_destination_ids: list[str], queue_delay: dict[str, float], transmission_delay: dict[str, float], waiting_time: dict[str, float], forecast_load: dict[str, float]) -> str:
        best_destination = None
        best_score = None
        for destination in legal_destination_ids:
            score = queue_delay.get(destination, 0.0) + transmission_delay.get(destination, 0.0) + waiting_time.get(destination, 0.0) + forecast_load.get(destination, 0.0)
            if best_score is None or score < best_score:
                best_score = score
                best_destination = destination
        if best_destination is None:
            raise ValueError("no legal destinations")
        return best_destination

