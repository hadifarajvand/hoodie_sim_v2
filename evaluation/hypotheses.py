from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Hypothesis:
    name: str
    metric: str
    baseline: str
    comparison_policy: str
    direction: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "metric": self.metric,
            "baseline": self.baseline,
            "comparison_policy": self.comparison_policy,
            "direction": self.direction,
        }


class HypothesisRegistry:
    def __init__(self) -> None:
        self._hypotheses = [
            Hypothesis("H1", "latency", "fifo", "heuristic", "less"),
            Hypothesis("H2", "drop_ratio", "fifo", "heuristic", "less"),
            Hypothesis("H3", "utilization", "fifo", "heuristic", "greater"),
        ]

    def list(self) -> list[Hypothesis]:
        return list(self._hypotheses)

    def to_dict(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self._hypotheses]
