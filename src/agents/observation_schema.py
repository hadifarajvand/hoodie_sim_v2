from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ObservationSchema:
    feature_names: tuple[str, ...] = (
        "task_size",
        "processing_density",
        "private_wait_time",
        "offload_wait_time",
        "causal_history_length",
    )

    def encode(self, observation: dict[str, Any]) -> tuple[float, ...]:
        return tuple(float(observation.get(name, 0.0)) for name in self.feature_names)
