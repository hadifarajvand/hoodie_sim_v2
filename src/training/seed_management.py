from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SeedManagement:
    training_seed: int = 0
    evaluation_seed: int = 0

    def training_episode_seed(self, episode_index: int) -> int:
        return self.training_seed + episode_index

    def evaluation_episode_seed(self, episode_index: int) -> int:
        return self.evaluation_seed + episode_index
