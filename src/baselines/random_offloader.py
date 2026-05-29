from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(slots=True)
class RandomOffloader:
    seed: int = 7

    def select(self, legal_destination_ids: list[str]) -> str:
        if not legal_destination_ids:
            raise ValueError("no legal destinations")
        return Random(self.seed).choice(list(legal_destination_ids))

