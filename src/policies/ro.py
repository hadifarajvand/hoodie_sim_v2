from __future__ import annotations

import random
from dataclasses import dataclass, field

from .common import legal_actions
from .policy_interface import PolicyContext, SharedPolicy


@dataclass(slots=True)
class RandomOffloadingPolicy(SharedPolicy):
    seed: int | None = None
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        if self.seed is not None:
            self.rng = random.Random(self.seed)

    def choose_action(self, context: PolicyContext) -> str:
        legal = legal_actions(context)
        if not legal:
            raise ValueError("No legal actions available")
        return self.rng.choice(legal)
