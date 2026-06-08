from __future__ import annotations

from collections import deque

import numpy as np

from .decision_maker_base import DescisionMakerBase


class BalancedCyclicOffloader(DescisionMakerBase):
    def __init__(self, number_of_actions, *args, **kwargs):
        self.number_of_actions = number_of_actions
        self._cycle = deque(self._build_cycle())

    def _build_cycle(self) -> list[int]:
        if self.number_of_actions <= 0:
            return [0]
        local = [0]
        cloud = [self.number_of_actions - 1] if self.number_of_actions > 1 else [0]
        horizontal = list(range(1, max(1, self.number_of_actions - 1)))
        return local + cloud + horizontal

    def choose_action(self, *args, **kwargs):
        action = self._cycle[0]
        self._cycle.rotate(-1)
        return int(action)


class MinimumLatencyEstimationOffloader(DescisionMakerBase):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "MLEO is not implemented as paper-faithful candidate-wise minimum latency estimation. Run Phase 3 before using MLEO for official Figure 10 evaluation."
        )


def official_policy_map() -> dict[str, str]:
    return {
        "HOODIE": "drl",
        "RO": "random",
        "FLC": "all_local",
        "VO": "all_vertical",
        "HO": "all_horizontal",
        "BCO": "balanced_cyclic",
        "MLEO": "mleo",
    }

